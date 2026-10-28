"""Reproducible Survivor Ace hub and task pages; never hosts game code."""
from pathlib import Path
from html import escape
from build_pokebonk import ext, ref, table, section

ROOT=Path(__file__).resolve().parents[1]
P='/survivor-ace/'
BASE='https://megabonk.org'
ADS='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8830315294299920" crossorigin="anonymous"></script>'
PATHS={'zh-Hant':P+'zh-hant/codes/','ja':P+'ja/codes/'}
SOURCES=[
 ('https://nekonokyositu.com/survivorace/16002/','タカネコ · 2026-10-28','報道碼、期限與日文輸入流程 / 掲載コード・期限・入力手順'),
 ('https://jisu.tw/噠噠戰機-禮包碼/','JISU · 2026-10-28 checked','繁中輸入流程、獎勵差異；商業代儲網站，非官方 / 手順と報酬の相違。非公式の商業サイト'),
 ('https://elpisoul.site/dadaace/dadaace-code/','Elpisoul · 2026-10-26','ACEWIN截止時區、DAY777差異、鑰匙用途；部分引述其他攻略 / 期限・キー用途。一部は他サイトの引用'),
 ('https://play.google.com/store/apps/details?hl=en&id=com.survivor.ace','Google Play · Gorilla Studio','遊戲實體 / ゲームの識別'),
]
def sources(lang):
 title='來源與核對範圍' if lang=='zh-Hant' else '出典と確認範囲'
 back='返回正文 ↑' if lang=='zh-Hant' else '本文に戻る ↑'
 return '<section class="sources" id="sources"><h2>'+title+'</h2><ol>'+''.join(f'<li id="source-{i}">{ext(u,l)} — {d.split(" / ")[0 if lang=="zh-Hant" else -1]}</li>' for i,(u,l,d) in enumerate(SOURCES,1))+'</ol><a class="back" href="#guide">'+back+'</a></section>'

