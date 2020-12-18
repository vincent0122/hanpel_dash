# -*- coding: utf-8 -*-

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from pandas import DataFrame

from datetime import datetime, timedelta
from datetime import datetime as dt

# change
import platform

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly import graph_objs as go
from plotly.graph_objs import *

import dash_core_components as dcc

import re
import json
import flask
import dash
import dash_table
# import matplotlib.colors as mcolors
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

# from precomputing import add_stopwords

# from dateutil import relativedelta
# from wordcloud import WordCloud, STOPWORDS
# from ldacomplaints import lda_analysis
# from sklearn.manifold import TSNE


#if platform.system() == 'Windows':
# 윈도우인 경우
#    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
#    rc('font', family=font_name)
#else:
# Mac 인 경우
#    rc('font', family='AppleGothic')

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server
app.config.suppress_callback_exceptions = True

# matplotlib.rcParams['axes.unicode_minus'] = False

# plt.rcParams['figure.figsize'] = [10, 6]
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'google-credentials.json', scope)  # Your json file here

gc = gspread.authorize(credentials)

stock = gc.open_by_key("1OScpKhy8zaWijwoEGzOsIiJWpE4bD1OokwvrkRD72Is").worksheet("재고현황")
eta = gc.open_by_key("1_0DwnDGTJm6iKEYZHwVC9mDsvIQSq_7AWTG7pckeaow").worksheet("ETA현황")
sales = gc.open_by_key("1GuIZD-JREqmDqSYDDa_iImknZRr3n9an7-zb3vklJAc").worksheet("2020")
sales19 = gc.open_by_key("1GuIZD-JREqmDqSYDDa_iImknZRr3n9an7-zb3vklJAc").worksheet("2019")
actualUse = gc.open_by_key("1OScpKhy8zaWijwoEGzOsIiJWpE4bD1OokwvrkRD72Is").worksheet("원료제품누적")
actualUse2019 = gc.open_by_key("1OScpKhy8zaWijwoEGzOsIiJWpE4bD1OokwvrkRD72Is").worksheet("2019")

stock_df = stock.get_all_values()
eta_df = eta.get_all_values()
actualUse_df = actualUse.get_all_values()
actualUse2019_df = actualUse2019.get_all_values()
sales_df = sales.get_all_values()
sales19_df = sales19.get_all_values()

stock_headers = stock_df.pop(2)
sales_headers = sales_df.pop(0)
sales19_headers = sales19_df.pop(0)
eta_headers = eta_df.pop(0)
actualUse_headers = actualUse_df.pop(0)
actualUse2019_df_headers = actualUse2019_df.pop(0)

stock_df = pd.DataFrame(stock_df, columns=stock_headers)
sales_df = pd.DataFrame(sales_df, columns=sales_headers)
sales19_df = pd.DataFrame(sales19_df, columns=sales19_headers)
eta_df = pd.DataFrame(eta_df, columns=eta_headers)
actualUse_df = pd.DataFrame(actualUse_df, columns=actualUse_headers)
actualUse2019_df = pd.DataFrame(actualUse2019_df, columns=actualUse2019_df_headers)
actUse_df = pd.concat([actualUse_df.iloc[:, [0, 2, 4]], actualUse2019_df.iloc[:, [0, 2, 4]]])

##설정값 - 시작#########
need = ['다바오DC', 'DC BROWN(로버트)', '코코맥스(프랭클린)', '코코맥스(INHILL)(52)', '코코맥스(P)', '코코맥스30', '코코맥스(W50)', '페어링파우더(FB)',
        'COCOP', 'COCOR', '코코맥스(ROYAL)', '다바오 LOW FAT', '맥주효모(중국)', '맥주효모(베트남)', '대두박', '젤라틴(고)', '젤라틴(중)', '젤라틴(저)',
        '변성타피오카', '바나나분말(톤백)', '바나나분말(지대)', '위너', '락토젠', '그로우어', '미라클', '구연산(지대)', '솔빈산칼륨(입자)', '솔빈산칼륨(가루)', '프로피온산칼슘',
        '프로틴파워(소이코밀20)', '소이코밀', 'ISP', '멀티락', '멀티락(新)', '씨센스 프리미엄', '디텍', '디텍(에이티바이오)', '케르세틴', '렌틸콩', '렌틸콩(지대)',
        '커피화분(허니텍)', '인도화분', 'CLA(유대표님 보관대행)', '바이오스플린트(유대표님 보관대행)']
