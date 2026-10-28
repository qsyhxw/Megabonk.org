"""Traditional Chinese beginner task, with local sources and edition boundaries."""
from build_pokebonk import ext,ref,section,table
P='/survivor-ace/'
ZP=P+'zh-hant/beginners-guide/'
JP=P+'ja/beginners-guide/'
SOURCES=[
 ('https://apps.apple.com/tw/iphone/story/id6800256713','App Store 台灣編輯介紹','自動射擊、隨機局內強化與局外成長；2026-10-28核對。'),
 ('https://www.4gamers.com.tw/news/detail/82663/survivor-ace-exhilarating-hands-on','4Gamers · 海德格 · 2026-10-23','繁中武器名稱、攻擊特性與科技研究／科研介紹；作者文章，不是本站實測。'),
 ('https://gamesakidori.com/dada-ace/dada-ace-beginner-guide/','ゲーム先取り · 2026-10-27','作者日本版iPhone約30分鐘記錄，僅補充裝備比對方式；不代表繁中版數值與介面已驗證。')]

def beginner_zh(shell):
 parts=[]
 start=f'<ol><li><strong>先適應移動。</strong>戰機會自動開火，先看清敵人和彈幕，再調整手指移動幅度。</li><li><strong>把選項分清楚。</strong>升級時先辨認是新增武器、強化已有武器，還是補攻擊／耐久等能力。</li><li><strong>結束後只追一個問題。</strong>先記下是打不中、清不掉，還是先被擊落，再決定下一次怎麼改。</li></ol><p>前兩項依遊戲介紹；最後一項是本站整理的判斷方法，不是保證通關的固定流程。'+ref(1)+ref(2)+'</p>'
 parts.append(('start','剛開始先做這三件事',start))
 weapons=table(['繁中資料中的武器','來源描述的特性','選擇前先問自己'],[
 ['高能激光','前方貫穿的能量攻擊','敵人會停在前方攻擊路線上嗎？'],
 ['灼熱射線','偏短射程、具有鎖定機制','靠近的目標是否正是目前要處理的敵人？'],
 ['速射機砲','向前射擊，後續強化可改變彈道與火力','原本的攻擊有持續命中，值得繼續強化嗎？']])
 weapons+=f'<p>武器名稱與特性依4Gamers的10月23日文章；右欄是本站依特性整理的選擇問題。這不是三選一必出清單，也不是強度排名。日本版作者另記錄過不同的開局三選，不應直接當成繁中版所有機體、關卡的預設武器。{ref(2)}{ref(3)}</p>'
 parts.append(('weapons','武器先比攻擊方式，不急著找唯一最強',weapons))
 draft=table(['這次遇到的情況','先比哪些選項','不要直接下的結論'],[
 ['攻擊一直落空','攻擊方向、範圍與追蹤特性','只要增加傷害數字就能解決'],
 ['能命中，但敵人越積越多','已有武器的強化與新武器能補的範圍','武器種類越多一定越強'],
 ['還沒打完就耗盡血量','眼前耐久選項的效果與另一個輸出選項','增加血量上限等於立即回復血量'],
 ['想要的武器沒出現','目前提供的候選能補哪一個不足','每次都能照攻略相同順序取得武器']])
 draft+=f'<p>隨機強化是遊戲本身的機制；表格是閱讀選項的檢查表，不是抽取機率或出現保證。先看手上已有的攻擊和目前敵人，再決定要延伸主力還是補另一種攻擊。{ref(1)}{ref(2)}</p>'
 parts.append(('draft','局內升級：新增武器，還是強化主力？',draft))
 growth=table(['決策位置','確認內容','資源投入前的問題'],[
 ['戰鬥中的強化畫面','這次出現的武器、配件或能力','能否補目前這一局的不足？'],
 ['局外科技研究／天賦相關畫面','顯示的能力、取得方式與金幣成本','眼前需要的是哪種基礎能力？'],
 ['局外科研','特定武器的藍圖需求、效果與解鎖條件','這是否是自己正在使用的武器路線？'],
 ['裝備強化畫面','強化前後的效果與消耗','下一級實際改善什麼，而非只看總戰力？']])
 growth+=f'<p>4Gamers把科技研究與特定武器的科研分開介紹，不能因名稱相近就當成同一個升級入口。裝備比對例子來自日本版作者，繁中介面名稱、成本和解鎖條件應以你的遊戲畫面為準。本站不提供未核實的全帳號固定養成順序。{ref(2)}{ref(3)}</p>'
 parts.append(('growth','局外養成：先確認入口、效果和花費',growth))
 retry='<ol><li>記下失敗關卡、使用武器，以及最後出現的升級選項。</li><li>用「打不中／清不掉／先被擊落」描述問題，不只記一個戰力數字。</li><li>下一次先改選項思路或一項局外強化，觀察相同問題是否仍出現。</li></ol><p>這是方便比較的記錄方式，不是本站完成通關測試的結論。一局成功也不足以證明某個配裝適用所有關卡。</p>'
 parts.append(('retry','卡關後，把下一次嘗試變成可比較的調整',retry))
 rewards=f'<p>先檢查已完成任務與遊戲內信件，再看禮包碼的來源期限。過去開服獎勵、別服清單或其他遊戲的代碼，都不能當成你現在必定能領取的資源。</p><p><a href="{P}zh-hant/codes/">噠噠戰機禮包碼與輸入位置 →</a></p><p>帳號、購買或獎勵未到帳問題，請透過{ext("https://play.google.com/store/apps/details?hl=zh_TW&id=com.survivor.ace","Google Play · 噠噠戰機應用程式支援")}查找開發者窗口。本站無法補發獎勵或恢復遊戲帳號。</p>'
 parts.append(('rewards','禮包碼與帳號問題，分別到哪裡處理？',rewards))
 sources='<section class="sources" id="sources"><h2>來源與適用範圍</h2><ol>'+''.join(f'<li id="source-{i}">{ext(u,l)} — {d}</li>' for i,(u,l,d) in enumerate(SOURCES,1))+'</ol><a class="back" href="#guide">返回正文 ↑</a></section>'
 toc='<aside class="toc" aria-label="本頁內容"><strong>本頁內容</strong>'+''.join(f'<a href="#{i}">{t}</a>' for i,t,_ in parts)+'<a href="#sources">來源</a></aside>'
 body=f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{P}">Survivor: Ace</a> / 繁中新手攻略</nav><header class="article-head" id="guide"><span class="tag">噠噠戰機 · 非官方攻略</span><h1>噠噠戰機新手攻略：武器選擇與養成順序</h1><p class="answer">先熟悉單指移動與自動射擊，再依「打不中、清不掉、先被擊落」判斷局內強化；回到局外後，分清裝備、科技研究和科研的效果與成本。先補眼前的不足，不把隨機選項當成每局必出的固定配裝。</p><p class="meta">Megabonk.org 編輯整理 · 核對日期：2026-10-28 · 依公開資料比對，非本站遊玩實測</p><p><a href="{JP}" lang="ja">日本語の序盤攻略 →</a></p></header><div class="article-layout"><article class="prose">'+''.join(section(*x) for x in parts)+sources+f'<section class="related"><h2>接著查看</h2><a href="{P}zh-hant/codes/">繁中禮包碼 →</a><a href="{P}#guides">Survivor: Ace 攻略總覽 →</a></section></article>'+toc+'</div>'
 return ZP,shell(ZP,'噠噠戰機新手攻略｜武器選擇與養成順序','噠噠戰機繁中新手指南：比較武器攻擊方式、局內升級與局外裝備、科技研究和科研，整理卡關後的調整順序，附來源與版本限制。',body,lang='zh-Hant',content=True)
