#https://qiita.com/tapitapi/items/9459362d8aee25137647
#https://qiita.com/hifistar/items/e1692bb8e918f129a75e

from django.shortcuts import render

from django.views.generic.base import TemplateView

import yfinance as yf

import math

from .services import get_kabuka_data, get_chart, get_portfolio

from django.shortcuts import redirect



# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'

def home_view(request):
    # 元々の株価データ
    context = get_kabuka_data()

    # ユーザーがログインしていたらポートフォリオ情報も追加
    if request.user.is_authenticated:
        context['portfolio'] = get_portfolio(request.user)
        context['balance'] = request.user.balance

    return render(request, 'tradeapp/home.html', context)


def nikkei_view(request):
    return render(request, 'tradeapp/nikkei.html')

def dow30_view(request):
    return render(request, 'tradeapp/dow30.html')

def sp500_view(request):
    return render(request, 'tradeapp/sp500.html')

def nasdaq_view(request):
    return render(request, 'tradeapp/nasdaq.html')

def dollar_yen_conversion_view(request):
    return render(request, 'tradeapp/dollar_yen_conversion.html')



import yfinance as yf
import math
from django.shortcuts import render


def search_view(request):
    stock_data = {}
    ticker_symbol = request.GET.get('ticker', '')

    # ティッカーシンボルに数字が含まれていたら .T を付ける
    if any(char.isdigit() for char in ticker_symbol) and not ticker_symbol.endswith(".T"):
        yf_symbol = ticker_symbol + ".T"
    else:
        yf_symbol = ticker_symbol

    chart_img = get_chart(yf_symbol)

    if ticker_symbol:
        ticker = yf.Ticker(yf_symbol)
        company_name = ticker.info.get("longName")

        # 当日株価データ
        hist = ticker.history(period="2d")
        if len(hist) >= 1:
            today = hist.iloc[-1]
            stock_price = math.ceil(today['Close'] * 100) / 100
            open_price = math.ceil(today['Open'] * 100) / 100
            high_price = math.ceil(today['High'] * 100) / 100
            low_price = math.ceil(today['Low'] * 100) / 100

            if len(hist) >= 2:
                prev_close = hist.iloc[-2]['Close']
                diff_price = math.ceil((stock_price - prev_close) * 100) / 100
                diff_percent = round((diff_price / prev_close) * 100, 2)
            else:
                diff_price = diff_percent = None
        else:
            stock_price = open_price = high_price = low_price = diff_price = diff_percent = None

        # 財務情報
        financials = ticker.financials

        def get_value(key):
            return financials.loc[key][0] if key in financials.index else None

        def format_trillion_billion_million(num):
            if num is None:
                return "-"
            num = float(num)
            result = ""
            if num >= 1_0000_0000_0000:
                result += f"{int(num // 1_0000_0000_0000)}兆"
                num %= 1_0000_0000_0000
            if num >= 1_0000_0000:
                result += f"{int(num // 1_0000_0000)}億"
                num %= 1_0000_0000
            if num >= 1_0000:
                result += f"{int(num // 1_0000)}万"
            return result or "-"

        stock_data = {
            'company_name': company_name,
            'chart_img': chart_img,
            'ticker': yf_symbol,
            'stock_price': stock_price,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'diff_price': diff_price,
            'diff_percent': diff_percent,
            'operating_income': format_trillion_billion_million(get_value('Operating Income')),
            'operating_expense': format_trillion_billion_million(get_value('Operating Expense')),
            'sg_and_a': format_trillion_billion_million(get_value('Selling General And Administration')),
            'gross_profit': format_trillion_billion_million(get_value('Gross Profit')),
            'cost_of_revenue': format_trillion_billion_million(get_value('Cost Of Revenue')),
            'total_revenue': format_trillion_billion_million(get_value('Total Revenue')),
            'operating_revenue': format_trillion_billion_million(get_value('Operating Revenue')),
            'net_income': format_trillion_billion_million(get_value('Net Income')),
        }

    return render(
        request,
        'tradeapp/search.html',
        {
            'stock_data': stock_data,
        }
    )






def trade_view(request):
    return render(request, 'tradeapp/trade.html')


#------------------------------------------------------------------------------------------------------------------


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio
from accounts.models import CustomUser
import yfinance as yf
from decimal import Decimal  



@login_required
def buy_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        qty = int(request.POST.get('quantity'))
        

        # 現在株価取得
        stock = yf.Ticker(ticker)
        price = Decimal(str(stock.history(period='1d')['Close'].iloc[-1]))

        user = request.user
        total_cost = price * Decimal(qty)

        if user.balance < total_cost:
            messages.error(request, "残高不足です。")
            return redirect('tradeapp:search_view')

        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            company_name=ticker,
            defaults={'purchase_price': price, 'quantity': qty}
        )

        if not created:
            total_shares = portfolio.quantity + qty
            portfolio.purchase_price = (
                portfolio.purchase_price * Decimal(portfolio.quantity)
                + price * Decimal(qty)
            ) / Decimal(total_shares)
            portfolio.quantity = total_shares
            portfolio.save()

        user.balance -= total_cost
        user.save()

        messages.success(request, f"{ticker} を {qty} 株購入しました。")
        return redirect('tradeapp:portfolio')

    return redirect('tradeapp:trade_view')



