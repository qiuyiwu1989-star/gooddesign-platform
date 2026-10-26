"""055 safe reader Markdown: no raw HTML, images or executable URI schemes."""
import html,re
from urllib.parse import urlsplit
E=lambda s:html.escape(str(s),quote=True)
def inline(text):
    tokens=[]
    def keep(markup):tokens.append(markup);return '\x00'+str(len(tokens)-1)+'\x00'
    text=re.sub(r'`([^`]+)`',lambda m:keep('<code>'+E(m[1])+'</code>'),text)
    def link(m):
        label,url=m[1],m[2].strip();u=urlsplit(url)
        if u.scheme.lower()not in {'','http','https','mailto'}or url.startswith('//')or '\\'in url:return label+'（链接未显示）'
        # Only render navigable frozen attachments; other source files stay readable labels.
        if not u.scheme and u.path and not u.path.endswith(('.html','.md','.json')):return label
        attrs=' target="_blank" rel="noopener noreferrer"' if u.scheme in {'http','https'}else''
        return keep('<a href="'+E(url)+'"'+attrs+'>'+E(label)+'</a>')
    text=re.sub(r'(?<!!)\[([^\]]+)\]\(([^\s)]+)\)',link,text)
    text=E(text);text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    for i,t in enumerate(tokens):text=text.replace('\x00'+str(i)+'\x00',t)
    return text

def document(text):
    lines=text.splitlines();out=[];i=0
    while i<len(lines):
        line=lines[i];i+=1
        if line.startswith('```'):
            code=[]
            while i<len(lines)and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=int(i<len(lines));out.append('<pre tabindex="0"><code>'+E('\n'.join(code))+'</code></pre>');continue
        if not line.strip():continue
        heading=re.match(r'^(#{1,6})\s+(.+)',line)
        if heading:
            n=min(len(heading[1])+1,6);out.append(f'<h{n}>'+inline(heading[2])+f'</h{n}>');continue
        if '|'in line and i<len(lines)and re.match(r'^\s*\|?\s*:?-{3,}',lines[i]):
            cols=lambda s:[x.strip()for x in s.strip().strip('|').split('|')]
            head=cols(line);i+=1;body=[]
            while i<len(lines)and '|'in lines[i]and lines[i].strip():body.append(cols(lines[i]));i+=1
            out.append('<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+inline(x)+'</th>'for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(x)+'</td>'for x in row)+'</tr>'for row in body)+'</tbody></table></div>');continue
        item=re.match(r'^\s*(?:[-*]|\d+[.)])\s+(.+)',line)
        if item:
            ordered=bool(re.match(r'^\s*\d',line));tag='ol'if ordered else'ul';items=[item[1]]
            while i<len(lines):
                m=re.match(r'^\s*(?:[-*]|\d+[.)])\s+(.+)',lines[i])
                if not m:break
                items.append(m[1]);i+=1
            out.append('<'+tag+'>'+''.join('<li>'+inline(x)+'</li>'for x in items)+'</'+tag+'>');continue
        out.append('<p>'+inline(line)+'</p>')
    return ''.join(out)
