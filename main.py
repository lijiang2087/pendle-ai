import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import sys

# === CONFIG ===
PT_ADDRESS = "0x77d8f09053c28faf1e00df6511b23125d438616f"
CHAIN_ID = "34443"  # Sonic
MATURITY_DATE = datetime(2025, 6, 27)
AAVE_USDC_YIELD = 0.065

# === Fetch price from Pendle /assets/prices endpoint ===
def get_asset_price():
    chain_id = "146"  # Sonic (in v1)
    asset_address = "0x77d8f09053c28faf1e00df6511b23125d438616f"
    url = f"https://api-v2.pendle.finance/core/v1/{chain_id}/assets/prices"
    params = {'addresses': asset_address}
    print(f"Fetching asset price from: {url} with params {params}")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Full API response:", data)

        price = data.get(asset_address.lower())
        if price:
            print(f"✅ Real-time PT price: ${price:.6f}")
            return float(price)
        else:
            print("⚠️ Address not in API response.")
            return None

    except Exception as e:
        print(f"❌ Network/API error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except ValueError as e:
        print(f"❌ JSON parse error: {e}")
        return None
    except KeyError as e:
        print(f"❌ Missing key in response: {e}")
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
    print(f"Attempting to fetch price for PT Asset: {PT_ADDRESS} on Chain ID: {CHAIN_ID}")
    pt_price = get_asset_price()

    if pt_price is None:
        send_email(
            subject="⚠️ Pendle PT Price Fetch Failed",
            body="Could not retrieve price for PT-aUSDC on Sonic.",
            to_email=os.getenv("EMAIL_USER")
        )
        return

    days_to_maturity = (MATURITY_DATE - datetime.utcnow()).days
    years_to_maturity = days_to_maturity / 365
    implied_yield = (1 / pt_price - 1) / years_to_maturity
    spread = implied_yield - AAVE_USDC_YIELD

    message = f"""🟢 Pendle PT-aUSDC Yield Report

✅ Chain: Sonic (ID: {CHAIN_ID})
✅ PT Price: ${pt_price:.6f}
✅ Implied Yield: {implied_yield:.2%}
✅ Aave Benchmark: {AAVE_USDC_YIELD:.2%}
✅ Spread: {spread:.2%}
✅ Maturity: {MATURITY_DATE.date()}
✅ Days Remaining: {days_to_maturity}

{"🚀 BUY SIGNAL" if spread > 0.015 else "📊 No arbitrage signal"}
"""

    print(message)
    send_email(
        subject="📈 PT-aUSDC Yield Alert",
        body=message,
        to_email=os.getenv("EMAIL_USER")
    )

if __name__ == "__main__":
    main()
