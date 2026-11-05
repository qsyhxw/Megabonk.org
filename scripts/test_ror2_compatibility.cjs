const assert=require('node:assert/strict'),{assess}=require('../assets/risk-of-rain-2/compatibility.js');
const cases=[['steam-on','epic','supported'],['steam-off','epic','mismatch'],['steam-off','steam-on','mismatch'],['steam-off','steam-off','supported'],['steam-on','steam-unknown','unknown'],['ps4','ps5','version'],['one','series','version'],['ps5','ps5','same-edition'],['ps5','series','unknown'],['switch2','switch','unknown'],['other','steam-on','unknown']];
for(const[a,b,state]of cases){assert.equal(assess(a,b).state,state,a+' '+b);assert.equal(assess(b,a).state,state,b+' '+a)}
console.log('PASS: 22 documented-pair and reversed-pair decisions, including unknown settings, conditional generations and unsupported assumptions.');
