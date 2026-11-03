'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
module.exports=async function checkPlanner(page,base,out){
 const address=base+'/azeroth-survivors/build-planner/';
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});await page.goto('about:blank');await page.goto(address);await page.locator('#planner-editor').waitFor({state:'visible'});
  const budget=page.locator('#plan-budget');await budget.fill('0');await budget.press('Tab');
  await page.getByRole('button',{name:'Add point to Arcane Focus',exact:true}).click();assert((await page.locator('#plan-message').innerText()).includes('No points remain'));
  await budget.fill('11');await budget.press('Tab');
  for(const name of ['Arcane Focus','Arcane Subtlety'])for(let i=0;i<5;i++)await page.getByRole('button',{name:'Add point to '+name,exact:true}).click();
  await page.getByRole('button',{name:'Add point to Arcane Concentration',exact:true}).click();assert((await page.locator('#plan-count').innerText()).startsWith('11 / 11'));
  await page.getByRole('button',{name:'Refund point from Arcane Focus',exact:true}).click();assert((await page.locator('#plan-message').innerText()).startsWith('Refund blocked'));
  assert(await page.locator('#plan-tray').evaluate(n=>{const r=n.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}));
  await page.locator('#plan-open').press('Enter');assert(await page.locator('#plan-dialog').isVisible());assert((await page.locator('#plan-result').innerText()).includes('Arcane Concentration'));
  await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>document.activeElement.id),'plan-open');
  await page.locator('[data-example="mage-fire"]').click();assert((await page.locator('#plan-count').innerText()).startsWith('31 / 51'));
  await page.locator('[data-example="warlock-affliction"]').click();assert.equal(await page.locator('#plan-class').inputValue(),'warlock');assert((await page.locator('#plan-count').innerText()).startsWith('31 / 51'));
  const safeNotes='测试 🌲 <img src=x onerror=alert(1)> & notes';await page.locator('#plan-notes').fill(safeNotes);
  await page.locator('#plan-save').click();await page.locator('#plan-reset').click();assert((await page.locator('#plan-count').innerText()).startsWith('0 / 51'));
  await page.locator('#plan-load').click();assert.equal(await page.locator('#plan-notes').inputValue(),safeNotes);
  await page.locator('#plan-open').click();const share=await page.locator('#plan-link').inputValue();assert(share.includes('#plan='));assert.equal(await page.locator('#plan-result img').count(),0);
  if(out){fs.mkdirSync(out,{recursive:true});await page.screenshot({path:path.join(out,'planner-'+width+'-result.png')});}
  await page.locator('#plan-close').click();assert.equal(await page.evaluate(()=>document.activeElement.id),'plan-open');
  const raw=JSON.parse(Buffer.from(new URLSearchParams(new URL(share).hash.slice(1)).get('plan'),'base64url').toString('utf8'));
  await page.locator('#plan-reset').click();await page.goto(share);await page.waitForFunction(()=>document.querySelector('#plan-count').textContent.startsWith('31 / 51'));assert.equal(await page.locator('#plan-notes').inputValue(),safeNotes);
  await page.locator('#plan-upload').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...raw,source:'old'}))});await page.waitForFunction(()=>document.querySelector('#plan-message').textContent.startsWith('Needs verification'));assert((await page.locator('#plan-count').innerText()).startsWith('31 / 51'));
  await page.locator('#plan-reset').click();await page.locator('#plan-upload').setInputFiles({name:'good.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(raw))});await page.waitForFunction(()=>document.querySelector('#plan-count').textContent.startsWith('31 / 51'));
  await page.locator('#plan-open').click();const downloadPromise=page.waitForEvent('download');await page.locator('#plan-download').click();const download=await downloadPromise;const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));assert.equal(exported.sequence.length,31);assert.equal(exported.notes,safeNotes);await page.keyboard.press('Escape');
  await page.locator('#plan-forget').click();assert.equal(await page.evaluate(()=>localStorage.getItem('az-build-draft-v1')),null);
  if(out){await page.locator('#planner-workbench').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'planner-'+width+'-editor.png')});}
  await page.locator('#plan-class').selectOption('mage');assert((await page.locator('#plan-count').innerText()).startsWith('31 / 51'));await page.locator('#plan-open').click();assert((await page.locator('#plan-result').innerText()).includes('Pyroclasm'));await page.keyboard.press('Escape');
  await page.locator('#plan-class').selectOption('warlock');assert((await page.locator('#plan-count').innerText()).startsWith('31 / 51'));
 }
 // Storage failure must leave a usable share/export path.
 const deny=await page.context().newPage();await deny.addInitScript(()=>{Storage.prototype.setItem=function(){throw Error('storage denied')}});await deny.goto(address);await deny.locator('#planner-editor').waitFor({state:'visible'});await deny.locator('#plan-save').click();assert((await deny.locator('#plan-message').innerText()).includes('storage is unavailable'));await deny.close();
 const failed=await page.context().newPage();await failed.route('**/data/azeroth-planner.json*',r=>r.abort());await failed.goto(address);await failed.waitForFunction(()=>document.querySelector('#planner-load-status').textContent.startsWith('Planner unavailable'));assert(await failed.locator('#planner-editor').isHidden());assert(await failed.locator('#examples table').count()===2);await failed.close();
 console.log('PASS planner browser: two viewport flows, visible results, gates/refunds, Unicode link restore, safe JSON import/export, explicit storage, denied-storage and failed-data fallbacks');
};
