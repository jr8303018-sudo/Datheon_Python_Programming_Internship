import csv
import sys

try:
    import yfinance as yf
except ImportError:
    print("The 'yfinance' library is required for live price lookups.")
    print("Please install it using: pip install yfinance")
    sys.exit(1)


def get_current_price(ticker):
    """Fetches the latest closing price for a given stock ticker."""
    try:
        stock = yf.Ticker(ticker.strip().upper())
        # Try to get the latest price from fast_info or history
        price = stock.fast_info.last_price
        if not price:
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        return float(price) if price else None
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None


def main():
    portfolio = {}

    print("=" * 50)
    print("       WELCOME TO THE INVESTMENT PORTFOLIO TRACKER")
    print("=" * 50)

    # 1. Collect Portfolio Positions
    while True:
        ticker = input(
            "\nEnter stock ticker symbol (e.g., AAPL, TSLA, MSFT) or type 'done' to finish: "
        ).strip()
        if ticker.lower() == "done":
            break

        if not ticker:
            print("Ticker cannot be empty. Please try again.")
            continue

        try:
            shares = float(input(f"Enter quantity of shares for {ticker.upper()}: "))
            buy_price = float(
                input(f"Enter average buy price per share for {ticker.upper()} ($): ")
            )
        except ValueError:
            print("Invalid input! Please enter numerical values for shares and price.")
            continue

        portfolio[ticker.upper()] = {"shares": shares, "buy_price": buy_price}

    if not portfolio:
        print("\nNo positions entered. Exiting program.")
        return

    # 2. Process Portfolio & Calculate Metrics
    print("\nFetching live market prices and calculating performance...")
    summary_data = []
    total_invested = 0.0
    total_current_value = 0.0

    for ticker, data in portfolio.items():
        shares = data["shares"]
        buy_price = data["buy_price"]
        invested_capital = shares * buy_price
        total_invested += invested_capital

        current_price = get_current_price(ticker)
        if current_price is None:
            print(f"Warning: Could not fetch price for {ticker}. Using buy price as fallback.")
            current_price = buy_price

        current_value = shares * current_price
        total_current_value += current_value

        gain_loss_dollar = current_value - invested_capital
        gain_loss_pct = (gain_loss_dollar / invested_capital) * 100 if invested_capital > 0 else 0.0

        summary_data.append(
            {
                "Ticker": ticker,
                "Shares": shares,
                "Buy Price ($)": round(buy_price, 2),
                "Current Price ($)": round(current_price, 2),
                "Invested Capital ($)": round(invested_capital, 2),
                "Current Value ($)": round(current_value, 2),
                "Gain/Loss ($)": round(gain_loss_dollar, 2),
                "Gain/Loss (%)": round(gain_loss_pct, 2),
            }
        )

    total_gain_loss = total_current_value - total_invested
    total_gain_loss_pct = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0.0

    # 3. Display Summary on Console
    print("\n" + "=" * 80)
    print(f"{'PORTFOLIO SUMMARY REPORT':^80}")
    print("=" * 80)
    print(
        f"{'Ticker':<8} | {'Shares':<8} | {'Buy ($)':<10} | {'Current ($)':<12} | {'Value ($)':<12} | {'Return (%)':<10}"
    )
    print("-" * 80)
    for row in summary_data:
        print(
            f"{row['Ticker']:<8} | "
            f"{row['Shares']:<8} | "
            f"{row['Buy Price ($)']:<10.2f} | "
            f"{row['Current Price ($)']:<12.2f} | "
            f"{row['Current Value ($)']:<12.2f} | "
            f"{row['Gain/Loss (%)']:>8.2f}%"
        )
    print("-" * 80)
    print(f"Total Invested Capital: ${total_invested:,.2f}")
    print(f"Total Current Value:    ${total_current_value:,.2f}")
    print(f"Total Profit / Loss:    ${total_gain_loss:,.2f} ({total_gain_loss_pct:.2f}%)")
    print("=" * 80)

    # 4. Export to CSV using Python's csv module
    csv_filename = "portfolio_summary.csv"
    try:
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = [
                "Ticker",
                "Shares",
                "Buy Price ($)",
                "Current Price ($)",
                "Invested Capital ($)",
                "Current Value ($)",
                "Gain/Loss ($)",
                "Gain/Loss (%)",
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in summary_data:
                writer.writerow(row)
            
            # Write total summary row at the end
            writer.writerow({})
            writer.writerow({
                "Ticker": "TOTAL",
                "Invested Capital ($)": round(total_invested, 2),
                "Current Value ($)": round(total_current_value, 2),
                "Gain/Loss ($)": round(total_gain_loss, 2),
                "Gain/Loss (%)": round(total_gain_loss_pct, 2),
            })
            
        print(f"\nSuccessfully exported transaction summary to '{csv_filename}'.")
    except IOError as e:
        print(f"\nError writing to CSV file: {e}")


if __name__ == "__main__":
    main()