"""Reviewed original v0.139.2 UI facts, not a combat model or copied build list.

Ranks, row gates and prerequisites transcribed from all 79 original Mage/Warlock
tooltips on 3 November 2026. Private captures preserve the inspection evidence.
"""
from pathlib import Path
import json,re,hashlib

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='45418605167579740a217b5beaafafb0bd5d04a2eab97afde3e3fd00a3a9b351'
def ident(name):return re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')

TREES={
 'mage':{
  'Arcane':[
   ('Arcane Focus',5,0,'Arcane damage'),('Arcane Subtlety',5,0,'Luck'),
   ('Improved Arcane Explosion',3,5,'Arcane Explosion area'),('Magic Absorption',5,5,'Maximum health'),
   ('Arcane Concentration',1,10,'Free Arcane Explosion interaction'),('Arcane Meditation',3,10,'Health recovery'),
   ('Arcane Mind',5,15,'Cooldown recovery'),('Improved Blink',3,15,'Movement speed'),
   ('Presence of Mind',1,20,'Additional missiles and a further target'),('Arcane Instability',3,20,'Damage and critical chance'),
   ('Arcane Fortitude',3,25,'Damage reduction'),('Arcane Reach',3,25,'Chance to strike twice'),
   ('Arcane Power',1,30,'Arcane Missiles starter and bounded repeat-strike cascades')],
  'Fire':[
   ('Improved Fireball',5,0,'Fireball cooldown'),('Impact',5,0,'Fire-hit stun chance'),
   ('Flame Throwing',2,5,'Fire area'),('Improved Flamestrike',5,5,'Flamestrike and Blast Wave damage'),
   ('Ignite',1,10,'Fire-critical damage over time'),('Incinerate',3,10,'Fire Blast damage'),
   ('Master of Elements',3,15,'Critical damage'),('Critical Mass',3,15,'Critical chance'),
   ('Hot Streak',1,20,'Free Pyroblast from repeated Fire critical hits'),('Fire Power',5,20,'Fire damage'),
   ('Burning Soul',3,25,'Maximum health'),('Improved Blast Wave',3,25,'Blast Wave and Pyroblast cooldowns'),
   ('Pyroclasm',1,30,'Pyroblast starter and Fire-kill explosions')],
  'Frost':[
   ('Frost Warding',5,0,'Damage reduction'),('Improved Frostbolt',5,0,'Frostbolt cooldown'),
   ('Elemental Precision',3,5,'Damage'),('Ice Shards',5,5,'Critical damage'),
   ('Frostbite',1,10,'Freeze chance on Frost hits'),('Piercing Ice',3,10,'Frost damage'),
   ('Shatter',5,15,'Damage against controlled enemies'),('Arctic Reach',2,15,'Frost control area'),
   ('Splitting Ice',1,20,'Frostbolt area interaction'),('Frost Channeling',3,20,'Cooldown recovery'),
   ('Permafrost',3,25,'Maximum health'),('Improved Ice Barrier',3,25,'Shield absorption'),
   ('Summon Water Elemental',1,30,'Frostbolt starter, elemental and periodic Frost Nova')]
 },
 'warlock':{
  'Affliction':[
   ('Suppression',5,0,'Luck'),('Shadow Embrace',5,0,'Damage over time'),
   ('Improved Curse of Agony',3,5,'Curse of Agony damage'),('Improved Drain Life',5,5,'Drain Life damage'),
   ('Nightfall',1,10,'Shadow Bolt and Corruption interactions'),('Soul Reaping',3,10,'Death Coil and Drain Life interaction'),
   ('Grim Reach',1,15,'Additional damage-over-time target'),('Shadow Mastery',5,15,'Shadow damage'),
   ('Contagion',1,20,'Damage-over-time spread after a kill'),('Amplify Curse',3,20,'Curse of Agony cooldown'),
   ('Siphon Life',1,25,'Healing from damage-over-time ticks'),('Fel Concentration',3,25,'Damage-over-time duration'),
   ('Seed of Corruption',1,30,'Corruption starter and afflicted-enemy death explosions')],
  'Demonology':[
   ('Demonic Familiar',5,0,'Permanent Imp and Immolate interaction'),('Demonic Embrace',5,0,'Maximum health'),
   ('Fel Stamina',3,5,'Damage reduction'),('Unholy Power',5,5,'Demon damage'),
   ('Soul Devourer',3,10,'Felhunter and damage-over-time consumption'),('Soul Link',3,10,'Voidwalker and shielding'),
   ('Demonic Echoes',3,10,'Demon repeat-strike chance'),('Master Demonologist',3,15,'Player damage and demon critical chance'),
   ('Legion Gate',1,20,'Lesser demons; changes under Demonic Supremacy'),('Demonic Supremacy',1,20,'Permanent greater demons; no lesser demons'),
   ('Summon Infernal',3,25,'Infernal summon chance'),('Summon Doomguard',3,25,'Doomguard summon chance'),
   ('Pact of the Nathrezim',1,30,'Dread Lord with Searing Pain scaling'),('Butcher',1,30,'Felguard with cleave and low-health interaction')],
  'Destruction':[
   ('Improved Shadow Bolt',5,0,'Shadow Bolt damage'),('Cataclysm',5,0,'Cooldown recovery'),
   ('Intensity',5,5,'Soulfire damage'),('Scorched Earth',5,5,'Hellfire damage and slow chance'),
   ('Shadow Cleave',1,10,'Additional Shadow Bolt targets'),('Improved Searing Pain',3,10,'Searing Pain and Immolate damage'),
   ('Destructive Reach',3,15,'Rain of Fire and Hellfire area'),('Devastation',5,15,'Critical chance'),
   ('Conflagrate',1,20,'Immolate starter and direct-hit explosions'),('Emberstorm',5,20,'Fire damage'),
   ('Ruin',3,25,'Critical damage'),('Bane',3,25,'Shadow Bolt and Immolate cooldowns'),
   ('Rain of Chaos',1,30,'A second Rain of Fire and slowing ground')]
 }
}
REQUIRES={
 'Presence of Mind':[('Arcane Concentration',1)],'Arcane Power':[('Presence of Mind',1)],
 'Hot Streak':[('Ignite',1)],'Pyroclasm':[('Hot Streak',1)],
 'Splitting Ice':[('Frostbite',1)],'Summon Water Elemental':[('Splitting Ice',1)],
 'Contagion':[('Nightfall',1)],'Seed of Corruption':[('Contagion',1)],
 'Soul Devourer':[('Demonic Familiar',5)],'Soul Link':[('Demonic Familiar',5)],
 'Pact of the Nathrezim':[('Legion Gate',1)],'Butcher':[('Legion Gate',1)],
 'Conflagrate':[('Shadow Cleave',1)],'Rain of Chaos':[('Conflagrate',1)]}
