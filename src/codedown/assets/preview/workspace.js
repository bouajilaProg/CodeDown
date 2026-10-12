const config = JSON.parse(document.getElementById('config').textContent);
const $ = id => document.getElementById(id);
const editor = $('editor'), frame = $('preview'), workspace = $('workspace'), divider = $('divider');
let dirty = false, diskText = '', timer, revision = 0, split = 50;
const preferences = {
  get(key) { try { return localStorage.getItem('codedown-' + key); } catch { return null; } },
  set(key, value) { try { localStorage.setItem('codedown-' + key, value); } catch {} }
};
$('filename').textContent = config.filename;
for (const name of config.themes) $('theme').add(new Option(name, name));
$('theme').value = config.theme;
function setSplit(value) {
  split = Math.min(85, Math.max(15, value));
  workspace.style.setProperty('--split', split + '%');
  divider.setAttribute('aria-valuenow', Math.round(split));
  preferences.set('split', split);
}
function setLayout(value) {
  workspace.dataset.layout = value;
  $('layout').value = value;
  divider.setAttribute('aria-orientation', value === 'vertical' ? 'horizontal' : 'vertical');
  preferences.set('layout', value);
}
const savedLayout = preferences.get('layout');
setLayout(['horizontal', 'vertical', 'preview', 'editor'].includes(savedLayout) ? savedLayout : (innerWidth < 650 ? 'vertical' : 'horizontal'));
const savedSplit = Number(preferences.get('split'));
setSplit(savedSplit >= 15 && savedSplit <= 85 ? savedSplit : 50);
$('layout').addEventListener('change', event => setLayout(event.target.value));
$('reset').addEventListener('click', () => setSplit(50));
divider.addEventListener('dblclick', () => setSplit(50));
divider.addEventListener('keydown', event => {
  const keys = workspace.dataset.layout === 'vertical' ? ['ArrowUp', 'ArrowDown'] : ['ArrowLeft', 'ArrowRight'];
  if (keys.includes(event.key)) { event.preventDefault(); setSplit(split + (event.key === keys[0] ? -2 : 2)); }
  if (event.key === 'Home') { event.preventDefault(); setSplit(50); }
});
divider.addEventListener('pointerdown', event => {
  divider.setPointerCapture(event.pointerId);
  frame.style.pointerEvents = 'none';
});
divider.addEventListener('pointermove', event => {
  if (!divider.hasPointerCapture(event.pointerId)) return;
  const rect = workspace.getBoundingClientRect(), vertical = workspace.dataset.layout === 'vertical';
  setSplit(100 * (vertical ? event.clientY - rect.top : event.clientX - rect.left) / (vertical ? rect.height : rect.width));
});
for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) divider.addEventListener(name, () => { frame.style.pointerEvents = ''; });
async function copy(text, button) {
  const label = button.textContent;
  try {
    if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
    else {
      const input = document.createElement('textarea'); input.value = text; document.body.append(input); input.select();
      const success = document.execCommand('copy'); input.remove();
      if (!success) throw new Error('Clipboard unavailable');
    }
    button.textContent = 'Copied!';
  } catch { button.textContent = 'Copy failed'; $('status').textContent = 'Could not access clipboard. Select the text and copy it manually.'; }
  setTimeout(() => { button.textContent = label; }, 1600);
}
$('copy-markdown').addEventListener('click', () => copy(editor.value, $('copy-markdown')));
frame.addEventListener('load', () => {
  const doc = frame.contentDocument;
  if (!doc) return;
  for (const pre of doc.querySelectorAll('pre')) {
    const code = pre.querySelector('code') || pre;
    const button = doc.createElement('button'); button.type = 'button'; button.className = 'copy-code'; button.textContent = 'Copy code';
    button.setAttribute('aria-label', 'Copy code block');
    button.addEventListener('click', () => copy(code.textContent, button));
    pre.before(button);
  }
  for (const link of doc.querySelectorAll('a')) {
    // Keep navigation from replacing the document being previewed.
    const href = link.getAttribute('href');
    if (href?.startsWith('#')) {
      link.addEventListener('click', event => {
        event.preventDefault();
        try { doc.getElementById(decodeURIComponent(href.slice(1)))?.scrollIntoView(); } catch {}
      });
    } else { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
  }
});
async function render() {
  const current = ++revision;
  $('status').textContent = 'Rendering…';
  try {
    const response = await fetch('/api/render', { method:'POST', headers:{ 'Content-Type':'application/json', 'X-Preview-Token':config.token }, body:JSON.stringify({ markdown:editor.value, theme:$('theme').value }) });
    const data = await response.json();
    if (current !== revision) return;
    if (!response.ok) throw new Error(data.error);
    $('theme-colors').textContent = (data.css.match(/:root\s*\{[^}]*\}/g) || []).join('\n');
    frame.srcdoc = data.html;
    $('status').textContent = dirty ? 'Preview updated · Browser edits are unsaved' : 'Preview updated · Watching source file';
  } catch (error) { if (current === revision) $('status').textContent = error.message; }
}
editor.addEventListener('input', () => {
  dirty = editor.value !== diskText;
  ++revision; clearTimeout(timer); timer = setTimeout(render, 200);
});
$('theme').addEventListener('change', render);
async function loadDocument(force = false) {
  try {
    const response = await fetch('/api/document'); const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    if (force || (!dirty && data.markdown !== diskText)) {
      diskText = data.markdown; editor.value = diskText; dirty = false; await render();
    } else if (dirty && data.markdown !== diskText) $('status').textContent = 'Source file changed · Reload file to replace your browser edits';
  } catch (error) { $('status').textContent = error.message; }
}
$('reload').addEventListener('click', () => { if (!dirty || window.confirm('Replace your browser edits with the source file?')) loadDocument(true); });
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
loadDocument(true);
setInterval(() => loadDocument(), 1500);
