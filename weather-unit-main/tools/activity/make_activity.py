"""야외 활동 = 동작 그림 3~4장을 넘기는 짧은 애니메이션 (M32).
동업자 10-14: 「캐릭터 움직임은 부자연스러워서 … 수영이면 수영하는듯한 동작 이미지4개정도 연결해서 1초지나면 넘어가는식」 → 방식 B.

  py make_activity.py <활동 key> [--hold 0.8] [--fade 0.15]
     입력 = ../활동_원본/<key>.png  : 2×2 칸(흰 테두리로 나뉜 정사각 장면 4개, 왼위→오위→왼아래→오아래 = 1→4번 동작)
     출력 = ../활동_20261014/activity_<key>_340.mp4 · .gif · _poster.png · _frame1~4.png

칸 나누기: 흰 테두리(밝은 가로·세로 줄)를 찾아 4칸으로 자르고, 칸마다 흰 여백을 잘라 정사각형 340으로 맞춘다.
넘기기: 칸마다 hold초 보여 주고 fade초 동안 다음 칸과 겹침(덜 끊겨 보이게). 마지막→첫 칸도 겹쳐 끊김 없이 반복.
ffmpeg: -t 는 -i 앞 (10-14 메모리 사고).
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "활동_원본"
OUT = HERE.parent / "활동_20261014"


def bright_lines(a, axis):
    """흰 테두리 줄: 그 줄의 거의 모든 픽셀이 밝음."""
    light = (a.min(2) > 235)
    return light.mean(axis=axis) > 0.97


def split_2x2(im):
    a = np.asarray(im.convert("RGB")).astype(int)
    h, w, _ = a.shape
    rows, cols = bright_lines(a, 1), bright_lines(a, 0)

    def cut(flags, n):
        """가운데 근처(±20%)의 흰 줄 묶음 한가운데를 경계로."""
        c, r = n // 2, n // 5
        idx = [i for i in range(c - r, c + r) if flags[i]]
        if not idx:
            return c
        return (idx[0] + idx[-1]) // 2
    ym, xm = cut(rows, h), cut(cols, w)
    panels = []
    for (y0, y1) in ((0, ym), (ym, h)):
        for (x0, x1) in ((0, xm), (xm, w)):
            p = im.crop((x0, y0, x1, y1)).convert("RGB")
            pa = np.asarray(p).astype(int)
            fr, fc = ~bright_lines(pa, 1), ~bright_lines(pa, 0)   # 흰 테두리가 아닌 줄
            ys, xs = np.nonzero(fr)[0], np.nonzero(fc)[0]
            p = p.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
            s = min(p.size)                                      # 가운데 정사각형
            l, t = (p.width - s) // 2, (p.height - s) // 2
            panels.append(p.crop((l, t, l + s, t + s)).resize((340, 340), Image.LANCZOS))
    return panels


def soften_below(img, start):
    """start(0~1) 아래를 흐리게 + 물 색으로 덮기 — 물에 거꾸로 비친 얼굴·팔 지우기 (수영, 10-14 동업자
    「물속에 팔 비친게 조금 부자연스러운데」 · Gemini에 고쳐 달라 해도 같게 나옴). 경계는 24px에 걸쳐 서서히."""
    from PIL import ImageFilter
    w, h = img.size
    y0 = int(h * start)
    region = img.crop((0, y0, w, h))
    a = np.asarray(region).reshape(-1, 3)
    water = tuple(int(v) for v in np.median(a, axis=0))           # 그 구역의 대표 물 색
    blur = region.filter(ImageFilter.GaussianBlur(10))
    tinted = Image.blend(blur, Image.new("RGB", region.size, water), 0.55)
    # 잔물결 몇 줄 (밝은 가로 곡선) — 너무 밋밋하지 않게
    from PIL import ImageDraw
    d = ImageDraw.Draw(tinted)
    for i, yy in enumerate(range(10, region.height, 22)):
        x0 = (i * 37) % 60
        d.arc((x0, yy, x0 + w * 0.55, yy + 10), 200, 340, fill=(235, 250, 255), width=2)
        d.arc((w * 0.45 - x0 / 2, yy + 8, w * 0.95, yy + 18), 200, 340, fill=(235, 250, 255), width=2)
    mask = Image.new("L", region.size, 255)
    md = ImageDraw.Draw(mask)
    for i in range(24):
        md.line((0, i, w, i), fill=int(255 * i / 24))
    out = img.copy()
    out.paste(tinted, (0, y0), mask)
    return out


def unmark(img, cx=0.883, cy=0.883, r=0.034):
    """Gemini 그림의 반짝이 로고(✦) 지우기 — 나누기 전 「전체 그림」에 한다.
    10-15: 로고는 그림마다 늘 같은 자리(1024 그림에서 오른쪽 아래 모서리로부터 120px 안쪽 = (904, 904), 지름 약 50px).
    전에는 4번째 칸 안에서 「밝은 곳」을 찾아 지웠는데, 장갑 · 길 테두리 · 물보라 · 꽃잎 배경을 로고로 착각해 얼룩이 생겼다
    → 정해진 자리의 작은 원 안에서, 주변(71px)보다 밝은 점만 주변 값으로 덮는다(어두운 선은 그대로)."""
    from PIL import ImageFilter
    w, h = img.size
    X, Y, rr = int(w * cx), int(h * cy), int(w * r)
    x0, y0, x1, y1 = X - rr - 40, Y - rr - 40, X + rr + 40, Y + rr + 40
    a = np.asarray(img.convert("RGB")).astype(int).copy()
    piece = img.convert("RGB").crop((x0, y0, x1, y1))
    reg = a[y0:y1, x0:x1]
    local = np.asarray(piece.filter(ImageFilter.MedianFilter(71))).astype(int)   # 로고(약 50px)보다 넓어야 로고 밝기가 안 섞임
    yy, xx = np.mgrid[y0:y1, x0:x1]
    near = (yy - Y) ** 2 + (xx - X) ** 2 <= rr ** 2
    bright = (reg.sum(2) - local.sum(2) > 8) & near
    m = Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
    bright = (np.asarray(m) > 0) & near
    reg[bright] = local[bright]
    a[y0:y1, x0:x1] = reg
    return Image.fromarray(a.astype(np.uint8))


def build(key, hold=0.8, fade=0.15, soften=None, use=None, colors=160):
    OUT.mkdir(exist_ok=True)
    frames = split_2x2(unmark(Image.open(RAW / f"{key}.png")))   # 로고 지우기는 나누기 전 전체 그림에서
    if use:   # 예: [1, 2] = 배경이 같은 칸만 골라 쓰기 (장마: 아래 2칸 배경이 달라 깜빡임)
        frames = [frames[i - 1] for i in use]
        for f in OUT.glob(f"activity_{key}_frame*.png"):
            f.unlink()
    if soften:
        frames = [soften_below(f, soften) for f in frames]
    for i, f in enumerate(frames, 1):
        f.save(OUT / f"activity_{key}_frame{i}.png")
    frames[0].save(OUT / f"activity_{key}_340_poster.png")
    ff = shutil.which("ffmpeg") or sys.exit("ffmpeg 없음")
    n, seg = len(frames), hold + fade
    total = round(n * hold, 2)
    # 입력: 칸마다 (hold+fade)초, 마지막 뒤에 첫 칸을 한 번 더 붙여 반복 이음새도 겹침
    seq = frames + [frames[0]]
    args = [ff, "-y", "-loglevel", "error"]
    for i in range(len(seq)):
        args += ["-loop", "1", "-t", f"{seg:.3f}", "-i", str(OUT / f"activity_{key}_frame{(i % n) + 1}.png")]
    chain, last = [], "[0:v]"
    for i in range(1, len(seq)):
        out = f"[x{i}]"
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={i * hold:.3f}{out}")
        last = out
    # 첫 fade 구간을 건너뛰고 n*hold 초만 → 끝과 처음이 같은 장면이라 끊김 없이 반복
    chain.append(f"{last}trim=start={fade / 2:.3f}:duration={total},setpts=PTS-STARTPTS,fps=15,format=yuv420p[v]")
    tmp = OUT / f"activity_{key}_340.mp4"
    subprocess.run(args + ["-filter_complex", ";".join(chain), "-map", "[v]", "-c:v", "libx264", "-crf", "22",
                           "-movflags", "+faststart", str(tmp)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(tmp), "-filter_complex",
                    f"fps=12,split[a][b];[a]palettegen=max_colors={colors}[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
                    "-loop", "0", str(OUT / f"activity_{key}_340.gif")], check=True)
    print(f"완료 {key}: {n}장 × {hold}s (겹침 {fade}s) = {total}s 반복")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    hold = float(a[a.index("--hold") + 1]) if "--hold" in a else 0.8
    fade = float(a[a.index("--fade") + 1]) if "--fade" in a else 0.15
    soften = float(a[a.index("--soften") + 1]) if "--soften" in a else None   # 예: 0.76 = 아래 24% 흐리게
    use = [int(x) for x in a[a.index("--use") + 1].split(",")] if "--use" in a else None   # 예: --use 1,2
    colors = int(a[a.index("--colors") + 1]) if "--colors" in a else 160   # GIF 400KB 넘으면 128 (10-15)
    build(a[0], hold, fade, soften, use, colors)
