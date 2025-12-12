import yfinance as yf
import pandas as pd

COMPANIES = {
    "Procter & Gamble": {"ticker": "PG", "type": "Public", "ir_url": "https://www.pginvestor.com/"},
    "Kimberly-Clark": {"ticker": "KMB", "type": "Public", "ir_url": "https://investor.kimberly-clark.com/"},
    "Essity": {"ticker": "ESSITY-B.ST", "type": "Public", "ir_url": "https://www.essity.com/investors/"},
    "Ontex": {"ticker": "ONTEX.BR", "type": "Public", "ir_url": "https://ontex.com/investors/"},
    "Zuru": {"ticker": None, "type": "Private", "ir_url": "https://zuru.com/"},
    "Drylock": {"ticker": None, "type": "Private", "ir_url": "https://drylocktechnologies.com/"}
}

def get_company_info(company_name):
    data = COMPANIES.get(company_name)
    if not data:
        return None
    
    info = {
        "name": company_name,
        "type": data["type"],
        "ir_url": data["ir_url"],
        "description": "Leading player in the hygiene and personal care industry."
    }

    # Static Fallback Data (Last Updated: Dec 2024)
    STATIC_FALLBACK = {
        "Procter & Gamble": {"market_cap": 401500000000, "current_price": 171.50, "currency": "USD", "sector": "Consumer Defensive", "industry": "Household & Personal Products"},
        "Kimberly-Clark": {"market_cap": 46200000000, "current_price": 136.20, "currency": "USD", "sector": "Consumer Defensive", "industry": "Household & Personal Products"},
        "Essity": {"market_cap": 16500000000, "current_price": 245.00, "currency": "SEK", "sector": "Consumer Defensive", "industry": "Household & Personal Products"},
        "Ontex": {"market_cap": 1400000000, "current_price": 17.50, "currency": "EUR", "sector": "Consumer Defensive", "industry": "Household & Personal Products"}
    }

    if data["ticker"]:
        try:
            ticker = yf.Ticker(data["ticker"])
            # Fast info fetch
            fast_info = ticker.fast_info
            
            # Check if we got valid data
            mkt_cap = fast_info.market_cap
            
            if mkt_cap is not None:
                info.update({
                    "market_cap": mkt_cap,
                    "current_price": fast_info.last_price,
                    "currency": fast_info.currency,
                    "sector": ticker.info.get('sector', 'N/A'),
                    "industry": ticker.info.get('industry', 'N/A'),
                    "website": ticker.info.get('website', data['ir_url']),
                    "long_summary": ticker.info.get('longBusinessSummary', 'No summary available.')
                })
            else:
                raise ValueError("No market cap returned")
                
        except Exception as e:
            print(f"Error fetching data for {company_name}: {e}. Using fallback.")
            # Use Fallback
            fallback = STATIC_FALLBACK.get(company_name, {})
            info.update({
                "market_cap": fallback.get("market_cap"),
                "current_price": fallback.get("current_price"),
                "currency": fallback.get("currency", "USD"),
                "sector": fallback.get("sector", "N/A"),
                "industry": fallback.get("industry", "N/A"),
                "website": data['ir_url'],
                "long_summary": "Data retrieved from offline archives due to connection issues."
            })
            info["error"] = str(e)
    else:
        # Manual data for private companies (Mock/Static for now)
        if company_name == "Zuru":
            info.update({
                "market_cap": None,
                "current_price": None,
                "currency": "USD",
                "sector": "Consumer Goods",
                "industry": "Toys & Personal Care",
                "long_summary": "Zuru is a disruptive, privately-held company known for its innovative toys and consumer goods. It does not publish public financial reports."
            })
        elif company_name == "Drylock":
            info.update({
                "market_cap": None,
                "current_price": None,
                "currency": "EUR",
                "sector": "Personal Care",
                "industry": "Hygiene Products",
                "long_summary": "Drylock Technologies is a family-owned manufacturer of hygiene products, focusing on innovation and sustainability. It publishes annual sustainability reports."
            })
            
    return info

def get_financials(company_name):
    data = COMPANIES.get(company_name)
    if not data or not data["ticker"]:
        return None
    
    try:
        ticker = yf.Ticker(data["ticker"])
        # Get annual financials
        fin = ticker.financials
        return fin
    except Exception as e:
        return None
