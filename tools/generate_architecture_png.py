"""Generate architecture PNGs (light/dark, thumbnail) without external graph libs.

Usage:
    python tools/generate_architecture_png.py \
            --theme light \
            --outfile dist/architecture.png \
            --title "AI Chatbot Architecture" \
            --thumbnail 320 \
            --show-version

Options:
    --theme light|dark (default: light)
    --thumbnail <max-width>  Generate additional scaled copy (e.g. 320)
    --show-version           Append version + UTC timestamp in title bar
    --outfile <path>         Output PNG (default dist/architecture.png)
    --title <text>           Custom title

Environment overrides:
    PROJECT_VERSION  Used when --show-version (fallback 0.0.0 if absent)
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import os
import argparse
import datetime

WIDTH, HEIGHT = 1600, 1000

THEMES = {
    "light": {
        "BG": (250, 252, 255),
        "BOX": (255, 255, 255),
        "BOX_BORDER": (60, 120, 200),
        "TEXT": (25, 40, 55),
        "ACCENT": (90, 160, 250),
    },
    "dark": {
        "BG": (18, 22, 28),
        "BOX": (32, 40, 52),
        "BOX_BORDER": (90, 150, 255),
        "TEXT": (232, 240, 248),
        "ACCENT": (135, 180, 255),
    },
}
FONT_STACK = ["Segoe UI", "Arial", "DejaVuSans", "LiberationSans"]

# Try to locate a font
font_cache = {}

def get_font(size: int):
    if size in font_cache:
        return font_cache[size]
    for name in FONT_STACK:
        try:
            f = ImageFont.truetype(name + ".ttf", size)
            font_cache[size] = f
            return f
        except Exception:
            continue
    font_cache[size] = ImageFont.load_default()
    return font_cache[size]

def build_canvas(theme: str):
    palette = THEMES[theme]
    base = Image.new("RGB", (WIDTH, HEIGHT), palette["BG"])
    return base, ImageDraw.Draw(base), palette

def _rounded_rect(draw_obj, xy, radius, outline, width, fill):
    try:
        draw_obj.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    except AttributeError:
        # Fallback: draw filled rounded rectangle manually
        x1, y1, x2, y2 = xy
        r = radius
        # center rects
        draw_obj.rectangle([x1+r, y1, x2-r, y2], fill=fill)
        draw_obj.rectangle([x1, y1+r, x2, y2-r], fill=fill)
        # corner circles
        for cx, cy in [(x1+r, y1+r), (x2-r, y1+r), (x1+r, y2-r), (x2-r, y2-r)]:
            draw_obj.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)
        # border (simple rectangle outline)
        draw_obj.rectangle([x1, y1, x2, y2], outline=outline)

def boxed(draw, palette, x, y, w, h, title, body=None):
    _rounded_rect(draw, [x, y, x+w, y+h], radius=18, fill=palette["BOX"], outline=palette["BOX_BORDER"], width=3)
    title_font = get_font(30)
    draw.text((x+14, y+10), title, font=title_font, fill=palette["TEXT"])
    if body:
        body_font = get_font(18)
        max_width = w - 28
        offset_y = y + 55
        for para in body.split("\n"):
            if not para.strip():
                offset_y += 8
                continue
            for line in textwrap.wrap(para, width= int(max_width/9.5)):
                draw.text((x+14, offset_y), line, font=body_font, fill=palette["TEXT"])
                offset_y += 22

def connector(draw, palette, ax, ay, bx, by, label=None):
    draw.line([ax, ay, bx, by], fill=palette["ACCENT"], width=4)
    if label:
        font = get_font(16)
        draw.text(((ax+bx)/2 + 6, (ay+by)/2 - 10), label, font=font, fill=palette["ACCENT"])

def render(theme: str, title: str, show_version: bool):
    img, draw, palette = build_canvas(theme)
    # Layout drawing
    boxed(draw, palette, 60, 40, 240, 140, "User", "Chat / Upload / Voice Input")
    boxed(draw, palette, 350, 40, 300, 180, "Streamlit UI", "Sidebar controls\nChat messages\nVoice & cache display")
    boxed(draw, palette, 700, 40, 360, 200, "Mode Manager", "auto / online / offline\nConnectivity tests\nFail streak degrade")
    boxed(draw, palette, 1100, 40, 420, 200, "Diagnostics", "Connectivity variants\nError classification\nLogs tail & actions")

    boxed(draw, palette, 120, 300, 320, 210, "Document Processing", "PDF/TXT detect\nChunk split (1000/200)\nFallback simple search")
    boxed(draw, palette, 520, 300, 320, 210, "Embeddings & Vector Store", "Sentence Transformers\nFAISS index\nRetriever (k=3)")
    boxed(draw, palette, 920, 300, 320, 210, "Retrieval & Prompt Build", "Relevant chunks merged\nAugment user prompt")
    boxed(draw, palette, 1280, 300, 260, 210, "Response Cache", "MD5 hash keyed\nInstant repeat answers")

    boxed(draw, palette, 200, 600, 300, 190, "Provider Chain", "Primary provider\nFallback rotation\nOfflineBot last")
    boxed(draw, palette, 560, 600, 260, 190, "Groq", "LLaMA / Mixtral\nFast inference")
    boxed(draw, palette, 870, 600, 260, 190, "Gemini", "Reasoning / multimodal")
    boxed(draw, palette, 1180, 600, 260, 190, "HuggingFace", "Open models repo\nDialoGPT etc.")

    connector(draw, palette, 300, 110, 350, 110)
    connector(draw, palette, 650, 110, 700, 110)
    connector(draw, palette, 1060, 110, 1100, 110)
    connector(draw, palette, 500, 130, 500, 300, "Uploads")
    connector(draw, palette, 820, 240, 820, 600, "Mode impact")
    connector(draw, palette, 440, 405, 520, 405, "Chunks")
    connector(draw, palette, 840, 405, 920, 405, "Top-k")
    connector(draw, palette, 1240, 405, 1280, 405, "Answer reuse")
    connector(draw, palette, 1080, 510, 1080, 600, "Prompt")
    connector(draw, palette, 350, 695, 560, 695, "Attempt 1")
    connector(draw, palette, 820, 695, 870, 695, "Fallback 2")
    connector(draw, palette, 1130, 695, 1180, 695, "Fallback 3")
    connector(draw, palette, 1410, 600, 1410, 510, "Response")
    connector(draw, palette, 1410, 510, 1410, 405)
    connector(draw, palette, 1410, 405, 1410, 240)
    connector(draw, palette, 1410, 240, 900, 240)
    connector(draw, palette, 900, 240, 900, 140, "Display")

    # Title + optional version stamp
    title_font = get_font(46)
    stamp = ""
    if show_version:
        version = os.getenv("PROJECT_VERSION", "0.0.0")
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        # Use ASCII hyphen instead of bullet to avoid font encoding issues
        stamp = f"  - v{version}  {ts}"
    draw.text((60, 955), f"{title}{stamp}", font=title_font, fill=palette["TEXT"])
    return img

def scale_image(img, max_width):
    if not max_width or img.width <= max_width:
        return img
    ratio = max_width / img.width
    new_size = (int(img.width * ratio), int(img.height * ratio))
    return img.resize(new_size, Image.LANCZOS)

def parse_args():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--theme", choices=list(THEMES.keys()), default="light")
    p.add_argument("--outfile", default="dist/architecture.png")
    p.add_argument("--thumbnail", type=int, default=None, help="Generate thumbnail with given max width")
    p.add_argument("--title", default="AI Chatbot Architecture")
    p.add_argument("--show-version", action="store_true")
    return p.parse_args()

def main():
    args = parse_args()
    outpath = Path(args.outfile)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    img = render(args.theme, args.title, args.show_version)
    img.save(outpath)
    print(f"✅ Wrote {outpath}")
    if args.thumbnail:
        thumb = scale_image(img, args.thumbnail)
        thumb_path = outpath.parent / (outpath.stem + f"_thumb{args.thumbnail}.png")
        thumb.save(thumb_path)
        print(f"✅ Wrote {thumb_path}")

if __name__ == "__main__":
    main()
