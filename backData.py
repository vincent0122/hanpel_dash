# -*- coding: utf-8 -*-

from google_auth import get_google
import pandas as pd

from datetime import timedelta
from datetime import datetime as dt


def set_items():
    basic_setting = {
        "items": ('다바오DC', 'DC BROWN(로버트)', '코코맥스(프랭클린)', '코코맥스(INHILL)(52)', '코코맥스(P)', '코코맥스30', '코코맥스(W50)', '페어링파우더(FB)',
                  'COCOP', 'COCOR', '코코맥스(ROYAL)', '다바오 LOW FAT', '맥주효모(중국)', '맥주효모(베트남)', '대두박', '젤라틴(고)', '젤라틴(중)', '젤라틴(저)',
                  '변성타피오카', '바나나분말(톤백)', '바나나분말(지대)', '위너', '락토젠', '그로우어', '미라클', '구연산(지대)', '솔빈산칼륨(입자)', '솔빈산칼륨(가루)',
                  '프로피온산칼슘', '프로틴파워(소이코밀20)', '소이코밀', 'ISP', '멀티락', '멀티락(新)', '씨센스 프리미엄', '디텍', '디텍(에이티바이오)', '케르세틴',
                  '렌틸콩', '렌틸콩(지대)', '커피화분(허니텍)', '인도화분', 'CLA(유대표님 보관대행)', '바이오스플린트(유대표님 보관대행)'),
        "period_to_check": 60
    }
    return basic_setting


def get_sheetsId():
    gsheets_ids = {
        'factory_report': '1owxqOWAI_A31eDKafUDKfehy9gfSkPZT5dECwxqeihU',  # 공장일지
        'eta_status': '1_0DwnDGTJm6iKEYZHwVC9mDsvIQSq_7AWTG7pckeaow',  # eta현황
        'sales_status': '1U4pgA9tfj2sciXj_6LMQ74Vff81OButlpOBb_RVvH9c',  # 판매관리대장2021
    }

    return gsheets_ids


def get_sheet():  # gs 밑에다가
    gc = get_google()
    gs = get_sheetsId()
    result = {
        "stock": gc.open_by_key(gs['factory_report']).worksheet("재고현황"),
        "actual_use_thisyear": gc.open_by_key(gs['factory_report']).worksheet("원료제품누적"),
        "actual_use_lastyear": gc.open_by_key(gs['factory_report']).worksheet("2020"),
        "sales21": gc.open_by_key(gs['sales_status']).worksheet("2021"),
        "sales20": gc.open_by_key(gs['sales_status']).worksheet("2020"),
        "eta": gc.open_by_key(gs['eta_status']).worksheet("ETA현황"),
    }
    return result


def get_sheet_values():
    result = get_sheet()
    range = {
        "stock": 'a3:g100',
        "actual_use_thisyear": 'a1:e6000',
        "actual_use_lastyear": 'a1:e6000',
        "sales21": 'a1:n4000',
        "sales20": 'a1:n4000',
        "eta": 'a1:aa100'
    }
    values = {}
    values_df = {}
    header = {}

    for key in result.keys():
        values[key] = result[key].get(range[key])
        header[key] = values[key].pop(0)
        values_df[key] = pd.DataFrame(values[key], columns=header[key])

    return values_df


def date_setting():
    need = set_items()
    date_data = {
        "last": dt.today() + timedelta(need['period_to_check']),
        "tod": dt.today(),
        "yesterday": dt.today() - timedelta(1),
        "tod_month": dt.today().month,
        "todPlus": dt.today() + timedelta(2)
    }

    return date_data


