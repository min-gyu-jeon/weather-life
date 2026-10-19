"""착장 세트 그림(Gemini) → 배경 제거 · 340 카드 · MP4 · GIF → 연결표 다시 만들기.

  py make_outfit_sets.py --prompts   ../착장세트_원본/착장세트_요청문.md 를 세트 목록(outfit_sets.py)에서 새로 만든다
  py make_outfit_sets.py             ../착장세트_원본/ 의 그림을 처리
       sheet_<f|m>_<season>.png = 한 장에 여러 명 → 윗줄 왼→오, 다음 줄 왼→오 순서로 잘라 요청문 순서대로 붙인다
       <세트 key>.png           = 한 벌씩 따로 만든 그림 (sheet보다 우선)
  출력 = ../착장세트_20261014/ (<key>_source.png 투명 · outfit_<key>_340_poster.png · .mp4 · .gif) → build_map.py 자동 실행

흰 배경 제거 = 그림 가장자리에서 이어진 흰색만 지운다(흰 티셔츠는 남음).
"""
import shutil, subprocess, sys
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
RAW = WORK / "착장세트_원본"
OUT = WORK / "착장세트_20261014"
FINAL = WORK / "최종_4계절_추천복장_20261013"
MALE_BASE = WORK / "남성캐릭터_기본_20261014" / "male_base_source.png"
sys.path.insert(0, str(HERE))
from outfit_sets import SETS, SEASON_KO, OCC_KO, new_sets  # noqa: E402


def cutout(im):
    a = np.asarray(im.convert("RGB")).astype(int)
    light = (a.min(2) > 225) & (a.max(2) - a.min(2) < 18)
    h, w = light.shape
    bg = np.zeros((h, w), bool)
    q = deque((y, x) for x in range(w) for y in (0, h - 1) if light[y, x])
    q.extend((y, x) for y in range(h) for x in (0, w - 1) if light[y, x])
    for y, x in q: bg[y, x] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    alpha = np.minimum(alpha, np.asarray(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8))))
    return Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA"), bg


def split_sheet(path, n):
    """한 장에 여러 명 → 사람마다 잘라 낸다. 줄(가로 띠) → 줄 안의 사람(세로 띠) 순서."""
    cut, bg = cutout(Image.open(path))
    fg = ~bg
    people = []
    rows = fg.any(1)
    y = 0
    while y < len(rows):
        if not rows[y]: y += 1; continue
        y0 = y
        while y < len(rows) and rows[y:y + 8].any(): y += 1
        if y - y0 < 80: continue
        cols = fg[y0:y].any(0)
        x = 0
        while x < len(cols):
            if not cols[x]: x += 1; continue
            x0 = x
            while x < len(cols) and cols[x:x + 8].any(): x += 1
            if x - x0 > 40:
                c = cut.crop((x0, y0, x, y))
                people.append(c.crop(c.getbbox()))
    if len(people) == n:
        return people
    print(f"{path.name}: 빈 줄로는 {len(people)}명만 찾음 → 칸 나누기로 다시 자름")
    return split_grid(cut, fg, n)