untilWh = 60
last = datetime.today() + timedelta(untilWh)
tod = datetime.today()
todPlus = datetime.today() + timedelta(2)
dataRange = []
###설정값 - 종료################

##피벗 전까지 데이터 가공 -- 시작
stock_df = stock_df.drop([stock_df.index[0], stock_df.index[1]])
stock_raw = stock_df.iloc[:, [0, 2]]
stock_raw.columns = ['제품명', '수량']
stock_product = stock_df.iloc[:, [4, 6]]
stock_product.columns = ['제품명', '수량']
stock_df = stock_raw.append(stock_product)
stock_df = stock_df[stock_df.제품명.isin(need)]
stock_df['Date'] = tod

sales_df = sales_df[sales_df.제품 != ""]
sales_df.loc[:, '수량'] = sales_df.수량.str.replace(',', '')
sales_df.loc[:, '수량'] = sales_df.수량.astype(float)
sales_df.loc[:, '금액'] = sales_df.금액.str.replace(',', '')
sales_df.loc[:, '금액'] = sales_df.금액.astype(float)
sales_bar = sales_df.iloc[:, [5, 6, 7, 10, 12, 13]]

sales19_df = sales19_df[sales19_df.제품 != ""]
sales19_df.loc[:, '수량'] = sales19_df.수량.str.replace(',', '')
sales19_df.loc[:, '수량'] = sales19_df.수량.astype(float)
sales19_df.loc[:, '금액'] = sales19_df.금액.str.replace(',', '')
sales19_df.loc[:, '금액'] = sales19_df.금액.astype(float)

# for i in range(2,untilWh+2):
#     stock_df.loc[i] = stock_df.loc[tod]

stock_df.loc[:, '수량'] = stock_df.수량.str.replace(',', '')
stock_df.loc[:, '수량'] = stock_df.수량.astype(float)

eta_df = eta_df.iloc[:, [0, 5, 6, 16, 17]]
eta_df2 = eta_df[eta_df.ETA != ""]
eta_df2 = eta_df2[eta_df2.수입자 != "대한산업"]
eta_df2.ETA.replace({'월초': '/5'}, regex=True, inplace=True)
eta_df2.ETA.replace({'월중': '/15'}, regex=True, inplace=True)
eta_df2.ETA.replace({'월말': '/28'}, regex=True, inplace=True)
eta_df2.ETA.replace({'월': '/15'}, regex=True, inplace=True)
eta_df2.loc[:, '계약수량'] = eta_df2.계약수량.astype(float)
eta_df2.계약수량 = eta_df2.계약수량 * 1000
eta_df2['ETA'] = pd.to_datetime(eta_df2['ETA'], format='%m/%d')
eta_df2['ETA'] = eta_df2['ETA'].mask(eta_df2['ETA'].dt.year == 1900, eta_df2['ETA'] + pd.offsets.DateOffset(year=2020))
eta_df2['ETA'] = eta_df2['ETA'].mask(eta_df2['ETA'].dt.month == 1, eta_df2['ETA'] + pd.offsets.DateOffset(year=2021))
eta_df2['ETA'] = eta_df2['ETA'].mask(eta_df2['ETA'].dt.month == 2, eta_df2['ETA'] + pd.offsets.DateOffset(year=2021))
eta_df2['ETA'] = eta_df2['ETA'].mask(eta_df2['ETA'].dt.month == 3, eta_df2['ETA'] + pd.offsets.DateOffset(year=2021))
eta_df2['ETA'] = eta_df2['ETA'] + timedelta(7)  # ETA +7일 후 입고된다고 가정
eta_df2 = eta_df2[pd.to_datetime(eta_df2.ETA, errors='coerce') <= last]
eta_df2 = eta_df2[eta_df2.입고상태 != "완"]
eta_df2['ETA'].mask(eta_df2['입고상태'] == '준', todPlus, inplace=True)
eta_df2['ETA'].mask(eta_df2['ETA'] <= tod, todPlus, inplace=True)
eta_df2 = eta_df2.rename({'ETA': 'Date', '계약수량': '수량'}, axis='columns')
eta_df2 = eta_df2.iloc[:, [1, 2, 3]]

