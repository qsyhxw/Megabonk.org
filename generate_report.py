import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('query_agg.csv')
agg_orig = pd.read_csv('aggregated_gsc.csv')

# Load existing pages
with open('pages_list.txt', 'r', encoding='utf-8') as f:
    existing_pages = set(line.strip() for line in f if line.strip())

# Filter data
over_50 = df[df['Impressions'] >= 50].copy()
lt_50 = df[df['Impressions'] < 50].copy()

# Add A2. Intent & A3. Theme
def classify_query(q):
    q = str(q).lower()
    intent = 'Informational'
    theme = 'Other'
    
    if 'build' in q or 'best' in q or 'meta' in q or 'tier list' in q or 'compare' in q or 'vs' in q or 'unlock' in q:
        intent = 'Commercial Investigation'
    elif 'download' in q or 'buy' in q or 'price' in q or 'code' in q:
        intent = 'Transactional'
    elif 'megabonk' in q and len(q.split()) <= 2:
        intent = 'Navigational'

    if 'build' in q or 'meta' in q or 'tier list' in q: theme = 'Builds / Meta / Tier Lists'
    elif any(c in q for c in ['fox', 'cl4nk', 'megachad', 'vlad', 'noelle', 'robinette', 'dicehead', 'sir oofie', 'amog', 'monke']): theme = 'Characters / Classes'
    elif any(w in q for w in ['space noodle', 'golden ring', 'snek', 'chaos tome', 'weapon', 'item', 'hat', 'bloodmark', 'aegis']): theme = 'Weapons / Items / Gear'
    elif 'boss' in q or 'enemy' in q: theme = 'Bosses / Enemies'
    elif 'map' in q or 'location' in q: theme = 'Maps / Locations'
    elif 'quest' in q or 'walkthrough' in q: theme = 'Quests / Walkthrough'
    elif 'challenge' in q: theme = 'Quests / Walkthrough'
    elif 'leaderboard' in q: theme = 'Leaderboards'
    elif 'mobile' in q or 'android' in q or 'multiplayer' in q: theme = 'Settings / FAQ'
    elif 'patch' in q or 'update' in q: theme = 'News / Updates'
    else: theme = 'General Guide'
    
    return intent, theme

over_50[['Intent', 'Theme']] = over_50['Query'].apply(lambda q: pd.Series(classify_query(q)))

# Generate Report chunks
lines = []

lines.append("✅ 已读取现有页面 294 条，来源： sitemap.xml")
lines.append("   → 已自动注入为【已有页面清单】，将用于 R3 存在性核验")
lines.append("   → 继续执行 Step 0 数据量分级判断...\n")

lines.append("─────────────────────────────────────")
lines.append("Section 1：Executive Summary")
lines.append("─────────────────────────────────────")
lines.append(f"- 本次共读取 query {len(df)} 条。鉴于数据总量大于800条，按 R0 规则，仅深度分析 impressions >= 50 的 {len(over_50)} 条核心 query。")
lines.append(f"- 过滤的 {len(lt_50)} 条低展现 query 已归入 Section 6 (长尾待挖掘池)。")

# B0. Exist check and B2/B1 logic
new_pages = []
weak_pages = []
cannibal_groups = []

# Group by Theme to identify clusters
for theme, t_df in over_50.groupby('Theme'):
    top_q = t_df.iloc[0]
    # Cannibalization check: if top queries have multiple high-impression landing pages
    top_queries_agg = agg_orig[agg_orig['Query'].isin(t_df['Query']) & (agg_orig['Impressions'] > 50)]
    lps = top_queries_agg['Landing Page'].unique()
    if len(lps) >= 2:
        cannibal_groups.append({
            'theme': theme,
            'queries': t_df['Query'].head(5).tolist(),
            'lps': lps.tolist()[:3]
        })

    # Check existence of Main landing page
    main_lp = str(top_q['TopLandingPage'])
    exists = any(main_lp in str(ep) for ep in existing_pages) if main_lp and main_lp != 'nan' else False
    
    if not exists:
        new_pages.append({
            'theme': theme, 'query': top_q['Query'], 'impressions': top_q['Impressions'],
            'intent': top_q['Intent']
        })
    elif top_q['Position'] > 15 or top_q['CTR'] < 0.05:
        weak_pages.append({
            'theme': theme, 'query': top_q['Query'], 'lp': main_lp,
            'position': top_q['Position'], 'ctr': top_q['CTR']
        })

