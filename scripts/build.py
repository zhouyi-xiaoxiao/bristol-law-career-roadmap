#!/usr/bin/env python3
"""Build a static, accessible career field guide and its local search index."""
import json, html, re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'src/content.json').read_text())
FRONTIER=json.loads((ROOT/'src/frontier.json').read_text()) if (ROOT/'src/frontier.json').exists() else {'items':[]}
def e(x): return html.escape(str(x),quote=True)
def prose(x): return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',e(x))
def ext(url,label,css=''):
    assert url.startswith(('https://','mailto:'))
    return f'<a class="{e(css)}" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span><span class="visually-hidden">（新标签页）</span></a>'
S=DATA['sections']; sources={x['url']:x for x in DATA['sources']}
for x in FRONTIER.get('items',[]):
    sources[x['url']]={'id':x['id'],'title':x['title'],'url':x['url'],'category':'AI 前沿','note':f"发布 {x['date']} · 核查 2026-09-22 · {x['access']}"}
SEARCH=[]
def index(id,title,text,section):
    SEARCH.append({'id':id,'title':title,'text':text,'section':section})
def block(b,sid,i):
    id=f'{sid}-item-{i}'
    kind=b['type']
    if kind=='paragraph':
        index(id,nav_names[sid]+' · '+b['text'][:22],b['text'],sid)
        return f'<p class="prose" id="{id}">{prose(b["text"])}</p>'
    if kind=='list':
        for n,t in enumerate(b['items']):index(f'{id}-{n}',nav_names[sid]+' · '+t[:22],t,sid)
        return '<ul class="bullet-list">'+''.join(f'<li id="{id}-{n}">{prose(t)}</li>' for n,t in enumerate(b['items']))+'</ul>'
    if kind=='callout':
        index(id,b['title'],b['text'],sid)
        return f'<aside class="callout" id="{id}"><h3>{e(b["title"])}</h3><p>{prose(b["text"])}</p></aside>'
    if kind=='steps':
        rows=[]
        for n,t in enumerate(b['items']):
            tid=f'{id}-{n}';index(tid,t['title'],t['body'],sid)
            rows.append(f'<li id="{tid}"><span class="step-num">{n+1:02d}</span><div><h3>{e(t["title"])}</h3><p>{prose(t["body"])}</p></div></li>')
        return '<ol class="steps">'+''.join(rows)+'</ol>'
    if kind=='cards':
        cards=[]
        for n,t in enumerate(b['items']):
            tid=f'{id}-{n}';index(tid,t['title'],t['body']+' '+t.get('meta',''),sid)
            meta=f'<span class="card-meta">{e(t["meta"])}</span>' if t.get('meta') else ''
            foot=''
            if t.get('url'):
                src=sources.get(t['url'],{});checked=src.get('checkedAt','2026-09-21')
                foot=f'<div class="card-footer">{ext(t["url"],t.get("linkLabel","原始来源"))}<span>核查 {e(checked)}</span></div>'
            cards.append(f'<article class="card" id="{tid}">{meta}<h3>{e(t["title"])}</h3><p>{prose(t["body"])}</p>{foot}</article>')
        return '<div class="cards">'+''.join(cards)+'</div>'
    if kind=='template':
        tid=b.get('id',f'{sid}-text-{i}');index(tid+'-panel',b['title'],b['text'],sid)
        return f'<details class="template" id="{tid}-panel"><summary>{e(b["title"])}</summary><div class="template-inner"><div class="template-text" id="{tid}">{e(b["text"])}</div><button type="button" class="copy-button" data-copy="{tid}">复制文本</button></div></details>'
    raise ValueError(kind)
nav_items=[('start','行动总览'),('frontier','近两个月 AI 前沿'),('ai','AI 实务工作流'),('roadmap','八个月行动路线'),('teams','找到业务团队'),('routes','四条进入路径'),('connections','联系与内推'),('bristol','活动与学校资源'),('recruitment','律所招聘入口'),('skills','能力与资格'),('templates','沟通与 AI 模板'),('sources','来源资料库')]
nav_names=dict(nav_items)
def nav():
    return '<nav class="chapter-nav" aria-label="章节导航">'+''.join(f'<a href="#{sid}" data-section="{sid}"><span class="nav-num">{i:02d}</span><span>{title}</span>{"<small>NEW</small>" if sid=="frontier" else ""}</a>' for i,(sid,title) in enumerate(nav_items))+'</nav>'
def heading(id,kicker,title,intro):
    return f'<header class="section-head"><p class="kicker">{e(kicker)}</p><h2 id="heading-{id}">{e(title)}</h2><p class="section-intro">{prose(intro)}</p></header>'