fixed_df = stock_df.append(eta_df2)
fixed_df = fixed_df[['Date', '제품명', '수량']]
fixed_df['Date'] = fixed_df['Date'].dt.strftime("%y/%m/%d")

for i in range(0, untilWh + 1):  # 나중에 10을 30으로 바꾸어야 함
    a = datetime.today() + timedelta(i)
    a = datetime.strftime(a, "%y/%m/%d")
    dataRange.append(a)

actUse_df = actUse_df[actUse_df.iloc[:, 2] != ""]
actUse_df = actUse_df[actUse_df.iloc[:, 1].isin(need)]
actUse_df['날짜'] = pd.to_datetime(actUse_df['날짜'], format="%Y. %m. %d")
actUse_df['날짜'] = actUse_df['날짜'].dt.strftime("%y/%m/%d")
actUse_df['사용/출고'] = actUse_df['사용/출고'].str.replace(',', '')
actUse_df['사용/출고'] = actUse_df['사용/출고'].astype(float)

a = pd.date_range(start='2019-01-01', end=datetime.today() - timedelta(1))
a = a.strftime("%y/%m/%d")
b = stock_df.제품명
raw_df = DataFrame(index=a, columns=b)
raw_df = raw_df.fillna(0)

##피벗 전까지 데이터 가공 --종료
fixed_df = fixed_df.pivot_table(index="Date", columns="제품명", values="수량", aggfunc='sum')
fixed_df.index.name = None
fixed_df.columns.name = ""
fixed_df = fixed_df.fillna(0)
fixed2_df = DataFrame(columns=fixed_df.columns, index=dataRange)
fixed2_df.index.name = None
fixed2_df.columns.name = ""
fixed2_df = fixed2_df.fillna(0)
fixed_df = fixed_df.add(fixed2_df)
fixed_df = fixed_df.fillna(0)

for i in range(1, untilWh + 1):
    fixed_df.iloc[i] = fixed_df.iloc[i - 1] + fixed_df.iloc[i]

actUse_df = actUse_df.pivot_table(index="날짜", columns="제품명", values="사용/출고", aggfunc='sum')
actUse_df = actUse_df.fillna(0)
actUse_df.columns.name = ""
actUse_df.index.name = None
raw_df.columns.name = ""
actUse_df = raw_df.add(actUse_df, fill_value=0)


##두가지 데이터 완성
# 1. fixed_df = 현재고 + ETA현황 재고(미래 입고 재고)
# 2. actUse_df = 2019년 1월부터 어제까지 아이템별 소진량

# default값 가중치 설정 110%
# option1 : 최근 x달치 평균
# option2 : 기간 설정


def SetColor(x):
    if (x < 0):
        return "#d3705a"
    else:
        return "#00754a"


# print(actUse_df)

EXTERNAL_STYLESHEETS = ["./assets/style.css"]
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
today = dt.today() - timedelta(1)
todaymt = dt.today() - timedelta(90)
today = today.strftime("%Y, %m, %d")
todaymt = todaymt.strftime("%Y, %m, %d")
list_of_products = need

salesTree = px.sunburst(sales_df,
                        path=['중분류', '제품', '거래처 중분류'],
                        values='금액',
                        color='중분류',
                        color_continuous_scale=px.colors.qualitative.Pastel,
                        hover_data={'제품': False,
                                    '거래처 중분류': False,
                                    '중분류': False})

salesTree.update_traces(hovertemplate=None, textinfo='percent root+label')

salesTree.update_layout(height=500, margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='#f2f0eb', plot_bgcolor='#f2f0eb',
                        hoverlabel=dict(
                            bgcolor="white"
                        ))

salesTree_cus = px.sunburst(sales_df,
                            path=['중분류', '거래처 중분류', '제품'],
                            values='금액',
                            color='거래처 중분류',
                            color_continuous_scale=px.colors.qualitative.Pastel)

