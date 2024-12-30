export interface StockData {
  stockCode: string;
  currentPrice: number;
  currentVolume: number;
  yesterdayClose: number;
  weeklyAvgPrice: number;
  weeklyAvgVolume: number;
  monthlyAvgPrice: number;
  monthlyAvgVolume: number;
}

export interface PriceVolume {
  price: number;
  volume: number;
}

export interface ComparisonData {
  dailyPriceChange: number;
  weeklyPriceChange: number;
  monthlyPriceChange: number;
  dailyVolumeChange: number;
  weeklyVolumeChange: number;
  monthlyVolumeChange: number;
}
