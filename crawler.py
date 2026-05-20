import json
import requests
import time

# ▼ 다른 단지가 필요하면 이 리스트 아래에 한 줄씩 계속 복사해서 넣으시면 됩니다!
TARGET_LIST = [
    {"name": "마포자이", "complex_id": "2981", "type": "매매"},
    {"name": "마포자이", "complex_id": "2981", "type": "전세"},
    {"name": "새로추가한단지", "complex_id": "735", "type": "매매"} # <- 방금 주신 코드의 735번 단지
]

def get_trade_type_code(trade_type_str):
    """문자열을 API용 거래 유형 코드로 변환"""
    mapping = {"매매": "A1", "전세": "B1", "월세": "B2"}
    return mapping.get(trade_type_str, "A1")

def parse_price_to_int(price_str):
    """'10억 5,000' 형태의 문자열을 정수(원 단위)로 변환"""
    clean_str = price_str.replace(",", "").replace(" ", "").replace("원", "")
    total = 0
    if "억" in clean_str:
        parts = clean_str.split("억")
        total += int(parts[0]) * 100000000
        if len(parts) > 1 and parts[1]:
            total += int(parts[1]) * 10000
    else:
        total += int(clean_str) * 10000
    return total

def main():
    results = []
    
    # 봇 차단을 피하기 위한 기본 헤더
    headers = {
        'accept': '*/*',
        'accept-language': 'ko,en;q=0.9',
        'referer': 'https://new.land.naver.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    for target in TARGET_LIST:
        complex_id = target['complex_id']
        trade_code = get_trade_type_code(target['type'])
        
        print(f"[{target['name']}] 데이터 수집 시작...")
        
        # API 주소에 단지번호(complex_id)와 거래유형(trade_code)을 자동으로 넣어서 요청합니다.
        api_url = f"https://new.land.naver.com/api/articles/complex/{complex_id}?realEstateType=APT&tradeType={trade_code}&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount=100&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=1&buildingNos=&areaNos=&type=list&order=rank"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                article_list = data.get('articleList', [])
                
                for item in article_list:
                    article_id = str(item.get('articleNo', ''))
                    building = item.get('buildingName', '정보없음')
                    floor_info = item.get('floorInfo', '정보없음')
                    price_text = item.get('dealOrWarrantPrc', '0')
                    
                    results.append({
                        "id": article_id,
                        "name": target["name"],
                        "type": target["type"],
                        "building": building,
                        "floor": floor_info,
                        "price_text": price_text,
                        "price_int": parse_price_to_int(price_text),
                        "link": f"https://new.land.naver.com/articles/{article_id}"
                    })
                
                print(f" -> {len(article_list)}개 매물 수집 성공.")
            else:
                print(f" -> 실패: 상태 코드 {response.status_code}")
                
        except Exception as e:
            print(f" -> 오류 발생: {e}")
            
        # API 서버 부하 방지를 위한 짧은 휴식
        time.sleep(2)

    # 결과를 JSON으로 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print("모든 데이터 수집이 완료되었습니다.")

if __name__ == "__main__":
    main()
