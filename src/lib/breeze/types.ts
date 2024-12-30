export interface CustomerDetailsResponse {
  Success: {
    exg_trade_date: {
      NSE: string;
      BSE: string;
      FNO: string;
      NDX: string;
    };
    exg_status: {
      NSE: "O" | "C"; // Open or Closed
      BSE: "O" | "C";
      FNO: "O" | "C";
      NDX: "O" | "C" | "X";
    };
    segments_allowed: {
      Trading: "Y" | "N";
      Equity: "Y" | "N";
      Derivatives: "Y" | "N";
      Currency: "Y" | "N";
    };
    idirect_userid: string;
    session_token: string;
    idirect_user_name: string;
    idirect_ORD_TYP: string;
    idirect_lastlogin_time: string;
    mf_holding_mode_popup_flg: "Y" | "N";
    commodity_exchange_status: "O" | "C";
    commodity_trade_date: string;
    commodity_allowed: string;
  };
  Status: number;
  Error: string | null;
}

export class MarketClosedError extends Error {
  constructor() {
    super("Market is currently closed");
    this.name = "MarketClosedError";
  }
}

export class UnauthorizedError extends Error {
  constructor() {
    super("Session has expired or is invalid");
    this.name = "UnauthorizedError";
  }
}
