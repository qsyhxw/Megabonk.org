import os
import re
from pathlib import Path

# ================= 配置区域 =================

BASE_URL = 'https://megabonk.org'
TARGET_DIR = 'tr'

# 【关键】这里定义你要生成哪些页面
# 左边：本地文件路径
# 右边：对应的网页 URL 后缀（不带 https://megabonk.org/）
FILES_MAP = {
    'index.html': '', 
    'leaderboard/index.html': 'leaderboard/', 
    'guides/builds/index.html': 'guides/builds/',
    'guides/builds/noelle-best-build.html': 'guides/builds/noelle-best-build',
    'guides/characters/fox-kitsune-guide.html': 'guides/characters/fox-kitsune-guide',
    # 你未来每翻译一个新页面，就在这里加一行
}

# ===========================================

# 提取出所有 "已知的土耳其语 URL" 集合，用于比对
KNOWN_TR_URLS = set(FILES_MAP.values())

def process_page(file_path, url_slug):
    source_file = Path(file_path)
    
    if not source_file.exists():
        print(f"⚠️ 跳过: 找不到文件 {file_path}")
        return

    print(f"正在处理: {file_path}")
    content = source_file.read_text(encoding='utf-8')

    # 1. 语言声明
    content = content.replace('<html lang="en">', '<html lang="tr">')

    # 2. Hreflang & Canonical
    en_full_url = f"{BASE_URL}/{url_slug}"
    tr_full_url = f"{BASE_URL}/tr/{url_slug}"
    
    # Canonical 指向自己 (TR)
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

    # 3. 【智能防死链】导航链接替换
    # 逻辑：只有当链接的目标也在 KNOWN_TR_URLS 里时，才加 /tr/
    
    def smart_link_replace(match):
        original_href = match.group(1)
        
        # 清理链接，去掉首尾斜杠，为了匹配 KNOWN_TR_URLS
        # 比如 /guides/builds/ -> guides/builds
        clean_link = original_href.strip('/')
        
        # 检查是否命中（完全匹配 or 包含匹配）
        # 比如 clean_link 是 "guides/builds"，它在 KNOWN_TR_URLS 里吗？
        if clean_link in KNOWN_TR_URLS:
            # 命中！这是一个已生成的土耳其页面，可以安全替换
            if original_href.startswith('/'):
                return f'href="/tr{original_href}"'
            elif original_href.startswith(BASE_URL):
                return f'href="{original_href.replace(BASE_URL, BASE_URL + "/tr")}"'
        
        # 没命中，或者是不相关链接 -> 保持原样（指向英文版）
        return f'href="{original_href}"'

    # 排除 .css, .js 等资源文件的正则
    link_pattern = re.compile(r'href=["\'](?!.*\.css|.*\.js|.*\.png|.*\.jpg)(.*?)["\']')
    content = link_pattern.sub(smart_link_replace, content)

    # 4. 保存
    target_path = Path(TARGET_DIR) / file_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding='utf-8')

# 执行
for f_path, u_slug in FILES_MAP.items():
    process_page(f_path, u_slug)
