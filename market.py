import requests
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import time


def fetch_market_data():
    url = "https://api.wallex.ir/v1/markets"

    try:
        # Send a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Extract required information from the response
        symbols = data.get('result', {}).get('symbols', {})
        grouped_data = {}
        usdt_prices = {"bid": "N/A", "ask": "N/A"}

        # First pass to find USDT coin data
        for market_name, market_info in symbols.items():
            symbol = market_info.get('symbol', 'N/A')
            stats = market_info.get('stats', {})
            bid_price = stats.get('bidPrice', 'N/A')
            ask_price = stats.get('askPrice', 'N/A')

            # Remove trailing zeros from prices
            bid_price = bid_price.rstrip('0').rstrip('.') if isinstance(bid_price, str) else bid_price
            ask_price = ask_price.rstrip('0').rstrip('.') if isinstance(ask_price, str) else ask_price

            # Check if the symbol is for USDT coin
            if symbol == "USDTTMN":
                usdt_prices = {"bid": bid_price, "ask": ask_price}
                break
        
        
        print(usdt_prices)

        # Second pass to group data
        for market_name, market_info in symbols.items():
            symbol = market_info.get('symbol', 'N/A')
            stats = market_info.get('stats', {})
            bid_price = stats.get('bidPrice', 'N/A')
            ask_price = stats.get('askPrice', 'N/A')

            # Remove trailing zeros from prices
            bid_price = bid_price.rstrip('0').rstrip('.') if isinstance(bid_price, str) else bid_price
            ask_price = ask_price.rstrip('0').rstrip('.') if isinstance(ask_price, str) else ask_price

            # Extract base coin and market type
            if symbol.endswith("TMN"):
                base_coin = symbol[:-3]
                market_type = "TMN"
            elif symbol.endswith("USDT"):
                base_coin = symbol[:-4]
                market_type = "USDT"
            else:
                continue

            # Exclude USDT coin from grouping
            if base_coin == "USDT" or base_coin == "FTM":
                continue

            # Group data by base coin
            if base_coin not in grouped_data:
                grouped_data[base_coin] = {"TMN": {"bid": "N/A", "ask": "N/A"}, "USDT": {"bid": "N/A", "ask": "N/A"}}

            grouped_data[base_coin][market_type] = {"bid": bid_price, "ask": ask_price}

        # Prepare data for DataFrame
        market_data = []
        for idx, (base_coin, prices) in enumerate(grouped_data.items(), start=1):
            tmn_bid = prices["TMN"]["bid"]
            tmn_ask = prices["TMN"]["ask"]
            usdt_bid = prices["USDT"]["bid"]
            usdt_ask = prices["USDT"]["ask"]

            tmn_mid = (sum([float(tmn_bid), float(tmn_ask)]) / 2  if tmn_bid != "N/A" and tmn_ask != "N/A" else "N/A")
            usdt_mid = (sum([float(usdt_bid), float(usdt_ask)]) / 2  if usdt_bid != "N/A" and usdt_ask != "N/A" else "N/A")
            # Calculate converted prices using USDT coin data
            sell_usdt = (float(usdt_bid) * float(usdt_prices["bid"]) if usdt_bid != "N/A" and usdt_prices["bid"] != "N/A" else "N/A")
            buy_usdt = (float(usdt_ask) * float(usdt_prices["ask"]) if usdt_ask != "N/A" and usdt_prices["ask"] != "N/A" else "N/A")
            op_buy_usdt = (float(usdt_mid) * float(usdt_prices["ask"]) if usdt_mid != "N/A" and usdt_prices["ask"] != "N/A" else "N/A")
            sop_buy_usdt = (float(usdt_bid) * float(usdt_prices["ask"]) if usdt_bid != "N/A" and usdt_prices["ask"] != "N/A" else "N/A")
            
            # Format floats to 4 decimal places
            if isinstance(sell_usdt, float):
                sell_usdt = f"{sell_usdt:.6f}"
            if isinstance(buy_usdt, float):
                buy_usdt = f"{buy_usdt:.6f}"
            if isinstance(op_buy_usdt, float):
                op_buy_usdt = f"{op_buy_usdt:.6f}"
            if isinstance(tmn_mid, float):
                tmn_mid = f"{tmn_mid:.6f}"
                tmn_mid = np.format_float_positional(float(tmn_mid), trim='-')                
                
            buy_tmn_gain = (float(sell_usdt) - float(tmn_ask) if tmn_ask != "N/A" and sell_usdt != "N/A" else "N/A")
            buy_usdt_gain = (float(tmn_bid) - float(buy_usdt) if tmn_bid != "N/A" and buy_usdt != "N/A" else "N/A")
            op_buy_tmn_gain = (float(sell_usdt) - float(tmn_mid) if tmn_mid != "N/A" and sell_usdt != "N/A" else "N/A")
            op_buy_usdt_gain = (float(tmn_bid) - float(op_buy_usdt) if tmn_bid != "N/A" and op_buy_usdt != "N/A" else "N/A")
            sop_buy_tmn_gain = (float(sell_usdt) - float(tmn_bid) if tmn_bid != "N/A" and sell_usdt != "N/A" else "N/A")
            sop_buy_usdt_gain = (float(tmn_bid) - float(sop_buy_usdt) if tmn_bid != "N/A" and sop_buy_usdt != "N/A" else "N/A")

            buy_tmn_p = (float(buy_tmn_gain) / float(tmn_ask) * 100 if buy_tmn_gain != "N/A" and tmn_ask != "N/A" else "N/A")
            buy_usdt_p = (float(buy_usdt_gain) / float(buy_usdt) * 100 if buy_usdt_gain != "N/A" and buy_usdt != "N/A" else "N/A")
            op_buy_tmn_p = (float(op_buy_tmn_gain) / float(tmn_mid) * 100 if op_buy_tmn_gain != "N/A" and tmn_mid != "N/A" else "N/A")
            op_buy_usdt_p = (float(op_buy_usdt_gain) / float(op_buy_usdt) * 100 if op_buy_usdt_gain != "N/A" and op_buy_usdt != "N/A" else "N/A")
            sop_buy_tmn_p = (float(sop_buy_tmn_gain) / float(tmn_bid) * 100 if sop_buy_tmn_gain != "N/A" and tmn_bid != "N/A" else "N/A")
            sop_buy_usdt_p = (float(sop_buy_usdt_gain) / float(sop_buy_usdt) * 100 if sop_buy_usdt_gain != "N/A" and sop_buy_usdt != "N/A" else "N/A")

            row = {
                # '#': idx,
                'Coin': base_coin,
                'tmn_bid': tmn_bid,
                'tmn_ask': tmn_ask,
                'tmn_mid': tmn_mid,
                'usdt_bid': usdt_bid,
                'usdt_ask': usdt_ask,
                'usdt_mid' : usdt_mid,
                'sell_usdt': sell_usdt,
                'buy_usdt': buy_usdt,
                'buy_tmn_p': buy_tmn_p,
                'buy_usdt_p': buy_usdt_p,
                'sop_buy_tmn_p': sop_buy_tmn_p,
                'sop_buy_usdt_p': sop_buy_usdt_p
            }
            print(row)
            market_data.append(row)


        # Convert the data into a pandas DataFrame
        df = pd.DataFrame(market_data)
        # Convert column 'A' to numeric, forcing errors to NaN
        col_a = 'sop_buy_tmn_p' # 'op_buy_tmn_p'  # 'buy_tmn_p'
        col_b = 'sop_buy_usdt_p' # 'op_buy_usdt_p'  # 'buy_usdt_p'
        df['T'] = pd.to_numeric(df[col_a], errors='coerce')

        # Filter rows where 'A_numeric' is not NaN
        filtered_df = df[df['T'].notna()]
        filtered_df['X'] = pd.to_numeric(filtered_df[col_b], errors='coerce')
        filtered_df = filtered_df[filtered_df['X'].notna()]

        filtered_df['Z'] = filtered_df[['X', 'T']].max(1)
        # filtered_df = filtered_df[filtered_df['Z'] > 1.0 ]
        # Sort by 'A_numeric'
        sorted_df = filtered_df.sort_values(by='Z', ascending=False)

        # Drop the helper column if needed
        sorted_df = sorted_df.drop(columns=['T', 'X', 'Z', 'sell_usdt', 'buy_usdt' ])
        # print(sorted_df)
        # sorted_df.reset_index(drop=True, inplace=True)

        # print(sorted_df.head(10))
        return sorted_df
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching market data: {e}")
    except ValueError:
        print("An error occurred while parsing the JSON response.")

if __name__ == "__main__":
    c = 0
    while(True):
        d = fetch_market_data()
        print('~'*120)
        c = c +1
        print(c)
        print(d.head(10))
        time.sleep(10)
        

