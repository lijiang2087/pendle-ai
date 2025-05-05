import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIG ===
PT_ADDRESS = "0x77d8f09053c28faf1e00df6511b23125d438616f"
MATURITY_DATE = datetime(2025, 7, 16)

# === Get Aave aUSDC yield from DeFiLlama ===
def get_aave_usdc_yield():
    try:
        url = "https://yields.llama.fi/pools"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        pools = res.json().get("data", [])

        for pool in pools:
            if (
                pool["project"].lower() == "aave-v3"
                and pool["symbol"].lower() == "ausdc"
                and "sonic" in pool["chain"].lower()
            ):
                apy = float(pool["apy"])
                print(f"✅ Aave aUSDC yield on Sonic: {apy:.2f}%")
                return apy / 100  # convert to decimal

        print("⚠️ Aave aUSDC yield not found — fallback to default")
        return 0.065
    except Exception as e:
        print(f"❌ Error fetching Aave yield: {e}")
        return 0.065

# === Get PT price from Pendle API ===
def get_asset_price():
    url = "https://api-v2.pendle.finance/core/v1/146/assets/prices"
    params = {"addresses": PT_ADDRESS}
    print(f"Fetching asset price from: {url} with params {params}")

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        print("Full API response:", data)

        price = data.get("prices", {}).get(PT_ADDRESS.lower())
        if isinstance(price, (float, int)):
            print(f"✅ Real-time PT price: ${price:.6f}")
            return float(price)
        else:
            print("⚠️ Price not found or invalid format.")
            return None
    except Exception as e:
        print(f"❌ Network/API error: {e}")
        return None

# === Email utility ===
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

# === Main logic ===
def main():
    print(f"Attempting to fetch price for PT Asset: {PT_ADDRESS}")
    pt_price = get_asset_price()

    if pt_price is None:
        send_email(
            subject="⚠️ Pendle PT Price Fetch Failed",
            body="Could not retrieve price for PT-aUSDC on Sonic.",
            to_email=os.getenv("EMAIL_USER")
        )
        return

    aave_yield = get_aave_usdc_yield()

    days_to_maturity = (MATURITY_DATE - datetime.utcnow()).days
    years_to_maturity = days_to_maturity / 365
    implied_yield = (1 / pt_price - 1) / years_to_maturity
    spread = implied_yield - aave_yield

    message = f"""🟢 Pendle PT-aUSDC Yield Report

✅ PT Price: ${pt_price:.6f}
📅 Maturity: {MATURITY_DATE.date()}
📆 Days Remaining: {days_to_maturity}

📈 Implied Yield: {implied_yield:.2%}
💰 Aave Benchmark: {aave_yield:.2%}
📊 Spread: {spread:.2%}

{"🚀 BUY SIGNAL" if spread > 0.015 else "📌 No arbitrage signal yet."}
"""

    print(message)
    send_email(
        subject="📈 PT-aUSDC Yield Alert",
        body=message,
        to_email=os.getenv("EMAIL_USER")
    )

if __name__ == "__main__":
    main()
