import json
import asyncio
import re
from playwright.async_api import async_playwright

# ※ 중요: 본인이 모니터링할 5개 단지의 실제 네이버 부동산 URL로 대체해야 합니다.
TARGET_LIST = [
    {"name": "염리동삼성래미안", "type": "매매", "url": "https://new.land.naver.com/complexes/1111?ms=...&a=APT&b=A1&e=RETAIL"},
    {"name": "염리동삼성래미안", "type": "전세", "url": "https://new.land.naver.com/complexes/1111?ms=...&a=APT&b=A1&e=RETAIL"},
    {"name": "마포자이", "type": "매매", "url": "https://new.land.naver.com/complexes/2222?ms=...&a=APT&b=A1&e=RETAIL"},
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
                await page.goto(target["url"], wait_until="networkidle")
                await page.wait_for_selector(".item_inner", timeout=15000)
                
                items = await page.query_selector_all(".item_inner")
                
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

                    link = f"https://new.land.naver.com/articles/{article_id}" if article_id else target["url"]

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

                await asyncio.sleep(5) 
                
            except Exception as e:
                print(f"{target['name']} 크롤링 중 오류: {e}")

        await browser.close()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    asyncio.run(main())
