"""turtle_art.py - Turtle graphics for ShopImpact.

Python's built-in `turtle` module opens a desktop window (it needs Tk), which
cannot run on a web server such as Streamlit Cloud. So this file implements a
tiny "SVG turtle" with the SAME ideas and commands as Python's turtle
(forward, left, right, penup, pendown, goto, circle, color, begin_fill ...).
Instead of drawing in a window, it records every move and renders an animated
SVG, so the drawing appears to be drawn stroke by stroke inside the web page.
"""
import json
import math


class SVGTurtle:
    def __init__(self, width=300, height=300):
        self.width, self.height = width, height
        self.x, self.y = 0.0, 0.0          # (0,0) is the canvas centre
        self.heading = 0.0                 # degrees, 0 = east, like turtle
        self.pen_down = True
        self.color = "#3F6B4F"
        self.pen_size = 4
        self._strokes = []                 # list of dicts: points, color, size
        self._current = None
        self._fills = []                   # list of dicts: points, color
        self._fill_points = None
        self._fill_color = None

    # ----- turtle-style commands -------------------------------------
    def pencolor(self, c):
        self.color = c
        self._current = None

    def width_(self, w):
        self.pen_size = w
        self._current = None

    def penup(self):
        self.pen_down = False
        self._current = None

    def pendown(self):
        self.pen_down = True

    def goto(self, x, y):
        self._move_to(x, y)

    def setheading(self, angle):
        self.heading = angle % 360

    def left(self, angle):
        self.heading = (self.heading + angle) % 360

    def right(self, angle):
        self.heading = (self.heading - angle) % 360

    def forward(self, dist):
        rad = math.radians(self.heading)
        self._move_to(self.x + dist * math.cos(rad), self.y + dist * math.sin(rad))

    def backward(self, dist):
        self.forward(-dist)

    def circle(self, radius, extent=360, steps=36):
        """Draw an arc like turtle.circle (positive radius turns left)."""
        step_angle = extent / steps
        step_len = 2 * abs(radius) * math.sin(math.radians(step_angle / 2))
        sign = 1 if radius >= 0 else -1
        self.left(sign * step_angle / 2)
        for _ in range(steps):
            self.forward(step_len)
            self.left(sign * step_angle)
        self.right(sign * step_angle / 2)

    def begin_fill(self, color):
        self._fill_points = [(self.x, self.y)]
        self._fill_color = color

    def end_fill(self):
        if self._fill_points and len(self._fill_points) > 2:
            self._fills.append({"points": self._fill_points, "color": self._fill_color})
        self._fill_points = None

    # ----- internals --------------------------------------------------
    def _move_to(self, x, y):
        if self.pen_down:
            if self._current is None:
                self._current = {"points": [(self.x, self.y)], "color": self.color, "size": self.pen_size}
                self._strokes.append(self._current)
            self._current["points"].append((x, y))
        if self._fill_points is not None:
            self._fill_points.append((x, y))
        self.x, self.y = x, y

    def _px(self, x, y):
        """Turtle coords (y up) to SVG coords (y down)."""
        return self.width / 2 + x, self.height / 2 - y

    def _path(self, points, close=False):
        coords = [self._px(*p) for p in points]
        d = "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in coords)
        return d + (" Z" if close else "")

    # ----- render -----------------------------------------------------
    def to_html(self, caption="", bg="transparent", speed=300, nonce=0):
        """Self-contained HTML page: the drawing is drawn stroke by stroke while a
        little turtle walks along the path. Tap the drawing to replay it."""
        parts, delay = [], 0.0
        timeline = []                                    # (delay, duration) per stroke
        for s in self._strokes:
            pts = s["points"]
            length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
            dur = max(0.12, length / speed)
            timeline.append((delay, dur))
            parts.append(
                f'<path d="{self._path(pts)}" fill="none" stroke="{s["color"]}" '
                f'stroke-width="{s["size"]}" stroke-linecap="round" stroke-linejoin="round" '
                f'pathLength="1" class="stroke" style="--d:{delay:.2f}s;--t:{dur:.2f}s"/>'
            )
            delay += dur + 0.04
        fills = "".join(                                 # fills fade in once the outline is finished
            f'<path d="{self._path(f["points"], True)}" fill="{f["color"]}" opacity="0" class="fill" '
            f'style="--d:{delay:.2f}s"/>' for f in self._fills)
        cap = f'<div class="cap">{caption}</div>' if caption else ""
        return f"""<!-- run {nonce} -->
<style>
 html,body{{margin:0;background:{bg};font-family:'Montserrat','Segoe UI',sans-serif;text-align:center;overflow:hidden}}
 svg{{max-width:100%;height:auto;cursor:pointer}}
 .play .stroke{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw var(--t) linear var(--d) forwards}}
 .play .fill{{animation:fade .9s ease var(--d) forwards}}
 .stroke{{stroke-dasharray:1;stroke-dashoffset:1}}
 @keyframes draw{{to{{stroke-dashoffset:0}}}}
 @keyframes fade{{to{{opacity:.6}}}}
 .cap{{font-size:14px;color:#2F5D3E;font-weight:700;padding-top:2px}}
 .replay{{font-size:12px;color:#6F9E7B;cursor:pointer;border:0;background:none;font-weight:600}}
</style>
<svg id="art" class="play" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
{fills}{''.join(parts)}
<g id="tt" opacity="0"><ellipse cx="0" cy="0" rx="11" ry="8" fill="#6F9E7B" stroke="#2F5D3E" stroke-width="2"/>
<circle cx="13" cy="0" r="5" fill="#8FBF98" stroke="#2F5D3E" stroke-width="2"/>
<circle cx="15" cy="-1.5" r="1" fill="#25352B"/>
<ellipse cx="-4" cy="-8" rx="3" ry="2" fill="#8FBF98"/><ellipse cx="-4" cy="8" rx="3" ry="2" fill="#8FBF98"/></g>
</svg>
{cap}<button class="replay" id="rp">\u21BB tap to replay</button>
<script>
 const TL = {json.dumps([[round(a, 3), round(b, 3)] for a, b in timeline])};
 const svg = document.getElementById('art'), tt = document.getElementById('tt');
 const strokes = Array.from(svg.querySelectorAll('.stroke'));
 const lens = strokes.map(p => p.getTotalLength());
 let raf = null;
 function walk(t0){{
   const t = (performance.now() - t0) / 1000;
   let shown = false;
   for (let i = 0; i < strokes.length; i++){{
     const [d, du] = TL[i];
     if (t >= d && t <= d + du){{
       const at = ((t - d) / du) * lens[i], p = strokes[i].getPointAtLength(at);
       const q = strokes[i].getPointAtLength(Math.min(lens[i], at + 1.5));
       const a = Math.atan2(q.y - p.y, q.x - p.x) * 180 / Math.PI;
       tt.setAttribute('transform', 'translate(' + p.x + ' ' + p.y + ') rotate(' + a + ')');
       tt.setAttribute('opacity', 1); shown = true; break;
     }}
   }}
   const end = TL.length ? TL[TL.length-1][0] + TL[TL.length-1][1] : 0;
   if (t < end + 0.2){{ raf = requestAnimationFrame(() => walk(t0)); }}
   else {{ tt.setAttribute('opacity', 0); }}
 }}
 function start(){{
   cancelAnimationFrame(raf); svg.classList.remove('play'); void svg.getBoundingClientRect();
   svg.classList.add('play'); tt.setAttribute('opacity', 0);
   if (strokes.length) walk(performance.now());
 }}
 svg.addEventListener('click', start); document.getElementById('rp').addEventListener('click', start);
 start();
</script>"""