opps=[
 ('law-fair','Law Fair','2026.10.01','Bristol','活动','待核实','Wills Memorial Building · 时段与参展名单在 MyCareer 核对','https://www.bristol.ac.uk/careers/events/'),
 ('legal-cheek','Legal Cheek Live','2026.10.20 · 13:30–16:30','Bristol','活动','免费','M Shed · 学生与毕业生可报名，名额以主办方为准','https://www.legalcheek.com/event/legal-cheek-live-in-bristol/'),
 ('hr-clinic','Human Rights Law Clinic','2026.09.30 · 17:00 截止','Bristol','实践','待核实','LLM可申请；须满足课程或经验条件，英国当地时间','https://www.bristol.ac.uk/law/research/centres/hric/human-rights-law-clinic/'),
 ('mediation','Pathways into Mediation','2026.10.13 · 12:00–13:30 BST','线上','活动','会员免费','报名截止 10.13 08:00 BST；非会员 £15，学生会员票适用条件另核','https://www.ciarb.org/events/pathways-into-mediation/'),
 ('alexander','Alexander Lecture','2026.12.03','线上','活动','免费','报名截止 12.02 08:00 GMT；此条为线上免费形式，线下另计','https://www.ciarb.org/events/alexander-lecture-2026/'),
 ('junhe','君合实习计划','常设入口 · 无统一截止','中国','招聘','不适用','一般2–3个月；具体办公室、岗位与可到岗月份另核','https://www.junhe.com/careers/internship/legal_prof'),
 ('cc','Clifford Chance 中国','全年受理 · 不保证有空缺','中国','招聘','不适用','北京／上海 · 三个月 · 以当前岗位要求为准','https://jobs.cliffordchance.com/apac-china')]
def opportunities():
    filters='<div class="filters" id="opportunity-filters"><label>地点<select id="filter-place"><option value="">全部地点</option>'+''.join(f'<option>{x}</option>' for x in ['Bristol','线上','中国'])+'</select></label><label>类型<select id="filter-type"><option value="">全部类型</option><option>活动</option><option>实践</option><option>招聘</option></select></label><label>费用<select id="filter-cost"><option value="">全部费用</option><option>免费</option><option>会员免费</option><option>待核实</option><option>不适用</option></select></label><button type="button" id="clear-filters" class="text-button">清空筛选</button></div><p class="result-count" id="opportunity-count" aria-live="polite">7 个入口 · 不等于已报名或正在招聘</p>'
    cards=[]
    for id,title,date,place,kind,cost,note,url in opps:
        index('opp-'+id,title,date+' '+place+' '+kind+' '+cost+' '+note,'bristol')
        cards.append(f'<article class="opportunity" id="opp-{id}" data-place="{place}" data-type="{kind}" data-cost="{cost}"><div class="opportunity-top"><span>{kind} / {place}</span><span class="tag">{cost}</span></div><h3>{title}</h3><p class="opportunity-date">{date}</p><p>{note}</p><div class="card-footer">{ext(url,"核对详情")}<span>官方入口 · 核查 09.22</span></div></article>')
    return '<div class="opportunity-explorer">'+filters+'<div class="opportunity-grid">'+''.join(cards)+'</div><p id="opportunity-empty" hidden>没有符合这些条件的入口。请放宽筛选；未知费用不会被归为免费。</p></div>'
def section(s):
    sid=s['id'];index(sid,s['title'],s.get('intro',''),sid)
    content=(''+opportunities() if sid=='bristol' else '')+''.join(block(b,sid,i) for i,b in enumerate(s['blocks']))
    return f'<section class="section" id="{sid}" aria-labelledby="heading-{sid}">{heading(sid,s.get("kicker",""),s["title"],s.get("intro",""))}<div class="section-body">{content}</div></section>'
front=[]
for t in FRONTIER.get('items',[]):
    index(t['id'],t['title'],t['fact']+' '+t['access'],'frontier')
    index(t['id']+'-practice',t['title']+' · 训练与限制',t['practice']+' '+t['limit'],'frontier')
    front.append(f'<article class="frontier-card" id="{e(t["id"])}"><div class="frontier-meta"><time datetime="{t["date"]}">{t["date"]}</time><span>{e(t["provider"])}</span></div><h3>{e(t["title"])}</h3><p>{prose(t["fact"])}</p><div class="access-note">{e(t["access"])}</div><details id="{e(t["id"])}-practice"><summary>转成我的法律训练</summary><p>{prose(t["practice"])}</p><p class="muted">{prose(t["limit"])}</p></details><div class="card-footer">{ext(t["url"],"官方发布")}<span>已核查 09.22</span></div></article>')
