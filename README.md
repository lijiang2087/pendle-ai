# Pendle AI - Principal Token Yield Monitor

An automated system that monitors Principal Tokens (PTs) on Pendle Finance and sends email notifications when favorable yield opportunities are detected.

## Overview

This tool specifically tracks PT-aUSDC tokens on the Sonic network, comparing their implied yields against Aave's aUSDC lending rates. When a significant yield spread is detected (indicating a potential arbitrage opportunity), it sends an email alert.

## Features

- 🔄 Automated monitoring every 12 hours
- 📊 Real-time price fetching from Pendle Finance API
- 💰 Yield comparison against Aave's aUSDC rates
- 📧 Email notifications with detailed yield analysis
- 🚀 Buy signals when spread exceeds 1.5%

## Current Configuration

- **Token**: PT-aUSDC on Sonic network
- **Token Address**: `0x77d8f09053c28faf1e00df6511b23125d438616f`
- **Maturity Date**: July 16, 2025
- **Check Frequency**: Every 12 hours

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lijiang2087/pendle-ai.git
   cd pendle-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - `EMAIL_USER`: Your Gmail address
   - `EMAIL_PASS`: Your Gmail app password

   For local development, create a `.env` file with these variables.

4. For GitHub Actions deployment:
   - Add the environment variables to your repository secrets
   - The workflow will automatically run every 12 hours

## Usage

### Local Run
```bash
python main.py
```

### GitHub Actions
The script runs automatically every 12 hours. You can also trigger it manually from the GitHub Actions tab.

## Email Alert Format

Each alert includes:
- Current PT price
- Days remaining until maturity
- Implied yield calculation
- Aave benchmark yield
- Spread analysis
- Buy signal (if spread > 1.5%)

## Dependencies

- Python 3.10+
- requests
- smtplib (built-in)
- email (built-in)

## Contributing

Feel free to open issues or submit pull requests for any improvements.

## License

MIT License
