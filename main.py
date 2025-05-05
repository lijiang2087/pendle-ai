import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# === CONFIG ===
PENDLE_POOL_URL = "https://yields.llama.fi/pools"
AAVE_USDC_YIELD = 0.065  # Update this if needed
MATURITY_DATE = datetime(2025, 1, 1)  # Update if PT changes

"""Fetches and prints the real-time price of a specific Pendle PT asset.

This script queries the Pendle Finance API v1 /assets/prices endpoint
to retrieve the current USD price for a predefined PT asset address on a specific chain.
"""

import requests
import sys
from typing import Union

# --- Configuration ---
CHAIN_ID = 146
PT_ADDRESS = "0x77d8f09053c28faf1e00df6511b23125d438616f" # Pendle PT address for PT_USDC (Silo-20)
API_BASE_URL = "https://api-v2.pendle.finance/core"
REQUEST_TIMEOUT = 10 # Seconds
# --- End Configuration ---

def get_asset_price(chain_id: int, asset_address: str) -> Union[float, None]:
    """Fetches the price of a given asset address using the /assets/prices endpoint.

    Args:
        chain_id: The chain ID for the network.
        asset_address: The asset address to fetch the price for.

    Returns:
        The price of the asset as a float, or None if an error occurs.
    """
    url = f"{API_BASE_URL}/v1/{chain_id}/assets/prices"
    params = {
        'addresses': asset_address
    }
    print(f"Fetching asset price from: {url} with params {params}")

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        data = response.json()

        # --- Price Extraction Logic ---
        # Handles potential variations in address casing in the API response key.
        asset_price = None
        if 'prices' in data:
            prices_dict = data['prices']
            if asset_address.lower() in prices_dict:
                asset_price = prices_dict[asset_address.lower()]
            elif asset_address.upper() in prices_dict:
                 asset_price = prices_dict[asset_address.upper()]
            elif asset_address in prices_dict:
                 asset_price = prices_dict[asset_address]

        if asset_price is None:
            print(f"Error: Could not find price for address '{asset_address}' in the 'prices' dictionary.", file=sys.stderr)
            # print("Response Data:", data) # Uncomment for debugging
            return None

        # Check if the extracted price is a valid number
        if isinstance(asset_price, (int, float)):
             return float(asset_price)
        else:
            print(f"Error: Price found for '{asset_address}' is not a valid number: {asset_price}", file=sys.stderr)
            # print("Response Data:", data) # Uncomment for debugging
            return None
        # --- End Price Extraction Logic ---

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Pendle API: {e}", file=sys.stderr)
        return None
    except ValueError as e: # Catches JSONDecodeError
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return None
    except KeyError as e:
        print(f"Error: Missing expected key '{e}' in API response structure.", file=sys.stderr)
        return None

if __name__ == "__main__":
    print(f"Attempting to fetch price for PT Asset: {PT_ADDRESS} on Chain ID: {CHAIN_ID}")
    price = get_asset_price(CHAIN_ID, PT_ADDRESS)

    if price is not None:
        # Format price to 6 decimal places
        print(f"---> Real-time price: ${price:.6f}")
    else:
        print("---> Failed to retrieve asset price.")

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
    pt_price = get_asset_price()
    
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
