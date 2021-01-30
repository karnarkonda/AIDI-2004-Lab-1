
import pandas as pd
import matplotlib.pyplot as plt



#  These stocks are preset here to be used to render a visualization in the event no Stock ticker is in the news.
placeholder_stock_ticker = {'AAPL': 'Apple sells of 100% stock. (Dummy header)',
                            'GOOGL': 'Alphabet sells of 100% stock. (Dummy header)'}
stock_tickers = {}
stock_history = {}
price_history_days = 5  # this is the default number of stock price days in retro to fetch

def prepare_stock_visualizations():
    global stock_history
    tickers = placeholder_stock_ticker if len(stock_tickers) <= 0 else stock_tickers

    for key in stock_history:
        dates = [x['date'] for x in stock_history[key]]
        prices = [x['price'] for x in stock_history[key]]
        volume = [x['volume'] for x in stock_history[key]]
        df = pd.DataFrame({'x': dates, '_price': prices, '_vol': volume})
        plt.plot('x', '_price', data=df, marker='', color='skyblue', linewidth=2, label='Price')
        plt.plot('x', '_vol', data=df, color='olive', linewidth=2, label='Volume')
        plt.title(label="{}:{}".format(str(key).upper(), tickers[key]), fontdict={'fontsize': 10, 'fontweight': 'bold'})
        plt.legend(loc="upper left")
        plt.grid(b=True)
        plt.xlabel(xlabel='Date', fontdict={'fontsize': 14, 'fontweight': 'bold'})
        plt.show()
def testing(module = None):
  pass
