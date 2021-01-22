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


def cleaning_datas():
    need = set_items()
    last = dt.today() + timedelta(need['period_to_check'])
    tod = dt.today()
    tod_month = tod.month
    todPlus = dt.today() + timedelta(2)
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
    values_df['stock']['Date'] = tod
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
    values_df['eta2'] = values_df['eta'][values_df['eta'].ETA != ""]
    values_df['eta2'] = values_df['eta2'][values_df['eta2'].수입자 != "대한산업"]
    values_df['eta2'].loc[:, '계약수량'] = values_df['eta2'].계약수량.astype(float)
    values_df['eta2'].계약수량 = values_df['eta2'].계약수량 * 1000

    if tod_month < 10:
        values_df['eta2']['ETA'] = values_df['eta2']['ETA'] + "/21"
    else:
        values_df['eta2']['ETA'] = values_df['eta2']['ETA'].mask(
            values_df['eta2']['ETA'].dt.month == 1, values_df['eta2']['ETA'] + "/22")
        values_df['eta2']['ETA'] = values_df['eta2']['ETA'].mask(
            values_df['eta2']['ETA'].dt.month == 2, values_df['eta2']['ETA'] + "/22")
        values_df['eta2']['ETA'] = values_df['eta2']['ETA'].mask(
            values_df['eta2']['ETA'].dt.month == 3, values_df['eta2']['ETA'] + "/22")

    values_df['eta2']['ETA'] = pd.to_datetime(
        values_df['eta2']['ETA'], format='%m/%d/%y')

    values_df['eta2']['ETA'] = values_df['eta2']['ETA'] + \
        timedelta(7)  # ETA +7일 후 입고된다고 가정
    values_df['eta2'] = values_df['eta2'][pd.to_datetime(
        values_df['eta2'].ETA, errors='coerce') <= last]
    values_df['eta2'] = values_df['eta2'][values_df['eta2'].입고상태 != "완"]
    values_df['eta2']['ETA'].mask(
        values_df['eta2']['입고상태'] == '준', todPlus, inplace=True)
    values_df['eta2']['ETA'].mask(
        values_df['eta2']['ETA'] <= tod, todPlus, inplace=True)  # 이 부분이 이상하네. 없어야지. 오류가 나야돼
    values_df['eta2'] = values_df['eta2'].rename(
        {'ETA': 'Date', '계약수량': '수량'}, axis='columns')
    values_df['eta2'] = values_df['eta2'].iloc[:, [1, 2, 3]]

    print(values_df['eta2'])


cleaning_datas()
# df_concat_merge('actual_use_thisyear', 'actual_use_lastyear', 'actUse_df')

# data_cleaning(stock)

# stock_df = stock.get_all_values()
# values_df['eta'] = eta.get_all_values()
# actualUse_df = actualUse.get_all_values()
# actualUse2019_df = actualUse2019.get_all_values()
# sales_df = sales.get_all_values()
# sales19_df = sales19.get_all_values()

# stock_headers = stock_df.pop(2)
# sales_headers = sales_df.pop(0)
# sales19_headers = sales19_df.pop(0)
# eta_headers = values_df['eta'].pop(0)
# actualUse_headers = actualUse_df.pop(0)
# actualUse2019_df_headers = actualUse2019_df.pop(0)

# stock_df = pd.DataFrame(stock_df, columns=stock_headers)
# sales_df = pd.DataFrame(sales_df, columns=sales_headers)
# sales19_df = pd.DataFrame(sales19_df, columns=sales19_headers)
# values_df['eta'] = pd.DataFrame(values_df['eta'], columns=eta_headers)
# actualUse_df = pd.DataFrame(actualUse_df, columns=actualUse_headers)
# actualUse2019_df = pd.DataFrame(actualUse2019_df, columns=actualUse2019_df_headers)
# actUse_df = pd.concat([actualUse_df.iloc[:, [0, 2, 4]], actualUse2019_df.iloc[:, [0, 2, 4]]])