@login_required
def sell_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        qty = int(request.POST.get('quantity'))

        user = request.user

        # 保有情報を取得
        try:
            portfolio = Portfolio.objects.get(user=user, company_name=ticker)
        except Portfolio.DoesNotExist:
            messages.error(request, "保有していない銘柄です。")
            return redirect('tradeapp:portfolio_view')

        if qty > portfolio.quantity:
            messages.error(request, "保有株数を超えています。")
            return redirect('tradeapp:portfolio_view')

        # 現在株価を取得
        stock = yf.Ticker(ticker)
        price = Decimal(str(stock.history(period='1d')['Close'].iloc[-1]))

        # 売却金額（現在値 × 数量）
        sell_amount = price * Decimal(qty)

        # 利益 = 現在値 - 購入価格
        profit_per_stock = price - portfolio.purchase_price
        realized_profit = profit_per_stock * Decimal(qty)

        # 残高に売却金額を追加
        user.balance += sell_amount
        user.save()

        # 保有株数を調整
        portfolio.quantity -= qty
        if portfolio.quantity == 0:
            portfolio.delete()
        else:
            portfolio.save()

        messages.success(request, f"{ticker} を {qty} 株売却しました。（確定利益: {realized_profit} 円）")
        return redirect('tradeapp:portfolio')

    return render(request, "tradeapp/sell.html")



@login_required
def portfolio_view(request):
    portfolio_data = get_portfolio(request.user)
    return render(request, 'tradeapp/portfolio.html', {
        'portfolio': portfolio_data,
        'balance': request.user.balance
    })


@login_required
def holdings_ratio(request):
    user = request.user
    portfolio = Portfolio.objects.filter(user=user)

    labels = []
    values = []

    temp_list = []

    # 保有株の現在価格×数量を計算
    for p in portfolio:
        stock = yf.Ticker(p.company_name)
        try:
            current_price = Decimal(str(stock.history(period='1d')['Close'].iloc[-1]))
        except IndexError:
            current_price = Decimal('0')  # データがない場合は0
        total_value = float(current_price * p.quantity)
        temp_list.append((p.company_name, total_value))

    # 保有額順にソート（残高はまだ追加しない）
    temp_list.sort(key=lambda x: x[1], reverse=True)

    # 分解してラベルと値に追加
    for name, val in temp_list:
        labels.append(name)
        values.append(val)

    # 残高を最後に追加
    labels.append("残高")
    values.append(float(user.balance))

    return render(request, "tradeapp/holdings_ratio.html", {
        "labels": labels,
        "values": values,
    })





from decimal import Decimal
from django.contrib import messages

@login_required
def add_balance(request):
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))

        user = request.user
        user.balance += amount
        user.save()

        messages.success(request, f"{amount} 円を残高に追加しました！")
        return redirect("tradeapp:portfolio")

    return redirect("tradeapp:portfolio")



from .forms import ContactForm
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views.generic import FormView



class ContactView(FormView):
    # 使用するテンプレート
    template_name ='contact.html'

    # 使用するフォームクラス（forms.pyのContactForm）
    form_class = ContactForm

    # フォーム送信が成功した後のリダイレクト(reverse_lazy)先
    success_url = '/'


    # フォームから送信が行われたときに実行する関数
    def form_valid(self, form):
        # 1.データの取得
        # フォームに入力されたデータをフィールド名を指定して取得
        # cleaned_data 正しく処理・整えられたデータ
        # clean が日本語できれいにするという意味
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        title = form.cleaned_data['title']
        message = form.cleaned_data['message']

        #2.メール送信するための準備
        # メールのタイトル
        subject = 'お問い合わせ: {}'.format(title)

        # メールの本文
        message = '送信者名：{0}\nメールアドレス：{1}\n タイトル：{2}\n メッセージ：{3}'.format(name, email, title, message)
        
        # 送信元のメールアドレス
        from_email = 'utm2577223@stu.o-hara.ac.jp'
        
        # 送信先のメールアドレス(Gmail)
        to_list = [email]

        # 送信するメールの作成
        message = EmailMessage(
                                subject=subject,
                                body=message,
                                from_email=from_email,
                                to=to_list,
                                )
        
        # メールサーバーからメールの送信
        message.send()
        

      # 送信完了後に表示するメッセージ
        messages.success(
            self.request, 'お問い合わせは正常に送信されました。')
            
        return super().form_valid(form)
    

#------------------------------------------ランキング-------------------------------------------

import yfinance as yf
import pandas as pd
import os
from django.shortcuts import render
from django.conf import settings
from datetime import datetime


def ranking(request):

    # =========================
    # CSV読み込み（超高速）
    # =========================
    csv_path = os.path.join(settings.BASE_DIR, "nikkei50.csv")
    master = pd.read_csv(csv_path)

    tickers = master["code"].tolist()

    # =========================
    # 株価API（1回だけ）
    # =========================
    data = yf.download(
        tickers=tickers,
        period="2d",
        interval="1d",
        group_by="ticker",
        progress=False
    )

    rows = []

    for _, row in master.iterrows():
        code = row["code"]
        name = row["name"]

        try:
            df = data[code]

            prev_close = df["Close"].iloc[-2]
            today_close = df["Close"].iloc[-1]

            rate = (today_close - prev_close) / prev_close * 100

            rows.append({
                "code": code.replace(".T", ""),
                "name": name,
                "price": round(today_close, 0),
                "rate": round(rate, 2)
            })

        except:
            continue

    df = pd.DataFrame(rows)

    top5_up = df.sort_values("rate", ascending=False).head(5).to_dict("records")
    top5_down = df.sort_values("rate").head(5).to_dict("records")

    context = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "top5_up": top5_up,
        "top5_down": top5_down,
    }

    return render(request, "tradeapp/ranking.html", context)
