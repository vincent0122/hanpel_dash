from google_auth import get_google

def get_sheets():
    gsheets_ids = [
        "1owxqOWAI_A31eDKafUDKfehy9gfSkPZT5dECwxqeihU", #공장일지
        "1_0DwnDGTJm6iKEYZHwVC9mDsvIQSq_7AWTG7pckeaow", #eta현황
        "1U4pgA9tfj2sciXj_6LMQ74Vff81OButlpOBb_RVvH9c", #판매관리대장
    ]
    return gsheets_ids


def get_sheet():
    gc = get_google()
    gs = get_sheets()

    stock = gc.open_by_key(gs[0]).worksheet("재고현황")
    actual_use_thisyear = gc.open_by_key(gs[0]).worksheet("원료제품누적")
    actual_use_lastyear = gc.open_by_key(gs[0]).worksheet("2020")
    eta = gc.open_by_key(gs[1]).worksheet("ETA현황")
    sales_thisyear = gc.open_by_key(gs[2]).worksheet("2021")
    sales_lastyear = gc.open_by_key(gs[2]).worksheet("2020")

    return stock, actual_use_lastyear, actual_use_thisyear, eta, sales_thisyear, sales_lastyear

def set_items():
    need = ['다바오DC', 'DC BROWN(로버트)', '코코맥스(프랭클린)', '코코맥스(INHILL)(52)', '코코맥스(P)', '코코맥스30', '코코맥스(W50)', '페어링파우더(FB)',
            'COCOP', 'COCOR', '코코맥스(ROYAL)', '다바오 LOW FAT', '맥주효모(중국)', '맥주효모(베트남)', '대두박', '젤라틴(고)', '젤라틴(중)', '젤라틴(저)', '변성타피오카', '바나나분말(톤백)', '바나나분말(지대)', '위너', '락토젠', '그로우어', '미라클', '구연산(지대)', '솔빈산칼륨(입자)', '솔빈산칼륨(가루)',
            '프로피온산칼슘', '프로틴파워(소이코밀20)', '소이코밀', 'ISP', '멀티락', '멀티락(新)', '씨센스 프리미엄', '디텍', '디텍(에이티바이오)', '케르세틴', '렌틸콩', '렌틸콩(지대)',
            '커피화분(허니텍)', '인도화분', 'CLA(유대표님 보관대행)', '바이오스플린트(유대표님 보관대행)']


get_sheet()

