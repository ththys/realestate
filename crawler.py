import json
import os
import requests
import time

def main():
    results = []
    headers = {
        'accept': '*/*',
        'accept-language': 'ko,en;q=0.9',
        'referer': 'https://new.land.naver.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    # 1. targets.txt 파일에서 단지 번호(숫자)들을 읽어옵니다.
    complex_ids = []
    if os.path.exists("targets.txt"):
        with open("targets.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    complex_ids.append(line)
    
    if not complex_ids:
        print("targets.txt 파일에 입력된 단지 번호가 없습니다.")
        return

    # 2. 읽어온 번호별로 순회하며 데이터를 수집합니다.
    for cid in complex_ids:
        print(f"단지 번호 [{cid}] 수집 시작...")
        api_url = f"https://new.land.naver.com/api/articles/complex/{cid}?realEstateType=APT&tradeType=A1&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&page=1&type=list&order=rank"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                article_list = data.get('articleList', [])
                
                for item in article_list:
                    results.append({
                        "complex_id": cid,
                        "building": item.get('buildingName', '정보없음'),
                        "floor": item.get('floorInfo', '정보없음'),
                        "price_text": item.get('dealOrWarrantPrc', '0'),
                        "link": f"https://new.land.naver.com/articles/{item.get('articleNo', '')}"
                    })
                print(f" -> {len(article_list)}개 매물 수집 완료.")
            else:
                print(f" -> 수집 실패 (상태 코드: {response.status_code})")
                
        except Exception as e:
            print(f" -> 오류 발생: {e}")
        
        # 연속 요청으로 인한 차단 방지용 잠시 대기
        time.sleep(2)

    # 3. 수집된 모든 데이터를 하나의 data.json 파일로 저장합니다.
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("모든 수집 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
