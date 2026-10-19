"""착장 세트 36벌을 한 장으로 (성별·계절 줄) → ../착장세트_20261014/착장세트_한눈에보기.png"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
m = json.loads((HERE / "outfit_visual_map.json").read_text(encoding="utf-8"))
S = 150
rows = [(g, s) for g in "FM" for s in ("spring", "summer", "autumn", "winter")]
KO = {"F": "여", "M": "남", "spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
cols = max(sum(1 for v in m["sets"].values() if v["gender"] == g and v["season"] == s) for g, s in rows)
W, LW = 80 + cols * (S + 8), 80
img = Image.new("RGB", (W, len(rows) * (S + 30) + 10), "white")
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("malgun.ttf", 14)
    small = ImageFont.truetype("malgun.ttf", 11)
except OSError:
    font = small = ImageFont.load_default()
for r, (g, s) in enumerate(rows):
    y = 10 + r * (S + 30)
    d.text((8, y + S // 2 - 8), f"{KO[g]} {KO[s]}", fill="#333", font=font)
    sets = [v for v in m["sets"].values() if v["gender"] == g and v["season"] == s]
    for c, v in enumerate(sets):
        x = LW + c * (S + 8)
        img.paste(Image.open(HERE / v["poster"]).convert("RGB").resize((S, S)), (x, y))
        d.text((x, y + S + 2), v["label"].split("· ", 2)[-1][:14], fill="#555", font=small)
out = HERE.parent / "착장세트_20261014" / "착장세트_한눈에보기.png"
img.save(out)
print(out, img.size)
