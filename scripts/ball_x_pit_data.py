"""Source-based recipe edges, not a damage or strength model. Checked 2026-10-30."""
SOURCES = {
 'official':('https://store.steampowered.com/app/2062430/BALL_x_PIT/','Steam · Kenny Sun and Friends / Devolver Digital','Current game and platform description'),
 'news':('https://steamcommunity.com/app/2062430/allnews/','Steam · developer announcements','Regal 26 Jan, Shadow 27 Apr, Naturalist 6 Aug 2026; Risen announcement 20 Sep'),
 'base':('https://www.reddit.com/r/BALLxPIT/comments/1nz0sod/all_ball_evolutions/','Reddit · tetracycloide','Full-release recipe post and corrections; older community observations'),
 'regal':('https://www.reddit.com/r/BALLxPIT/comments/1qnmyrv/regal_update_all_evolutions/','Reddit · hashtagtylerh','Regal recipes and laser clarification; 2026 update discussion'),
 'shadow':('https://www.reddit.com/r/BALLxPIT/comments/1sxd07s/shadow_update_all_evolutions/','Reddit · hashtagtylerh','Shadow recipes and max-level/core/Evolution instructions; 2026 discussion'),
 'naturalist':('https://www.reddit.com/r/BALLxPIT/comments/1vh5hhi/new_evolutions/','Reddit · LurkingIgges in Ok_Command1519’s thread','Naturalist recipes; some community names differ from the English guide'),
 'recipes':('https://www.dexerto.com/wikis/ball-x-pit/all-evolution-recipes-combinations/','Dexerto · Nathan Warby','6 Aug 2026 update; English recipe names and final chains'),
 'passives':('https://gamefaqs.gamespot.com/pc/539487-ball-x-pit/faqs/82316','GameFAQs · DCRage','Version 4.0, 15 Aug 2026; use recipe ingredients, not disputed effect values or update chronology'),
 'new':('https://allthings.how/ball-x-pit-how-to-unlock-the-naturalist-update-s-new-characters-and-evolutions/','AllThingsHow Staff','7 Aug 2026; four Naturalist passive recipes; automatic-evolution wording is not used'),
 'pairs':('https://www.reddit.com/r/BALLxPIT/comments/1x8eobc/best_character_combos/','Reddit · W0mb0C0mb019 and respondents','Progress-limited pairing question and conflicting preferences; exact post date not verified'),
 'tier':('https://www.dexerto.com/wikis/ball-x-pit/character-tier-list-2/','Dexerto · Cande Maldonado','6 Aug 2026 ranking; editorial opinion, not our benchmark'),
 'characters':('https://www.dexerto.com/wikis/ball-x-pit/all-characters-how-to-unlock-them-2/','Dexerto · James Busby','6 Aug 2026; houses/characters. Fixed biome drop claims are not adopted'),
 'trophy':('https://daynglsgameguides.com/2025/10/15/ball-x-pit-trophy-guide-roadmap/','Dayngls’ Guides · Dayngls','Base-game trophy route, originally 15 Oct 2025; later updated 15 Jun 2026'),
 'shield':('https://steamcommunity.com/app/2062430/discussions/0/624436409753006542/','Steam Community · Seasoul / NyX','19 Oct 2025: stone-ally requirement and success reply'),
 'ios':('https://apps.apple.com/us/app/ball-x-pit/id6738703497','App Store · Devolver','US mobile listing; regional availability and prices may differ'),
 'switch':('https://www.nintendo.com/us/store/products/ball-x-pit-nintendo-switch-2-edition-switch-2/','Nintendo · Switch 2 Edition','Official qualitative resolution/frame-rate improvement; no numerical benchmark'),
}
# One documented path per output; aliases/alternative inputs are kept separately.
RAW = {
 'Base':'''Assassin|Iron+Ghost
Berserk|Charm+Burn
Black Hole|Dark+Sun
Blizzard|Freeze+Lightning
Bomb|Burn+Iron
Flash|Lightning+Light
Flicker|Light+Dark
Freeze Ray|Freeze+Laser (Horizontal)
Frozen Flame|Burn+Freeze
Glacier|Freeze+Earthquake
Hemorrhage|Bleed+Iron
Holy Laser|Laser (Horizontal)+Laser (Vertical)
Incubus|Charm+Dark
Inferno|Burn+Wind
Laser Beam|Laser (Horizontal)+Light
Leech|Brood Mother+Bleed
Lightning Rod|Lightning+Iron
Lovestruck|Charm+Light
Maggot|Cell+Brood Mother
Magma|Burn+Earthquake
Mosquito King|Vampire+Brood Mother
Mosquito Swarm|Vampire+Egg Sac
Noxious|Poison+Wind
Nuclear Bomb|Bomb+Poison
Overgrowth|Earthquake+Cell
Phantom|Dark+Ghost
Radiation Beam|Poison+Laser (Horizontal)
Sacrifice|Bleed+Dark
Sandstorm|Earthquake+Wind
Satan|Incubus+Succubus
Shotgun|Iron+Egg Sac
Soul Sucker|Vampire+Ghost
Spider Queen|Brood Mother+Egg Sac
Storm|Lightning+Wind
Succubus|Charm+Vampire
Sun|Burn+Light
Swamp|Poison+Earthquake
Vampire Lord|Vampire+Bleed
Virus|Ghost+Poison
Voluptuous Egg Sac|Egg Sac+Cell
Wraith|Freeze+Ghost
Nosferatu|Vampire Lord+Spider Queen+Mosquito King''',
 'Regal':'''Banished Flame|Burn+Dark
Brimstone|Stone+Burn
Catapult|Stone+Egg Sac
Fireworks|Burn+Egg Sac
Landslide|Stone+Earthquake
Laser Cutter|Steel+Laser (Horizontal)
Steel|Iron+Stone''',
 'Shadow':'''Banshee|Phantom+Wraith
Erosion|Time+Wind
Heart Swallower|Bleed+Ghost
Reaper|Soul Sucker+Heart Swallower
Sniper|Shotgun+Assassin
Time Bomb|Time+Bomb
Timestop|Time+Freeze
Venom|Poison+Freeze
Warp|Time+Light
X Ray|Holy Laser+Laser Beam''',
 'Naturalist':'''Armageddon|Inferno+Storm
Mosquito Kingdom|Mosquito King+Mosquito Swarm
Lightning Bug|Lightning+Brood Mother
Elemental|Burn+Freeze+Earthquake+Wind
Drill|Earthquake+Iron
Tumor|Flesh+Radiation Beam
Flesh Mound|Flesh+Brood Mother
Petrify|Flesh+Stone
Offspring|Flesh+Cell
Zombie|Flesh+Vampire'''
}
ALTERNATIVES = {
 'Assassin':[['Iron','Dark']], 'Berserk':[['Charm','Bleed']], 'Blizzard':[['Freeze','Wind']],
 'Freeze Ray':[['Freeze','Laser (Vertical)']], 'Laser Beam':[['Laser (Vertical)','Light']],
 'Lovestruck':[['Charm','Lightning']], 'Noxious':[['Dark','Wind']],
 'Radiation Beam':[['Poison','Laser (Vertical)'],['Cell','Laser (Horizontal)'],['Cell','Laser (Vertical)']],
 'Vampire Lord':[['Vampire','Dark']], 'Virus':[['Cell','Poison'],['Bleed','Poison']],
 'Brimstone':[['Poison','Burn']], 'Laser Cutter':[['Steel','Laser (Vertical)']],
}
BALLS=[dict(name=line.split('|')[0],inputs=line.split('|')[1].split('+'),version=v,
 source={'Base':'base','Regal':'regal','Shadow':'shadow','Naturalist':'naturalist'}[v],
 alternatives=ALTERNATIVES.get(line.split('|')[0],[]))
 for v,lines in RAW.items() for line in lines.splitlines()]
