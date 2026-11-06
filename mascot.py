"""mascot.py - Pip, the kindcart sprout, and the kindcart logo.

Pip has four emotional states (images in assets/):
  before   - droopy and curious, before the user has learned anything
  learning - waving, while exploring impacts and swaps
  excited  - celebrating an eco-friendly choice
  goal     - proud gardener after reaching a goal or earning a badge

`pip_widget()` builds a small interactive web component (HTML + CSS + JavaScript)
that runs in the browser, so Pip stays lively WITHOUT re-running the Python app:
  * a different idle animation for each state (sway, wave, hop, proud pulse)
  * Pip's head tilts to follow the mouse / finger
  * hover or tap: Pip hops, sparkles pop out and Pip says something new
  * the speech bubble is typed out letter by letter while Pip "talks"
  * every ~20 seconds Pip shares a random eco tip
If an image file is missing the app still runs and shows a plant emoji instead.
"""
import base64
import json
from functools import lru_cache
from pathlib import Path

import data

ASSETS = Path(__file__).parent / "assets"


@lru_cache(maxsize=None)
def _b64(filename):
    return base64.b64encode((ASSETS / filename).read_bytes()).decode()


def pip_img(state="learning", width=150, css_class="bob"):
    """Plain <img> for Pip (used where the interactive widget is not needed)."""
    info = data.PIP_STATES.get(state, data.PIP_STATES["learning"])
    try:
        return (f'<img class="{css_class}" alt="Pip the sprout ({state})" width="{width}" '
                f'src="data:image/png;base64,{_b64(info["file"])}"/>')
    except FileNotFoundError:
        return f'<span style="font-size:{width // 2}px">\U0001F331</span>'


def logo_img(width=46):
    try:
        return f'<img alt="kindcart logo" width="{width}" src="data:image/png;base64,{_b64("logo.png")}"/>'
    except FileNotFoundError:
        return "\U0001F6D2"


def logo_path():
    """Path for the browser-tab icon, or an emoji if the file is missing."""
    path = ASSETS / "logo.png"
    return str(path) if path.exists() else "\U0001F331"


