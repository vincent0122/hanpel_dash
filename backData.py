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
    values = {}
    values_df = {}
    header = {}

    for key in result.keys():
        values[key] = result[key].get_all_values()  # 이거를 빨리 할 수 있는 방법을 찾아라
    for key in result.keys():
        if key == "stock":
            i = 2  # 재고현황 시트는 2행을 헤더로 따와야함
        else:
            i = 0
        header[key] = values[key].pop(i)

    for key in result.keys():
        values_df[key] = pd.DataFrame(values[key], columns=header[key])

    return values_df


def drop_columns():
    need = set_items()
    last = dt.today() + timedelta(need['period_to_check'])
    tod = dt.today()
    todPlus = dt.today() + timedelta(2)
    values_df = get_sheet_values()
    values_df['stock'] = values_df['stock'].drop(
        [values_df['stock'].index[0], values_df['stock'].index[1]])
    values_df['stock2'] = values_df['stock'].iloc[:, [0, 2]]
    values_df['stock2'].columns = ['제품명', '수량']
    values_df['stock3'] = values_df['stock'].iloc[:, [4, 6]]
    values_df['stock3'].columns = ['제품명', '수량']
    values_df['stock'] = values_df['stock2'].append(values_df['stock3'])
    values_df['stock'] = values_df['stock'][values_df['stock'].제품명.isin(
        need['items'])]
    values_df['stock']['Date'] = tod

    print(values_df['stock'])


def df_concat_merge(data_key1, data_key2, new_key):
    values_df = get_sheet_values()

    if new_key == 'actUse_df':
        values_df[new_key] = pd.concat([values_df[data_key1].iloc[:, [0, 2, 4]],
                                        values_df[data_key2].iloc[:, [0, 2, 4]]])
    else:
        values_df[new_key] = pd.concat(
            [values_df[data_key1], values_df[data_key2]])

    del values_df[data_key1]
    del values_df[data_key2]

    return values_df


drop_columns()
# df_concat_merge('actual_use_thisyear', 'actual_use_lastyear', 'actUse_df')


# data_cleaning(stock)

# stock_df = stock.get_all_values()
# eta_df = eta.get_all_values()
# actualUse_df = actualUse.get_all_values()
# actualUse2019_df = actualUse2019.get_all_values()
# sales_df = sales.get_all_values()
# sales19_df = sales19.get_all_values()

# stock_headers = stock_df.pop(2)
# sales_headers = sales_df.pop(0)
# sales19_headers = sales19_df.pop(0)
# eta_headers = eta_df.pop(0)
# actualUse_headers = actualUse_df.pop(0)
# actualUse2019_df_headers = actualUse2019_df.pop(0)

# stock_df = pd.DataFrame(stock_df, columns=stock_headers)
# sales_df = pd.DataFrame(sales_df, columns=sales_headers)
# sales19_df = pd.DataFrame(sales19_df, columns=sales19_headers)
# eta_df = pd.DataFrame(eta_df, columns=eta_headers)
# actualUse_df = pd.DataFrame(actualUse_df, columns=actualUse_headers)
# actualUse2019_df = pd.DataFrame(actualUse2019_df, columns=actualUse2019_df_headers)
# actUse_df = pd.concat([actualUse_df.iloc[:, [0, 2, 4]], actualUse2019_df.iloc[:, [0, 2, 4]]])
