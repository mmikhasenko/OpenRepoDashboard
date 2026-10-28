const bad = new Set(['failure','timed_out','action_required','startup_failure']);
let data, category='All', query='';
const $=s=>document.querySelector(s);
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
function link(text,url){const a=el('a','',text);try{const u=new URL(url);if(u.protocol==='https:'&&u.hostname==='github.com')a.href=u.href;}catch{}return a;}
function time(seconds){if(seconds==null)return '';return seconds<60?`${seconds}s`:`${Math.floor(seconds/60)}m ${seconds%60}s`;}
function age(date){if(!date)return '';const days=Math.floor((Date.now()-Date.parse(date))/86400000);return days===0?'today':days===1?'1 day ago':`${days} days ago`;}
function workflowLabel(w){return w.state!=='active'?'Disabled':w.status==='no_runs'?'No recent evidence':w.status.replaceAll('_',' ');}
function render(){
 if(!data)return;
 const repos=data.repositories.filter(r=>(category==='All'||r.category===category)&&r.repository.toLowerCase().includes(query));
 const attention=$('#attention'), collection=$('#collection');attention.replaceChildren();collection.replaceChildren();let incidents=0;
 for(const r of repos){
  const failures=r.workflows.filter(w=>bad.has(w.status)&&w.state==='active');
  if(failures.length||r.errors.length){incidents++;const row=el('article','incident');row.append(el('span','symbol','!'));const body=el('div');body.append(el('h3','',r.repository),el('p','',r.errors.length?'Some data unavailable · '+r.errors.join('; '):failures.map(w=>w.name+' failed · '+age(w.date)).join(' / ')));row.append(body,link('Open on GitHub ↗',failures[0]?.url||r.url));attention.append(row);}
  const card=el('article','card'),top=el('div','card-top');top.append(el('span','owner',r.repository.split('/')[0]),el('span','tag',r.category));card.append(top);const title=el('h3');title.append(link(r.repository.split('/')[1],r.url));card.append(title,el('p','description',r.description||'Open-source project'));
  const active=r.workflows.filter(w=>w.state==='active');
  const ci=active.find(w=>/^(CI|test|tests|testing|continuous integration)$/i.test(w.name))||active.find(w=>/\b(test|ci)\b/i.test(w.name));
  const line=el('div','statusline');
  const status=r.errors.length?'Incomplete data':failures.length?`${failures.length} failing`:active.some(w=>['in_progress','queued','waiting','pending'].includes(w.status))?'Running':!active.length?'No active workflows':active.some(w=>!w.date||Date.now()-Date.parse(w.date)>30*86400000)?'No recent evidence':active.every(w=>w.status==='success')?'Checks passing':'Review checks';
  line.append(el('span','pill '+(failures.length?'bad':status==='Checks passing'?'good':''),status));if(ci)line.append(link(`CI ${time(ci.duration)||workflowLabel(ci)}`,ci.url));card.append(line);
  const counts=el('div','counts');counts.append(link(`${r.prs.length} open PR${r.prs.length===1?'':'s'}`,r.url+'/pulls'),link(`${r.issues.length} issue${r.issues.length===1?'':'s'}`,r.url+'/issues'));card.append(counts);
  const details=el('details');details.append(el('summary','','Workflows & open work'));
  for(const w of r.workflows){const row=el('div','detail-row');row.append(link(w.name,w.url),el('small','',`${workflowLabel(w)}${w.duration!=null?' · '+time(w.duration):''}${w.date?' · '+age(w.date):''}`));details.append(row);}
  for(const [kind,items] of [['PR',r.prs],['Issue',r.issues]])for(const item of items.slice(0,10)){const row=el('div','detail-row');row.append(link(`${kind} #${item.number} · ${item.title}`,item.html_url),el('small','',`${item.author} · updated ${age(item.updated_at)}`));details.append(row);}
  const copy=el('button','copy','Copy agent context');copy.addEventListener('click',async()=>{const prompt=`Investigate ${r.repository} (${r.url}). Dashboard snapshot: ${data.updated_at}.\nCategory: ${r.category}.\n${failures.map(w=>`${w.name}: ${w.status} ${w.url}`).join('\n')}\n${r.errors.join('\n')}\nOpen PRs: ${r.url}/pulls\nUse the local-only .local/checkouts.json in OpenRepoDashboard to locate a checkout, if available. Verify current GitHub state and repository instructions before making changes. Do not publish local paths or secrets.`;try{await navigator.clipboard.writeText(prompt);copy.textContent='Copied';}catch{copy.textContent='Copy unavailable in this browser';}});details.append(copy);card.append(details);collection.append(card);
 }
 $('#attention-count').textContent=incidents?`${incidents} project${incidents===1?'':'s'}`:'Nothing flagged';
 if(!incidents)attention.append(el('div','empty',repos.length?'No workflow failures flagged in this snapshot. Open PRs and issues are listed below.':'No matching projects.'));
 $('#repo-count').textContent=`${repos.length} repositories`;
}
document.querySelectorAll('[data-category]').forEach(b=>b.addEventListener('click',()=>{category=b.dataset.category;document.querySelectorAll('[data-category]').forEach(n=>{n.classList.toggle('selected',n===b);n.setAttribute('aria-pressed',String(n===b));});render();}));
$('#search').addEventListener('input',e=>{query=e.target.value.toLowerCase();if(data)render();});
fetch('data.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Snapshot unavailable');return r.json();}).then(d=>{data=d;const stale=Date.now()-Date.parse(d.updated_at)>36*3600000;$('#freshness').textContent=`${stale?'Snapshot is stale · ':''}Updated ${new Date(d.updated_at).toLocaleString()} · refreshes daily`;$('#freshness').classList.toggle('stale',stale);render();}).catch(()=>{$('#freshness').textContent='Repository data unavailable. Check the collection workflow on GitHub.';$('#freshness').classList.add('stale');});