def cleaning_datas():
    need = set_items()
    date_data = date_setting()
    values_df = get_sheet_values()
    # values_df['stock'] = values_df['stock'].drop(
    #    [values_df['stock'].index[0], values_df['stock'].index[1]])

    def change_comma_to_float(key, col_name):
        values_df[key].loc[:, col_name] = values_df[key][col_name].str.replace(
            ',', '')
        values_df[key].loc[:,
                           col_name] = values_df[key][col_name].astype(float)
        return values_df

    values_df['stock2'] = values_df['stock'].iloc[:, [0, 2]]
    values_df['stock2'].columns = ['제품명', '수량']
    values_df['stock3'] = values_df['stock'].iloc[:, [4, 6]]
    values_df['stock3'].columns = ['제품명', '수량']
    values_df['stock'] = values_df['stock2'].append(values_df['stock3'])
    values_df['stock'].columns = ['제품명', '수량']
    values_df['stock'] = values_df['stock'][values_df['stock']['제품명'].isin(
        need['items'])]
    values_df['stock']['Date'] = date_data['tod']
    del values_df['stock2']
    del values_df['stock3']

    values_df['actual_use'] = pd.concat([values_df['actual_use_thisyear'].iloc[:, [0, 2, 4]],
                                         values_df['actual_use_lastyear'].iloc[:, [0, 2, 4]]])
    del values_df['actual_use_thisyear']
    del values_df['actual_use_lastyear']

    values_df["sales21"] = values_df["sales21"][values_df["sales21"]['제품'] != ""]
    values_df["sales20"] = values_df["sales20"][values_df["sales20"]['제품'] != ""]
    change_comma_to_float("sales21", '수량')
    change_comma_to_float("sales21", '금액')
    change_comma_to_float("sales20", '수량')
    change_comma_to_float("sales20", '금액')
    change_comma_to_float("stock", '수량')

    values_df['eta'] = values_df['eta'].iloc[:, [0, 5, 6, 16, 17]]
    values_df['eta'] = values_df['eta'][values_df['eta'].ETA != ""]
    values_df['eta'] = values_df['eta'][values_df['eta'].수입자 != "대한산업"]
    values_df['eta'].loc[:, '계약수량'] = values_df['eta'].계약수량.astype(float)
    values_df['eta'].계약수량 = values_df['eta'].계약수량 * 1000

    if date_data['tod_month'] < 10:
        values_df['eta']['ETA'] = values_df['eta']['ETA'] + "/21"
    else:
        values_df['eta']['ETA'] = values_df['eta']['ETA'].mask(
            values_df['eta']['ETA'].dt.month == 1, values_df['eta']['ETA'] + "/22")
        values_df['eta']['ETA'] = values_df['eta']['ETA'].mask(
            values_df['eta']['ETA'].dt.month == 2, values_df['eta']['ETA'] + "/22")
        values_df['eta']['ETA'] = values_df['eta']['ETA'].mask(
            values_df['eta']['ETA'].dt.month == 3, values_df['eta']['ETA'] + "/22")

    values_df['eta']['ETA'] = pd.to_datetime(
        values_df['eta']['ETA'], format='%m/%d/%y')

    values_df['eta']['ETA'] = values_df['eta']['ETA'] + \
        timedelta(7)  # ETA +7일 후 입고된다고 가정
    values_df['eta'] = values_df['eta'][pd.to_datetime(
        values_df['eta'].ETA, errors='coerce') <= date_data['last']]
    values_df['eta'] = values_df['eta'][values_df['eta'].입고상태 != "완"]
    values_df['eta']['ETA'].mask(
        values_df['eta']['입고상태'] == '준', date_data['todPlus'], inplace=True)
    values_df['eta']['ETA'].mask(
        values_df['eta']['ETA'] <= date_data['tod'], date_data['todPlus'], inplace=True)
    values_df['eta'] = values_df['eta'].rename(
        {'ETA': 'Date', '계약수량': '수량'}, axis='columns')
    values_df['eta'] = values_df['eta'].iloc[:, [1, 2, 3]]

    values_df['fixed_df'] = values_df['stock'].append(values_df['eta'])
    values_df['fixed_df'] = values_df['fixed_df'][['Date', '제품명', '수량']]
    values_df['fixed_df']['Date'] = values_df['fixed_df']['Date'].dt.strftime(
        "%y/%m/%d")

    dataRange = []
    for i in range(0, need['period_to_check'] + 1):  # 나중에 10을 30으로 바꾸어야 함
        a = dt.today() + timedelta(i)
        a = dt.strftime(a, "%y/%m/%d")
        dataRange.append(a)

    values_df['actual_use'] = values_df['actual_use'][values_df['actual_use'].iloc[:, 2] != ""]
    values_df['actual_use'] = values_df['actual_use'][values_df['actual_use'].iloc[:, 1].isin(
        need['items'])]
    values_df['actual_use']['날짜'] = pd.to_datetime(
        values_df['actual_use']['날짜'], format="%Y. %m. %d")
    values_df['actual_use']['날짜'] = values_df['actual_use']['날짜'].dt.strftime(
        "%y/%m/%d")
    values_df['actual_use']['사용/출고'] = values_df['actual_use']['사용/출고'].str.replace(
        ',', '')
    values_df['actual_use']['사용/출고'] = values_df['actual_use']['사용/출고'].astype(
        float)

    a = pd.date_range(start='2020-01-01', end=dt.today() - timedelta(1))
    a = a.strftime("%y/%m/%d")
    b = values_df['stock']['제품명']
    raw_df = pd.DataFrame(index=a, columns=b)
    raw_df = raw_df.fillna(0)

    # 피벗 전까지 데이터 가공 --종료
    values_df['fixed_df'] = values_df['fixed_df'].pivot_table(
        index="Date", columns="제품명", values="수량", aggfunc='sum')
    values_df['fixed_df'].index.name = None
    values_df['fixed_df'].columns.name = ""
    values_df['fixed_df'] = values_df['fixed_df'].fillna(0)
    values_df['fixed2_df'] = pd.DataFrame(
        columns=values_df['fixed_df'].columns, index=dataRange)
    values_df['fixed2_df'].index.name = None
    values_df['fixed2_df'].columns.name = ""
    values_df['fixed2_df'] = values_df['fixed2_df'].fillna(0)
    values_df['fixed_df'] = values_df['fixed_df'].add(values_df['fixed2_df'])
    values_df['fixed_df'] = values_df['fixed_df'].fillna(0)
    del values_df['fixed2_df']

    for i in range(1, need['period_to_check'] + 1):
        values_df['fixed_df'].iloc[i] = values_df['fixed_df'].iloc[i -
                                                                   1] + values_df['fixed_df'].iloc[i]

    values_df['actual_use'] = values_df['actual_use'].pivot_table(
        index="날짜", columns="제품명", values="사용/출고", aggfunc='sum')
    values_df['actual_use'] = values_df['actual_use'].fillna(0)
    values_df['actual_use'].index.name = None
    values_df['actual_use'].columns.name = ""
    raw_df.columns.name = ""
    values_df['actual_use'] = raw_df.add(values_df['actual_use'], fill_value=0)

    return values_df


######데이터가공 종료##########
values_df = cleaning_datas()
