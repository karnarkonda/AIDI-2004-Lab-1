"""
This Python script does the below listed actions in sequence.
1: Scans the Newswire news release contents for stocks in the news and keeps track of all news releases it ever scanned.
2: For identified stocks in news, it scrapes Stock Price & Volume figures from Yahoo finance website for 5 days prior.


STUDENT NUMBER: 100440449-77790
STUDENT NAME: AKANMU OLUKAYODE
SEMESTER: AIDI - WINTER 2021
"""


import requests as rq
import pandas as pd
import sqlite3 as databee
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup, Tag

#  These stocks are preset here to be used to render a visualization in the event no Stock ticker is in the news.
placeholder_stock_ticker = {'AAPL': 'Apple sells of 100% stock. (Dummy header)',
                            'GOOGL': 'Alphabet sells of 100% stock. (Dummy header)'}
stock_tickers = {}
stock_history = {}
price_history_days = 5  # this is the default number of stock price days in retro to fetch


def execute():
    # 1. Scan Newswire and Parse content for Stock.
    scan_parse_news()

    # 2. Scan Yahoo finance for stock symbols.
    get_stock_price_and_volume()


def scan_parse_news():
    # Scan and Parse News from Newswire Website
    page = rq.get('https://www.prnewswire.com/news-releases/news-releases-list/')
    global stock_tickers

    if page.status_code == 200:

        soup = BeautifulSoup(page.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.get('class') and 'news-release' in link.get('class'):
                print('=================')
                print("Processing: {}".format(link.get('href')))
                log_news_article(link)
                print('=================')
    else:
        print("Error fetching Webpage")


def log_news_article(link=None) -> bool:
    """
    This function checks if an Article has been previously parsed.
    :param link:
    :return: boolean
    """
    prev_logged = True
    if link:
        news_link = link.get('href')
        news_title = link.text

        # Check if Article has been previously parsed.
        prev_logged = check_article(news_title)
        if not prev_logged:
            # Parse News article content.
            scrape_parse_news_content(news_link, news_title)
            # Save article as parsed
            save_news_article(news_title, news_link)

    return prev_logged


def scrape_parse_news_content(link=None, headline=None):
    if link:
        # Get news content
        news = rq.get('https://www.prnewswire.com{}'.format(link))
        if news.status_code == 200:
            news_soup = BeautifulSoup(news.text, 'html.parser')
            for section in news_soup.find_all('section'):
                if 'release-body' in section.get('class'):
                    print('---> Found release body')
                    for child in section.children:
                        if isinstance(child, Tag):
                            # Parse the news content to search for stock tickers.
                            print("======= Child ====")
                            print(str(child.text).strip())
                            match_lst = re.findall("[A-Z]+:[A-Z]+", child.text)
                            print("=====>> Match List ===>: {}".format(match_lst))
                            # Cache stock-tickers found
                            for ticker in match_lst:
                                global stock_tickers
                                stock_tickers[ticker.split(':')[1]] = headline
        else:
            print("==>> Failed to fetch News Content <<==")


def get_stock_price_and_volume():
    global placeholder_stock_ticker, stock_tickers, stock_history
    tickers = placeholder_stock_ticker if len(stock_tickers) <= 0 else stock_tickers

    for key in tickers:
        try:
            # Get Stocks historical price data page from Yahoo finance.
            stock_history_url = 'https://finance.yahoo.com/quote/{}/history?p={}'.format(key, key)
            prices_info = rq.get(stock_history_url)

            if prices_info.status_code == 200:
                soup = BeautifulSoup(prices_info.text, 'html.parser')

                # Get Price table body from HTML DOM
                price_table_body = soup.find('table', attrs={'data-test': 'historical-prices'}).find('tbody')

                # Process the number of Price historical days required.
                count = 0
                stock_history[key] = []
                for child in price_table_body.children:
                    if count == price_history_days:
                        break
                    extract_price_row_data(child, key)
                    count = count + 1

                # Print Captured data
                print("===>> Stock History: {}".format(stock_history))

            else:
                print("==>> Check status code: {}".format(prices_info.status_code))

        except Exception as err:
            print("Exception caught: {}".format(str(err)))


def extract_price_row_data(table_row=None, stock=None):
    print(stock)
    row_capture = {}
    count = 0
    for data in table_row.children:
        # Capture date info
        if count == 0:
            print(data.text)
            row_capture['date'] = data.text
        if count == 5:
            print(data.text)
            row_capture['price'] = data.text
        if count == 6:
            print(data.text)
            row_capture['volume'] = data.text
        count = count + 1

    stock_history[stock].append(row_capture)


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


""" Database functions - (Using Sqlite 3 file based RDBMS) """


def initialize_database():
    try:
        conn = databee.connect('news.db')
        conn.execute("""CREATE TABLE IF NOT EXISTS parsed_news (
                    title varchar(5000) NOT NULL PRIMARY KEY,
                    link varchar(5000)
                    )"""
                     )
        conn.close()

    except Exception as err:
        print("Error Initialising database: {}".format(str(err)))


def check_article(art_title=None) -> bool:
    """
     A function to perform/run an article check
    :param art_title:
    :return: bool
    """
    check = False
    if art_title:
        try:
            conn = databee.connect('news.db')
            qry_resp = conn.execute(""" SELECT * FROM parsed_news WHERE title = ?""", (art_title,))
            rows = qry_resp.fetchall()
            if len(rows) > 0:
                check = True
        except Exception as err:
            print("Error in executing query: {}".format(str(err)))

    return check


def save_news_article(art_title=None, art_link=None):
    """
    A function to perform/run a Table insert

    :param art_title:
    :param art_link:
    :return:
    """
    if art_title and art_link:
        try:
            conn = databee.connect('news.db')
            conn.execute("""INSERT INTO parsed_news VALUES (?, ?)""", (art_title, art_link))
            conn.commit()
            print("Insert Done")

        except Exception as err:
            print("Error in executing query: {}".format(str(err)))

#########################################################################


# File execution starts here
if __name__ == '__main__':
    initialize_database()
    execute()
