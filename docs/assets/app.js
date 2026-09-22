(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const sections = [...document.querySelectorAll('main > section[id]')];
  const nav = [...document.querySelectorAll('.chapter-nav a')];
  const menu = $('.mobile-nav');
  const input = $('#site-search');
  const panel = $('#search-results');
  const entries = JSON.parse($('#search-data').textContent);
  const names = Object.fromEntries(nav.map(a => [a.dataset.section, a.querySelector('span:nth-child(2)').textContent]));
  function closeMenu(focus) { menu.open = false; if (focus) menu.querySelector('summary').focus(); }
  function route() {
    let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch { id = ''; }
    let target = id ? document.getElementById(id) : $('#start');
    if (!target || !target.closest('main')) target = $('#start');
    let section = target.closest('main > section') || $('#start');
    sections.forEach(s => { s.hidden = s !== section; });
    nav.forEach(a => { const active = a.dataset.section === section.id; a.classList.toggle('active', active); if(active) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
    $('#current-chapter').textContent = names[section.id] || '行动总览';
    if (target.id.startsWith('opp-')) { resetFilters(); }
    if (section.id === 'sources') { $('#source-category').value = ''; filterSources(); }
    for(let el = target; el && el !== section; el = el.parentElement) if(el.tagName === 'DETAILS') el.open = true;
    closeMenu(false);
    target.setAttribute('tabindex','-1');
    target.focus({preventScroll:true});
    requestAnimationFrame(() => {
      if(target === section || target.id === 'main') window.scrollTo({top:0,behavior:'instant'});
      else target.scrollIntoView({block:'start',behavior:'instant'});
    });
  }
  window.addEventListener('hashchange', route);
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]');
    if(a) {
      if(a.hash === '#main') { e.preventDefault(); const current=sections.find(s=>!s.hidden)||$('#start'); current.setAttribute('tabindex','-1');current.focus({preventScroll:true});current.scrollIntoView({block:'start'});return; }
      if(a.closest('#search-list')) { if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return; e.preventDefault();const hash=a.hash;clearSearch();if(location.hash===hash)route();else location.hash=hash; }
      else if(a.hash === location.hash) route();
    }
    if(menu.open && !menu.contains(e.target)) closeMenu(false);
  });
  document.addEventListener('keydown', e => {
    if(e.key === 'Escape') { if(menu.open) closeMenu(true); if(!panel.hidden) { clearSearch(); input.focus(); } }
    if(e.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !document.activeElement.isContentEditable) {e.preventDefault();input.focus();}
  });
  function clearSearch() { input.value = ''; panel.hidden = true; $('#search-list').replaceChildren(); }
  $('#clear-search').addEventListener('click', () => { clearSearch();input.focus(); });
  function search() {
    const query=input.value.trim().toLocaleLowerCase();
    if(!query) return clearSearch();
    const terms=query.split(/\s+/);
    const found=entries.map(row => ({...row,score:terms.every(t=>(row.title+' '+row.text).toLocaleLowerCase().includes(t)) ? (row.title.toLocaleLowerCase().includes(query)?2:1):0})).filter(row=>row.score).sort((a,b)=>(b.score-(b.section==='sources'?.1:0))-(a.score-(a.section==='sources'?.1:0)));
    panel.hidden=false; $('#search-count').textContent=found.length?`${found.length} 条结果${found.length>20?' · 显示前 20 条':''}`:'没有找到结果，试试“君合”“免费”或“语音”。';
    const list=$('#search-list'); list.replaceChildren();
    found.slice(0,20).forEach(row=>{ const li=document.createElement('li'),a=document.createElement('a'),category=document.createElement('span'),title=document.createElement('strong'),snippet=document.createElement('small');a.href='#'+row.id;category.className='search-category';category.textContent=names[row.section]||'资料';title.textContent=row.title;const at=row.text.toLocaleLowerCase().indexOf(query);const start=Math.max(0,at-22);snippet.textContent=(start?'…':'')+row.text.slice(start,start+105)+(row.text.length>start+105?'…':'');a.append(category,title,snippet);li.append(a);list.append(li); });
  }
  input.addEventListener('input',search);
  const checks=[...document.querySelectorAll('[data-task]')],key='bristol-law-career.tasks.v2';
  let state={};
  try { const value=JSON.parse(localStorage.getItem(key)||'{}');if(value&&typeof value==='object'&&!Array.isArray(value))state=value; } catch { $('#storage-note').textContent='本浏览器无法保存；勾选仅在当前页面有效。'; }
  checks.forEach(c=>{c.checked=state[c.dataset.task]===true;c.addEventListener('change',()=>{state[c.dataset.task]=c.checked;save();});});
  function count(){ $('#task-count').textContent=`${checks.filter(c=>c.checked).length} / ${checks.length} 完成`; }
  function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch{$('#storage-note').textContent='本浏览器无法保存；勾选仅在当前页面有效。';}count();}
  $('#reset-tasks').addEventListener('click',()=>{checks.forEach(c=>c.checked=false);state={};save();});count();
  function filterOpportunities(){const vals=['place','type','cost'].map(x=>[x,$('#filter-'+x).value]);let count=0;document.querySelectorAll('.opportunity').forEach(row=>{row.hidden=vals.some(([k,v])=>v&&row.dataset[k]!==v);if(!row.hidden)count++;});$('#opportunity-count').textContent=`${count} 个入口 · 不等于已报名或正在招聘`;$('#opportunity-empty').hidden=count!==0;}
  function resetFilters(){['place','type','cost'].forEach(x=>$('#filter-'+x).value='');filterOpportunities();}
  ['place','type','cost'].forEach(x=>$('#filter-'+x).addEventListener('change',filterOpportunities));$('#clear-filters').addEventListener('click',resetFilters);
  function filterSources(){const value=$('#source-category').value;let count=0;document.querySelectorAll('.source-list>li').forEach(row=>{row.hidden=Boolean(value&&row.dataset.category!==value);if(!row.hidden)count++;});$('#source-count').textContent=`${count} 条来源`;}
  $('#source-category').addEventListener('change',filterSources);
  document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const target=document.getElementById(button.dataset.copy);try{await navigator.clipboard.writeText(target.textContent);button.textContent='已复制';$('#copy-status').textContent='已复制，请按真实情况替换内容。';setTimeout(()=>button.textContent='复制文本',2200);}catch{const range=document.createRange();range.selectNodeContents(target);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);button.textContent='已选中，请手动复制';$('#copy-status').textContent='无法自动复制，请手动复制选中的文字。';}}));
  route();
})();
