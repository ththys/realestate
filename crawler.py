import json
import os
import requests
import time

def load_targets():
    """targets.txt 파일에서 검색할 단지 번호와 거래 유형을 불러옵니다."""
    targets = []
    if os.path.exists("targets.txt"):
        with open("targets.txt", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.split(',')
                    if len(parts) >= 3:
                        targets.append({
                            "name": parts[0].strip(),
                            "complex_id": parts[1].strip(), # 단지 고유 번호 (예: 2981)
                            "type": parts[2].strip()        # 매매, 전세, 월세
                        })
    return targets

def get_trade_type_code(trade_type_str):
    """문자열을 API용 거래 유형 코드로 변환"""
    mapping = {"매매": "A1", "전세": "B1", "월세": "B2"}
    return mapping.get(trade_type_str, "A1")

def parse_price_to_int(price_str):
    """API에서 내려주는 문자열(예: '10억 5,000')을 정수(원 단위)로 변환"""
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
    targets = load_targets()
    if not targets:
        print("targets.txt 파일에 올바른 데이터가 없습니다. (형식: 단지명, 단지번호, 거래유형)")
        return

    results = []
    
    # 봇 차단을 피하기 위한 기본 헤더 (쿠키 및 토큰 제외)
    headers = {
        'accept': '*/*',
        'accept-language': 'ko,en;q=0.9',
        'referer': 'https://new.land.naver.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for target in targets:
        complex_id = target['complex_id']
        trade_code = get_trade_type_code(target['type'])
        
        print(f"[{target['name']}] 데이터 수집 시작...")
        
        # 1페이지 데이터 요청 (필요시 page= 파라미터를 반복문으로 돌려 전체 매물 수집 가능)
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
