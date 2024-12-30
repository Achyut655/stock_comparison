import { StockData, ComparisonData } from "./stock";

export function calculateChanges(data: StockData): ComparisonData {
  return {
    dailyPriceChange: calculatePercentageChange(
      data.currentPrice,
      data.yesterdayClose
    ),
    weeklyPriceChange: calculatePercentageChange(
      data.currentPrice,
      data.weeklyAvgPrice
    ),
    monthlyPriceChange: calculatePercentageChange(
      data.currentPrice,
      data.monthlyAvgPrice
    ),
    dailyVolumeChange: calculatePercentageChange(
      data.currentVolume,
      data.weeklyAvgVolume
    ),
    weeklyVolumeChange: calculatePercentageChange(
      data.currentVolume,
      data.weeklyAvgVolume
    ),
    monthlyVolumeChange: calculatePercentageChange(
      data.currentVolume,
      data.monthlyAvgVolume
    ),
  };
}

function calculatePercentageChange(current: number, previous: number): number {
  return ((current - previous) / previous) * 100;
}

export function calculateAverages(data: number[]): number {
  return data.reduce((sum, val) => sum + val, 0) / data.length;
}

export function calculateHistoricalAverages(
  historicalData: any[],
  days: number
) {
  const recentData = historicalData.slice(0, days);

  const avgPrice = calculateAverages(
    recentData.map((day) => day.close) // close is now a number after conversion
  );

  const avgVolume = calculateAverages(
    recentData.map((day) => day.volume) // volume is already a number
  );

  return { avgPrice, avgVolume };
}
