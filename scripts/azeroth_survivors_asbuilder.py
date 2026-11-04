"""Reviewed ASBuilder web/addon workflow and scoped visual catalog additions."""
from html import escape
import json
from pathlib import Path
from azeroth_survivors_content import SOURCES, a, ext, para, ref, steps, table

ROOT = Path(__file__).resolve().parents[1]


def register_sources():
    SOURCES['asbuilder_web'] = (
        'https://asbuilds.app/', 'Cadoky · ASBuilder online',
        'Read and interacted with on 4 November 2026. A local Warrior plan was created with Cleave, Quick Strike Ring, Mark of the Chosen and Choker of Enlightenment. Stage copying, explicit Save, reload persistence and ASB2 export/import back into the web tool passed. Talents and Armory views were inspected. No public build was posted, account created, addon installed or game save imported. The response sets X-Frame-Options DENY and CSP frame-ancestors none. Public sprite v=0134 supplies the manually reviewed name/icon pairs; this does not verify current gameplay values or grant an open artwork licence.')
    SOURCES['asbuilder_author'] = (
        'https://github.com/cadoky/ASBuilder', 'Cadoky · ASBuilder addon project',
        'Author README read 4 November 2026. Documents spell targets, jewelry alternatives, stages, ASB2 sharing, /asb and the benilla-config/AddOns desktop folder. Card-screen panels are described for game 0.126.0+. The addon cannot read game talent data and offers a screenshot link. Documentation review only; no installation or in-game code-import test.')


def tool_capture():
    return '<figure class="asbuilder-screen"><a href="/assets/azeroth-survivors/images/asbuilder-loadout-1280.webp" target="_blank" rel="noopener"><img src="/assets/azeroth-survivors/images/asbuilder-loadout-800.webp" srcset="/assets/azeroth-survivors/images/asbuilder-loadout-800.webp 800w, /assets/azeroth-survivors/images/asbuilder-loadout-1280.webp 1280w" sizes="(max-width:800px) calc(100vw - 36px), 1000px" width="1280" height="889" loading="lazy" alt="ASBuilder online Warrior plan with a spell, ring, trinket and amulet selected"></a><figcaption>ASBuilder web interface captured 4 November 2026. Local workflow example with four selected entries, kept private. Tool UI by Cadoky; Warcraft artwork © Blizzard Entertainment. The displayed item text belongs to the planner snapshot. '+ref('asbuilder_web')+'</figcaption></figure>'


