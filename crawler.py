import json
import asyncio
import re
from playwright.async_api import async_playwright

# 검색할 단지명과 거래 유형만 지정 (URL 필요 없음)
TARGET_LIST = [
    {"name": "염리동삼성래미안", "type": "매매"},
    {"name": "마포자이", "type": "전세"},
    {"name": "마포래미안푸르지오", "type": "매매"}
]

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

async def main():
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for target in TARGET_LIST:
            try:
                # 1. 네이버 부동산 메인 화면 접속
                await page.goto("https://new.land.naver.com/complexes", wait_until="networkidle")
                
                # 2. 검색창 찾기 및 단지명 입력
                search_input = await page.wait_for_selector(".search_input", timeout=10000)
                await search_input.fill(target["name"])
                await search_input.press("Enter")
                
                # 3. 검색 결과 자동완성 목록 대기 후 첫 번째 결과 클릭
                await page.wait_for_selector(".autocomplete_list .item a", timeout=10000)
                first_result = await page.query_selector(".autocomplete_list .item a")
                if first_result:
                    await first_result.click()
                else:
                    print(f"{target['name']} - 검색 결과를 찾을 수 없습니다.")
                    continue
                
                # 4. 지도 로딩 대기
                await asyncio.sleep(3) 

                # 5. 거래 유형(매매, 전세, 월세) 탭 클릭
                type_btn_selector = f"button:has-text('{target['type']}')"
                await page.wait_for_selector(type_btn_selector, timeout=5000)
                type_btn = await page.query_selector(type_btn_selector)
                if type_btn:
                    await type_btn.click()
                
                # 6. 매물 리스트 로딩 대기
                await page.wait_for_selector(".item_inner", timeout=10000)
                items = await page.query_selector_all(".item_inner")
                
                # 7. 데이터 추출
                for item in items:
                    parent_a = await item.query_selector("a.item_link")
                    article_id = ""
                    if parent_a:
                        class_attr = await parent_a.get_attribute("class")
                        match = re.search(r'article:(\d+)', class_attr or "")
                        if match:
                            article_id = match.group(1)

                    price_el = await item.query_selector(".price_line .price")
                    price_text = await price_el.inner_text() if price_el else "0"
                    
                    info_el = await item.query_selector_all(".info_area .line")
                    building = await info_el[0].inner_text() if len(info_el) > 0 else "정보없음"
                    floor = await info_el[1].inner_text() if len(info_el) > 1 else "정보없음"

                    link = f"https://new.land.naver.com/articles/{article_id}" if article_id else page.url

                    results.append({
                        "id": article_id or str(hash(building + price_text)),
                        "name": target["name"],
                        "type": target["type"],
                        "building": building,
                        "floor": floor,
                        "price_text": price_text,
                        "price_int": parse_price_to_int(price_text),
                        "link": link
                    })

                # 차단 방지를 위한 휴식 시간 (필수)
                print(f"{target['name']} ({target['type']}) 수집 완료.")
                await asyncio.sleep(5) 
                
            except Exception as e:
                print(f"{target['name']} 크롤링 중 오류: {e}")
                # 오류 발생 시 스크린샷 저장 (디버깅 용도)
                await page.screenshot(path=f"error_{target['name']}.png")

        await browser.close()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    asyncio.run(main())
