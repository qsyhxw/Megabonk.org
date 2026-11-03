from scripts.site_analytics import write_html
import os
import re
from pathlib import Path

# ================= 配置区域 =================

BASE_URL = 'https://megabonk.org'
TARGET_DIR = 'tr'

# 文件映射表
FILES_MAP = {
    'index.html': '', 
    'leaderboard/index.html': 'leaderboard/', 
    'guides/builds/index.html': 'guides/builds/',
    'guides/builds/noelle-best-build.html': 'guides/builds/noelle-best-build',
    'guides/characters/fox-kitsune-guide.html': 'guides/characters/fox-kitsune-guide',
    #在这里添加更多...
}

# ===========================================

KNOWN_TR_URLS = set(FILES_MAP.values())

def process_page(file_path, url_slug):
    # 1. 检查文件是否已存在 【核心修改！】
    target_path = Path(TARGET_DIR) / file_path
    
    if target_path.exists():
        print(f"🛑 跳过: {target_path} 已存在，防止覆盖你的翻译。")
        return  # 直接结束，不再往下执行覆盖操作

    # --- 如果文件不存在，才执行下面的生成逻辑 ---
    
    source_file = Path(file_path)
    if not source_file.exists():
        print(f"⚠️ 跳过: 找不到源文件 {file_path}")
        return

    print(f"🚀 正在生成新文件: {file_path}")
    content = source_file.read_text(encoding='utf-8')

    # 修改语言声明
    content = content.replace('<html lang="en">', '<html lang="tr">')

    # Hreflang & Canonical
    en_full_url = f"{BASE_URL}/{url_slug}"
    tr_full_url = f"{BASE_URL}/tr/{url_slug}"
    
    # 替换 Canonical
    content = re.sub(r'<link\s+rel=["\']canonical["\']\s+href=["\'].*?["\']\s*/?>', 
                     f'<link rel="canonical" href="{tr_full_url}">', content)

    # 注入 Hreflang
    hreflang_tags = f'''
    <link rel="alternate" hreflang="en" href="{en_full_url}" />
    <link rel="alternate" hreflang="tr" href="{tr_full_url}" />
    <link rel="alternate" hreflang="x-default" href="{en_full_url}" />
    '''
    if '</head>' in content:
        content = content.replace('</head>', f'{hreflang_tags}\n</head>')

    # 链接替换逻辑
    def smart_link_replace(match):
        original_href = match.group(1)
        clean_link = original_href.strip('/')
        if clean_link in KNOWN_TR_URLS:
            if original_href.startswith('/'):
                return f'href="/tr{original_href}"'
            elif original_href.startswith(BASE_URL):
                return f'href="{original_href.replace(BASE_URL, BASE_URL + "/tr")}"'
        return f'href="{original_href}"'

    link_pattern = re.compile(r'href=["\'](?!.*\.css|.*\.js|.*\.png|.*\.jpg)(.*?)["\']')
    content = link_pattern.sub(smart_link_replace, content)

    # 保存文件
    target_path.parent.mkdir(parents=True, exist_ok=True)
    write_html(target_path, content, encoding='utf-8')

# 执行
for f_path, u_slug in FILES_MAP.items():
    process_page(f_path, u_slug)