def page():
    return dict(
        id='AZASB01', slug='asbuilder/', title='ASBuilder Guide: Online Builds, Addon & Share Codes',
        h1='ASBuilder for Azeroth Survivors',
        desc='Create an ASBuilder plan online, arrange stages and jewelry, and copy an ASB2 code. Compare web planning, the in-game addon and local talent tools.',
        answer='ASBuilder is Cadoky’s Azeroth Survivors planning tool. Its online version at asbuilds.app lets you choose a class, arrange spells and jewelry by stage, edit talents and keep a browser draft. The separate addon displays planned choices during a run. '+ext('https://asbuilds.app/','ASBuilds.app · open ASBuilder online')+' · '+a('build-planner/','Use our Mage &amp; Warlock talent planner here')+ref('asbuilder_web')+ref('asbuilder_author'),
        review_note='Checked 4 November 2026 · Web planning, saving and ASB2 round trip inspected · Addon installation and current game-stat parity need verification',
        parts=[
            ('choose','Choose the ASBuilder workflow you need',
             table(['Your task','Where to do it','Check before continuing'],[
                 ['Plan cards and jewelry for a run','ASBuilder online · Loadout','Select the class and stage before adding a pick.'],
                 ['Plan talents or pre-run equipment','ASBuilder online · Talents / Armory','Compare its tree and item text with your current game.'],
                 ['See the next planned pick while playing','ASBuilder addon · /asb','Install the author package in the client you actually use.'],
                 ['Keep an ordered Mage or Warlock talent route on this site',a('build-planner/','Megabonk.org talent planner'),'Uses its stated v0.139.2 snapshot and separate share format.']])+para('A new character’s earned points and available equipment still constrain the plan. A public build’s popularity does not establish your current version or progression. '+ref('asbuilder_web')+ref('asbuilder_author'))),
            ('create','Create an ASBuilder plan online',
             steps(['Open ASBuilds.app. Dismiss the first-use tour with Skip, or follow its four screens. Choose a class and enter a Build name. Use + New build when you want another draft.',
                    'In Loadout, choose Early Game, Mid Game, End Game or Endless. These stage names can be changed. Click a spell icon to add it, set its target rank and move it into priority order.',
                    'Choose Rings, Trinkets and Amulet in the picker. The web layout offers two main rings and two alternatives, two main trinkets and two alternatives, and one main amulet with three alternatives. Alternatives are fallback choices, rather than extra worn slots.',
                    'Move to the next stage. Copy previous carries the earlier picks forward so you can adjust the next targets. Record a reason for changing spells or jewelry in Notes.',
                    'Use Talents to inspect the class tree and Armory for pre-run equipment. Check the corresponding rules in your current game before following the finished plan.',
                    'Click Save after editing. Reload and confirm the intended class, stage and entries remain before closing the tab. Keep an export as a separate backup.'])+para('Our 4 November check completed these loadout choices, stage copying, explicit saving and reload recovery in a desktop Chrome session. The same plan was viewed at a 390-pixel mobile width. Talent allocation accuracy, physical-phone input and game-side use were outside this check. '+ref('asbuilder_web'))+tool_capture()),
            ('codes','Copy, import and back up a build',
             steps(['Copy code exports the selected build as an ASB2 code. Keep the complete string together with your game version and a short note about the plan.',
                    'Import code accepts an ASB2 build or an ASBP whole-profile code in the web interface. Our ASB2 check added another build to the list. Inspect the imported class, stages and picks before editing.',
                    'Copy whole profile is the separate backup route for the browser’s collection of plans. A profile import can merge plans, so check the list afterward.',
                    'Share publicly uses a separate account/publication flow. Review notes and image links before choosing publication. We checked local code sharing without creating an account or publishing a build.'])+para('The ASB2 round trip was verified between two states of the web planner. Import into the game addon still needs a client-specific check. Game progress is backed up through '+a('save-backup/','the game’s own save export')+'. Our on-site talent planner uses its own link and JSON format. '+ref('asbuilder_web')+ref('asbuilder_author'))),
            ('addon','Use the addon with the right client',
             para(ext('https://github.com/cadoky/ASBuilder/releases/latest','GitHub · Cadoky’s latest ASBuilder addon')+' is the author’s download route. The README places the ASBuilder folder inside <code>benilla-config/AddOns/</code>, then restarts the game and opens the planner with <code>/asb</code> or its book button. '+ref('asbuilder_author'))+
             para('For the browser client, follow '+a('addons/#browser','Options → AddOns → Install AddOns')+' and check the package in that client. The original AddOns capture documents that dated interface. We have not installed ASBuilder there or confirmed its current import behaviour.')+
             para('The author describes an in-run tracker and stage targets. Its README says the addon cannot read game talent data and instead supports a talent screenshot link. The online Talents editor is a separate feature visible on the web tool. '+ref('asbuilder_author')+ref('asbuilder_web'))),
            ('embed','Can you create a build inside this page?',
             para('ASBuilds.app currently refuses framing by other sites. Its 4 November response sends <code>X-Frame-Options: DENY</code> and CSP <code>frame-ancestors \'none\'</code>. An iframe on this page would be blocked by the browser. '+ref('asbuilder_web'))+
             para('Use '+ext('https://asbuilds.app/','ASBuilds.app · online planner')+' in its own tab and keep this guide beside it. For an editable tool on Megabonk.org, '+a('build-planner/','open the Mage &amp; Warlock talent planner')+'. A working ASBuilder embed would require a publisher-supported embedding route or a policy change from its owner.')),
            ('questions','ASBuilder questions',
             '<h3>Do I need the addon to plan online?</h3>'+para('The web loadout flow worked without an addon installation or account in our check. The addon is the route for displaying the plan during a game run. '+ref('asbuilder_web')+ref('asbuilder_author'))+
             '<h3>Where are my private plans saved?</h3>'+para('The web interface stores plans in the current browser. Use its Save and export controls before clearing site data or changing device. Public sharing is a separate action. '+ref('asbuilder_web'))+
             '<h3>Does a code prove that the build works on the latest patch?</h3>'+para('A successful import confirms that the planner could read the code. Check talents, spell effects and item previews against the current game before applying it. '+a('patch-notes/#source-monitor','Check our original-client version record')+' · '+a('items/#visual-catalog','Match the jewelry name and icon')+ref('asbuilder_web')))
        ], related=[('addons/','Install and compare addons'),('builds/','Choose a class route'),('items/#visual-catalog','Identify jewelry'),('build-planner/','Plan Mage or Warlock talents here')])