NAV=[('Start here',P+'#start'),('Guides',P+'#guides'),('Codes',P+'#codes'),('Megabonk','/')]
def shell(path,title,desc,body,lang='en',content=False,image='',error=False):
 nav=''.join(f'<a href="{u}"'+(' aria-current="page"' if path==u else '')+f'>{l}</a>' for l,u in NAV)
 groups=[PATHS,{'zh-Hant':P+'zh-hant/beginners-guide/','ja':P+'ja/beginners-guide/'}]
 alts=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE+u}">' for group in groups if path in group.values() for l,u in group.items())
 return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{BASE+path}">{alts}
{ADS if content else ''}{'<meta name="robots" content="noindex,follow">' if error else ''}<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/pokebonk/site.css"><link rel="stylesheet" href="/assets/survivor-ace/site.css">
<meta property="og:type" content="article"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{BASE+path}">
{f'<meta property="og:image" content="{BASE+image}">' if image else ''}<link rel="stylesheet" href="/assets/guide-article-layout.css"></head><body class="sa guide-layout"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{P}"><img src="/assets/survivor-ace/logo.svg" width="44" height="44" alt=""><span>Survivor: Ace<small>Megabonk.org · Independent</small></span></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav><details class="mobile-nav"><summary>Menu ☰</summary><nav class="mobile-links" aria-label="Mobile navigation">{nav}</nav></details></div></header>
<main class="wrap" id="main">{body}</main><footer class="footer"><div class="wrap footer-grid"><div><strong>Megabonk.org · Independent guides</strong><p>Survivor: Ace names belong to their owners. This website is not affiliated with Gorilla Studio. Source-based reporting; no code redemption test.</p><a href="/">Megabonk Wiki →</a></div><nav aria-label="Site information"><a href="{P}about/">About these guides</a><a href="{P}contact/">Contact</a><a href="/privacy-policy">Privacy</a></nav></div></footer></body></html>'''

def codes(lang):
 zh=lang=='zh-Hant'
 h1='噠噠戰機禮包碼與輸入方法' if zh else 'ダダエースのコードと入力方法'
 title='噠噠戰機禮包碼與輸入方法｜來源核對' if zh else 'ダダエースのギフトコード・入力方法と期限'
 desc='整理噠噠戰機已報道禮包碼、輸入位置及來源期限，標出獎勵衝突與未實兌限制，避免混用噠噠特攻代碼。' if zh else 'ダダエースの掲載コード、入力手順、期限を整理。報酬の食い違いと未検証の範囲を示し、ダダサバイバーとの取り違えを防ぎます。'
 answer='來源列出 ACETW66、ACETW88、ACETW99、ACEWIN 等代碼，本站未實兌。左上選單→設定→禮包碼，確認後查信箱。ACE777、DAY777 已超過來源期限；未註期限的碼也不保證有效。' if zh else '出典にはACEJP000、ACEJP888、ACEWINなどが掲載されていますが、当サイトでは未交換です。左上三本線→設定→ギフトコードで入力し、メールを確認。ACE777・DAY777は出典の期限を経過しています。'
 rows=[]
 for code,scope in [('ACETW66','TW'),('ACETW88','TW'),('ACETW99','TW'),('ACEJP000','JP'),('ACEJP888','JP'),('KRGIFT00','KR'),('KRGIFT55','KR'),('KRGIFT66','KR'),('KRGIFT88','KR'),('ACEWIN26','—'),('GOODACE','—'),('ACE666','—')]:
  rows.append([f'<code>{code}</code>',scope,'來源未註期限；未實兌' if zh else '期限記載なし・未交換'])
 rows.append(['<code>ACEWIN</code>','—','來源稱11/8截止；精確時區見下方' if zh else '出典は11/8まで。時刻の注記は下記'])
 body=f'<p>{"報道清單，不是已驗證有效碼。TW／JP／KR只是字串中的標記，不能證明對應伺服器限制或跨服可用。" if zh else "掲載情報の一覧であり、有効性を確認した一覧ではありません。TW・JP・KRは文字列の目印で、利用地域や共通利用の証明ではありません。"}{ref(1)}</p>'
 body+=table(['禮包碼' if zh else 'コード','字串標記' if zh else '文字列の目印','核對狀態' if zh else '確認状態'],rows)
 parts=[('codes','已報道禮包碼' if zh else '掲載されているコード',body)]
 expired=table(['代碼' if zh else 'コード','來源截止日' if zh else '出典の期限','處理方式' if zh else '扱い'],[['ACE777','2026-10-22','不列為有效碼' if zh else '有効コードに含めない'],['DAY777','2026-10-23','不列為有效碼' if zh else '有効コードに含めない']])
 expired+=f'<p>{"以上是來源列出的期限，不是本站測得的失效結果。ACEWIN 的日文清單寫11/8；Elpisoul寫11/8 00:00（UTC+8），換算日本時間為同日01:00。原始公告未核實，請在此之前查看遊戲內公告，不把這個時間當官方保證。" if zh else "上記は出典の期限であり、当サイトの失効テスト結果ではありません。ACEWINはタカネコが11/8まで、Elpisoulが11/8 00:00（UTC+8）と記載。日本時間では同日01:00です。元の告知は未確認なので、その時刻を公式の保証として扱わず、事前にゲーム内告知を確認してください。"}{ref(1)}{ref(3)}</p>'
 parts.append(('expiry','先看期限，再看獎勵' if zh else '期限を先に確認する',expired))
 steps=['進入遊戲大廳，點左上方三橫線選單。','開啟「設定」，選「禮包碼」（Gift Code）。','貼上完整代碼，去掉前後空白，按確認。','回到遊戲內信箱查看結果及實際獎勵。'] if zh else ['ロビー左上の三本線を開く。','「設定」から「ギフトコード」を選ぶ。','コード全文を入力し、前後の空白を除いてOKを押す。','ゲーム内メールで結果と実際の報酬を確認する。']
 parts.append(('redeem','禮包碼在哪裡輸入？' if zh else 'コードの入力場所', '<ol>'+''.join('<li>'+x+'</li>' for x in steps)+f'</ol><p>{"繁中路徑依JISU圖文、日文路徑依タカネコ圖文；未在本站裝置操作。找不到欄位時先核對遊戲名稱與版本，不套用另一遊戲的兌換網頁。" if zh else "手順はタカネコの画像付き説明とJISUの記事を照合したものです。当サイトの端末での実施記録ではありません。欄が見つからない場合はゲーム名と版を確認し、別ゲーム用の交換ページを使わないでください。"}{ref(1)}{ref(2)}</p>'))
 conflict=table(['項目','繁中JISU' if zh else 'JISU記事','日文來源' if zh else '日本語出典'],[['ACETW66','晶片密鑰×2' if zh else 'チップキー×2','精英密鑰×2' if zh else 'エリートキー×2'],['DAY777','—','タカネコ：精英×5；Elpisoul：精英×2' if zh else 'タカネコ：エリート×5、Elpisoul：エリート×2']])
 conflict+=f'<p>{"這些差異未獲原始公告解決，所以不根據攻略表預算資源或付款。先確認帳號實際收到哪種鑰匙，再看遊戲內可使用的箱子；不能把晶片鑰匙和裝備鑰匙當同一種。重抽攻略中的舊開服抽數也不能當成今天的保證。" if zh else "相違を解消できる元の告知は未確認です。記事の数字を前提に資源計画や購入を決めず、受け取ったキーの種類と開けられる箱をゲーム内で確認してください。チップ用と装備用を混同せず、過去の開始時ガチャ回数も現在の保証にしないでください。"}{ref(1)}{ref(2)}{ref(3)}</p>'
 parts.append(('differences','獎勵說法不同時怎麼判斷？' if zh else '報酬が食い違う場合の判断',conflict))
 helptext='若提示已領取，先查同帳號信箱記錄；若提示無效，記下完整錯誤與代碼，對照來源截止日。未標期限、跨語言清單出現，都不能排除地域、帳號或版本條件；不要反覆輸入同碼來判斷伺服器故障。找不到入口或沒有收到信件時，保留版本及畫面，使用商店所列遊戲客服。' if zh else '受取済みと表示されたら同じアカウントのメールを確認。無効の場合はエラー文とコードを控え、出典の期限と照合してください。期限未記載や他言語の記事への掲載だけでは、地域・アカウント・版の条件を否定できません。同じコードの再入力だけでサーバー障害と判断せず、入口がない、メールが届かない場合は版と画面を控えてストア記載のサポートへ。'
 parts.append(('help','輸入失敗或沒收到？' if zh else '入力できない・届かないとき',f'<p>{helptext}{ref(2)}</p><p>'+ext('https://play.google.com/store/apps/details?hl=en&id=com.survivor.ace','Google Play · App support')+'</p>'))
 identity='本頁是 Gorilla Studio 的飛行射擊遊戲 Survivor: Ace／噠噠戰機，不是 Survivor.io／噠噠特攻。請認準Android套件 com.survivor.ace；舊作的代碼、玩家ID及兌換方式不能直接照搬。' if zh else '対象はGorilla Studioの空戦ゲームSurvivor: Ace（ダダエース）。Survivor.io（ダダサバイバー）とは別です。Androidの識別子はcom.survivor.ace。旧作のコードやプレイヤーIDを使う手順をそのまま当てはめないでください。'
 parts.append(('which-game','先確認不是噠噠特攻' if zh else 'ダダサバイバーとの取り違えを防ぐ',f'<p>{identity}{ref(4)}</p><p>'+ext('https://www.survivor-ace.com/','Survivor: Ace · Official website')+'</p>'))
 community='巴哈姆特板可作社群入口；本次正文存取受限，未核實活躍度，也不把它稱為官方客服。更新碼請由遊戲官網的社群連結查公告；本站沒有取得原公告的代碼只標「來源報道」，不標官方已驗證。' if zh else 'コミュニティの投稿は開発元の回答と区別してください。新しい告知はゲーム公式サイトから案内されるアカウントへ。当サイトが元の告知を確認できていないコードは、公式確認済みではなく記事掲載情報として扱います。'
 parts.append(('community','公告與社群入口' if zh else '告知・コミュニティ',f'<p>{community}</p>'+ ('<p>'+ext('https://forum.gamer.com.tw/B.php?bsn=86353','巴哈姆特 · 噠噠戰機板')+'</p>' if zh else '')))
 other='ja' if zh else 'zh-Hant'
 language=f'<p><a href="{PATHS[other]}" lang="{other}">'+('日本語のコード案内 →' if zh else '繁體中文禮包碼說明 →')+'</a></p>'
 toc='<aside class="toc" aria-label="On this page"><strong>'+('本頁內容' if zh else '目次')+'</strong>'+''.join(f'<a href="#{i}">{t}</a>' for i,t,_ in parts)+'<a href="#sources">'+('來源' if zh else '出典')+'</a></aside>'
 body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">Survivor: Ace</a> / '+('禮包碼' if zh else 'コード')+f'</nav><header class="article-head" id="guide"><span class="tag">Survivor: Ace · Independent guide</span><h1>{h1}</h1><p class="answer">{answer}{ref(1)}{ref(2)}</p><p class="meta">Megabonk.org editors · 2026-10-28 · '+('非官方資料整理，未實兌' if zh else '非公式・出典照合、交換テストなし')+f'</p>{language}</header><div class="article-layout"><article class="prose">'+''.join(section(*part) for part in parts)+sources(lang)+'<section class="related"><h2>'+('站內相關入口' if zh else '関連するページ')+f'</h2>{language}<a href="{P}zh-hant/beginners-guide/" lang="zh-Hant">繁中新手攻略 →</a><a href="{P}ja/beginners-guide/" lang="ja">日本語：序盤攻略 →</a><a href="{P}#guides">Survivor: Ace · Guides →</a></section></article>'+toc+'</div>'
 return PATHS[lang],shell(PATHS[lang],title,desc,body,lang,True)

def build():
 pages=[codes(l) for l in PATHS]
 from survivor_ace_hub import make_pages
 pages+=make_pages(shell)
 from survivor_ace_zh import beginner_zh
 pages.append(beginner_zh(shell))
 for slug,title,text in [
  ('about/','About the Survivor Ace guides','<p>Megabonk.org publishes these independent, source-based task guides to Survivor: Ace. We are not Gorilla Studio, the publisher or game support. The hub and Chinese and Japanese beginner guides compare source-based upgrade decisions and edition limits. The Chinese and Japanese code articles distinguish reported strings, source deadlines and unresolved reward differences; we do not claim to have redeemed them.</p><p>We review the cited public pages and keep their dates and limits next to the relevant statements. Code availability can change between reviews. No account, game login or redemption service is offered here.</p><p><a href="'+PATHS['zh-Hant']+'">繁體中文禮包碼 →</a> · <a href="'+PATHS['ja']+'">日本語コード →</a></p>'),
  ('contact/','Contact the guide editors','<p>For corrections to these Survivor: Ace guides, email <a href="mailto:qsyhxw@gmail.com?subject=%5BMegabonk.org%5D%20Website%20feedback">qsyhxw@gmail.com</a>. Include the article URL, source URL, region and date. Do not send passwords or account credentials. We do not promise a response time.</p><p>For redemption, purchase or account problems, use '+ext('https://play.google.com/store/apps/details?hl=en&id=com.survivor.ace','Google Play · Survivor: Ace App support')+'. We cannot credit game rewards or recover accounts.</p><p><a href="'+PATHS['zh-Hant']+'">繁體中文禮包碼 →</a> · <a href="'+PATHS['ja']+'">日本語コード →</a></p>')]:
  path=P+slug
  pages.append((path,shell(path,title+' | Megabonk.org','Publisher, source-review method and contact for the independent Survivor Ace task guides.',f'<article class="legal" id="guide"><nav class="crumbs"><a href="/">Megabonk.org</a></nav><h1>{title}</h1><p class="meta">Updated 2026-10-28</p>{text}</article>')))
 pages.append((P+'404.html',shell(P+'404','Page not found | Survivor: Ace Guides','This guide page could not be found.',f'<article class="legal"><h1>Page not found</h1><p>Find the current guides and code pages from the <a href="{P}">Survivor: Ace guide index</a>.</p></article>',error=True)))
 for path,html in pages:
  f=ROOT/path.lstrip('/') if path.endswith('.html') else ROOT/path.lstrip('/')/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(html,encoding='utf-8')
 print('Built '+str(len(pages))+' pages; 5 content pages inherit AdSense once; trust/404 excluded.')

if __name__=='__main__':build()