# ---------------------------------------------------------------------------
# Eco drawings (each one is a short turtle program)
# ---------------------------------------------------------------------------
def _lens(t, base, tip, bulge, fill):
    """Draw a leaf-like lens from base to tip (two curved edges, filled)."""
    bx, by = base
    dx, dy = tip[0] - bx, tip[1] - by
    length = math.hypot(dx, dy)
    px, py = -dy / length, dx / length             # unit vector perpendicular to the axis
    n = 24
    t.penup(); t.goto(bx, by); t.pendown(); t.begin_fill(fill)
    for i in range(1, n + 1):                      # one edge, base -> tip
        s = i / n; off = bulge * math.sin(math.pi * s)
        t.goto(bx + dx * s + px * off, by + dy * s + py * off)
    for i in range(1, n + 1):                      # other edge, tip -> base
        s = 1 - i / n; off = -bulge * math.sin(math.pi * s)
        t.goto(bx + dx * s + px * off, by + dy * s + py * off)
    t.end_fill()


def _line(t, a, b):
    t.penup(); t.goto(*a); t.pendown(); t.goto(*b)


def draw_leaf(color="#5E9C6B", vein="#3F6B4F"):
    t = SVGTurtle(300, 280)
    base, tip = (-80, -95), (85, 105)
    t.pencolor(color); t.width_(5)
    _lens(t, base, tip, 62, "#BFE3C0")
    t.pencolor(vein); t.width_(3)
    _line(t, (base[0] - 18, base[1] - 18), tip)    # stem + centre vein
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    for s in (0.3, 0.5, 0.7):                      # side veins
        cx, cy = base[0] + dx * s, base[1] + dy * s
        _line(t, (cx, cy), (cx - 38, cy + 30))
        _line(t, (cx, cy), (cx + 38, cy - 30))
    return t