EXCLUDES={'Soul Devourer':['Soul Link'],'Soul Link':['Soul Devourer'],
          'Pact of the Nathrezim':['Butcher'],'Butcher':['Pact of the Nathrezim']}

def sequence(pairs):return [ident(n) for n,r in pairs for _ in range(r)]

def reference():
 result={'schema':1,'version':'0.139.2','build':'5cb6deb36','source_sha256':SOURCE_SHA,
         'checked':'2026-11-03','source':'https://wow.aethus.pl/','max_points':51,'classes':{},'examples':{}}
 for cls,trees in TREES.items():
  result['classes'][cls]={'name':cls.title(),'trees':[]}
  for tree,nodes in trees.items():
   entries=[]
   for name,cap,gate,summary in nodes:
    entry={'id':ident(name),'name':name,'max':cap,'gate':gate,'summary':summary,
           'requires':[{'id':ident(n),'rank':r} for n,r in REQUIRES.get(name,[])],
           'excludes':[ident(n) for n in EXCLUDES.get(name,[])]}
    if name=='Legion Gate':entry['requires_any']=[{'id':ident(n),'rank':3} for n in ['Soul Devourer','Soul Link']]
    entries.append(entry)
   result['classes'][cls]['trees'].append({'name':tree,'nodes':entries})
 result['examples']={
  'mage-fire':{'classId':'mage','name':'Fire: a 31-point core to adapt','budget':51,
   'sequence':sequence([('Improved Fireball',5),('Improved Flamestrike',5),('Ignite',1),('Impact',5),('Flame Throwing',2),('Critical Mass',3),('Hot Streak',1),('Fire Power',5),('Master of Elements',3),('Pyroclasm',1)]),
   'skills':'Keep the actual opening spell working. With Pyroclasm allocated, support Pyroblast and the Fire offers that serve the run. A specific card is not guaranteed.',
   'gear':'Compare the worn Armory bonuses first. Use the gear guide to locate a missing piece; no named set or amulet is required to load this talent plan.',
   'notes':'Editorial example, not a best-build ranking. Leaves 20 points unallocated. Improve recovery or damage only after identifying the failure in your own run.'},
  'warlock-affliction':{'classId':'warlock','name':'Affliction: a 31-point core to adapt','budget':51,
   'sequence':sequence([('Shadow Embrace',5),('Improved Curse of Agony',3),('Suppression',2),('Nightfall',1),('Improved Drain Life',5),('Shadow Mastery',4),('Contagion',1),('Shadow Mastery',1),('Amplify Curse',3),('Siphon Life',1),('Fel Concentration',3),('Grim Reach',1),('Seed of Corruption',1)]),
   'skills':'Establish Corruption or Curse of Agony from the offers you receive. Seed changes the opening to Corruption. Compare Drain Life or survival offers when recovery is missing.',
   'gear':'Keep the talent plan separate from class gear and in-run jewelry. Inspect an available DoT or recovery modifier instead of waiting for one exact item.',
   'notes':'Editorial example, not a measured clear-rate or boss-damage winner. Leaves 20 points unallocated. Contagion needs a death; an isolated boss does not supply the same chain.'}}
 return result

def write_reference():
 path=ROOT/'data/azeroth-planner.json'
 path.write_text(json.dumps(reference(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':write_reference()
