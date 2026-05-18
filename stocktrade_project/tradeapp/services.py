import yfinance as yf

import math


def get_kabuka_data():
    #日経平均を取得
    nikkei = yf.Ticker("^N225")
    #現在の株価を取得
    nikkei_price = nikkei.history(period="1d")['Close'].iloc[-1]
    #小数第２位で切り上げ
    nikkei_price = math.ceil(nikkei_price * 100) / 100

    #dowを取得
    dow30 = yf.Ticker("^DJI")
    #現在の株価を取得
    dow30_price = dow30.history(period="1d")['Close'].iloc[-1]
    #小数第２位で切り上げ
    dow30_price = math.ceil(dow30_price * 100) / 100

    #sp500を取得
    sp500 = yf.Ticker("^GSPC")
    #現在の株価を取得
    sp500_price = sp500.history(period="1d")['Close'].iloc[-1]
    #小数第２位で切り上げ
    sp500_price = math.ceil(sp500_price * 100) / 100

    #nasdaqを取得
    nasdaq = yf.Ticker("^IXIC")
    #現在の株価を取得
    nasdaq_price = nasdaq.history(period="1d")['Close'].iloc[-1]
    #小数第２位で切り上げ
    nasdaq_price = math.ceil(nasdaq_price * 100) / 100

    #ドル円を取得
    nasdaq = yf.Ticker("JPY=X")
    #現在の株価を取得
    jpy_usd_price = nasdaq.history(period="1d")['Close'].iloc[-1]
    #小数第２位で切り上げ
    jpy_usd_price = math.ceil(jpy_usd_price * 100) / 100

    
    
    context = {
        'nikkei_price': nikkei_price,
        'dow30_price' : dow30_price,
        'sp500_price' : sp500_price,
        'nasdaq_price' : nasdaq_price,
        'jpy_usd_price' : jpy_usd_price,
    }
    return context


import plotly.graph_objects as go

def get_chart(ticker_symbol: str):
    """
    与えられた銘柄コードから Plotly ローソク足チャートの HTML を返す関数
    """
    if not ticker_symbol:
        return None

    # Yahoo用のデータ取得（例：日本株は .T が必要）
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="3mo")  # 過去3ヶ月

    if hist.empty:
        return None

    # Plotly ローソク足チャート作成
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close']
            )
        ]
    )

    fig.update_layout(
        title=f"{ticker_symbol} ローソク足チャート",
        xaxis_title="日付",
        yaxis_title="株価",
        height=400,
        template="plotly_white"
    )

    # HTMLとして返す（script含む安全版）
    chart_img = fig.to_html(full_html=False, include_plotlyjs="cdn")

    return chart_img

#---------------------------------ニュース取得----------------------------------------------------
# utils/news_api.py
import requests

API_KEY = "YOUR_API_KEY"

def get_stock_news(ticker):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "apikey": API_KEY
    }
    res = requests.get(url, params=params)
    data = res.json()
    return data.get("feed", [])

#=-----------------------------------------------------------------------------------------


from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import yfinance as yf
from .models import Portfolio

def get_portfolio(user):
    """
    指定ユーザーのポートフォリオ情報を取得して計算済みデータを返す
    """
    portfolio = Portfolio.objects.filter(user=user)
    portfolio_data = []

    for p in portfolio:
        stock = yf.Ticker(p.company_name)
        # 株価取得
        history = stock.history(period='1d')
        if not history.empty:
            current_price = history['Close'].iloc[-1]
            current_price = round(current_price, 1)


        else:
            current_price = Decimal('0')  # データがない場合は0にする

        total_value = Decimal(str(current_price)) * p.quantity
        profit = (Decimal(str(current_price)) - p.purchase_price) * p.quantity
        """profit = profit.quantize(Decimal('1'))"""


        portfolio_data.append({
            "company": p.company_name,
            "purchase_price": p.purchase_price,
            "quantity": p.quantity,
            "current_price": current_price,
            "total_value": total_value,
            "profit": profit,
        })

    return portfolio_data