PASSIVES=[
 ('Cornucopia',['Baby Rattle','War Horn'],'Base','base'),
 ('Gracious Impaler',["Reacher’s Spear","Deadeye’s Amulet"],'Base','base'),
 ('Odiferous Shell',['Wretched Onion','Breastplate'],'Base','base'),
 ('Phantom Regalia',['Ghostly Corset','Ethereal Cloak'],'Base','base'),
 ('Soul Reaver',['Vampiric Sword','Everflowing Goblet'],'Base','passives'),
 ('Tormentor’s Mask',['Spiked Collar','Crown of Thorns'],'Base','base'),
 ('Wings of the Anointed',['Radiant Feather','Fleet Feet'],'Base','base'),
 ('Deadeye’s Cross',['Ruby Hilted Dagger','Diamond Hilted Dagger','Sapphire Hilted Dagger','Emerald Hilted Dagger'],'Base','base'),
 ('Deadeye’s Impaler',['Gracious Impaler','Deadeye’s Cross'],'Regal','regal'),
 ('Grotesque Artillery',['Hand Fan','Turret'],'Regal','regal'),
 ('Argent Stopwatch',['Hourglass','Silver Bullet'],'Shadow','shadow'),
 ('Arrow of Fate',["Lover’s Quiver",'Hand Mirror'],'Shadow','shadow'),
 ('Full Metal Rapier',['Iron Onesie','Sword Breaker'],'Shadow','shadow'),
 ('Ardent Tire',['Rubber Headband','Wagon Wheel'],'Naturalist','new'),
 ('Inglorious Hammer',['Platinum Dumbbell','Upturned Hatchet'],'Naturalist','new'),
 ('Remote Detonator',['Magnet','Pressure Valve'],'Naturalist','new'),
 ('Windweaver',['Bottled Tornado','Slingshot'],'Naturalist','new'),
]
ITEMS=[dict(name=n,inputs=i,version=v,source=s,alternatives=[]) for n,i,v,s in PASSIVES]
CHARACTERS=[
 ('The Warrior','Available from the start','Base'),
 ('The Itchy Finger',"Sheriff’s Office",'Base'),('The Embedded',"Veteran’s Hut",'Base'),
 ('The Repentant','Haunted House','Base'),('The Cohabitants','Cozy Home','Base'),
 ('The Physicist','Laboratory','Base'),('The Spendthrift','Mansion','Base'),
 ('The Flagellant','Monastery','Base'),('The Shade','Mausoleum','Base'),
 ('The Radical','Campground','Base'),('The Empty Nester','Single Family Home','Base'),
 ('The Shieldbearer','Iron Fortress','Base'),('The Cogitator','Villa','Base'),
 ('The Tactician',"Captain’s Quarters",'Base'),('The Juggler','Theater','Base'),
 ('The Makeshift Sisyphus','Rocky Hill','Base'),('The Falconer','Falconry Hut','Regal'),
 ('The Carouser','Party House','Regal'),('The Tiptoer','Hidden Temple','Shadow'),
 ('The Tunneler','Stone Domain','Shadow'),('The Hoary Hoarder','Unstable Tower','Naturalist'),
 ('The Ballbearer','Ball House','Naturalist')]
