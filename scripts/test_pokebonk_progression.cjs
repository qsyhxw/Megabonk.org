const assert=require('node:assert/strict'),D=require('../data/pokebonk-progression-reference.json'),M=require('../assets/pokebonk/progression-math.js'),P=require('../assets/pokebonk/panel-math.js');
function close(actual,expected,label){for(const[k,v]of Object.entries(expected)){if(typeof v==='number')assert(Math.abs(actual[k]-v)<1e-9,label+' '+k+': '+actual[k]+' != '+v);else if(v&&typeof v==='object')close(actual[k],v,label+'.'+k)}}
for(const f of D.fixtures){const def=D.moves.find(x=>x.key===f.key),r={level:f.target,cards:f.cards.map(x=>({r:x.rarity,k:x.keys}))},m=M.upgrade(def,r,D.arches,D.rarities,10);assert.equal(m.known,f.target-1);close(m.mods,f.mods,f.key+' mods');close(M.packet(def,m,{},D.arches),f.packet,f.key+' packet')}
for(const f of D.combinedFixtures)close(P.caps(P.groups(P.base(f.raw,f.stage,f.lab),f.groups)),f.expected,'grouped Alpha fixture');
const def=D.moves.find(x=>x.key==='water-gun');
assert.equal(M.upgrade(def,{level:99},D.arches,D.rarities).level,8);
assert.equal(M.upgrade(def,{level:99},D.arches,D.rarities,10).level,10);
const unknown=M.upgrade(def,{level:8},D.arches,D.rarities);assert.equal(unknown.known,0);assert(Math.abs(unknown.mods.dmg-1.56)<1e-9);assert.equal(unknown.mods.cd,1);
assert.equal(M.upgrade(def,{level:2,cards:[{r:0,k:['dmg','dmg']}]},D.arches,D.rarities).known,0);
assert.equal(M.upgrade(def,{level:2,cards:[{r:3,k:['dmg','cd']}]},D.arches,D.rarities).known,0);
const lab=D.lab[0],b=M.budget(D.lab,{}, {[lab.id]:lab.max},0);assert.equal(b.total,lab.costs.reduce((a,b)=>a+b,0));assert.equal(b.left,-b.total);
const own={[lab.id]:lab.max},target={[lab.id]:0};assert.equal(M.budget(D.lab,own,target,100).total,0);assert.equal(M.budget(D.lab,own,target,100).effective[lab.id],lab.max);assert.equal(own[lab.id],lab.max);assert.equal(target[lab.id],0);
assert.equal(M.packet({...def,arch:'weather'},unknown,{},D.arches),null);
console.log('PASS 12 original-runtime upgrade/packet fixtures, 2 grouped Alpha fixtures, caps, missing/distinct card rules and non-refund budget boundaries.');