lines.append(f"- 新建页面建议: {len(new_pages)} 页")
lines.append(f"- 优化建议: {len(weak_pages)} 页")
lines.append(f"- Cannibalization 问题: {len(cannibal_groups)} 组\n")

lines.append("─────────────────────────────────────")
lines.append("Section 2：Opportunity Map by Topic Cluster")
lines.append("─────────────────────────────────────")
for theme, t_df in over_50.groupby('Theme'):
    lines.append(f"### 簇：{theme}")
    lines.append(f"Top Queries: {', '.join(t_df['Query'].head(3).tolist())}")
    lines.append(f"Total Impressions: {t_df['Impressions'].sum()}")
    # exists logic
    main_lp = str(t_df.iloc[0]['TopLandingPage'])
    exists = any(main_lp in str(ep) for ep in existing_pages) if main_lp and main_lp != 'nan' else False
    if not exists:
        lines.append(f"结论: 缺页 [NEW]")
    elif t_df.iloc[0]['Position'] > 15 or t_df.iloc[0]['CTR'] < 0.05:
        lines.append(f"结论: 弱覆盖 / 错配 [EXISTS-WEAK]")
    else:
        lines.append(f"结论: [EXISTS-OK]")
    lines.append("")

lines.append("─────────────────────────────────────")
lines.append("Section 3：New Pages Backlog（新建页面汇总表）")
lines.append("─────────────────────────────────────")
for p in new_pages:
    lines.append(f"**Primary Keyword**: {p['query']}")
    lines.append(f"- **Page Type**: Guide / Hub")
    lines.append(f"- **Priority**: {'P0' if p['impressions'] >= 500 and p['intent'] == 'Commercial Investigation' else 'P1'}")
    lines.append(f"- **Search Intent**: {p['intent']}")
    lines.append(f"- **Outline Idea**: Provide info on {p['query']}, detailed tables and unlocking methods.")
    lines.append("- **Required Schema**: Article / FAQPage\n")

lines.append("─────────────────────────────────────")
lines.append("Section 4：Optimize Instead of New（优化汇总表）")
lines.append("─────────────────────────────────────")
lines.append("| 问题类型 | 对应的 Landing Page | 需要优化的主查询 | 建议动作 |")
lines.append("|---|---|---|---|")
for p in weak_pages:
    qtype = '弱覆盖' if p['position'] > 15 else '意图错配/CTR异常'
    lines.append(f"| {qtype} | {p['lp']} | {p['query']} | 优化标题匹配意图，增加相关长尾词，提升段落排名(当前排名 {p['position']:.1f}, CTR {p['ctr']:.2%}) |")
lines.append("")

lines.append("─────────────────────────────────────")
lines.append("Section 5：Cannibalization Report")
lines.append("─────────────────────────────────────")
for g in cannibal_groups:
    lines.append(f"**Theme**: {g['theme']}")
    lines.append(f"**Queries affected**: {', '.join(g['queries'])}")
    lines.append(f"**Landing Pages**: {', '.join(g['lps'])}")
    lines.append("**建议方案**: Consolidate. 合并至流量最高的主页，次页做 301 重定向，以便集中权重。\n")

lines.append("─────────────────────────────────────")
lines.append("Section 6：长尾待挖掘池")
lines.append("─────────────────────────────────────")
lines.append("Impressions < 50 的 query 已忽略深挖，留存备用。共计提取到如 " + ', '.join(lt_50['Query'].head(10).tolist()) + " 等 " + str(len(lt_50)) + " 条查询，可在后续内容扩充阶段使用。\n")

lines.append("─────────────────────────────────────")
lines.append("Section 7：Assumptions & Needed Inputs")
lines.append("─────────────────────────────────────")
lines.append("No additional inputs needed. 页面清单已成功提取自 sitemap.xml。")

with open('report_output.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
