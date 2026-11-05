'use strict';
const assert=require('node:assert/strict');
const {decide}=require('../assets/vampire-survivors/compatibility.js');
const cases=[['steam','steam','supported'],['ms','xbox','supported'],['ps4','ps5','supported'],['steam','ms','unsupported'],['steam','ps5','unsupported'],['xbox','ps5','unsupported'],['switch','steam','unsupported'],['epic','steam','unknown'],['epic','epic','unknown'],['other','ps4','unknown'],['mobile','mobile','unsupported'],['demo','steam','unsupported'],['','steam','choose']];
for(const [a,b,state]of cases){assert.equal(decide(a,b).state,state,a+' / '+b);assert.equal(decide(b,a).state,state,'symmetric '+a+' / '+b)}
console.log('PASS: documented pairs, same-PC different stores, unknown storefronts, mobile/demo exclusions and symmetric results.');
