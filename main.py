import requests
import os
import sys
from datetime import datetime, timezone, timedelta

# ==========================================
# [중요] GitHub Secrets에서 불러올 정보들
# ==========================================
try:
    # 환경변수 "TELEGRAM_CHAT_ID"의 값을 파이썬 변수 'CHAT_ID'에 저장합니다.
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
except KeyError:
    print("오류: 환경 변수 TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
    # GitHub Actions 환경에서 환경변수가 없으면 스크립트 종료
    if "GITHUB_ACTIONS" in os.environ:
        sys.exit(1)
# ==========================================


def send_telegram_message(message):
    """텔레그램으로 메시지를 전송하는 함수"""
    try:
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            # [수정 1] 위에서 선언한 글로벌 변수 CHAT_ID를 사용해야 합니다.
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.get(send_url, params=params, timeout=5)
        if response.status_code != 200:
             print(f"텔레그램 전송 실패: {response.text}")
    except Exception as e:
        print(f"텔레그램 전송 에러 발생: {e}")


def get_crypto_prices(tickers):
    """업비트 시세 조회 함수"""
    url = f"https://api.upbit.com/v1/ticker?markets={tickers}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        price_dict = {}
        for coin_info in data:
            price_dict[coin_info['market']] = coin_info['trade_price']
        return price_dict
    except Exception as e:
        print(f"업비트 시세 조회 실패: {e}")
        return None


# --- 메인 실행부 1: 시세 알림 ---
if __name__ == "__main__":
    print("--- [1부] 시세 알림 로직 시작 ---")
    TARGET_COINS = "KRW-BTC,KRW-DOGE"
    prices = get_crypto_prices(TARGET_COINS)
    
    if prices is not None and len(prices) > 0:
        KST = timezone(timedelta(hours=9))
        now_time = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
        
        btc_price = prices.get('KRW-BTC')
        doge_price = prices.get('KRW-DOGE')

       
        message += f"⏰ 시간(KST): {now_time}\n\n"
        
        if btc_price: message += f"🔸 BTC: {btc_price:,.0f} KRW\n"
        if doge_price: message += f"🔹 DOGE: {doge_price:,.0f} KRW\n"

        if btc_price or doge_price:
            send_telegram_message(message)
            print("시세 알림 전송 완료")
        else:
             print("시세 데이터 추출 실패")
    else:
        print("업비트 API 호출 실패")
    print("\n")

