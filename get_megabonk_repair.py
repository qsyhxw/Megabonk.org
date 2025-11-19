import json
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# === 配置 ===
TARGET_COUNT = 150

# === 辅助函数 ===
def parse_score(score_str):
    try:
        s = score_str.lower().strip()
        if 'm' in s:
            return int(float(s.replace('m', '')) * 1000000)
        elif 'k' in s:
            return int(float(s.replace('k', '')) * 1000)
        else:
            return int(s.replace(',', ''))
    except:
        return 0

def extract_name_from_url(url):
    if not url: return ""
    clean_url = url.split('?')[0]
    filename = clean_url.split('/')[-1]
    name = filename.split('.')[0]
    return name

def process_single_rank(page, rank, is_retry=False):
    """
    封装好的单行采集函数，用于主循环和补录循环
    """
    target_index = rank - 1
    row_selector = f'div[data-index="{target_index}"]'
    row_locator = page.locator(row_selector)
    
    # 1. 自动寻路
    search_attempts = 0
    while row_locator.count() == 0 and search_attempts < 20:
        # 如果是补录模式，且要是找前几名，可能需要往回滚
        if is_retry and rank < 10:
            page.mouse.wheel(0, -500) # 往上滚
        else:
            page.mouse.wheel(0, 300) # 往下滚
            
        time.sleep(0.3)
        search_attempts += 1
    
    if row_locator.count() == 0:
        print(f"❌ 无法找到第 {rank} 名")
        return None

    # 2. 确保视野 & 防遮挡
    try:
        row_locator.scroll_into_view_if_needed()
        # 【关键修复】往下滚一点，再往上回一点，确保不被 Header 遮挡
        page.mouse.wheel(0, -150) 
        time.sleep(0.5)
    except:
        pass

    # 3. 展开逻辑
    expanded = False
    retry_click = 0
    
    while not expanded and retry_click < 3:
        box = row_locator.bounding_box()
        if not box: break
        
        initial_height = box['height']
        if initial_height > 150:
            expanded = True
            break
        
        # 点击策略
        if retry_click == 0:
            # 点最右边
            click_x = box['x'] + box['width'] * 0.95
            click_y = box['y'] + box['height'] / 2
            page.mouse.click(click_x, click_y)
        else:
            # 强制点中间
            row_locator.click(force=True)
        
        time.sleep(0.8 + retry_click * 0.5) # 补录时多等一会
        
        new_box = row_locator.bounding_box()
        if new_box and new_box['height'] > initial_height + 50:
            expanded = True
        else:
            retry_click += 1

    # 4. 数据提取
    try:
        imgs = row_locator.locator('img').all()
        items = []
        weapons = []
        tomes = []
        char_name = ""
        country_data = None
        
        for img in imgs:
            src = img.get_attribute('src')
            if not src: continue
            name_id = extract_name_from_url(src)
            
            if "/weapon/" in src:
                if name_id not in weapons: weapons.append(name_id)
            elif "/tome/" in src:
                if name_id not in tomes: tomes.append(name_id)
            elif "/passive/" in src or "/item/" in src:
                if name_id not in items: items.append(name_id)
            elif "/flags/" in src:
                country_data = {"code": name_id, "name": name_id}
            elif "/characters/" in src:
                char_name = name_id
            elif "twitch" not in src and "youtube" not in src and "discord" not in src:
                    if name_id not in items and name_id not in weapons and name_id not in tomes and name_id != char_name:
                        items.append(name_id)

        text = row_locator.inner_text()
        parts = [p.strip() for p in text.replace('\n', '|').split('|') if p.strip()]
        
        score_str = "0"
        player_name = "Unknown"
        for idx, part in enumerate(parts):
            if re.match(r'^\d+(\.\d+)?[mk]?$', part.lower()):
                score_str = part
                if idx + 1 < len(parts): player_name = parts[idx+1]
                break

        links = row_locator.locator('a').all()
        video_url = ""
        for link in links:
            href = link.get_attribute('href')
            if href and ("twitch" in href or "youtu" in href):
                video_url = href
                break

        return {
            "rank": rank,
            "playerName": player_name,
            "kills": parse_score(score_str),
            "character": char_name,
            "country": country_data,
            "weapons": weapons,
            "tomes": tomes,
            "items": items,
            "videoURL": video_url
        }
    except Exception as e:
        print(f"❌ 解析出错: {e}")
        return None

def scrape_repair():
    print(f"🚀 启动完美版采集 (含自动补录)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 900})

        print("🌏 访问 Megabonk...")
        page.goto("https://megabonk.fun", timeout=90000, wait_until="domcontentloaded")
        page.wait_for_selector('div[data-index="0"]', timeout=60000)
        
        collected_data_map = {} # 使用字典 rank -> data，方便更新
        
        # === 第一阶段：主循环 ===
        print("==== 第一阶段：顺序采集 1-150 ====")
        for rank in range(1, TARGET_COUNT + 1):
            data = process_single_rank(page, rank)
            if data:
                collected_data_map[rank] = data
                status = "✅" if len(data['items']) > 0 else "❌待补录"
                print(f"   {status} #{rank} {data['playerName']} | 物品: {len(data['items'])}")
            else:
                print(f"   ❌ #{rank} 采集失败")

        # === 第二阶段：智能补录 ===
        print("\n==== 第二阶段：检查并补录缺失数据 ====")
        
        # 找出物品数为 0 的 Rank
        retry_ranks = []
        for rank in range(1, TARGET_COUNT + 1):
            if rank in collected_data_map:
                if len(collected_data_map[rank]['items']) == 0:
                    retry_ranks.append(rank)
            else:
                retry_ranks.append(rank) # 如果完全没抓到也要补
        
        if not retry_ranks:
            print("🎉 完美！没有需要补录的数据。")
        else:
            print(f"⚠️ 发现 {len(retry_ranks)} 条数据不完整，开始补录: {retry_ranks}")
            
            for rank in retry_ranks:
                print(f"   🔄 正在补录 #{rank} ...")
                
                # 补录时，我们尝试多给几次机会
                retry_attempts = 0
                success = False
                while retry_attempts < 2 and not success:
                    new_data = process_single_rank(page, rank, is_retry=True)
                    if new_data and len(new_data['items']) > 0:
                        collected_data_map[rank] = new_data
                        print(f"      ✅ 补录成功！#{rank} 物品: {len(new_data['items'])}")
                        success = True
                    else:
                        print(f"      ... 尝试 {retry_attempts+1} 失败，重试中")
                        # 稍微动一下鼠标，或者滚一下，改变环境
                        page.mouse.wheel(0, -100)
                        time.sleep(1)
                        retry_attempts += 1
                
                if not success:
                    print(f"      ❌ 补录放弃：#{rank} (可能真的没有物品)")

        # === 保存 ===
        final_list = sorted(collected_data_map.values(), key=lambda x: x['rank'])
        
        final_output = {
            "count": len(final_list),
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": final_list
        }

        with open("leaderboard-data.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
            
        print(f"\n🎉 全部结束！最终采集 {len(final_list)} 条。")
        browser.close()

if __name__ == "__main__":
    scrape_repair()