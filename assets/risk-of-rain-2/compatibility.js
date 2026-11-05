(function(root){
 'use strict';
 function assess(a,b){
  const steam=x=>x.startsWith('steam-'),pc=x=>steam(x)||x==='epic';
  if(!a||!b)return {state:'unknown',title:'Choose both copies',text:'Select each player’s exact copy before checking.',action:'Steam players also need to inspect their crossplay preference.'};
  if(pc(a)&&pc(b)){
   if(a==='steam-unknown'||b==='steam-unknown')return {state:'unknown',title:'Check the Steam setting first',text:'The PC route depends on Steam crossplay preferences. A PC store name alone cannot settle whether the two sessions match.',action:'Check both settings, then select ON or OFF as actually shown in the game.'};
   if((a==='epic'&&b==='steam-off')||(b==='epic'&&a==='steam-off')||(steam(a)&&steam(b)&&a!==b))return {state:'mismatch',title:'The selected settings do not match',text:'Steam crossplay OFF cannot join Epic or a Steam crossplay-ON session.',action:a==='epic'||b==='epic'?'The Steam player must enable crossplay and restart to use the Steam–Epic route.':'Agree on ON for both or OFF for both, restart after changing it, then invite again.'};
   return {state:'supported',title:'A documented PC route',text:a==='steam-off'?'Both Steam copies have crossplay OFF: use the normal Steam multiplayer route.':'Both copies can use the crossplay-enabled PC route; this checks documentation, not your connection.',action:'Restart after changing settings. For Steam/Epic use the publisher’s account-linking and lobby/invitation steps below.'};
  }
  if((a==='ps4'&&b==='ps5')||(b==='ps4'&&a==='ps5')||(a==='one'&&b==='series')||(b==='one'&&a==='series'))return {state:'version',title:'Cross-generation versions need checking',text:'2K announced a split with the next console update. The reviewed notice still uses conditional rollout wording, so this checker does not assert your installed versions can connect.',action:'Compare the actual editions and patch notes on both consoles before buying or starting. Same title and entitlement do not settle it.'};
  if(a===b&&['ps4','ps5','one','series','switch'].includes(a))return {state:'same-edition',title:'Use the same-edition console route',text:'You selected the same console edition. Use its own online multiplayer; this is not a promise about a different generation or console family.',action:'Match installed versions and check platform online-service requirements. No console matchmaking was tested by this guide.'};
  return {state:'unknown',title:'No documented route for this pair here',text:'The reviewed Steam/Epic and console-generation notices do not establish native online play for this exact pair. Unconfirmed is not a live connection test or proof that a future update cannot add it.',action:'Ask the publisher about both exact editions before purchasing for crossplay. A room code, backward-compatible console or shared save does not prove support.'};
 }
 if(typeof module!=='undefined')module.exports={assess};
 if(!root.document)return;
 const d=root.document,form=d.querySelector('#pair-form');if(!form)return;
 const result=d.querySelector('#pair-result'),dialog=d.querySelector('#pair-dialog'),open=d.querySelector('#pair-open');let current;
 function close(){if(dialog.open)dialog.close();open.focus()}
 form.addEventListener('submit',e=>{e.preventDefault();current=assess(form.elements.player1.value,form.elements.player2.value);result.hidden=false;result.dataset.state=current.state;d.querySelector('#pair-summary').textContent=current.title;d.querySelector('#pair-next').textContent=current.action;d.querySelector('#pair-status').textContent=current.title+'. Open the result for the rule and next step.';open.focus({preventScroll:true});result.scrollIntoView({block:'center',behavior:'instant'})});
 open.addEventListener('click',()=>{d.querySelector('#pair-title').textContent=current.title;d.querySelector('#pair-text').textContent=current.text;d.querySelector('#pair-action').textContent=current.action;dialog.showModal();d.querySelector('#pair-close').focus()});
 d.querySelector('#pair-close').addEventListener('click',close);dialog.addEventListener('cancel',e=>{e.preventDefault();close()});
 d.querySelector('#pair-table').addEventListener('click',()=>dialog.close());
 form.addEventListener('change',()=>{result.hidden=true;d.querySelector('#pair-status').textContent='Copies changed. Check again for an updated result.'});
 form.addEventListener('reset',()=>{result.hidden=true;current=null;d.querySelector('#pair-status').textContent='Choices cleared. Choose both copies to check again.'});
 })(typeof window==='undefined'?globalThis:window);