def draw_footprint(color="#5E9C6B"):
    """A foot (sole + five toes), drawn with ovals."""
    t = SVGTurtle(260, 300)
    t.pencolor(color); t.width_(5)

    def oval(cx, cy, rx, ry, fill):
        pts = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
               for a in range(0, 361, 15)]
        t.penup(); t.goto(*pts[0]); t.pendown(); t.begin_fill(fill)
        for p in pts[1:]:
            t.goto(*p)
        t.end_fill()

    oval(0, -40, 52, 92, "#BFE3C0")                 # sole
    for cx, cy, r in ((-38, 52, 15), (-16, 72, 14), (8, 79, 13), (30, 74, 12), (48, 60, 11)):
        oval(cx, cy, r, r, "#BFE3C0")                # five toes
    return t


def draw_badge(color="#E3A857", ribbon="#E3B7A0"):
    """A medal: two ribbon tails, a circle and a five-point star."""
    t = SVGTurtle(260, 300)
    t.width_(4); t.pencolor(ribbon)
    for sx in (-1, 1):                               # ribbon tails (behind the medal)
        pts = [(sx * 50, -20), (sx * 12, -45), (sx * 8, -125), (sx * 30, -103), (sx * 52, -125)]
        t.penup(); t.goto(*pts[0]); t.pendown(); t.begin_fill("#F2CFC0")
        for p in pts[1:] + [pts[0]]:
            t.goto(*p)
        t.end_fill()
    t.pencolor(color); t.width_(6)
    t.penup(); t.goto(0, -45); t.setheading(0); t.pendown()
    t.begin_fill("#F6E3B4"); t.circle(75, 360, 48); t.end_fill()   # the medal
    t.pencolor("#3F6B4F"); t.width_(4)                # five-point star, turtle style
    t.penup(); t.goto(-36, 55 - 38); t.setheading(0); t.pendown()
    t.begin_fill("#BFE3C0")
    for _ in range(5):
        t.forward(72); t.right(144)
    t.end_fill()
    return t


def draw_sprout(color="#5E9C6B"):
    """A seedling in a pot (shown before the first purchase is logged)."""
    t = SVGTurtle(260, 300)
    t.pencolor("#C9A27A"); t.width_(5)
    pot = [(-55, -50), (55, -50), (42, -125), (-42, -125)]
    t.penup(); t.goto(*pot[0]); t.pendown(); t.begin_fill("#EFE4C8")
    for p in pot[1:] + [pot[0]]:
        t.goto(*p)
    t.end_fill()
    _line(t, (-62, -50), (62, -50))                  # pot rim
    t.pencolor(color); t.width_(6)
    _line(t, (0, -50), (0, 50))                      # stem
    t.width_(4)
    _lens(t, (0, 5), (-85, 70), 26, "#BFE3C0")       # left leaf
    _lens(t, (0, 30), (88, 100), 28, "#BFE3C0")      # right leaf
    return t


def draw_footprint_status(status):
    """Footprint coloured by monthly status: green / amber / red (soft pastel)."""
    colors = {"green": "#5E9C6B", "amber": "#E3A857", "red": "#D98C7A"}
    return draw_footprint(colors.get(status, colors["green"]))
