'use strict';
(() => {
 const planner=document.querySelector('[data-planner]');
 if(planner){
  const data=JSON.parse(document.querySelector('#recipe-data').textContent),byName=new Map(data.map(r=>[r.name,r]));
  const target=document.querySelector('#target'),version=document.querySelector('#version'),owned=[...document.querySelectorAll('.owned')],view=document.querySelector('#view-route'),clear=document.querySelector('#clear-route'),status=document.querySelector('#route-status'),dialog=document.querySelector('#route-dialog'),output=document.querySelector('#route-output');
  const original=[...target.options].map(o=>({value:o.value,text:o.textContent}));let opener;
  const selection=()=>{view.disabled=!target.value;document.body.classList.toggle('route-ready',!!target.value);document.querySelector('#route-selection').textContent=target.value?target.value+' · '+owned.filter(x=>x.value).length+' carried':'Choose a target';status.textContent=target.value?'Selected: '+target.value+'. '+owned.filter(x=>x.value).length+' carried entries. Open the ingredient route to check what remains.':'Choose a target to plan a route.';};
  const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text)el.textContent=text;if(cls)el.className=cls;return el;};
  version.addEventListener('change',()=>{const prior=target.value;target.replaceChildren();for(const o of original){if(!o.value||version.value==='All'||byName.get(o.value)?.version===version.value){const el=node('option',o.text);el.value=o.value;target.append(el);}}if([...target.options].some(o=>o.value===prior))target.value=prior;selection();});
  target.addEventListener('change',selection);owned.forEach(o=>o.addEventListener('change',selection));
  view.addEventListener('click',()=>{
   if(!target.value)return;
   opener=view;const counts=new Map();for(const s of owned)if(s.value)counts.set(s.value,(counts.get(s.value)||0)+1);
   const missing=new Map(),used=new Map();output.replaceChildren();document.querySelector('#route-title').textContent=target.value+' ingredient route';
   const walk=(name,depth=0)=>{
    const li=node('li');li.append(node('strong',name));
    if((counts.get(name)||0)>0){counts.set(name,counts.get(name)-1);used.set(name,(used.get(name)||0)+1);li.append(node('span',' — already carried','carried'));return li;}
    const r=byName.get(name);
    if(!r||depth>12){missing.set(name,(missing.get(name)||0)+1);li.append(node('span',' — starting ingredient needed'));return li;}
    li.append(node('span',' — '+r.version+' recipe'));const ul=node('ul');r.inputs.forEach(i=>ul.append(walk(i,depth+1)));li.append(ul);return li;
   };
   const tree=node('ul',null,'route-tree');tree.append(walk(target.value));output.append(tree,node('h3','Remaining starting ingredients'));
   if(missing.size){const ul=node('ul');for(const [name,count]of missing)ul.append(node('li',name+' × '+count));output.append(ul);}else output.append(node('p','No ingredients remain in this plan: the selected target is already marked carried.'));
   output.append(node('p','Each carried entry is consumed once by the plan. Duplicate leaves show total recipe demand, not simultaneous slot use. Upgrade components and choose Evolution at a core; unlock and slot requirements must be checked in your run.'));
   dialog.showModal();
  });
  document.querySelector('#route-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',()=>opener?.focus());
  clear.addEventListener('click',()=>{version.value='All';version.dispatchEvent(new Event('change'));target.value='';owned.forEach(o=>o.value='');selection();target.focus();});
  selection();
 }
 const checklist=document.querySelector('[data-checklist]');
 if(checklist){
  const key='megabonk.ball-x-pit.clears.v1',boxes=[...checklist.querySelectorAll('[data-clear]')],status=document.querySelector('#clear-progress');let saved={},storage=true;
  try{saved=JSON.parse(localStorage.getItem(key)||'{}');if(!saved||typeof saved!=='object')saved={};}catch{storage=false;}
  boxes.forEach(b=>b.checked=saved[b.dataset.clear]===true);
  const update=()=>{status.textContent=boxes.filter(b=>b.checked).length+' / '+boxes.length+' manual clear notes.'+(storage?' Saved on this device.':' Storage unavailable; changes last for this visit only.');};
  boxes.forEach(b=>b.addEventListener('change',()=>{saved[b.dataset.clear]=b.checked;try{localStorage.setItem(key,JSON.stringify(saved));}catch{storage=false;}update();}));
  document.querySelector('#reset-clears').addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);saved={};try{localStorage.removeItem(key);}catch{storage=false;}update();});
  update();
 }
})();
