import json
import requests
import time

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

    print("데이터 수집 시작...")
    
    # ▼ 여기에 복사해 오신 API 주소를 그대로 넣으시면 됩니다. (현재 735번 매매 주소 적용됨)
    api_url = "https://new.land.naver.com/api/articles/complex/735?realEstateType=APT%3APRE%3AABYG%3AJGC&tradeType=A1&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount=300&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=1&buildingNos=&areaNos=&type=list&order=rank"
    
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
                
                # 단지명과 거래유형은 일단 고정값으로 넣습니다. (원하시면 '해당단지이름'을 실제 이름으로 변경하세요)
                results.append({
                    "id": article_id,
                    "name": "모니터링 단지", 
                    "type": "매매", 
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

    # 결과를 JSON으로 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print("수집 완료 및 저장 성공.")

if __name__ == "__main__":
    main()
