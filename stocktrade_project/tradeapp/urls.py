from django.urls import path, include
from . import views

app_name = 'tradeapp'

urlpatterns = [
    path('', views.home_view, name='home'),
    #　検索画面
    path('search/', views.search_view, name = "search_view"),
    path('nikkei/', views.nikkei_view, name = "nikkei_view"),#　日経グラフ
    path('dow30/', views.dow30_view, name = "dow30_view"),   #　dow30グラフ
    path('sp500/', views.sp500_view, name = "sp500_view"),   #　sp500グラフ
    path('nasdaq/', views.nasdaq_view, name = "nasdaq_view"),#　NASDAQグラフ  #ドル円グラフ
    path('dollar_yen_conversion/', views.dollar_yen_conversion_view, name = "dollar_yen_conversion_view"),
    # 購入画面
    path('buy/', views.buy_stock, name='buy_stock'),
    # 売却画面
    path('sell/', views.sell_stock, name='sell_stock'),
    # ポートフォリオ
    path('portfolio/', views.portfolio_view, name='portfolio'),
    # 残高追加
    path('add_balance/', views.add_balance, name='add_balance'),
    # 保有率
    path('holdings_ratio/', views.holdings_ratio, name='holdings_ratio'),
    # ランキング
    path("ranking/", views.ranking, name="ranking"),


    path('contact/',views.ContactView.as_view(),name='contact'),

]
