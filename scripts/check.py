#!/usr/bin/env python3
import json, re, hashlib
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.external=[]; self.h1=0; self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and 'href' in a:
            self.links.append(a['href'])
            if a['href'].startswith('https:'):
                self.external.append(a)
        if tag=='h1': self.h1+=1
        if tag=='script': self.scripts.append(a.get('src',''))
raw=(ROOT/'docs/index.html').read_text()
p=Document();p.feed(raw)
assert len(p.ids)==len(set(p.ids)), 'Duplicate IDs'
assert p.h1==1, 'Expected one H1'
assert all(h[1:] in p.ids for h in p.links if h.startswith('#')), 'Broken chapter anchor'
assert all('noopener' in a.get('rel','') for a in p.external), 'Unsafe external tab'
assert all(not s.startswith('http') for s in p.scripts), 'Unexpected third-party script'
assert len(set(a['href'] for a in p.external))>=25, 'Incomplete source collection'
assert '2027 年 5 月起，可回国全职实习' in raw, 'Availability was changed'
assert not any(t in raw for t in ['待课程安排确认','具体时间待课程安排确认','YOUR_TOKEN','ghp_','gho_']), 'Unexpected placeholder or private value'
assert all((ROOT/'docs'/x).is_file() for x in ['assets/style.css','assets/app.js','assets/favicon.svg'])
print(json.dumps({'status':'PASS','ids':len(p.ids),'links':len(p.links),'unique_external_links':len(set(a['href'] for a in p.external)),'sha256':hashlib.sha256(raw.encode()).hexdigest()},ensure_ascii=False))
