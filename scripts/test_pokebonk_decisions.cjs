const assert=require('assert'),fs=require('fs'),M=require('../assets/pokebonk/decisions.js'),d=require('../data/pokebonk-decisions-reference.json'),r=require('../data/pokebonk-tools-reference.json');
const close=(a,b)=>assert(Math.abs(a-b)<1e-10,`${a} != ${b}`);
assert.equal(Object.keys(d.leagueRequirements).length,79);assert.equal(d.leagueRequirements['108'][1].goal,7000);assert.equal(d.latestReview.version,'0.8.68');assert.equal(d.moves.length,310);assert.equal(new Set(d.moves.map(m=>m.key)).size,310);
for(const m of d.moves){assert(m.cd>0&&Number.isFinite(m.dmg));assert.deepEqual(m.owners,r.league.filter(x=>x.kit.some(k=>k.key===m.key)).map(x=>x.id))}
for(const[type,fixture]of Object.entries(d.alphaFixtures))for(const[mode,mods]of Object.entries(fixture)){const actual=M.alpha(d.alphaTypes,mode==='shiny'?[]:[type],mode==='shiny'?type:'',mode==='doll'?1:0,0);for(const mod of mods){const got=actual.sums[mod.stat];if(mod.add!=null)close(got.add,mod.add);if(mod.mul!=null)close(1+got.bonus,mod.mul)}}
const team=M.alpha(d.alphaTypes,['ground','ground'],'ground',2,3);close(team.sums.armor.add,32);close(team.damage,1.75);close(team.rate,1.45);
for(const x of d.conditionFixtures)close(M.conditions(x.hp*100,0,null,true,0,0,false).rage,1+x.rage);
close(M.conditions(40,0,1.4,false,0,0,false).passive,1);close(M.conditions(39.99,0,1.4,false,0,0,false).passive,1.4);
close(M.conditions(100,1000,null,false,2,3,true).club,2);close(M.conditions(100,0,null,false,0,3,true).metalArmor,1.9);
let b=M.budget(d.lab,d.budgetPriorities.fusion,{},1274);assert.equal(b.spent,0);assert.equal(b.next.short,1);
b=M.budget(d.lab,d.budgetPriorities.fusion,{},1275);assert.equal(b.levels['slot-move'],1);assert.equal(b.spent,1275);
b=M.budget(d.lab,d.budgetPriorities.fusion,{'slot-move':1},85);assert.equal(b.spent,85);assert.equal(b.levels.dmg,1);assert.equal(b.steps.length,1);
b=M.budget(d.lab,d.budgetPriorities.alpha,{},2974);assert.equal(b.spent,0);assert.equal(b.next.short,1);
const max=Object.fromEntries(d.lab.map(x=>[x.id,x.max]));b=M.budget(d.lab,d.budgetPriorities.survival,max,1e6);assert.equal(b.spent,0);assert.equal(b.next,null);
for(const x of d.lab)assert.deepEqual(x,r.lab.find(y=>y.id===x.id));
assert(d.proof.legendary.includes('joinLeague'));assert.equal(d.releaseRules.legendaryJoin,'weakened');
console.log('PASS 310 kit-owner mappings; 54 original Alpha fixtures; real rage fixtures/threshold/caps; owned-level/priority-saving budgets; current legendary rule');
