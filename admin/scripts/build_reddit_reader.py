"""Build an offline Reddit chat/discussion reader from an iLEAPP report.

This is an optional presentation of existing exported rows. It performs no
network requests and never writes to the source report's SQLite database.
"""
import argparse
import json
import sqlite3
from pathlib import Path


def _quote(value):
    return '"' + value.replace('"', '""') + '"'


def _value(row, label):
    found = row.get(label)
    return '' if found is None else found


def _role(raw, view, key):
    col = view.get(key)
    return raw[col] if col in raw.keys() and raw[col] is not None else ''


def load_records(report):
    """Select display fields only; preserve artifact/row/source references."""
    report = Path(report).resolve()
    manifest = json.loads((report / '_lava_data.lava').read_text(encoding='utf-8'))
    wanted = {'reddit_cached_posts', 'reddit_cached_comments', 'reddit_chats',
              'reddit_chat_messages'}
    records = []
    # Use the known report-relative database, rather than trusting an arbitrary manifest path.
    uri = (report / '_lava_artifacts.db').as_uri() + '?mode=ro'
    db = sqlite3.connect(uri, uri=True)
    db.row_factory = sqlite3.Row
    try:
        for artifact in manifest.get('artifacts', {}).get('Reddit', []):
            table = artifact.get('tablename')
            if table not in wanted:
                continue
            columns = artifact['column_map']
            # column_map is SQL column -> original header, as written by lavafuncs.
            for raw in db.execute('SELECT rowid AS __reader_rowid, * FROM ' + _quote(table)):
                row = {label: raw[sql] for sql, label in columns.items()}
                source = _value(row, 'Source File') or artifact.get('source_path', '')
                account = _value(row, 'Account') or _value(row, 'Account ID')
                record = {'table': table, 'rowid': raw['__reader_rowid'],
                          'account': account, 'source': source}
                if table in ('reddit_chats', 'reddit_chat_messages'):
                    view = artifact.get('data_views', {}).get('conversation', {})
                    channel = _role(raw, view, 'conversationDiscriminatorColumn')
                    record.update(kind='chat', text=_role(raw, view, 'textColumn'),
                                  author=_role(raw, view, 'senderColumn'), created=_role(raw, view, 'timeColumn'),
                                  direction=_role(raw, view, 'directionColumn'),
                                  sentValue=view.get('directionSentValue'),
                                  title=_role(raw, view, 'conversationLabelColumn'), channel=channel,
                                  id=_value(row, 'Event ID') or _value(row, 'Message ID (as stored)'),
                                  event=_value(row, 'Event Type'), attachment=_value(row, 'Attachment'))
                    # Missing IDs must not collapse unrelated messages into one conversation.
                    record['group'] = json.dumps([table, account, source,
                                                  channel or ['unassigned', record['rowid']]])
                else:
                    comment = table == 'reddit_cached_comments'
                    post_id = _value(row, 'Post ID (from permalink)') if comment else _value(row, 'Object ID')
                    record.update(kind='comment' if comment else 'post',
                                  text=_value(row, 'Text'), author=_value(row, 'Author Name') or _value(row, 'Author ID'),
                                  created=_value(row, 'Content Created'), edited=_value(row, 'Content Edited'),
                                  title=_value(row, 'Cached Post Title') if comment else _value(row, 'Title'),
                                  community=_value(row, 'Community (from permalink)') if comment else _value(row, 'Community'),
                                  postId=post_id, id=_value(row, 'Object ID'),
                                  permalink=_value(row, 'Permalink'), own=_value(row, 'Is Own (as stored)'))
                    record['group'] = json.dumps(['discussion', account, source,
                                                  post_id or ['unassigned', table, record['rowid']]])
                records.append(record)
    finally:
        db.close()
    return records


