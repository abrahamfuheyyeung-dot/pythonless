import requests
from datetime import datetime

def get_exchange_rate(from_currency, to_currency):
    """Fetch exchange rate between two currencies."""
    try:
        # Using exchangerate-api.com free tier (1500 requests/month)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if to_currency.upper() not in data['rates']:
            return None
        
        return data['rates'][to_currency.upper()]
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def convert_currency(from_currency, to_currency, amount):
    """Convert amount from one currency to another."""
    # Validate amount
    try:
        amount = float(amount)
        if amount < 0:
            print("Error: Amount must be positive")
            return None
    except ValueError:
        print("Error: Invalid amount. Please enter a number.")
        return None
    
    # Get exchange rate
    rate = get_exchange_rate(from_currency, to_currency)
    
    if rate is None:
        print(f"Error: Could not find exchange rate for {from_currency} to {to_currency}")
        return None
    
    converted_amount = amount * rate
    return converted_amount, rate

def main():
    print("=" * 50)
    print("      CURRENCY CONVERTER")
    print("=" * 50)
    
    while True:
        try:
            # Get user inputs
            from_currency = input("\nEnter from currency (e.g., USD): ").strip()
            to_currency = input("Enter to currency (e.g., EUR): ").strip()
            amount_str = input("Enter amount to convert: ").strip()
            
            # Validate inputs
            if not from_currency or not to_currency:
                print("Error: Please enter both currencies")
                continue
            
            # Perform conversion
            result = convert_currency(from_currency, to_currency, amount_str)
            
            if result:
                converted_amount, rate = result
                print("\n" + "-" * 50)
                print(f"{amount_str} {from_currency.upper()} = {converted_amount:.2f} {to_currency.upper()}")
                print(f"Exchange rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
            
            # Ask if user wants to convert again
            again = input("\nConvert another amount? (yes/no): ").strip().lower()
            if again not in ['yes', 'y']:
                print("\nThank you for using the currency converter!")
                break
        
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
