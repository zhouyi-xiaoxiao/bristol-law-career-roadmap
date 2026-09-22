#!/usr/bin/env python3
"""Build a dependency-free, progressively enhanced Chinese career guide."""
import json
import html
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'src/content.json').read_text())
def e(value):
    return html.escape(str(value), quote=True)
def prose(value):
    safe = e(value)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
def external(url, label, css=''):
    if not url.startswith(('https://', 'mailto:')):
        raise ValueError(f'Unsafe link: {url}')
    return f'<a class="{e(css)}" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span><span class="visually-hidden">（在新标签页打开）</span></a>'

SECTIONS = DATA['sections']
expected = ['roadmap','routes','teams','connections','bristol','recruitment','skills','ai','templates']
assert [s['id'] for s in SECTIONS] == expected, 'Unexpected chapter order'

def block(b, sid, i):
    kind = b['type']
    if kind == 'paragraph':
        return f'<p>{prose(b["text"])}</p>'
    if kind == 'list':
        return '<ul>' + ''.join(f'<li>{prose(t)}</li>' for t in b['items']) + '</ul>'
    if kind == 'callout':
        return f'<aside class="callout"><h3>{e(b["title"])}</h3><p>{prose(b["text"])}</p></aside>'
    if kind == 'steps':
        return '<ol class="steps">' + ''.join(f'<li><h3>{e(t["title"])}</h3><p>{prose(t["body"])}</p></li>' for t in b['items']) + '</ol>'
    if kind == 'cards':
        cards = []
        for t in b['items']:
            meta = f'<span class="card-meta">{e(t["meta"])}</span>' if t.get('meta') else ''
            link = external(t['url'], t.get('linkLabel', '查看官方入口'), 'card-link') if t.get('url') else ''
            cards.append(f'<article class="card">{meta}<h3>{e(t["title"])}</h3><p>{prose(t["body"])}</p>{link}</article>')
        return '<div class="cards">' + ''.join(cards) + '</div>'
    if kind == 'template':
        tid = f'{sid}-text-{i}'
        return f'<details class="template"><summary>{e(b["title"])}</summary><div class="template-inner"><div class="template-text" id="{tid}">{e(b["text"])}</div><button class="copy-button" type="button" data-copy="{tid}" aria-label="复制：{e(b["title"])}">复制文本</button></div></details>'
    raise ValueError(f'Unknown block type {kind}')

nav_titles = ['月度行动时间线','四条职业路线','找到具体业务团队','内推与其他入口','布大活动与资源','律所招聘窗口','能力与资格准备','AI 训练方法','联系与 AI 模板']
nav_items = [('start','本周从这里开始')] + [(s['id'], nav_titles[i]) for i,s in enumerate(SECTIONS)] + [('sources','全部来源与链接')]
def nav():
    return '<nav class="chapter-nav" aria-label="章节导航">' + ''.join(f'<a href="#{sid}"><span class="nav-num" aria-hidden="true">{i:02d}</span><span>{e(title)}</span></a>' for i,(sid,title) in enumerate(nav_items)) + '</nav>'

def section(s, number):
    content = ''.join(block(b, s['id'], i) for i,b in enumerate(s['blocks']))
    return f'<section class="section" id="{s["id"]}" aria-labelledby="heading-{s["id"]}"><div class="section-head"><span class="section-number" aria-hidden="true">{number:02d}</span><div class="section-heading"><div class="kicker">{e(s.get("kicker", ""))}</div><h2 id="heading-{s["id"]}">{e(s["title"])}</h2><p class="section-intro">{prose(s.get("intro", ""))}</p></div></div><div class="section-body">{content}</div></section>'

groups = {}
seen = set()
sources = []
for s in DATA['sources']:
    if s['url'] in seen: continue
    seen.add(s['url']); sources.append(s)
    groups.setdefault(s['category'], []).append(s)
source_html = ''
n = 0
for category, items in groups.items():
    source_html += f'<div class="source-group"><h3>{e(category)}</h3><ul class="source-list">'
    for s in items:
        n += 1
        source_html += f'<li id="source-{e(s["id"])}"><span class="source-ref">{n:02d}</span><div>{external(s["url"],s["title"],"source-title")}<span class="source-note">{prose(s.get("note",""))}</span><span class="source-domain">{e(urlsplit(s["url"]).netloc)}</span></div></li>'
    source_html += '</ul></div>'

