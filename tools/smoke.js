// Test de fumée : node tools/smoke.js [capture-0.png]. Sert le dépôt sans serveur (interception Playwright). Échoue sur toute erreur JS.
// Captures : -0 au départ, -mid en plein combat, -1 à la fin.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..'),TYPES={html:'text/html',webp:'image/webp',png:'image/png',woff2:'font/woff2',js:'text/javascript'};
(async()=>{const b=await chromium.launch(),p=await b.newPage({viewport:{width:1400,height:850}});const errs=[];
 await p.route('http://jeu.local/**',r=>{const f=path.join(ROOT,decodeURIComponent(new URL(r.request().url()).pathname));
  if(!f.startsWith(ROOT)||!fs.existsSync(f))return r.fulfill({status:404,body:''});const fic=fs.statSync(f).isDirectory()?path.join(f,'index.html'):f;
  r.fulfill({body:fs.readFileSync(fic),contentType:TYPES[path.extname(fic).slice(1)]||'application/octet-stream'})});
 p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'||m.type()==='assert')errs.push(m.text())});
 const shot=process.argv[2]||'smoke-0.png';
 await p.goto('http://jeu.local/');await p.waitForTimeout(1500);await p.screenshot({path:shot});
 // Le héros attaque l'adversaire le plus proche, achète ses talents, se repose, boit ses potions.
 const joue=n=>p.evaluate(n=>{const T=__test;T.pause(true);const S=T.S,h=T.hero;window.__c=window.__c||{comas:0,was:0};const c=window.__c;
  for(let k=0;k<n&&S.mons.length&&h.vie>0;k++){if(!h.cible||h.cible.pv<=0){const m=S.mons.filter(m=>m.pv>0).sort((a,b)=>Math.hypot(a.x-h.x,a.y-h.y)-Math.hypot(b.x-h.x,b.y-h.y))[0];if(m)T.cible(m)}
   const libre=['frappe','double','cri','rage_depart','frappe_melee','enrag','double_tourbillon','rage_crit'].find(t=>!h.talents.has(t));
   if(libre&&Math.floor(h.xp/100)>h.depense){h.talents.add(libre);h.depense++}
   if(!S.combat&&!h.coma&&h.pv<h.vie*h.endu+16-6&&h.reposOk&&h.reposCourts<h.vie)T.reposCourt();
   if(h.coma&&!c.was)c.comas++;c.was=h.coma;if(h.pv<12)T.potion();if(k%120===0){T.frappeFurieuse();T.criDeGuerre()}T.step(0.05)}
  return {restants:S.mons.length,vie:h.vie,pv:h.pv,xp:h.xp,t:Math.round(S.t),comas:c.comas}},n);
 await joue(260);await p.evaluate(()=>__test.pause(false));await p.waitForTimeout(250);await p.screenshot({path:shot.replace(/0\.png$/,'mid.png')});
 console.log(JSON.stringify(await joue(8000)));
 await p.evaluate(()=>__test.pause(false));await p.waitForTimeout(500);await p.screenshot({path:shot.replace(/0\.png$/,'1.png')});
 await b.close();if(errs.length){console.error('ERREURS',errs);process.exit(1)}})();
