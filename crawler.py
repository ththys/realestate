import json
import requests

def parse_price_to_int(price_str):
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
    headers = {
        'accept': '*/*',
        'accept-language': 'ko,en;q=0.9',
        'referer': 'https://new.land.naver.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    # 복사해 온 API 주소를 여기에 붙여넣습니다. (현재 735번 매매)
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
                
                results.append({
                    "id": article_id,
                    "building": building,
                    "floor": floor_info,
                    "price_text": price_text,
                    "price_int": parse_price_to_int(price_text),
                    "link": f"https://new.land.naver.com/articles/{article_id}"
                })
    except Exception as e:
        print(f"오류 발생: {e}")

    # 결과를 data.json으로 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
