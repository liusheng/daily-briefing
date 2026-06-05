#!/usr/bin/env python3
"""Generate a styled cover image for daily briefing / WeChat Official Account.

Usage:
    python generate-cover.py [--date DATE] [--headlines "h1|h2|h3|h4|h5"] [--output PATH]

Defaults:
    --date     : today in YYYY-MM-DD format
    --headlines: fallback headlines if none provided
    --output   : ./daily_cover_<date>.png

Produces a 1200×630 PNG (WeChat recommended cover size) with:
- Dark navy gradient background
- "监听站1379" title + date
- "DAILY BRIEFING" tagline top-left
- Up to 5 headlines with bullet dots
- Decorative dots + accent bars
- Clean bottom (no data source footer, no branding)

Dependencies: Pillow (PIL), Noto Sans CJK + DejaVu fonts
"""

from PIL import Image, ImageDraw, ImageFont
import argparse, os, random, datetime, sys

# ── Colour palette ──
BG_TOP     = (13, 20, 38)
BG_BOT     = (28, 38, 55)
ACCENT     = (59, 130, 246)
ACCENT2    = (139, 92, 246)
WHITE      = (248, 250, 252)
GRAY       = (156, 163, 175)
SUBTLE     = (107, 114, 128)
DARK_LINE  = (71, 85, 105)

W, H = 1200, 630

# ── Font paths ──
FONT_BOLD_CN = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG_CN  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD_EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def make_cover(date_str: str, headlines: list[str], output_path: str):
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)

    # ── Gradient fill ──
    for y in range(H):
        ratio = y / H
        r = int(BG_TOP[0] * (1-ratio) + BG_BOT[0] * ratio)
        g = int(BG_TOP[1] * (1-ratio) + BG_BOT[1] * ratio)
        b = int(BG_TOP[2] * (1-ratio) + BG_BOT[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Fonts ──
    f_en_big    = ImageFont.truetype(FONT_BOLD_EN, 120)
    f_title     = ImageFont.truetype(FONT_BOLD_CN, 58)
    f_sub       = ImageFont.truetype(FONT_REG_CN,  22)
    f_date      = ImageFont.truetype(FONT_REG_CN,  20)
    f_headline  = ImageFont.truetype(FONT_REG_CN,  22)

    # ── Decorative elements ──
    draw.ellipse([W-160, -50, W-60, 50], fill=(59, 130, 246, 25))
    draw.ellipse([W-120, -20, W-20, 30], fill=(139, 92, 246, 18))

    # ── Left accent bar ──
    draw.rectangle([40, 95, 43, 530], fill=ACCENT)

    # ── Tagline ──
    draw.text((60, 95), "DAILY BRIEFING", fill=ACCENT, font=f_sub)

    # ── Title ──
    draw.text((60, 145), "监听站1379", fill=WHITE, font=f_title)

    # ── Date ──
    draw.text((60, 222), date_str, fill=GRAY, font=f_date)

    # ── Separator ──
    draw.line([(60, 268), (550, 268)], fill=DARK_LINE, width=1)

    # ── Headlines (up to 5) ──
    y_start = 298
    for i, text in enumerate(headlines[:5]):
        y = y_start + i * 45
        draw.ellipse([58, y+8, 66, y+16], fill=ACCENT)
        draw.text((78, y+4), text, fill=WHITE, font=f_headline)

    # ── AI watermark ──
    draw.text((820, 100), "AI", fill=(59, 130, 246, 10), font=f_en_big)

    # ── Decorative dots ──
    random.seed(42)
    for _ in range(40):
        x = random.randint(820, 1150)
        y = random.randint(90, 550)
        r = random.randint(2, 5)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(139, 92, 246, 10))

    # ── Save ──
    img.save(output_path, "PNG")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate daily briefing cover image")
    parser.add_argument("--date",
                        default=datetime.date.today().strftime("%Y.%m.%d · %A"),
                        help="Date string (e.g. '2026年5月29日 · 星期五')")
    parser.add_argument("--headlines", default="",
                        help="Pipe-separated headlines: 'h1|h2|h3|h4|h5'")
    parser.add_argument("--output", default="",
                        help="Output PNG path")
    args = parser.parse_args()

    headlines = args.headlines.split("|") if args.headlines else [
        "Claude Opus 4.8 发布 · Anthropic 融资 650 亿",
        "OpenClaw 37.5 万星标，开源 AI 持续升温",
        "AI Agent 授权疲劳成 UX 设计新命题",
        "GPU 实时推理达 3,000 tok/s，效率突破",
        "n8n 持续增长，低代码+AI 融合加速",
    ]

    out = args.output or f"daily_cover_{datetime.date.today().isoformat()}.png"
    path = make_cover(args.date, headlines, out)
    print(f"Cover saved: {path}")
