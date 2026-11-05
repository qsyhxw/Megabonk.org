/* Reviewed rules: poncle's online FAQ, checked 5 November 2026.
   Absence of a documented pairing is unknown, not inferred compatibility. */
(function(){
 'use strict';
 function decide(a,b){
  if(!a||!b)return {state:'choose',title:'Choose both copies first',text:'Select the device and storefront each player will actually launch.'};
  if(a==='mobile'||b==='mobile')return {state:'unsupported',title:'No documented native online route for mobile',text:'The current online FAQ excludes mobile at launch. Local mobile co-op is a separate mode; the developer documents landscape play with additional Bluetooth controllers. Do not buy another copy expecting phone-to-PC online play.'};
  if(a==='demo'||b==='demo')return {state:'unsupported',title:'The old browser demo is not the online edition',text:'The original itch.io demo predates native online co-op. Choose the current commercial edition on a supported device; its progress is separate from the old demo.'};
  if(a===b&&['steam','ms','xbox','ps4','ps5','switch'].includes(a))return {state:'supported',title:'A documented online route is available',text:'Use the same current commercial edition and start Online. Each player needs their own device and copy. The host chooses the stage; for a DLC run everyone must own that DLC. A console online subscription may also be required.'};
  if((['ms','xbox'].includes(a)&&['ms','xbox'].includes(b))||(['ps4','ps5'].includes(a)&&['ps4','ps5'].includes(b)))return {state:'supported',title:'Supported within this platform ecosystem',text:'poncle explicitly documents this pairing. Each player still needs a device and copy. Start Online, share the room code (or use Xbox platform invites), and check that everyone owns the DLC you plan to use.'};
  if(['epic','other'].includes(a)||['epic','other'].includes(b))return {state:'unknown',title:'This exact storefront pairing needs confirmation',text:'The reviewed FAQ does not name this exact pair. Do not infer compatibility from both copies running on a PC, or from cross-save support. Check the developer FAQ for your precise stores before buying or troubleshooting a room code.'};
  return {state:'unsupported',title:'These copies cross separate online ecosystems',text:'The current FAQ does not support cross-ecosystem play. A room code does not bridge Steam and consoles, Xbox and PlayStation, or other separate ecosystems. Use a documented compatible pair, or investigate the separate shared-screen Remote Play route on Steam.'};
 }
 if(typeof module!=='undefined'&&module.exports)module.exports={decide};
 if(typeof document==='undefined')return;
 const form=document.getElementById('pair-form');if(!form)return;
 const result=document.getElementById('pair-result'),title=document.getElementById('pair-title'),text=document.getElementById('pair-text'),status=document.getElementById('pair-status');
 form.addEventListener('submit',e=>{e.preventDefault();const d=decide(form.elements.player1.value,form.elements.player2.value);title.textContent=d.title;text.textContent=d.text;result.hidden=false;result.dataset.state=d.state;status.textContent='Result ready below: '+d.title;result.scrollIntoView({block:'center',behavior:'instant'});title.focus({preventScroll:true});});
 form.addEventListener('reset',()=>{result.hidden=true;status.textContent='Choose two copies to check a documented route.';});
})();
