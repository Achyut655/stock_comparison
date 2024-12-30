"use server";

import { env } from "@/lib/env";
import { BreezeAPI } from "./api";
import { StockData, ComparisonData } from "./stock";
import {
  calculateChanges,
  calculateHistoricalAverages,
} from "./stockCalculations";
import { STOCK_INDICES, IndexType } from "../constants";

function formatDateForAPI(date: Date): string {
  // Format: YYYY-MM-DDT00:00:00.000Z
  return date.toISOString();
}

export async function getLoginUrl() {
  const api = new BreezeAPI(
    process.env.BREEZE_API_KEY!,
    process.env.BREEZE_SECRET_KEY!
  );
  return api.initiateLogin();
}

export async function handleApiSession(
  apiSession: string,
  stockCode: string = "NIFTY"
): Promise<ComparisonData & { currentPrice: number }> {
  try {
    const api = new BreezeAPI(env.BREEZE_API_KEY, env.BREEZE_SECRET_KEY);
    await api.getCustomerDetails(apiSession);

    // Get dates and convert to UTC midnight
    const today = new Date();
    today.setUTCHours(0, 0, 0, 0);

    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
    oneMonthAgo.setUTCHours(0, 0, 0, 0);

    const toDate = formatDateForAPI(today);
    const fromDate = formatDateForAPI(oneMonthAgo);

    console.log("Date range:", { fromDate, toDate }); // For debugging

    const historicalData = await api.getHistoricalData(
      stockCode,
      fromDate,
      toDate
    );

    if (!historicalData.length) {
      throw new Error("No historical data available");
    }

    // Use most recent data point for current values
    const currentData = historicalData[0];
    const weeklyAvg = calculateHistoricalAverages(historicalData, 5);
    const monthlyAvg = calculateHistoricalAverages(historicalData, 21);

    const stockData: StockData = {
      stockCode,
      currentPrice: currentData.close,
      currentVolume: currentData.volume,
      yesterdayClose: historicalData[1]?.close || currentData.close,
      weeklyAvgPrice: weeklyAvg.avgPrice,
      weeklyAvgVolume: weeklyAvg.avgVolume,
      monthlyAvgPrice: monthlyAvg.avgPrice,
      monthlyAvgVolume: monthlyAvg.avgVolume,
    };

    const result = calculateChanges(stockData);
    return {
      ...result,
      currentPrice: stockData.currentPrice,
    };
  } catch (error) {
    if (
      error instanceof Error &&
      error.message.includes("No historical data")
    ) {
      throw new Error(
        `No data available for stock code: ${stockCode}. Please check if the stock code is correct.`
      );
    }
    console.error("Error in session handling:", error);
    throw error;
  }
}

export async function handleMultipleStocks(
  apiSession: string,
  indexType: IndexType
): Promise<(ComparisonData & { stockCode: string; currentPrice: number })[]> {
  const api = new BreezeAPI(env.BREEZE_API_KEY, env.BREEZE_SECRET_KEY);
  await api.getCustomerDetails(apiSession);

  const stocks = STOCK_INDICES[indexType];
  const results = await Promise.allSettled(
    stocks.map((stock) => handleApiSession(apiSession, stock))
  );

  return results
    .map((result, index) => {
      if (result.status === "fulfilled") {
        return {
          ...result.value,
          stockCode: stocks[index],
        };
      }
      return null;
    })
    .filter((result): result is NonNullable<typeof result> => result !== null);
}