frontier='<section class="section" id="frontier" aria-labelledby="heading-frontier">'+heading('frontier','FRONTIER BRIEF / 2026.07.22 — 09.22','AI 已经不止是对话框。','精选近两个月可核实的能力更新。产品事实、开放范围与我们的练习建议分别呈现；“企业预览”不是“学生已能免费使用”。')+'<p class="editor-note">阅读重点：从生成一段答案，转向可检查的文档、证据表和多步任务。以下是官方能力说明，不是本网站完成的模型评测。</p><div class="frontier-grid">'+''.join(front)+'</div><a class="button primary" href="#ai">把新能力变成作品集</a></section>'
source_rows=[]
for n,s in enumerate(sources.values()):
    id='source-'+s['id'];index(id,s['title'],s.get('note','')+' '+s['category'],'sources')
    checked=s.get('checkedAt','2026-09-22' if s['category']=='AI 前沿' else '2026-09-21')
    source_rows.append(f'<li id="{id}" data-category="{e(s["category"])}"><span class="source-ref">{n+1:02d}</span><div><span class="source-category">{e(s["category"])}</span>{ext(s["url"],s["title"],"source-title")}<p class="source-note">{prose(s.get("note",""))}</p><span class="source-domain">{e(urlsplit(s["url"]).netloc)} · 核查 {checked}</span></div></li>')
