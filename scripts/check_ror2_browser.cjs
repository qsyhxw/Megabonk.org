'use strict';
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const base=process.env.ROR2_BASE||'http://127.0.0.1:4196',out=process.env.ROR2_QA_DIR||'_private/ror2-build-20261105/views';
const routes=['/risk-of-rain-2/crossplay/','/risk-of-rain-2/gold-portal/','/risk-of-rain-2/ru/bulwarks-ambry/'];
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true,channel:'chrome'}),c=await browser.newContext(),p=await c.newPage();let views=0;const errors=[],external=[];p.on('pageerror',e=>errors.push(e.message));await c.route('**/*',r=>{if(new URL(r.request().url()).origin!==base){external.push(r.request().url());return r.abort()}return r.continue()});
try{
for(const route of routes){
 const response=await p.goto(base+route,{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);assert.equal(await p.locator('h1').count(),1);assert.equal(await p.locator('link[rel=canonical]').getAttribute('href'),'https://megabonk.org'+route);assert.equal(await p.locator('script[src*=adsbygoogle]').count(),1);assert.equal(await p.locator('script[src*=umami]').count(),1);assert.equal(await p.locator('main iframe').count(),0);assert.equal(await p.locator('figure.game-image').count(),1);
 console.log('meta',route,(await p.title()).length,(await p.locator('meta[name=description]').getAttribute('content')).length);
 for(const width of [1920,1440,901,900,899,768,390]){
  await p.setViewportSize({width,height:900});await p.evaluate(()=>document.fonts.ready);await p.addStyleTag({content:'html{scroll-behavior:auto!important}'});await p.locator('figure img').evaluateAll(async a=>{for(const im of a){im.loading='eager';await im.decode()}});assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),route+' overflow '+width);
  assert.equal(await p.locator('.desktop-nav').isVisible(),width>900);
  if(width<=900){await p.locator('.mobile-nav summary').press('Enter');assert(await p.locator('.mobile-links').isVisible());await p.locator('.mobile-nav summary').press('Enter');assert(!await p.locator('.mobile-links').isVisible())}else{const y=await p.locator('.desktop-nav a').evaluateAll(a=>a.map(n=>n.getBoundingClientRect().top));assert(Math.max(...y)-Math.min(...y)<2)}
  const style=await p.locator('.article-layout').evaluate(n=>({display:getComputedStyle(n).display,dir:getComputedStyle(n).flexDirection}));assert.equal(style.dir,'column');
  if([1440,390].includes(width)){const name=route.replaceAll('/','_')+width;await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(out,name+'-top.png')});await p.locator('figure').scrollIntoViewIfNeeded();await p.waitForTimeout(150);await p.screenshot({path:path.join(out,name+'-body.png')});await p.locator('footer').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(out,name+'-footer.png')});const [popup]=await Promise.all([p.waitForEvent('popup'),p.locator('figure a[target="_blank"]').click()]);await popup.waitForLoadState('domcontentloaded');assert(popup.url().includes('/assets/risk-of-rain-2/'));await popup.close()}
  views++;
 }
 const refs=await p.locator('a[href^="#"]').evaluateAll(a=>a.map(x=>x.getAttribute('href')));for(const h of refs)assert(await p.locator('[id="'+h.slice(1)+'"]').count(),route+' '+h);
 const srcs=await p.locator('.sources li>a').evaluateAll(a=>a.map(x=>x.href));assert.equal(new Set(srcs).size,srcs.length);
 for(const a of await p.locator('.sources li>a').all()){assert.equal(await a.getAttribute('target'),'_blank');assert((await a.innerText()).includes('↗'))}
 assert(await p.locator('a[href="/risk-of-rain-2/"]').count()>0);
}
for(const width of [1440,390]){
 await p.setViewportSize({width,height:844});await p.goto(base+routes[0]);
 for(const[a,b,state]of [['steam-on','epic','supported'],['steam-off','epic','mismatch'],['ps4','ps5','version'],['steam-unknown','epic','unknown']]){
  await p.locator('[name=player1]').selectOption(a);await p.locator('[name=player2]').selectOption(b);await p.getByRole('button',{name:'Check our copies',exact:true}).focus();await p.keyboard.press('Enter');assert.equal(await p.locator('#pair-result').getAttribute('data-state'),state);assert(await p.locator('#pair-open').evaluate(n=>{let r=n.getBoundingClientRect();return r.top>=0&&r.bottom<innerHeight}));await p.locator('#pair-open').press('Enter');assert(await p.locator('#pair-dialog').isVisible());assert((await p.locator('#pair-text').innerText()).length>30);await p.screenshot({path:path.join(out,'tool-'+width+'-'+state+'.png')});await p.keyboard.press('Escape');assert(!await p.locator('#pair-dialog').isVisible());assert(await p.locator('#pair-open').evaluate(n=>document.activeElement===n));await p.locator('#pair-open').click();await p.locator('#pair-close').click();assert(await p.locator('#pair-open').evaluate(n=>document.activeElement===n));
 }
 await p.getByRole('button',{name:'Clear choices'}).click();assert(!await p.locator('#pair-result').isVisible());
}
await p.goto(base+'/');await p.locator('#game-risk-of-rain-2 a.game-card-main').click();assert(p.url().endsWith('/risk-of-rain-2/'));for(const route of routes){await p.locator('.hub-grid a[href="'+route+'"]').click();assert(p.url().endsWith(route));await p.goBack()}
await p.goto(base+'/privacy-policy');assert.equal(await p.locator('#risk-of-rain-2').count(),1);assert.equal(await p.locator('script[src*=adsbygoogle]').count(),0);
const ad=await p.goto(base+'/ads.txt');assert.equal(ad.status(),200);assert(ad.headers()['content-type'].includes('text/plain'));assert.equal((await ad.text()).split('google.com, pub-8830315294299920, DIRECT, f08c47fec0942fa0').length,2);
const xml=await p.goto(base+'/sitemap.xml');assert.equal(xml.status(),200);assert(xml.headers()['content-type'].includes('xml'));await p.waitForTimeout(200);assert(await p.locator('#webkit-xml-viewer-source-xml,.pretty-print').count());await p.screenshot({path:path.join(out,'sitemap.png')});assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({views,routes,errors,externalRequestsIntercepted:[...new Set(external)]},null,2));console.log('PASS',views,'responsive views; both widths visible results/modal/close focus, keyboard, three root entries, images, privacy, ads, native XML.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
