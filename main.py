import requests
import os
import sys
from datetime import datetime, timezone, timedelta

# ==========================================
# [중요] GitHub Secrets에서 불러올 정보들
# ==========================================
try:
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]
except KeyError:
    print("오류: 환경 변수 TELEGRAM_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
    # 로컬 테스트용 (필요시 주석 해제하고 사용, GitHub에 올릴 땐 주석 처리 필수)
    # TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"
    # CHAT_ID = "YOUR_CHAT_ID_HERE"
    
    # GitHub Actions 환경에서 환경변수가 없으면 스크립트 종료
    if "GITHUB_ACTIONS" in os.environ:
        sys.exit(1)

# ==========================================


def send_telegram_message(message):
    """텔레그램으로 메시지를 전송하는 함수"""
    try:
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML" # 보기 좋게 꾸미기 위해 HTML 모드 사용
        }
        response = requests.get(send_url, params=params, timeout=5)
        if response.status_code != 200:
             print(f"텔레그램 전송 실패: {response.text}")
    except Exception as e:
        print(f"텔레그램 전송 에러 발생: {e}")


def get_crypto_prices(tickers):
    """
    업비트에서 여러 코인의 현재가를 한 번에 가져오는 함수
    tickers: 콤마로 구분된 마켓 코드 문자열 (예: "KRW-BTC,KRW-DOGE")
    Return: {'KRW-BTC': 가격, 'KRW-DOGE': 가격} 형태의 딕셔너리
    """
    url = f"https://api.upbit.com/v1/ticker?markets={tickers}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 응답받은 리스트 데이터를 보기 편하게 딕셔너리로 변환
        price_dict = {}
        for coin_info in data:
            market_code = coin_info['market']
            price = coin_info['trade_price']
            price_dict[market_code] = price
            
        return price_dict
    except Exception as e:
        print(f"업비트 시세 조회 실패: {e}")
        return None


# --- 메인 실행부 ---
if __name__ == "__main__":
    print("스크립트 실행 시작...")

    # 조회할 코인 목록 (콤마로 연결)
    TARGET_COINS = "KRW-BTC,KRW-DOGE"
    
    # 시세 정보 가져오기
    prices = get_crypto_prices(TARGET_COINS)
    
    if prices is not None and len(prices) > 0:
        # 한국 시간(KST) 구하기
        KST = timezone(timedelta(hours=9))
        now_time = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
        
        # 각 코인별 가격 추출 (데이터가 없을 경우를 대비해 .get 사용)
        btc_price = prices.get('KRW-BTC')
        doge_price = prices.get('KRW-DOGE')

        # 메시지 내용 구성
        message = f"💰 **업비트 주요 코인 시세 알림**\n\n"
        message += f"⏰ 시간(KST): {now_time}\n\n"
        
        if btc_price:
            message += f"🔸 **비트코인(BTC):** {btc_price:,.0f} KRW\n"
        
        if doge_price:
            message += f"🔹 **도지코인(DOGE):** {doge_price:,.0f} KRW\n"

        # 정보가 하나라도 있으면 전송
        if btc_price or doge_price:
            send_telegram_message(message)
            print(f"전송 완료: BTC({btc_price}), DOGE({doge_price})")
        else:
             print("작업 실패: 시세 데이터를 추출하지 못했습니다.")

    else:
        print("작업 실패: 업비트 API 호출 실패로 메시지를 보내지 않았습니다.")

def send_telegram_test():
    import requests
    import os

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": "🔥 강제 테스트 메시지 - 고양시 전송 확인"
    }

    requests.post(url, data=data)

if __name__ == "__main__":
    send_telegram_test()