source_filters='<label class="source-filter">分类<select id="source-category"><option value="">全部来源</option>'+''.join(f'<option>{e(c)}</option>' for c in dict.fromkeys(s['category'] for s in sources.values()))+'</select></label>'
source_section='<section class="section" id="sources" aria-labelledby="heading-sources">'+heading('sources',f'REFERENCE LIBRARY / {len(sources)} SOURCES','每一条重要信息，都应能回到原文。','AI更新核查于2026年9月22日；既有职业来源以各条核查日期为准。网页更新时间不等于每个岗位重新核实，不把常设入口标为实时空缺。')+source_filters+'<p id="source-count" class="result-count" aria-live="polite">'+str(len(sources))+' 条来源</p><ol class="source-list">'+''.join(source_rows)+'</ol></section>'
sections={s['id']:section(s) for s in S}
tasks=[('teams','挑出 10 个具体团队','留下项目、律师和岗位入口','teams'),('sample','做一份能复核的样本','把 AI 草稿变成有来源的作品','ai'),('event','选一场值得去的活动','先看讲者，再准备两个问题','bristol'),('contact','开启一次具体交流','带着问题联系一位业务律师','connections')]
task_html=''.join(f'<div class="task-row"><label><input type="checkbox" data-task="{id}"><span><strong>{title}</strong><small>{desc}</small></span></label><a href="#{link}" aria-label="{title}：查看方法">查看</a></div>' for id,title,desc,link in tasks)
start=f'''<section id="start" aria-labelledby="main-title"><div class="edition-line"><span>法律职业 · 研究与行动</span><span>VOL. 02 / SEP 2026</span></div><div class="hero"><div><p class="kicker">BRISTOL → CHINA</p><h1 id="main-title">不只进入行业。<br>开始建立你的<span>专业优势。</span></h1><p class="hero-copy">从布大 LLM 到中国商事法律团队。<br>找到对的人，交出可信的作品，用好新一代 AI。</p><div class="hero-actions"><a class="button primary" href="#frontier">读近两个月 AI 前沿 <span aria-hidden="true">↗</span></a><a class="button quiet" href="#roadmap">看八个月路线</a></div></div><aside class="hero-note"><span class="note-label">你的下一站</span><p class="hero-date">May <em>2027</em></p><p class="availability">2027 年 5 月起，可回国全职实习</p><div class="note-rule"></div><p>不是多投几份简历。<br>是让一个具体团队，看见你的价值。</p><a href="#teams">从研究团队开始 ↗</a></aside></div><div class="home-grid"><div class="weekly"><div class="subheading"><h2>先把这一周做好</h2><span id="task-count" aria-live="polite">0 / 4 完成</span></div>{task_html}<div class="task-foot"><span id="storage-note">勾选仅存于当前浏览器，不代表已申请。</span><button type="button" id="reset-tasks" class="text-button">重置</button></div></div><aside class="feature-note"><span class="kicker">THE NEW LEGAL TOOLKIT</span><h2>从“会提问”<br>到“能交付”。</h2><p>多文档审查、证据溯源、浏览器协作、实时语音。把前沿能力转成你能展示的四份作品。</p><a href="#ai">打开 AI 实务工作流 <span aria-hidden="true">↗</span></a><div class="feature-bottom"><span>{len(FRONTIER.get('items',[])):02d} 条近期更新</span><span>人工复核优先</span></div></aside></div><div class="home-bottom"><div><span class="kicker">NEXT DATE</span><h3>09.30 · HR Clinic 申请截止</h3><p>2026/27 批次，17:00 英国当地时间。有课程／经历条件，兴趣匹配再申请。</p><a href="#opp-hr-clinic">看资格与原始入口 ↗</a></div><div><span class="kicker">HOW TO USE</span><h3>别从头读完，从问题进入。</h3><p>用上方搜索直达“君合”“免费”“语音”或“法考”。按章节阅读，保留全部来源。</p><a href="#sources">浏览 {len(sources)} 条来源 ↗</a></div></div><details class="assumptions"><summary>适用背景与固定安排</summary><p>按“温州大学国际经贸规则本科 → Bristol LLM”的假设背景设计。2027年5月可全职到岗是既定规划条件；可持续实习时长按真实安排填写。网站不承诺录用或认证个人资格。AI模块是学习方法与工具信息，不是已连接模型的在线法律服务。</p></details></section>'''
body=start+frontier+''.join(sections[sid] for sid,_ in nav_items if sid in sections)+source_section
payload=json.dumps(SEARCH,ensure_ascii=False).replace('<','\\u003c')
doc=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#173d35"><meta name="description" content="Bristol LLM回国职业工作台：近两个月AI前沿、法律实务工作流、商事团队定位、实习路径、活动招聘和原始来源。"><meta property="og:title" content="Bristol / China — 法律职业研究与行动"><meta property="og:description" content="不只进入行业。开始建立你的专业优势。2026—2027法律职业行动指南。"><title>Bristol / China — 法律职业研究与行动</title><link rel="icon" href="assets/favicon.svg"><link rel="stylesheet" href="assets/style.css"><script defer src="assets/app.js"></script></head><body><noscript><div class="no-script-note">当前未启用 JavaScript：展示完整指南与来源，搜索、筛选和进度保存不可用。</div><style>.utility-bar,.filters,.source-filter,.copy-button,.task-foot,#task-count,.task-row input,.footer>span:last-child{{display:none!important}}</style></noscript><a class="skip-link" href="#main">跳至正文</a><header class="site-header"><a class="brand" href="#start" aria-label="法律职业行动指南首页"><span class="brand-mark">B<span>/</span>C</span><span class="brand-name">法律职业研究与行动<small>BRISTOL / CHINA</small></span></a><div class="header-right"><span class="header-edition">2026 — 2027 FIELD GUIDE</span><details class="mobile-nav"><summary>目录</summary>{nav()}</details></div></header><div class="layout"><aside class="sidebar"><p class="sidebar-title">你的职业工作台</p>{nav()}<div class="sidebar-bottom"><span class="live-dot"></span> 2027.05 可全职到岗<p>编辑更新 · 2026.09.22<br>基于公开来源，持续人工判断。</p>{ext('https://github.com/zhouyi-xiaoxiao/bristol-law-career-roadmap','查看源代码')}</div></aside><div class="main-wrap"><div class="utility-bar"><span id="current-chapter">行动总览</span><div class="search-wrap"><label class="visually-hidden" for="site-search">搜索全部内容</label><input id="site-search" type="search" autocomplete="off" placeholder="搜索团队、活动或 AI 能力…" aria-controls="search-results"><kbd>/</kbd></div></div><div id="search-results" hidden><div class="search-results-head"><p id="search-count" aria-live="polite"></p><button type="button" id="clear-search" class="text-button">清空</button></div><ul id="search-list"></ul></div><main id="main">{body}</main><footer class="footer"><span>BRISTOL / CHINA <small>独立职业行动指南 · 非招聘承诺</small></span><span>无登录 · 无追踪 · 本地保存进度</span></footer></div></div><p id="copy-status" class="visually-hidden" role="status" aria-live="polite"></p><script type="application/json" id="search-data">{payload}</script></body></html>'''
(ROOT/'docs/index.html').write_text(doc)
print(json.dumps({'status':'built','sections':12,'sources':len(sources),'frontier_updates':len(FRONTIER.get('items',[])),'search_entries':len(SEARCH),'bytes':len(doc.encode())},ensure_ascii=False))
