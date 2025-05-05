import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIG ===
PENDLE_POOL_URL = "https://yields.llama.fi/pools"
AAVE_USDC_YIELD = 0.065  # Update this if needed
MATURITY_DATE = datetime(2025, 1, 1)  # Update if PT changes

# === Fetch PT-aUSDC price from DefiLlama ===
import requests

def get_pt_ausdc_price():
    try:
        # Step 1: Get all assets
        assets_response = requests.get("https://api-v2.pendle.finance/core/v3/1/assets/all")
        assets_response.raise_for_status()
        assets = assets_response.json()

        # Step 2: Find PT-aUSDC asset
        pt_ausdc_asset = next((asset for asset in assets if "PT-aUSDC" in asset.get("name", "")), None)
        if not pt_ausdc_asset:
            print("PT-aUSDC asset not found.")
            return None

        # Step 3: Get market data for PT-aUSDC
        market_id = pt_ausdc_asset["market"]
        market_data_response = requests.get(f"https://api-v2.pendle.finance/core/v2/1/markets/{market_id}/data")
        market_data_response.raise_for_status()
        market_data = market_data_response.json()

        # Extract the price
        pt_price = market_data.get("ptPrice")
        return pt_price

    except Exception as e:
        print(f"Error fetching PT-aUSDC price: {e}")
        return None

# === Email logic ===
def send_email(subject, body, to_email):
    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        print("✅ Email sent successfully.")

# === Main Logic ===
def main():
    pt_price = get_pt_ausdc_price()
    
    if pt_price is None:
        message = "⚠️ PT-aUSDC price not found in Pendle data.\n\nCheck API availability or symbol naming."
        print(message)
        send_email(
            subject="Pendle PT-aUSDC Price Fetch Failed",
            body=message,
            to_email=os.getenv("EMAIL_USER")
        )
        return

    days_to_maturity = (MATURITY_DATE - datetime.utcnow()).days
    years_to_maturity = days_to_maturity / 365
    implied_yield = (1 / pt_price - 1) / years_to_maturity
    spread = implied_yield - AAVE_USDC_YIELD

    message = f"""🟢 Pendle PT-aUSDC Yield Report

Current PT-aUSDC price: ${pt_price:.4f}
Implied annualized yield: {implied_yield:.2%}
Aave yield: {AAVE_USDC_YIELD:.2%}
Spread: {spread:.2%}
Maturity date: {MATURITY_DATE.date()}
Days to maturity: {days_to_maturity}

{"✅ Opportunity: BUY PT" if spread > 0.015 else "ℹ️ No strong arbitrage signal"}
"""
    print(message)
    send_email(
        subject="Pendle PT-aUSDC Yield Alert",
        body=message,
        to_email=os.getenv("EMAIL_USER")
    )

if __name__ == "__main__":
    main()