volumeTree = px.treemap(sales_df, path=['중분류', '제품', '거래처 중분류'], values='수량', color='중분류',
                        color_continuous_scale='RdBu')

volumeTree_cus = px.treemap(sales_df, path=['거래처 중분류', '제품'], values='수량', color='거래처 중분류',
                            color_continuous_scale='RdBu')

salesTree19 = px.sunburst(sales19_df,
                          path=['중분류', '제품', '거래처 중분류'],
                          values='금액',
                          color='중분류',
                          color_continuous_scale=px.colors.qualitative.Pastel)

salesTree19.update_layout(height=500, paper_bgcolor='#f2f0eb', plot_bgcolor='#f2f0eb')

salesTree19_cus = px.sunburst(sales19_df,
                              path=['중분류', '거래처 중분류', '제품'],
                              values='금액',
                              color='거래처 중분류',
                              color_continuous_scale=px.colors.qualitative.Pastel)

volumeTree19 = px.treemap(sales19_df, path=['중분류', '제품', '거래처 중분류'], values='수량', color='중분류',
                          color_continuous_scale='RdBu')
volumeTree19_cus = px.treemap(sales19_df, path=['거래처 중분류', '제품'], values='수량', color='거래처 중분류',
                              color_continuous_scale='RdBu')

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px"), width=2),
                    dbc.Col(
                        dbc.NavbarBrand(" HANPEL DASHBOARD", className="ml-2"), width=10
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

TOTAL_GRAPH = [
    # dbc.CardHeader(html.H5("전체 아이템 재고 예상")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-bigrams-comps",
                children=[
                    dbc.Alert(
                        "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                        id="no-data-alert-bigrams_comp",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(["기간과 가중치를 선택하세요",
                                              dcc.DatePickerRange(
                                                  id="date-picker",
                                                  start_date=todaymt,
                                                  end_date=today,
                                                  min_date_allowed=dt(2019, 4, 1),
                                                  max_date_allowed=today,
                                                  initial_visible_month=dt(2019, 4, 1),
                                                  display_format="YYYY - MM - DD",
                                              ),
                                              dcc.Slider(
                                                  id="n-selection-slider",
                                                  min=1,
                                                  max=2,
                                                  step=0.1,
                                                  marks={
                                                      1: "100%",
                                                      1.1: "110%",
                                                      1.2: "120%",
                                                      1.3: "130%",
                                                      1.4: "140%",
                                                      1.5: "150%",
                                                      1.6: "160%",
                                                      1.7: "170%",
                                                      1.8: "180%",
                                                      1.9: "190%",
                                                      2: "200%",
                                                  },
                                                  value=1,
                                              )
                                              ]),
                                    md=10)
                        ]
                    ),
                    dcc.Graph(id="total-graph"),
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),
]

ITEM_GRAPH = [
    # dbc.CardHeader(html.H5("아이템별")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-bigrams-scatter",
                children=[
                    dbc.Alert(
                        "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                        id="no-data-alert-bigrams",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(["아이템 :",
                                              dcc.Dropdown(
                                                  id="item-selector",
                                                  options=[
                                                      {"label": i, "value": i}
                                                      for i in list_of_products
                                                  ],
                                                  multi=False,
                                                  value="다바오DC",
                                                  style=
                                                  {
                                                      # 'width': '135px',
                                                      'color': 'black',
                                                      'background-color': '#f2f0eb',
                                                      'font-weight': 'bold'
                                                  }
                                              )]),
                                    ),
                            dbc.Col(html.Div(["사용량(kg) : ", dcc.Input(id='using', value='1000', type='number')])),
                            dbc.Col(html.Div(["기  간(일) : ", dcc.Input(id='period', value='30', type='number')])),
                        ]
                    ),
                    dcc.Graph(id="one-graph"),
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0, "height": "500px", "overflow": "scroll"},
    ),
]

