"""
Run once to generate assets/icon.png
Design: TV screen + WiFi waves on Roku purple background
"""
from PIL import Image, ImageDraw

SIZE = 512
BG_COLOR      = (108, 40, 217)   # Roku purple
WHITE         = (255, 255, 255)
SCREEN_COLOR  = (80, 20, 175)    # darker purple for TV screen fill

img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ── Rounded square background ──────────────────────────────────────────
draw.rounded_rectangle([0, 0, SIZE, SIZE], radius=90, fill=BG_COLOR)

# ── TV body ────────────────────────────────────────────────────────────
tv_x1, tv_y1 = 90,  230
tv_x2, tv_y2 = 422, 390
draw.rounded_rectangle([tv_x1, tv_y1, tv_x2, tv_y2], radius=18, fill=WHITE)

# TV screen (inner fill)
pad = 16
draw.rounded_rectangle(
    [tv_x1 + pad, tv_y1 + pad, tv_x2 - pad, tv_y2 - pad],
    radius=8, fill=SCREEN_COLOR
)

# TV stand — neck
neck_w = 18
neck_x1 = SIZE // 2 - neck_w // 2
draw.rectangle([neck_x1, tv_y2, neck_x1 + neck_w, tv_y2 + 28], fill=WHITE)

# TV stand — base
base_w = 100
draw.rounded_rectangle(
    [SIZE // 2 - base_w // 2, tv_y2 + 22,
     SIZE // 2 + base_w // 2, tv_y2 + 46],
    radius=8, fill=WHITE
)

# ── WiFi waves (3 arcs, centred above TV) ─────────────────────────────
cx    = SIZE // 2
top_y = 60          # top of the largest arc bounding box

for i, (r, alpha) in enumerate([(120, 255), (80, 200), (40, 150)]):
    opacity = alpha
    arc_color = WHITE + (opacity,)  # RGBA
    bbox = [cx - r, top_y + i * 40, cx + r, top_y + i * 40 + r * 1.1]
    draw.arc(bbox, start=200, end=340, fill=arc_color, width=14 - i * 3)

# ── WiFi dot ───────────────────────────────────────────────────────────
dot_r = 12
draw.ellipse([cx - dot_r, 195 - dot_r, cx + dot_r, 195 + dot_r], fill=WHITE)

img.save("assets/icon.png")
print("Saved assets/icon.png")
