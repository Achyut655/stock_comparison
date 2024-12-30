import axios from "axios";
import crypto from "crypto";
import {
  CustomerDetailsResponse,
  MarketClosedError,
  UnauthorizedError,
} from "./types";

interface HistoricalDataResponse {
  Success: Array<{
    close: string;
    datetime: string;
    exchange_code: string;
    expiry_date: string;
    high: string;
    low: string;
    open: string;
    open_interest: number;
    product_type: string;
    right: string;
    stock_code: string;
    strike_price: string;
    volume: number;
  }>;
  Error: string | null;
  Status: number;
}

interface QuoteResponse {
  Success: Array<{
    exchange_code: string;
    stock_code: string;
    ltp: number;
    ltt: string;
    volume: string;
    best_bid_price: number;
    best_bid_quantity: string;
    best_offer_price: number;
    best_offer_quantity: string;
    open: number;
    high: number;
    low: number;
    previous_close: number;
    ltp_percent_change: number;
    total_quantity_traded: string;
  }>;
  Status: number;
  Error: string | null;
}

export class BreezeAPI {
  private baseUrl = "https://api.icicidirect.com";
  private apiKey: string;
  private secretKey: string;
  private sessionToken: string | null = null;

  constructor(apiKey: string, secretKey: string) {
    this.apiKey = apiKey;
    this.secretKey = secretKey;
  }

  private computeChecksum(timestamp: string, data: string): string {
    const rawChecksum = `${timestamp}\r\n${data}`;
    const checksum = crypto
      .createHmac("sha256", this.secretKey)
      .update(rawChecksum)
      .digest("base64");
    return `token ${checksum}`;
  }

  private getTimestamp(): string {
    return new Date().toISOString().split(".")[0] + ".000Z";
  }

  private getISOTimestamp(): string {
    const date = new Date();
    return date.toISOString().split(".")[0] + ".000Z";
  }

  private getHeaders(data: string = "") {
    const timestamp = new Date().getTime().toString();
    return {
      "Content-Type": "application/json",
      "X-Checksum": this.computeChecksum(timestamp, data),
      "X-Timestamp": timestamp,
      "X-AppKey": this.apiKey,
      "X-SessionToken": this.sessionToken || "",
    };
  }

  async initiateLogin(): Promise<string> {
    const loginUrl = `${
      this.baseUrl
    }/apiuser/login?api_key=${encodeURIComponent(this.apiKey)}`;
    // This should redirect to the login page
    return loginUrl;
  }

  async getCustomerDetails(apiSession: string) {
    try {
      const response = await axios<CustomerDetailsResponse>({
        method: "get",
        url: `${this.baseUrl}/breezeapi/api/v1/customerdetails`,
        headers: {
          "Content-Type": "application/json",
        },
        data: JSON.stringify({
          SessionToken: apiSession,
          AppKey: this.apiKey,
        }),
      });

      const data = response.data;

      if (data.Status !== 200 || !data.Success) {
        throw new Error(data.Error || "Failed to get customer details");
      }

      // Check if market is open
      if (data.Success.exg_status.NSE !== "O") {
        throw new MarketClosedError();
      }

      // Check if equity trading is allowed
      if (data.Success.segments_allowed.Equity !== "Y") {
        throw new Error("Equity trading is not allowed for this account");
      }

      this.sessionToken = data.Success.session_token;
      return data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        throw new UnauthorizedError();
      }
      throw error;
    }
  }

  async getHistoricalData(stockCode: string, fromDate: string, toDate: string) {
    if (!this.sessionToken) throw new Error("Not authenticated");

    const url = "https://breezeapi.icicidirect.com/api/v2/historicalcharts";

    // Use full ISO date format
    const params = new URLSearchParams({
      stock_code: stockCode,
      exch_code: "NSE",
      interval: "1day",
      from_date: fromDate, // Now in format: YYYY-MM-DDT00:00:00.000Z
      to_date: toDate, // Now in format: YYYY-MM-DDT00:00:00.000Z
    });

    try {
      console.log("Historical data request:", {
        url,
        params: Object.fromEntries(params),
        headers: {
          "X-SessionToken": this.sessionToken,
          apikey: this.apiKey,
        },
      });

      const response = await axios.get<HistoricalDataResponse>(url, {
        headers: {
          "X-SessionToken": this.sessionToken,
          apikey: this.apiKey,
        },
        params,
      });
      console.log(response.data);

      if (response.data.Status !== 200) {
        throw new Error(response.data.Error!);
      }

      // Convert string values to numbers for required fields
      return response.data.Success.map((item) => ({
        ...item,
        close: parseFloat(item.close),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        open: parseFloat(item.open),
      }));
    } catch (error) {
      console.error("Historical data fetch error:", error);
      if (axios.isAxiosError(error)) {
        console.error("API error details:", error.response?.data);
      }
      throw new Error(`Failed to fetch historical data for ${stockCode}`);
    }
  }
}
