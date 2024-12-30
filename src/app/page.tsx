import { Suspense } from "react";
import { getLoginUrl, handleMultipleStocks } from "../lib/breeze/actions";
import { ComparisonData } from "../lib/breeze/stock";
import { STOCK_INDICES, IndexType } from "@/lib/constants";
import { MarketClosedError, UnauthorizedError } from "@/lib/breeze/types";

function ErrorMessage({ error }: { error: Error }) {
  const message = error.message;
  let action = null;

  if (error instanceof MarketClosedError) {
    action = (
      <p className="mt-2">
        Please try again during market hours (9:15 AM - 3:30 PM IST).
      </p>
    );
  } else if (error instanceof UnauthorizedError) {
    action = (
      <a href="/login" className="mt-2 text-blue-500 underline block">
        Please login again
      </a>
    );
  }

  return (
    <div className="p-4 border border-red-300 bg-red-50 text-red-700 rounded">
      <h2 className="font-bold mb-2">Error</h2>
      <p>{message}</p>
      {action}
    </div>
  );
}

function PercentageCell({ value }: { value: number }) {
  const colorClass = value >= 0 ? "text-green-600" : "text-red-600";
  const sign = value >= 0 ? "+" : "";
  return (
    <td className={`border p-2 ${colorClass} font-semibold`}>
      {sign}
      {value.toFixed(2)}%
    </td>
  );
}

function StockInfo({
  stockCode,
  currentPrice,
}: {
  stockCode: string;
  currentPrice: number;
}) {
  return (
    <div className="mb-4 p-4 bg-gray-50 rounded">
      <h2 className="text-xl font-bold">{stockCode}</h2>
      <p className="text-gray-600">Current Price: ₹{currentPrice.toFixed(2)}</p>
    </div>
  );
}

function StockTable({
  data,
  stockCode,
  currentPrice,
}: {
  data: ComparisonData;
  stockCode: string;
  currentPrice: number;
}) {
  return (
    <>
      <StockInfo stockCode={stockCode} currentPrice={currentPrice} />
      <table className="min-w-full border">
        <thead>
          <tr>
            <th className="border p-2 bg-gray-50">Metric</th>
            <th className="border p-2 bg-gray-50">vs Yesterday</th>
            <th className="border p-2 bg-gray-50">vs Weekly Avg</th>
            <th className="border p-2 bg-gray-50">vs Monthly Avg</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border p-2 font-medium">Price Change</td>
            <PercentageCell value={data.dailyPriceChange} />
            <PercentageCell value={data.weeklyPriceChange} />
            <PercentageCell value={data.monthlyPriceChange} />
          </tr>
          <tr>
            <td className="border p-2 font-medium">Volume Change</td>
            <PercentageCell value={data.dailyVolumeChange} />
            <PercentageCell value={data.weeklyVolumeChange} />
            <PercentageCell value={data.monthlyVolumeChange} />
          </tr>
        </tbody>
      </table>
    </>
  );
}

function IndexSelector({
  currentIndex,
  apisession,
}: {
  currentIndex: IndexType;
  apisession: string;
}) {
  return (
    <form className="mb-4">
      <input type="hidden" name="apisession" value={apisession} />
      <select
        name="index"
        defaultValue={currentIndex}
        className="border p-2 mr-2"
      >
        {Object.keys(STOCK_INDICES).map((index) => (
          <option key={index} value={index}>
            {index.replace("_", " ")}
          </option>
        ))}
      </select>
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Change Index
      </button>
    </form>
  );
}

function StocksGrid({
  stocks,
}: {
  stocks: (ComparisonData & { stockCode: string; currentPrice: number })[];
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {stocks.map((stock) => (
        <div key={stock.stockCode} className="border rounded-lg p-4">
          <StockTable
            data={stock}
            stockCode={stock.stockCode}
            currentPrice={stock.currentPrice}
          />
        </div>
      ))}
    </div>
  );
}

export default async function Home({
  searchParams,
}: {
  searchParams: { apisession?: string; index?: IndexType };
}) {
  const { apisession: api_session, index = "NIFTY_50" } = searchParams;

  if (!api_session) {
    const loginUrl = await getLoginUrl();
    return (
      <div className="p-4">
        <h1 className="text-2xl mb-4">Stock Comparison</h1>
        <a href={loginUrl} className="text-blue-500 underline">
          Login to Breeze
        </a>
      </div>
    );
  }

  try {
    const stocks = await handleMultipleStocks(api_session, index as IndexType);

    return (
      <div className="p-4">
        <h1 className="text-2xl mb-4">Stock Comparison</h1>
        <IndexSelector
          currentIndex={index as IndexType}
          apisession={api_session}
        />
        <Suspense
          fallback={
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-20 bg-gray-200 rounded mb-4"></div>
                  <div className="h-40 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          }
        >
          <StocksGrid stocks={stocks} />
        </Suspense>
      </div>
    );
  } catch (error) {
    return (
      <div className="p-4">
        <h1 className="text-2xl mb-4">Stock Comparison</h1>
        <IndexSelector
          currentIndex={index as IndexType}
          apisession={api_session}
        />
        <ErrorMessage
          error={
            error instanceof Error ? error : new Error("Unknown error occurred")
          }
        />
      </div>
    );
  }
}