def visual_catalog():
    data=json.loads((ROOT/'data/azeroth-asbuilder-icons.json').read_text(encoding='utf8'))
    body=para('Match both the name and icon when copying a plan. This visual index records the ASBuilder catalog checked on 4 November 2026. Use the effect comparisons above and the actual offer in your game to decide what to take. Legendary names can group several class/spell variants, so a matching necklace picture alone does not establish the affected spell or current stats. '+ref('asbuilder_web'))
    for key,label in [('rings','Rings'),('trinkets','Trinkets'),('amulets','General amulets'),('legends','Legendary name groups')]:
        rows=''
        for entry in data['catalog'][key]:
            note=' <small>Source icon unavailable.</small>' if entry['icon'] is None else ''
            rows+='<li><strong>'+escape(entry['name'])+'</strong>'+note+'</li>'
        body+='<details class="az-catalog-group"><summary>'+label+' · '+str(len(data['catalog'][key]))+' labels</summary><ul class="az-icon-catalog">'+rows+'</ul></details>'
    return ('visual-catalog','Match rings, trinkets, amulets and legendary icons',body+para('These are the planner’s display categories and name groups. Shared icons and variants prevent adding these numbers into a complete current-game item total. For a planned sequence, '+a('asbuilder/#create','follow the ASBuilder web workflow')+'. '+ref('asbuilder_web')))


def apply_asbuilder(pages):
    register_sources()
    for item in pages:
        if item['slug']=='addons/':
            item['parts']=[('asbuilder','ASBuilder online and the in-run addon',para('Use '+a('asbuilder/','the ASBuilder guide')+' for online class/loadout planning, stages, ASB2 codes and browser backups. ASBuilds.app now has Loadout, Talents and Armory views. The separate addon opens with /asb and shows planned priorities in-game. '+ref('asbuilder_web')+ref('asbuilder_author'))+para('The web editor and addon have different talent-data boundaries. The author’s addon README still describes a screenshot link because addons cannot read game talent data. The browser installation steps below describe the original client menu, rather than a verified ASBuilder install.')) if i=='asbuilder' else (i,t,h) for i,t,h in item['parts']]
            item['review_note']+=' · ASBuilder web workflow checked 4 November 2026'
        if item['slug']=='items/':
            item['parts'].insert(3,visual_catalog())
            item['review_note']+=' · Visual name/icon catalog added 4 November 2026; older effect descriptions retain their stated version'
        if item['slug']=='builds/':
            item['parts']=[(i,t,h+para(a('asbuilder/','ASBuilder web loadouts and addon codes')+' offers staged spell and jewelry planning. Its code format is separate from our on-site talent planner.')) if i=='planner' else (i,t,h) for i,t,h in item['parts']]
        if item['slug']=='build-planner/':
            item['parts'][-1]=(item['parts'][-1][0],item['parts'][-1][1],item['parts'][-1][2]+para('For other classes and staged jewelry choices, '+a('asbuilder/','see the ASBuilder online workflow')+'. Its ASB2 exports use a separate format.'))
    return pages+[page()]


def home_asbuilder(html):
    return html.replace('href="/azeroth-survivors/addons/#asbuilder"','href="/azeroth-survivors/asbuilder/"')