ETA_STATUS = [
    # dbc.CardHeader(html.H5("ETA현황")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="eta-status",
                children=[
                    dash_table.DataTable(
                        id='eta_table',
                        columns=[{"name": i, "id": i} for i in eta_df.columns],
                        data=eta_df.to_dict('records'),
                        style_cell={
                            'backgroundColor': '#f2f0eb',
                            'color': 'black',
                            'textAlign': 'center',
                            'font-weight': 'bold'
                        },
                        fixed_rows={'headers': True},
                    )
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0, "height": "500px", "overflow": "scroll"},
    ),
]

TREEMAP = [
    # dbc.CardHeader(html.H5("매출액 / 수량 전체 보기")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="매출",
                                        children=[
                                            dcc.Loading(
                                                id="sales-treemap",
                                                children=[
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(dcc.Graph(id='salesTree', figure=salesTree,
                                                                              clickData={'points': [{'id': '코코넛분말'}]})),
                                                            dbc.Col(dcc.Graph(id='monthData')),
                                                        ]
                                                    ),
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="매출(거래처별)",
                                        children=[
                                            dcc.Loading(
                                                id="sales-treemap-cus",
                                                children=[
                                                    dcc.Graph(figure=salesTree_cus)
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="수량",
                                        children=[
                                            dcc.Loading(
                                                id="Volume-treemap",
                                                children=[
                                                    dbc.Col(dcc.Graph(figure=volumeTree)),

                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="수량(거래처별)",
                                        children=[
                                            dcc.Loading(
                                                id="Volume-treemap-cus",
                                                children=[
                                                    dcc.Graph(figure=volumeTree_cus)
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=12,
                    ),
                ]
            )
        ]
    ),
]

TREEMAP19 = [
    # dbc.CardHeader(html.H5("매출액 / 수량 전체 보기")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert19",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs19",
                                children=[
                                    dcc.Tab(
                                        label="매출",
                                        children=[
                                            dcc.Loading(
                                                id="sales-treemap19",
                                                children=[dcc.Graph(figure=salesTree19)],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="매출(거래처별)",
                                        children=[
                                            dcc.Loading(
                                                id="sales-treemap-cus19",
                                                children=[
                                                    dcc.Graph(figure=salesTree19_cus)
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="수량",
                                        children=[
                                            dcc.Loading(
                                                id="Volume-treemap19",
                                                children=[
                                                    dcc.Graph(figure=volumeTree19)
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="수량(거래처별)",
                                        children=[
                                            dcc.Loading(
                                                id="Volume-treemap-cus19",
                                                children=[
                                                    dcc.Graph(figure=volumeTree19_cus)
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=12,
                    ),
                ]
            )
        ]
    ),
]

BODY = dbc.Container(
    [
        dbc.Row([dbc.Col(dbc.Card(TOTAL_GRAPH)), ], style={"marginTop": 30}),
        dbc.Row(
            [
                dbc.Col(dbc.Card(ITEM_GRAPH), md=6),
                dbc.Col(dbc.Card(ETA_STATUS), md=6),
            ],
            style={"marginTop": 30},
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Card(TREEMAP)),
                dbc.Col(dbc.Card(TREEMAP19)),
            ],
            style={"marginTop": 30}),
    ],
    className="mt-12",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div(children=[NAVBAR, BODY])


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("total-graph", "figure"),
    [
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("n-selection-slider", "value"),
        # Input("location-dropdown", "value"),
    ],
)
def update_graph(start, end, wv):
    actUse_df.index = pd.to_datetime(actUse_df.index, format="%y/%m/%d")
    lately = actUse_df.loc[start: end]
    lately.index = lately.index.strftime("%y/%m/%d")
    b = round(lately.mean())
    lately = b * wv

    final_his_df = fixed_df.copy()

    for i in range(1, len(fixed_df)):
        final_his_df.iloc[i] = fixed_df.iloc[i] - lately * i

    a = final_his_df.columns.tolist()
    itemNum = len(final_his_df.columns) / 7
    itemNum = int(itemNum)
    k = 0

    fig = make_subplots(rows=itemNum + 1, cols=7, shared_xaxes=True, vertical_spacing=0.06, subplot_titles=a)

    for i in range(1, itemNum + 2):
        for j in range(1, 8):
            fig.add_trace(go.Scatter(x=final_his_df.index, y=final_his_df.iloc[:, k], mode='lines+markers',
                                     marker=dict(size=3, color=list(map(SetColor, final_his_df.iloc[:, k]))),
                                     line=dict(color="#00754a")
                                     ), row=i, col=j)

            k = k + 1
            if k == len(final_his_df.columns):
                break

    for l in fig['layout']['annotations']:
        l['font']['size'] = 13

    fig.update_layout(height=850, showlegend=False, paper_bgcolor='#f2f0eb', plot_bgcolor='#f2f0eb')
    fig.update_yaxes(zeroline=False, showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_xaxes(zeroline=False, showgrid=False, showticklabels=False)

    return fig


##하단 그래프 시작

@app.callback(
    Output("one-graph", "figure"),
    [
        Input("item-selector", "value"),
        Input("using", "value"),
        Input("period", "value"),
    ],
)
def update_graph(item, used, per):
    lately = int(used) / int(per)
    item_df = fixed_df[item]
    final_item_df = item_df
    final_item_df.index = final_item_df.index.str[3:8]

    for i in range(1, len(item_df)):
        final_item_df.iloc[i] = item_df.iloc[i] - lately * i

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=final_item_df.index, y=final_item_df.values, mode='lines+markers',
                              marker=dict(size=6, color=list(map(SetColor, final_item_df.values))),
                              line=dict(color="#00754a")))
    fig2.update_layout(showlegend=False, height=400, paper_bgcolor='#f2f0eb', plot_bgcolor='#f2f0eb', margin=dict(
        l=10,
        r=0,
        b=0,
        t=50,
        pad=4
    ), )
    fig2.update_yaxes(zeroline=False, showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig2.update_xaxes(zeroline=False, showgrid=True, gridwidth=1, gridcolor='lightgray', tick0=today, dtick=10)

    return fig2


##썬버스트 콜백 그래프
@app.callback(
    Output("monthData", "figure"),
    [Input("salesTree", "clickData")], )
def update_bargraph(clickData):
    j_data = json.dumps(clickData, indent=2)
    p_data = json.loads(j_data)
    id_data = p_data['points'][0]['id']
    id_data = id_data.split("/")

    if len(id_data) == 3:
        sales_edit = sales_bar[sales_bar['중분류'] == id_data[0]]
        sales_edit = sales_edit[sales_edit['제품'] == id_data[1]]
        sales_edit = sales_edit[sales_edit['거래처 중분류'] == id_data[2]]
        tt = id_data[2]

    elif len(id_data) == 2:
        sales_edit = sales_bar[sales_bar['중분류'] == id_data[0]]
        sales_edit = sales_edit[sales_edit['제품'] == id_data[1]]
        tt = id_data[1]

    elif len(id_data) == 1:
        sales_edit = sales_bar[sales_bar['중분류'] == id_data[0]]
        tt = id_data[0]

    sales_edit = sales_edit.groupby(by='구분').sum().reset_index()
    qty_sum = sales_edit["수량"].sum()
    qty_sum = '{:,.0f}'.format(qty_sum)
    amount_sum = sales_edit["금액"].sum()
    amount_sum = '{:,.0f}'.format(amount_sum)
    sales_edit["수량2"] = pd.to_numeric(sales_edit["수량"])
    sales_edit["수량2"] = sales_edit["수량2"].apply(lambda x: "{:,}".format(int(x)))

    monthbar = px.bar(sales_edit, x="수량", y="구분", text="수량2", orientation='h', barmode='group')
    monthbar.update_yaxes(dtick=1, fixedrange=True, title=None)
    monthbar.update_xaxes(gridcolor='lightgray', showticklabels=False)
    monthbar.update_traces(hoverinfo=None)
    monthbar.update_layout(paper_bgcolor='#f2f0eb', plot_bgcolor='#f2f0eb',
                           margin=dict(
                               l=0,
                               r=0,
                               b=0,
                               t=150,
                               pad=4
                           ),
                           title=dict(
                               text='<b>' + tt + '<br>' + qty_sum + "(수량)_" + amount_sum + '(금액)</b>',
                               x=0.5,
                               font=dict(
                                   family="Segoe UI",
                                   size=15)
                           ))

    return monthbar


if __name__ == "__main__":
    app.run_server(debug=False)