def keep_main(c):
    """잘린 칸에서 가장 큰 덩어리(그 사람)만 남기고, 옆사람 머리 조각 같은 작은 덩어리는 지운다."""
    a = np.asarray(c).copy()
    fg = a[..., 3] > 0
    h, w = fg.shape
    lab = np.zeros((h, w), np.int32)
    sizes, cur = [0], 0
    for sy in range(0, h, 2):
        for sx in range(0, w, 2):
            if not fg[sy, sx] or lab[sy, sx]: continue
            cur += 1; n = 0; q = deque([(sy, sx)]); lab[sy, sx] = cur
            while q:
                y, x = q.popleft(); n += 1
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < h and 0 <= nx < w and fg[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = cur; q.append((ny, nx))
            sizes.append(n)
    if cur <= 1:
        return c
    big = int(np.argmax(sizes))
    a[..., 3] = np.where(lab == big, a[..., 3], 0)
    out = Image.fromarray(a, "RGBA")
    return out.crop(out.getbbox())


def split_grid(cut, fg, n):
    """요청문대로의 배치(4명 이하 = 1줄, 그 이상 = 2줄 · 윗줄이 1명 더 많거나 같음)에서
    예상 경계 근처의 가장 비어 있는 선으로 자른다."""
    rows = [n] if n <= 4 else [(n + 1) // 2, n // 2]
    ys, xs = np.nonzero(fg)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1

    def cut_at(proj, lo, hi, k):
        """proj[lo:hi] 를 k칸으로: 각 예상 경계 ±12% 안에서 값이 가장 작은 곳."""
        out, span = [lo], hi - lo
        for i in range(1, k):
            c = lo + span * i // k
            r = max(4, span * 12 // 100)
            seg = proj[c - r:c + r]
            out.append(c - r + int(np.argmin(seg)))
        return out + [hi]

    yb = cut_at(fg.sum(1), y0, y1, len(rows))
    people = []
    for (ya, yb_), k in zip(zip(yb, yb[1:]), rows):
        band = fg[ya:yb_]
        bx = np.nonzero(band.any(0))[0]
        xb = cut_at(band.sum(0), bx.min(), bx.max() + 1, k)
        for xa, xb_ in zip(xb, xb[1:]):
            people.append(keep_main(cut.crop((xa, ya, xb_, yb_))))
    return people


def poster(src, season, H=310):
    bgim = Image.open(FINAL / f"{season}_bg.png").convert("RGBA").resize((340, 340))
    c = src.crop(src.getbbox())
    k = H / c.height
    c = c.resize((max(1, round(c.width * k)), H), Image.LANCZOS)
    bgim.alpha_composite(c, ((340 - c.width) // 2, (340 - H) // 2))
    return bgim.convert("RGB")


def video(png, mp4, gif):
    ff = shutil.which("ffmpeg") or sys.exit("ffmpeg 없음")
    # -t 는 -i 앞(입력 길이): 뒤에 두면 GIF 팔레트 단계가 끝없는 입력을 모아 메모리 부족 (10-14 VS Code까지 꺼짐)
    subprocess.run([ff, "-y", "-loglevel", "error", "-loop", "1", "-t", "3", "-i", str(png), "-r", "15", "-frames:v", "45",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart", str(mp4)], check=True)
    subprocess.run([ff, "-y", "-loglevel", "error", "-loop", "1", "-t", "3", "-i", str(png), "-filter_complex",
                    "fps=15,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
                    "-loop", "0", str(gif)], check=True)


ATTACH = {("F", s): FINAL / f"{s}_source.png" for s in SEASON_KO}
ATTACH.update({("M", s): MALE_BASE for s in SEASON_KO})
# 겨울 원본은 햄스터 모자로 머리 윗부분이 가려짐 → 모자 없는 하프코트 그림(M28)을 첨부
ATTACH[("F", "winter")] = WORK / "추가착장_4계절_20261014" / "winter_halfcoat_source.png"


def write_prompts():
    RAW.mkdir(exist_ok=True)
    L = ["# 착장 세트 — Gemini 요청문 (자동 생성: `py make_outfit_sets.py --prompts`)", "",
         "**방법**: 아래 묶음마다 Gemini **새 대화** → 「첨부」 그림 1장 첨부 → 글 붙여넣기 → 결과를 「저장 이름」으로 이 폴더(`06_제작작업\\착장세트_원본\\`)에 저장.",
         "사람끼리 붙어 나오거나 수가 모자라면, 그 세트만 「한 벌씩」 글로 다시 만들어 `<세트 이름>.png`로 저장하면 된다.",
         "다 넣으면 Claude가 `py make_outfit_sets.py` 로 처리한다.", ""]
    n = 0
    for g in "FM":
        for s in SEASON_KO:
            todo = new_sets(g, s)
            if not todo: continue
            n += 1
            who = "girl" if g == "F" else "boy"
            rows = "in one row" if len(todo) <= 4 else f"in 2 rows ({(len(todo) + 1) // 2} on the top row, {len(todo) // 2} on the bottom row)"
            L += [f"## {n}. {'여' if g == 'F' else '남'} · {SEASON_KO[s]} {len(todo)}벌", "",
                  f"- 첨부: `{ATTACH[(g, s)].relative_to(WORK)}`", f"- 저장 이름: **`sheet_{g.lower()}_{s}.png`**", "",
                  "```",
                  f"Using the attached {who} as the exact character, draw a character sheet: the SAME {who} {len(todo)} times {rows}, "
                  "each one standing separately with clear white space between them (they must not touch or overlap). "
                  f"Keep EXACTLY the same face, eyes, blush, smile, hair style and hair colour, body, proportions, front-facing pose with arms slightly out, "
                  "line art and pastel colouring as the attachment. All the same size, whole body from hair to shoes visible. "
                  "Plain white background. No text, no labels, no logo, no hat, no bag. Modest, everyday clothes.",
                  "",
                  "Outfits, in this order (left to right" + (", top row first" if len(todo) > 4 else "") + "):"]
            L += [f"{i}. {t['draw']}" for i, t in enumerate(todo, 1)]
            L += ["```", "", "| 순서 | 세트 이름(한 벌씩 만들 때 저장 이름) | 내용 |", "|---|---|---|"]
            L += [f"| {i} | `{t['key']}.png` | {OCC_KO[t['occ']]} · {t['label']} |" for i, t in enumerate(todo, 1)]
            L += ["", "<details><summary>한 벌씩 만들 때 글</summary>", "", "```",
                  "Edit this exact image. Change ONLY the clothes and shoes. Keep EXACTLY the same face, eyes, blush, smile, hair, body, pose, "
                  "proportions, line art and colouring. No logo, no text, no hat, no bag. Plain white background. Whole body visible.",
                  "New clothes: <위 목록의 한 줄>", "```", "</details>", ""]
    (RAW / "착장세트_요청문.md").write_text("\n".join(L), encoding="utf-8")
    print(f"요청문 {n}묶음 → {RAW / '착장세트_요청문.md'}")
    write_prompt_page()


def prompt_text(g, s, todo):
    who = "girl" if g == "F" else "boy"
    rows = "in one row" if len(todo) <= 4 else f"in 2 rows ({(len(todo) + 1) // 2} on the top row, {len(todo) // 2} on the bottom row)"
    head = (f"Using the attached {who} as the exact character, draw a character sheet: the SAME {who} {len(todo)} times {rows}, "
            "each one standing separately with clear white space between them (they must not touch or overlap). "
            "Keep EXACTLY the same face, eyes, blush, smile, hair style and hair colour, body, proportions, front-facing pose with arms slightly out, "
            "line art and pastel colouring as the attachment. All the same size, whole body from hair to shoes visible. "
            "Plain white background. No text, no labels, no logo, no hat, no bag. Modest, everyday clothes.")
    order = "Outfits, in this order (left to right" + (", top row first" if len(todo) > 4 else "") + "):"
    return head + "\n\n" + order + "\n" + "\n".join(f"{i}. {t['draw']}" for i, t in enumerate(todo, 1))


def write_prompt_page():
    """묶음마다: 올릴 그림(미리보기) · 복사 버튼 달린 글 · 저장 이름 · 완료 여부. 브라우저로 연다."""
    import html as H
    cards, n = [], 0
    for g in "FM":
        for s in SEASON_KO:
            todo = new_sets(g, s)
            if not todo: continue
            n += 1
            att = ATTACH[(g, s)]
            done = all((OUT / f"outfit_{t['key']}_340_poster.png").exists() for t in todo)
            rel = "../" + att.relative_to(WORK).as_posix()
            names = "".join(f"<li>{H.escape(OCC_KO[t['occ']])} · {H.escape(t['label'])}</li>" for t in todo)
            thumbs = "".join(f'<img src="../착장세트_20261014/outfit_{t["key"]}_340_poster.png" alt="">' for t in todo) if done else ""
            cards.append(f"""
<section class="card{' done' if done else ''}">
  <h2>{n}. {'여자' if g == 'F' else '남자'} · {SEASON_KO[s]} <small>{len(todo)}벌</small> {'<span class="ok">완료</span>' if done else ''}</h2>
  {f'<div class="thumbs">{thumbs}</div>' if done else f'''
  <div class="row">
    <div class="att"><b>① 올릴 그림</b><img src="{rel}" alt=""><code>{H.escape(str(att))}</code>
      <button type="button" data-copy="{H.escape(str(att))}">경로 복사</button></div>
    <div class="txt"><b>② 붙여넣을 글</b><textarea readonly>{H.escape(prompt_text(g, s, todo))}</textarea>
      <button type="button" class="main" data-from="prev">글 복사</button></div>
  </div>
  <p><b>③ 받은 그림</b> → 경로만 Claude에게 보내기 (저장 이름 몰라도 됨) · 들어갈 옷: </p><ol>{names}</ol>'''}
</section>""")
    page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>착장 세트 만들기</title><style>
body{{margin:0;background:#f4f6fa;color:#222a36;font:15px/1.6 "Malgun Gothic",system-ui,sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:20px 16px 60px;display:grid;gap:16px}}
h1{{font-size:21px;margin:0}} h2{{font-size:17px;margin:0 0 10px}} small{{color:#667085;font-weight:400}}
.card{{background:#fff;border:1px solid #dbe1ea;border-radius:12px;padding:16px}} .card.done{{background:#f1f8f3}}
.row{{display:grid;grid-template-columns:220px 1fr;gap:14px}} @media(max-width:700px){{.row{{grid-template-columns:1fr}}}}
.att img{{display:block;width:100%;max-width:200px;height:200px;object-fit:contain;background:#fafafa;border:1px solid #dbe1ea;border-radius:8px;margin:6px 0}}
code{{display:block;font-size:11.5px;word-break:break-all;color:#475467;margin-bottom:6px}}
textarea{{width:100%;box-sizing:border-box;height:210px;font:12.5px/1.45 Consolas,monospace;border:1px solid #dbe1ea;border-radius:8px;padding:8px;margin:6px 0}}
button{{font:inherit;font-size:13px;border:1px solid #c9d3e3;background:#e6eef8;border-radius:999px;padding:5px 14px;cursor:pointer}}
button.main{{background:#3a6ea5;color:#fff;border-color:#3a6ea5;font-size:14px;padding:7px 18px}}
.ok{{background:#2f7d4f;color:#fff;border-radius:999px;padding:1px 10px;font-size:12px;margin-left:6px}}
.thumbs{{display:flex;flex-wrap:wrap;gap:8px}} .thumbs img{{width:110px;height:110px;border-radius:8px;border:1px solid #dbe1ea}}
ol{{margin:4px 0 0}} p{{margin:10px 0 0}}
</style></head><body><div class="wrap">
<h1>착장 세트 만들기 — Gemini</h1>
<p>묶음마다: Gemini <b>새 대화</b> → ① 그림 올리기 → ② 「글 복사」 눌러 붙여넣기 → ③ 받은 그림 경로를 Claude에게. 완료된 묶음은 초록색.</p>
{''.join(cards)}
</div><script>
document.querySelectorAll('button').forEach(function(b){{b.onclick=function(){{
  var t=b.dataset.copy||b.previousElementSibling.value;
  var done=function(){{var o=b.textContent;b.textContent='복사됨 ✓';setTimeout(function(){{b.textContent=o}},1500)}};
  if(navigator.clipboard)navigator.clipboard.writeText(t).then(done,function(){{fallback()}});else fallback();
  function fallback(){{var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();done()}}
}}}});
</script></body></html>"""
    (RAW / "착장세트_만들기.html").write_text(page, encoding="utf-8")
    print(f"안내 페이지 → {RAW / '착장세트_만들기.html'}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if "--prompts" in sys.argv:
        return write_prompts()
    OUT.mkdir(exist_ok=True)
    done = 0
    for g in "FM":
        for s in SEASON_KO:
            todo = new_sets(g, s)
            if "--force" not in sys.argv and all((OUT / f"outfit_{t['key']}_340_poster.png").exists() for t in todo):
                continue   # 이미 처리한 묶음은 건너뜀 (다시 하려면 --force)
            figs = {}
            sheet = RAW / f"sheet_{g.lower()}_{s}.png"
            singles = {t["key"]: RAW / f"{t['key']}.png" for t in todo}
            if sheet.exists() and not all(p.exists() for p in singles.values()):
                figs = dict(zip([t["key"] for t in todo], split_sheet(sheet, len(todo))))
            for k, p in singles.items():
                if p.exists():
                    c = cutout(Image.open(p))[0]
                    figs[k] = c.crop(c.getbbox())
            for t in todo:
                if t["key"] not in figs: continue
                fig = figs[t["key"]]
                fig.save(OUT / f"{t['key']}_source.png")
                png = OUT / f"outfit_{t['key']}_340_poster.png"
                poster(fig, s).save(png)
                video(png, OUT / f"outfit_{t['key']}_340.mp4", OUT / f"outfit_{t['key']}_340.gif")
                done += 1
                print(f"완료 {t['key']}: {fig.size[0]}×{fig.size[1]}")
    print(f"처리 {done}벌")
    if done:
        subprocess.run([sys.executable, "-I", str(HERE / "build_map.py")], check=True)
        write_prompt_page()   # 완료 표시 갱신


if __name__ == "__main__":
    main()