# Evidence is assigned using textContent. '<' is also escaped in the embedded JSON,
# preventing a source string such as </script> from terminating the data element.
PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reddit — Chats and cached discussions</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#172b3a;font:15px system-ui,sans-serif}header{padding:20px 26px;background:#fff;border-bottom:1px solid #d8e0e6}h1{font-size:24px;margin:0 0 8px}p{margin:7px 0;line-height:1.45}.muted{color:#536777;font-size:13px}.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:15px}button,input,select{font:inherit;padding:9px;border:1px solid #a7b6c2;border-radius:7px;background:white}button{cursor:pointer}button.active{background:#174d71;color:white}input[type=search]{min-width:250px;flex:1}main{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 237px);min-height:450px}aside{overflow:auto;border-right:1px solid #d8e0e6;padding:12px}#detail{overflow:auto;padding:24px}#groups button{display:block;width:100%;text-align:left;margin:0 0 8px;padding:12px;word-break:break-word}#groups button.selected{border:2px solid #174d71}.group-title{display:block;font-weight:650}.group-sub{display:block;font-size:12px;color:#526776;margin-top:6px}.card{background:#fff;border:1px solid #d8e0e6;border-radius:10px;margin:12px 0;padding:15px;max-width:1050px;overflow-wrap:anywhere}.card.post{border-left:4px solid #bc5519}.card.outgoing{margin-left:12%;background:#e6f1fa}.card.incoming{margin-right:12%}.card.unknown{border-left:4px solid #a7b6c2}.card h3{font-size:17px;margin:9px 0}.body{white-space:pre-wrap;line-height:1.55;margin-top:10px}details{font-size:12px;color:#526776;margin-top:12px;white-space:pre-wrap}.badge{font-size:12px;font-weight:650;color:#174d71}.notice{padding:10px 13px;border-radius:7px;background:#fff3d6;font-size:13px;line-height:1.45}.empty{padding:24px;color:#526776}a{color:#174d71}@media(max-width:750px){main{grid-template-columns:1fr;height:auto}aside{max-height:35vh}#detail{padding:15px}}
</style></head><body>
<header><h1>Reddit review</h1>
<p>Private chats and cached public discussions, with links back to the exported records.</p>
<p class="muted"><a href="_HTML/index.html">Open the full iLEAPP tables</a> · Times shown in UTC · Entirely local; no media or web content is fetched</p>
<div class="controls"><button id="chats" class="active">Chats</button><button id="discussions">Cached discussions</button><input id="search" type="search" placeholder="Search text, author, title or ID" aria-label="Search Reddit records"><select id="account" aria-label="Filter by account"><option value="">All source accounts</option></select></div>
<div class="controls"><label><input type="checkbox" id="stubs"> Include ID-only post records</label><span id="counts" class="muted"></span></div></header>
<main><aside><div id="groups"></div></aside><section id="detail" aria-live="polite"></section></main>
<script id="records" type="application/json">__RECORDS__</script>
<script>
'use strict';
const records=JSON.parse(document.getElementById('records').textContent);
const byId=id=>document.getElementById(id);
function el(tag,text,cls){const node=document.createElement(tag);if(text!==undefined)node.textContent=String(text);if(cls)node.className=cls;return node;}
function stamp(raw){if(raw===''||raw===null||raw===undefined)return 'Date not retained';const n=Number(raw);if(!Number.isFinite(n))return 'Date not retained';const date=new Date(n*1000);return Number.isNaN(date.getTime())?'Date not retained':date.toISOString().replace('T',' ').replace('.000Z',' UTC').replace('Z',' UTC');}
const groups=new Map();
for(const r of records){if(!groups.has(r.group))groups.set(r.group,{id:r.group,rows:[],kind:r.kind==='chat'?'chat':'discussion'});groups.get(r.group).rows.push(r);}
for(const g of groups.values()){
 const post=g.rows.find(r=>r.kind==='post');const first=g.rows[0];
 g.account=String(first.account||'Account not recorded');
 g.title=String((post&&post.title)||g.rows.find(r=>r.title)?.title||(g.kind==='chat'?'Chat · '+([...new Set(g.rows.map(r=>r.author).filter(Boolean))].join(', ')||first.channel||'without stored ID'):'Post '+(first.postId||'without established post link')));
 g.community=String(g.rows.find(r=>r.community)?.community||'');
 g.comments=g.rows.filter(r=>r.kind==='comment').length;
 g.stub=g.kind==='discussion'&&g.comments===0&&!g.rows.some(r=>r.text||r.title);
 g.search=g.rows.map(r=>[r.text,r.author,r.title,r.id,r.postId,r.community,r.channel].join(' ')).join(' ').toLowerCase();
}
for(const account of [...new Set([...groups.values()].map(g=>g.account))].sort()){const option=el('option',account);option.value=account;byId('account').append(option);}
let mode='chat',selected='';
function renderDetail(g){
 const target=byId('detail');target.replaceChildren();
 if(!g){target.append(el('p','Select a chat or discussion from the list.','empty'));return;}
 target.append(el('h2',g.title),el('p',(g.community?'r/'+g.community+' · ':'')+g.account,'muted'));
 target.append(el('p',g.kind==='chat'?'Chats use the existing iLEAPP conversation grouping and stored/inferred direction fields. Reactions and redaction events remain labeled. Blank direction stays unknown.':'This is a flat grouping of cached content by post ID within one source database. It is not the full discussion, a reply hierarchy, or evidence of reading. Dates are content creation dates. ID-only records may have no title, text or date.','notice'));
 const sorted=[...g.rows].sort((a,b)=>{if(g.kind==='discussion'&&a.kind!==b.kind)return a.kind==='post'?-1:1;const av=a.created===''?Infinity:Number(a.created),bv=b.created===''?Infinity:Number(b.created);return av-bv||a.rowid-b.rowid;});
 for(const r of sorted){
  const direction=r.kind==='chat'?(r.direction===r.sentValue?'outgoing':r.direction==='Incoming'?'incoming':'unknown'):r.kind;
  const card=el('article',undefined,'card '+direction);
  const type=r.kind==='post'?'Cached post':r.kind==='comment'?'Cached comment':r.event||'Chat message';
  card.append(el('div',type+(r.kind==='chat'?' · '+(r.direction||'Direction unknown'):''),'badge'));
  card.append(el('p',(r.author||'Author not retained')+' · '+stamp(r.created),'muted'));
  if(r.kind==='post'&&r.title)card.append(el('h3',r.title));
  card.append(el('div',r.text||'Text not retained in this cached record.','body'));
  if(r.attachment)card.append(el('p','Attachment reference: '+r.attachment,'muted'));
  const d=el('details');d.append(el('summary','Source and record details'));
  d.append(el('div','Artifact: '+r.table+'\nExport row: '+r.rowid+'\nSource account: '+(r.account||'Not recorded')+'\nSource: '+r.source+'\nObject/message ID: '+(r.id||'Not retained')+(r.postId?'\nPost ID: '+r.postId:'')+(r.permalink?'\nStored permalink: '+r.permalink:'')+(r.edited?'\nContent edited: '+stamp(r.edited):'')+(r.own!==undefined?'\nIs Own (as stored): '+r.own:'')));
  card.append(d);target.append(card);
 }
}
function render(){
 const q=byId('search').value.toLowerCase().trim(),account=byId('account').value;
 const visible=[...groups.values()].filter(g=>g.kind===mode&&(!account||g.account===account)&&(!g.stub||byId('stubs').checked)&&(!q||g.search.includes(q))).sort((a,b)=>b.comments-a.comments||a.title.localeCompare(b.title));
 const list=byId('groups');list.replaceChildren();
 for(const g of visible){const button=el('button');if(g.id===selected)button.classList.add('selected');button.append(el('span',g.title,'group-title'),el('span',(g.community?'r/'+g.community+' · ':'')+g.account+' · '+(g.kind==='chat'?g.rows.length+' records':g.comments+' cached comments'),'group-sub'));button.addEventListener('click',()=>{selected=g.id;render();});list.append(button);}
 if(!visible.length)list.append(el('p','No matching records.','empty'));
 byId('counts').textContent=visible.length+' '+(mode==='chat'?'chats':'discussions')+' · '+visible.reduce((n,g)=>n+g.rows.length,0)+' records shown';
 renderDetail(visible.find(g=>g.id===selected)||null);
}
for(const [id,value] of [['chats','chat'],['discussions','discussion']])byId(id).addEventListener('click',()=>{mode=value;selected='';byId('chats').classList.toggle('active',mode==='chat');byId('discussions').classList.toggle('active',mode==='discussion');render();});
for(const id of ['search','account','stubs'])byId(id).addEventListener('input',render);
render();
</script></body></html>
'''


def build(report, output=None):
    """Write only the new reader file; source tables and manifest stay untouched."""
    report = Path(report)
    destination = Path(output) if output else report / 'Reddit_Reader.html'
    records = load_records(report)
    payload = json.dumps(records, ensure_ascii=True).replace('<', r'\u003c')
    destination.write_text(PAGE.replace('__RECORDS__', payload), encoding='utf-8')
    return len(records)


def main():
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument('report', type=Path, help='iLEAPP report containing _lava_data.lava')
    args = command.parse_args()
    count = build(args.report)
    print(f'Wrote Reddit_Reader.html containing {count} exported records')


if __name__ == '__main__':
    main()