_WIDGET = """<!-- pip %(nonce)s -->
<style>
 html,body{margin:0;background:transparent;font-family:'Montserrat','Segoe UI',sans-serif;overflow:hidden}
 .wrap{display:flex;align-items:center;gap:18px;padding:6px 8px;flex-wrap:nowrap}
 .pipbox{position:relative;width:%(w)spx;flex:0 0 auto;cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent}
 .tilt{transition:transform .25s ease-out;transform:rotate(var(--tilt,0deg));transform-origin:50%% 90%%}
 .pipbox img{width:100%%;display:block;transform-origin:50%% 95%%}
 .st-before img{animation:sway 4.5s ease-in-out infinite}
 .st-learning img{animation:wave 2.2s ease-in-out infinite}
 .st-excited img{animation:hop 1.1s ease-in-out infinite}
 .st-goal img{animation:proud 2.4s ease-in-out infinite}
 .talking img{filter:brightness(1.05)}
 .jump img{animation:jump .7s ease-out 1 !important}
 @keyframes sway{0%%,100%%{transform:rotate(-3deg) scaleY(.97)}50%%{transform:rotate(3deg) scaleY(1)}}
 @keyframes wave{0%%,100%%{transform:rotate(-6deg) translateY(0)}50%%{transform:rotate(6deg) translateY(-5px)}}
 @keyframes hop{0%%,100%%{transform:translateY(0) scale(1.04,.94)}45%%{transform:translateY(-22px) scale(.96,1.05)}}
 @keyframes proud{0%%,100%%{transform:scale(1) translateY(0)}50%%{transform:scale(1.06) translateY(-6px)}}
 @keyframes jump{0%%{transform:translateY(0) scale(1.05,.92)}35%%{transform:translateY(-38px) rotate(-8deg) scale(.95,1.06)}70%%{transform:translateY(0) rotate(5deg) scale(1.06,.93)}100%%{transform:none}}
 .spark{position:absolute;pointer-events:none;font-size:20px;animation:rise 1.2s ease-out forwards}
 @keyframes rise{0%%{opacity:1;transform:translate(0,0) scale(.6)}100%%{opacity:0;transform:translate(var(--dx),-70px) scale(1.2)}}
 .bubble{flex:1 1 auto;min-width:0;background:%(banner)s;border:2px solid %(border)s;border-radius:20px;padding:14px 20px;color:%(text)s;font-size:%(fs)s;line-height:1.45;position:relative;min-height:56px}
 .bubble:before{content:"";position:absolute;left:-14px;top:30px;border:8px solid transparent;border-right-color:%(banner)s;border-left:0}
 .bubble b{color:%(head)s}
 .hint{display:block;margin-top:6px;font-size:.72rem;color:%(head)s;opacity:.65}
 .caret{display:inline-block;width:2px;height:1em;background:%(head)s;margin-left:2px;vertical-align:-2px;animation:blink .8s steps(1) infinite}
 @keyframes blink{50%%{opacity:0}}
 @media (max-width:520px){.wrap{gap:10px}.pipbox{width:%(wsmall)spx}.bubble{padding:10px 12px;font-size:.92rem}}
</style>
<div class="wrap">
 <div class="pipbox st-%(state)s" id="pip" title="Tap me!">
  <div class="tilt" id="tilt">%(img)s</div>
 </div>
 <div class="bubble"><b>Pip says:</b> <span id="msg"></span><span class="caret" id="caret"></span>
  <span class="hint">\U0001F449 Tap or hover over Pip for more tips</span></div>
</div>
<script>
 const MAIN = %(msg)s, CHATTER = %(chatter)s, BURST = %(burst)s;
 const pip = document.getElementById('pip'), tilt = document.getElementById('tilt');
 const msg = document.getElementById('msg'), caret = document.getElementById('caret');
 let timer = null, lastSpark = 0, lastSay = Date.now();
 function say(text){
   clearInterval(timer); msg.textContent = ''; pip.classList.add('talking'); let i = 0;
   timer = setInterval(() => {
     msg.textContent = text.slice(0, ++i);
     if (i >= text.length){ clearInterval(timer); pip.classList.remove('talking'); }
   }, 22);
   lastSay = Date.now();
 }
 function sparkle(n){
   const icons = ['\\u2728','\\U0001F33F','\\U0001F331','\\u2B50','\\U0001F343'];
   for (let k = 0; k < n; k++){
     const s = document.createElement('span'); s.className = 'spark';
     s.textContent = icons[Math.floor(Math.random()*icons.length)];
     s.style.left = (10 + Math.random()*80) + '%%'; s.style.top = (Math.random()*50) + '%%';
     s.style.setProperty('--dx', (Math.random()*80-40) + 'px');
     s.style.animationDelay = (k*0.08) + 's'; pip.appendChild(s); setTimeout(() => s.remove(), 1500);
   }
 }
 function jump(){ pip.classList.remove('jump'); void pip.offsetWidth; pip.classList.add('jump'); setTimeout(() => pip.classList.remove('jump'), 750); }
 function chat(){ say(CHATTER[Math.floor(Math.random()*CHATTER.length)]); jump(); sparkle(6); }
 pip.addEventListener('click', chat);
 pip.addEventListener('mouseenter', () => { if (Date.now() - lastSpark > 2500){ lastSpark = Date.now(); sparkle(3); } });
 document.addEventListener('mousemove', e => {
   const r = pip.getBoundingClientRect(); const dx = (e.clientX - (r.left + r.width/2)) / window.innerWidth;
   tilt.style.setProperty('--tilt', Math.max(-9, Math.min(9, dx*28)) + 'deg');
 });
 document.addEventListener('touchstart', e => { const t = e.touches[0]; const r = pip.getBoundingClientRect();
   tilt.style.setProperty('--tilt', Math.max(-9, Math.min(9, ((t.clientX - r.left - r.width/2)/window.innerWidth)*28)) + 'deg'); }, {passive:true});
 setInterval(() => { if (!timer || Date.now() - lastSay > 20000){ chat(); } }, 20000);
 say(MAIN); if (BURST){ setTimeout(() => { sparkle(10); jump(); }, 300); }
</script>"""


def pip_widget(state, message, colors, chatter, burst=False, width=150, nonce=0, font_size="1.02rem"):
    """Return the interactive Pip HTML (use with streamlit.components.v1.html, height about 210)."""
    info = data.PIP_STATES.get(state, data.PIP_STATES["learning"])
    try:
        img = f'<img alt="Pip the sprout ({state})" src="data:image/png;base64,{_b64(info["file"])}"/>'
    except FileNotFoundError:
        img = '<div style="font-size:90px;text-align:center">\U0001F331</div>'
    return _WIDGET % {
        "nonce": nonce, "w": width, "wsmall": int(width * 0.75), "state": state, "img": img,
        "msg": json.dumps(message, ensure_ascii=False).replace("</", "<\\/"),
        "chatter": json.dumps(chatter, ensure_ascii=False).replace("</", "<\\/"),
        "burst": "true" if burst else "false", "fs": font_size,
        "banner": colors["banner"], "border": colors["border"], "text": colors["text"], "head": colors["head"],
    }