document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#102747"><meta name="description" content="Bristol LLM 回国法律职业行动指南：2026年9月至2027年5月路线、头部律所与团队定位、内推方法、英国活动、招聘窗口及AI训练，附官方来源。"><meta property="og:type" content="website"><meta property="og:title" content="Bristol → China｜法律职业行动指南"><meta property="og:description" content="从2026年9月入学，到2027年5月全职实习。把方向、能力和联系，变成具体机会。"><title>Bristol → China｜法律职业行动指南 2026—2027</title><link rel="icon" type="image/svg+xml" href="assets/favicon.svg"><link rel="stylesheet" href="assets/style.css"><script defer src="assets/app.js"></script></head>
<body><a class="skip-link" href="#main">跳至正文</a><header class="site-header"><div class="header-inner"><a class="brand" href="#start" aria-label="法律职业行动指南首页"><span class="brand-mark" aria-hidden="true">B.</span><span class="brand-name">法律职业行动指南<small>BRISTOL → CHINA</small></span></a><div class="header-meta"><span>2026.09 — 2027.05</span><span class="edition">LLM · 回国实习</span></div><details class="mobile-nav"><summary>目录</summary>{nav()}</details></div></header>
<div class="layout"><aside class="sidebar"><p class="sidebar-title">CONTENTS / 行动目录</p>{nav()}<div class="sidebar-note"><b>2027 年 5 月起可全职到岗</b>正式招聘、团队直投、专业推荐并行推进。<br><br>整理于 2026.09.22<br>招聘与活动资料主要核查于 2026.09.21</div></aside><main id="main">
<section id="start" aria-labelledby="main-title"><div class="intro"><div class="intro-top"><span class="eyebrow">A FIELD GUIDE TO YOUR FIRST LEGAL ROLE</span><span class="date-pill">2026 — 2027</span></div><h1 id="main-title">从 Bristol，<br>走向<span>法律实习。</span></h1><p class="intro-text">八个月，准备能力、找到团队、建立联系。把每一步，落实到具体行动与官方入口。</p><div class="intro-bottom"><span class="availability">2027 年 5 月起，可回国全职实习</span><a href="#roadmap">先看完整时间线 ↓</a></div></div>
<div class="quicklinks"><a class="quicklink" href="#bristol">活动与报名 <span>↗</span></a><a class="quicklink" href="#recruitment">招聘窗口 <span>↗</span></a><a class="quicklink" href="#templates">联系模板 <span>↗</span></a></div>
<div class="section-head"><span class="section-number" aria-hidden="true">00</span><div class="section-heading"><div class="kicker">START THIS WEEK</div><h2>先做四件事，就能开始。</h2><p class="section-intro">按“温州大学国际经贸规则本科 → Bristol LLM”的假设背景设计。先探索商事律所，也保留企业法务与合规路线。</p></div></div>
<div class="week-grid"><article class="week-item"><b>01 / 定方向</b><h3>先研究 10 个团队</h3><p>选 1—2 个城市、两个业务方向，记录近期项目与具体律师，而不只记律所名字。</p><a href="#teams">学习找团队</a></article><article class="week-item"><b>02 / 做材料</b><h3>准备中英文简历</h3><p>写清法考状态、可到岗日期和真实经历，开始做一份短研究样本。</p><a href="#skills">查看能力清单</a></article><article class="week-item"><b>03 / 进现场</b><h3>准备 10 月的活动</h3><p>优先关注 10 月 1 日 Law Fair，以及 10 月 20 日免费律所交流活动。</p><a href="#bristol">查看日期与报名</a></article><article class="week-item"><b>04 / 开对话</b><h3>联系一个具体的人</h3><p>从读过的文章或听过的分享切入，先请教一个问题，再逐步建立专业联系。</p><a href="#connections">了解内推方法</a></article></div>
<aside class="callout"><h3>这份指南的固定前提</h3><p>已按你的确认，将“2027 年 5 月起可全职到岗”作为求职安排，不再以前置离校风险阻碍行动。可持续实习时长仍按真实安排填写。页面中的月度动作是策略建议；招聘窗口与活动日期另有来源标注，未核实的具体日期不作推测。</p></aside></section>
{''.join(section(s,i+1) for i,s in enumerate(SECTIONS))}
<section class="section" id="sources" aria-labelledby="heading-sources"><div class="section-head"><span class="section-number" aria-hidden="true">10</span><div class="section-heading"><div class="kicker">SOURCE LIBRARY / {len(sources)} LINKS</div><h2 id="heading-sources">全部来源与链接</h2><p class="section-intro">保留原始入口，方便进一步核对与申请。资料主要核查于 2026 年 9 月 21 日；页面整理于 9 月 22 日。不是实时招聘数据库，活动名额、日期与资格以主办方最新说明为准。</p></div></div><div class="section-body">{source_html}</div></section>
<footer class="footer"><div><strong>Bristol → China</strong><br>把方向、能力与联系，变成具体机会。<br>本页为职业规划资料整理，不代表雇主招聘承诺或个人执业资格认证。</div><div><a href="#start">回到顶部 ↑</a><br>{external('https://github.com/zhouyi-xiaoxiao/bristol-law-career-roadmap','网站源代码')}<br>无登录 · 无追踪 · 无第三方脚本</div></footer>
</main></div><p id="copy-status" class="visually-hidden" role="status" aria-live="polite"></p></body></html>'''
(ROOT/'docs/index.html').write_text(document,encoding='utf-8')
print(json.dumps({'output':'docs/index.html','sections':len(SECTIONS),'sources':len(sources),'bytes':len(document.encode())},ensure_ascii=False))
