"""옷 아이콘 (64×64 SVG). 같은 선 색·굵기, 위→아래 그라데이션, 오른쪽 그늘·왼쪽 빛, 바닥 그림자, 옷깃·단추·주머니 등 세부.
build_map.py 가 svg(key) 로 불러 쓴다. 키 목록 = KEYS.
"""

OUT = "#5a4a46"        # 바깥 선 (캐릭터 선화와 비슷한 짙은 갈색)


def _hex(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(c, t, k):
    a, b = _hex(c), _hex(t)
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(a, b))


def light(c, k=0.35): return mix(c, "#ffffff", k)
def dark(c, k=0.28): return mix(c, "#2a1f1c", k)


class Icon:
    def __init__(self, key):
        self.key, self.defs, self.body, self.n = key, [], [], 0

    def _id(self, p):
        self.n += 1
        return f"{self.key}_{p}{self.n}"

    def shape(self, d, color, shade=True, sw=2.2):
        """옷 한 조각: 그라데이션 칠 + 그늘/빛(같은 모양 안에서만) + 바깥 선."""
        g, cp = self._id("g"), self._id("c")
        self.defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1">'
                         f'<stop offset="0" stop-color="{light(color, .28)}"/><stop offset="1" stop-color="{color}"/></linearGradient>'
                         f'<clipPath id="{cp}"><path d="{d}"/></clipPath>')
        self.body.append(f'<path d="{d}" fill="url(#{g})"/>')
        if shade:
            self.body.append(f'<g clip-path="url(#{cp})"><path d="M38 0 Q46 30 40 64 L64 64 L64 0 Z" fill="{dark(color, .5)}" opacity=".16"/>'
                             f'<ellipse cx="22" cy="20" rx="9" ry="13" fill="#fff" opacity=".28"/></g>')
        self.body.append(f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="{sw}" stroke-linejoin="round"/>')
        return self

    def line(self, d, color, w=1.4, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{da}/>')
        return self

    def fill(self, d, color, stroke=True, w=1.6):
        s = f' stroke="{OUT}" stroke-width="{w}" stroke-linejoin="round"' if stroke else ""
        self.body.append(f'<path d="{d}" fill="{color}"{s}/>')
        return self

    def dots(self, pts, color, r=1.3):
        self.body.extend(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>' for x, y in pts)
        return self

    def svg(self, top=7, bottom=57):
        """top/bottom = 그림의 위·아래 끝(대략). 작은 그림(신발·반바지)은 가운데로 옮기고 그림자를 바로 밑에 둔다."""
        dy = 0 if bottom - top > 44 else round(33 - (top + bottom) / 2, 1)
        sh = f'<ellipse cx="32" cy="{bottom + 2.4}" rx="{19 if bottom - top > 30 else 22}" ry="2.4" fill="#5a4a46" opacity=".13"/>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
                f'<defs>{"".join(self.defs)}</defs><g transform="translate(0 {dy})">{sh}{"".join(self.body)}</g></svg>\n')


# ---------- 기본 모양 ----------
TEE_S = ("M21 11 Q26 9 27 8 Q32 14 37 8 Q38 9 43 11 L54 21 Q55 23 53 25 L48.5 29.5 Q46.5 31 45 29 L44.5 27.5 "
         "L44.5 54 Q44.5 56 42.5 56 L21.5 56 Q19.5 56 19.5 54 L19.5 27.5 L19 29 Q17.5 31 15.5 29.5 L11 25 Q9 23 10 21 Z")
TEE_L = ("M21 11 L27 8 Q32 14 37 8 L43 11 Q48 13 51 19 Q55 32 57 48 Q57.5 51 55 51.5 L51 52 Q49 52 48.5 50 L44.5 31 "
         "L44.5 54 Q44.5 56 42.5 56 L21.5 56 Q19.5 56 19.5 54 L19.5 31 L15.5 50 Q15 52 13 52 L9 51.5 Q6.5 51 7 48 "
         "Q9 32 13 19 Q16 13 21 11 Z")
CUFFS_L = "M48.6 47.2 L56.6 46.6 M7.4 46.6 L15.4 47.2"
HEM = "M19.6 51.5 H44.4"
TANK = ("M24 8 Q25.5 7 27 8 Q28 16 32 16 Q36 16 37 8 Q38.5 7 40 8 Q40 16 43 21 Q45 25 45 30 L45 54 Q45 56 43 56 "
        "L21 56 Q19 56 19 54 L19 30 Q19 25 21 21 Q24 16 24 8 Z")
STRAP = ("M25 8 L26.5 8 L27 20 Q32 23 37 20 L37.5 8 L39 8 L40 22 Q43 27 43 32 L43 52 Q43 54 41 54 L23 54 Q21 54 21 52 "
         "L21 32 Q21 27 24 22 Z")
PANTS = ("M19 10 L45 10 Q46 10 46 12 L47.5 55 Q47.5 57 45.5 57 L36 57 Q34.5 57 34.3 55.5 L32 25 L29.7 55.5 "
         "Q29.5 57 28 57 L18.5 57 Q16.5 57 16.5 55 L18 12 Q18 10 19 10 Z")
WIDE = ("M19 10 L45 10 Q46 10 46.3 12 L50.5 55 Q50.6 57 48.5 57 L35.5 57 Q34 57 33.8 55.5 L32 25 L30.2 55.5 "
        "Q30 57 28.5 57 L15.5 57 Q13.4 57 13.5 55 L17.7 12 Q18 10 19 10 Z")
TAPER = ("M19 10 L45 10 Q46 10 46 12 L44.8 52 L44.8 56 Q44.8 57.5 43.3 57.5 L36.7 57.5 Q35.2 57.5 35.2 56 L35.2 52 "
         "L32 25 L28.8 52 L28.8 56 Q28.8 57.5 27.3 57.5 L20.7 57.5 Q19.2 57.5 19.2 56 L19.2 52 L18 12 Q18 10 19 10 Z")
SHORTS = ("M18 13 L46 13 Q47 13 47.3 15 L50 36 Q50 38 48 38.3 L36 39 Q34.5 39 34.2 37.5 L32 25 L29.8 37.5 "
          "Q29.5 39 28 39 L16 38.3 Q14 38 14 36 L16.7 15 Q17 13 18 13 Z")
WAIST = "M18.2 15 H45.8"


def skirt(y):
    return f"M22 12 L42 12 Q43 12 43.3 13.5 L{50 + (y - 40) * .12:.1f} {y} Q{50.5 + (y - 40) * .12:.1f} {y + 2} {48.5 + (y - 40) * .12:.1f} {y + 2} L{15.5 - (y - 40) * .12:.1f} {y + 2} Q{13.5 - (y - 40) * .12:.1f} {y + 2} {14 - (y - 40) * .12:.1f} {y} L20.7 13.5 Q21 12 22 12 Z"


JACKET = ("M21 11 L27 8 L32 17 L37 8 L43 11 Q48 13 51 19 Q55 32 57 46 Q57.5 49 55 49.5 L51 50 Q49 50 48.5 48 L45 31 "
          "L45 50 Q45 52 43 52 L21 52 Q19 52 19 50 L19 31 L15.5 48 Q15 50 13 50 L9 49.5 Q6.5 49 7 46 "
          "Q9 32 13 19 Q16 13 21 11 Z")
COAT = ("M21 10 L27 7 L32 17 L37 7 L43 10 Q48 12 51 18 Q55 32 57 48 Q57.5 51 55 51.5 L51 52 Q49 52 48.5 50 L45.5 32 "
        "L46.5 59 Q46.5 61 44.5 61 L19.5 61 Q17.5 61 17.5 59 L18.5 32 L15.5 50 Q15 52 13 52 L9 51.5 Q6.5 51 7 48 "
        "Q9 32 13 18 Q16 12 21 10 Z")
COAT_S = COAT.replace("L46.5 59 Q46.5 61 44.5 61 L19.5 61 Q17.5 61 17.5 59", "L46 55 Q46 57 44 57 L20 57 Q18 57 18 55")
LAPEL = "M27 7.5 L29.5 20 L32 17 L34.5 20 L37 7.5"
HOOD = "M21.5 12 Q22 3 32 3 Q42 3 42.5 12 Q37 17 32 17 Q27 17 21.5 12 Z"
SNEAKER = ("M7 44 Q7 33 15 31 L22 30 Q26 30 28 33 L31 36 Q38 39 50 40.5 Q57 41.5 57 46 L57 47.5 L7 47.5 Z")
SOLE = "M6.5 47.5 L57.5 47.5 Q58 51 55 51 L9 51 Q6 51 6.5 47.5 Z"
BOOT = "M17 12 Q17 10 19 10 L32 10 Q34 10 34 12 L34 36 Q44 37 52 41 Q57 43.5 56.5 47.5 L17 47.5 Z"
LOAFER = "M8 46 Q8 38 17 37 Q30 37 44 39.5 Q55 41 56.5 45 L57 47.5 L8 47.5 Z"


def tee_short(k, c, extra=None):
    i = Icon(k).shape(TEE_S, c)
    i.line("M27 8.5 Q32 15.5 37 8.5", dark(c), 1.5).line("M11.5 25.5 L16 29 M48 29 L52.5 25.5", dark(c, .18), 1.2)
    if extra: extra(i)
    return i


def tee_long(k, c, extra=None):
    i = Icon(k).shape(TEE_L, c)
    i.line("M27 8.5 Q32 15.5 37 8.5", dark(c), 1.5).line(CUFFS_L, dark(c), 1.3)
    if extra: extra(i)
    return i


def collar(i, c):
    i.fill("M26.5 8 L32 17 L28 19 L24.5 11 Z", light(c, .5)).fill("M37.5 8 L32 17 L36 19 L39.5 11 Z", light(c, .5))
    return i


def buttons(i, c, ys, x=32):
    i.line(f"M{x} 17 V55", dark(c, .35), 1.1)
    return i.dots([(x + 1.6, y) for y in ys], dark(c, .45), 1.1)


def pants(k, c, d=PANTS, extra=None):
    i = Icon(k).shape(d, c).line(WAIST if d != TAPER else "M18.1 14 H45.9", dark(c), 1.3)
    i.line("M32 14 V24", dark(c, .35), 1.1)
    if extra: extra(i)
    return i


def coat(k, c, d=COAT, extra=None):
    i = Icon(k).shape(d, c).fill(LAPEL + " Z", light(c, .18), w=1.3).line(CUFFS_L, dark(c), 1.3)
    if extra: extra(i)
    return i


def shoe(k, c, sole="#f7f5f2", d=SNEAKER, extra=None):
    i = Icon(k).shape(d, c).shape(SOLE, sole, shade=False, sw=1.8)
    if extra: extra(i)
    return i


# ---------- 아이콘 ----------
def build(key):
    C = {}
    # 상의
    if key == "tank_m":
        i = Icon(key).shape(TANK, "#dfe7ee"); i.line("M27 8.6 Q28 16.6 32 16.6 Q36 16.6 37 8.6", dark("#dfe7ee"), 1.4)
        i.line("M24.5 9 Q24.5 16 21.5 21 M39.5 9 Q39.5 16 42.5 21", dark("#dfe7ee", .2), 1.1); return i
    if key == "strap_top":
        i = Icon(key).shape(STRAP, "#f6cdd8"); i.line("M27 20.5 Q32 23.5 37 20.5", dark("#f6cdd8"), 1.3)
        return i.line("M23 50 H41", dark("#f6cdd8", .2), 1.1)
    if key == "sport_top":
        c = "#b9a6e3"; i = Icon(key).shape("M25 12 L27.5 12 L28.5 21 Q32 24.5 35.5 21 L36.5 12 L39 12 L41.5 27 Q42.5 33 41.5 39 L22.5 39 Q21.5 33 22.5 27 Z", c)
        return i.fill("M22.5 34 L41.5 34 L41.5 39 L22.5 39 Z", dark(c, .25), w=1.4)
    if key == "tee_short": return tee_short(key, "#bcd8f2")
    if key == "sport_tee":
        return tee_short(key, "#9fe0c8", lambda i: i.line("M19.8 34 L44.2 34", "#ffffff", 2.2).line("M44 22 L50 27", "#ffffff", 1.6))
    if key == "collar_tee":
        c = "#cfe7d2"; i = tee_short(key, c); collar(i, c); return buttons(i, c, [21, 26], x=32).line("M32 27 V55", "none")
    if key == "shirt_short":
        c = "#fbe7b8"; i = Icon(key).shape(TEE_S, c); collar(i, c); buttons(i, c, [24, 32, 40, 48])
        return i.dots([(25, 33), (38, 41), (24, 47), (40, 26)], "#f08a7a", 1.6).dots([(36, 34), (27, 41), (39, 49)], "#79b98f", 1.4)
    if key == "knit_thin":
        c = "#dbe9c8"; i = tee_short(key, c)
        for y in (32, 37, 42, 47): i.line(f"M21 {y} H43", dark(c, .18), 1, "1.5 1.8")
        return i.line(HEM, dark(c), 1.3)
    if key == "tee_long": return tee_long(key, "#f2e6d6", lambda i: i.line(HEM, dark("#f2e6d6", .18), 1.1))
    if key == "shirt":
        c = "#dde9f8"; i = Icon(key).shape(TEE_L, c); collar(i, c); buttons(i, c, [24, 31, 38, 45, 52])
        return i.line(CUFFS_L, dark(c), 1.3).fill("M21.5 24 H28 V30 H21.5 Z", light(c, .2), w=1.1)
    if key == "check_shirt":
        c = "#e9a6a0"; i = Icon(key).shape(TEE_L, c); collar(i, c)
        for x in (24, 30, 36, 42): i.line(f"M{x} 14 V56", dark(c, .35), 1, None)
        for y in (24, 32, 40, 48): i.line(f"M18 {y} H46", dark(c, .35), 1)
        return buttons(i, c, [25, 35, 45]).line(CUFFS_L, dark(c), 1.3)
    if key == "blouse":
        c = "#fff3f3"; i = Icon(key).shape(TEE_L, c)
        i.fill("M26 8.5 Q29 13 32 15 Q35 13 38 8.5 Q36 18 32 19 Q28 18 26 8.5 Z", "#ffffff", w=1.3)
        i.line("M28 19 Q32 23 36 19", dark(c, .25), 1.1).line("M10 44 Q12 47 9 49 M54 44 Q52 47 55 49", dark(c, .25), 1.1)
        return i.dots([(32, 26), (32, 33), (32, 40)], "#e7b7c2", 1.3)
    if key == "sweatshirt":
        c = "#cfd5e8"; i = tee_long(key, c)
        return i.fill("M19.6 51 H44.4 V54 Q44.4 56 42.4 56 H21.6 Q19.6 56 19.6 54 Z", dark(c, .12), w=1.2).line("M30 9 L32 13 L34 9", dark(c), 1.1)
    if key == "hoodie":
        c = "#b8c6b2"; i = Icon(key).shape(HOOD, dark(c, .1)).shape(TEE_L, c)
        i.line("M27 8.5 Q32 15.5 37 8.5", dark(c), 1.4).line("M30 15 V23 M34 15 V23", OUT, 1.1).line(CUFFS_L, dark(c), 1.3)
        return i.fill("M24 38 H40 L42 47 H22 Z", dark(c, .1), w=1.2)
    if key == "knit":
        c = "#e9cfb3"; i = tee_long(key, c)
        for x in (23, 26.5, 30, 33.5, 37, 40.5): i.line(f"M{x} 51.5 V55.5", dark(c, .3), 1)
        return i.line(HEM, dark(c, .3), 1.2).line("M25 22 Q32 26 39 22 M24 30 Q32 34 40 30", dark(c, .12), 1)
    if key == "turtleneck":
        c = "#d9c19f"; i = Icon(key).shape("M25.5 3 H38.5 Q39.5 3 39.5 4 V12 H24.5 V4 Q24.5 3 25.5 3 Z", dark(c, .08)).shape(TEE_L, c)
        i.line("M27.5 4 V12 M30.5 4 V12 M33.5 4 V12 M36.5 4 V12", dark(c, .3), .9).line(CUFFS_L, dark(c), 1.3)
        return i.line("M27 18 Q24.5 26 27 34 Q29.5 42 27 50 M37 18 Q39.5 26 37 34 Q34.5 42 37 50", dark(c, .3), 1.4)
    if key == "knit_vest":
        c = "#c9b6e4"; i = Icon(key).shape(TANK.replace("Q28 16 32 16 Q36 16 37 8", "Q28 18 32 26 Q36 18 37 8"), c)
        i.line("M27 9 L32 26.5 L37 9", dark(c, .3), 1.3)
        for y in (34, 42): i.line(f"M21 {y} L26 {y + 4} L32 {y} L38 {y + 4} L43 {y}", dark(c, .2), 1.1)
        return i.line("M19.5 51.5 H44.5", dark(c, .3), 1.2)
    if key == "pajama":
        c = "#cfe0f5"; i = Icon(key).shape(TEE_S.replace("L44.5 54 Q44.5 56 42.5 56 L21.5 56 Q19.5 56 19.5 54", "L44.5 42 Q44.5 44 42.5 44 L21.5 44 Q19.5 44 19.5 42"), c)
        collar(i, c).dots([(32, 24), (32, 31), (32, 38)], dark(c, .4), 1.1)
        i.shape("M21 44 L43 44 L45 59 L34.5 59 L32 50 L29.5 59 L19 59 Z", light(c, .1))
        return i.dots([(25, 28), (39, 34), (26, 52), (40, 54), (37, 22)], "#f3d36b", 1.2)
    # 하의
    if key == "shorts": return Icon(key).shape(SHORTS, "#e3d3b5").line(WAIST, dark("#e3d3b5"), 1.3).line("M18 22 Q21 25 24 22 M40 22 Q43 25 46 22", dark("#e3d3b5", .25), 1)
    if key == "sport_shorts":
        c = "#4d5566"; i = Icon(key).shape(SHORTS, c).line(WAIST, light(c, .3), 1.4)
        return i.line("M15.6 30 L17 37.5 M48.4 30 L47 37.5", "#c4f06b", 1.8).line("M30 15 L29 19 M34 15 L35 19", "#ffffff", 1)
    if key == "jeans":
        c = "#6f93c6"; i = pants(key, c)
        i.line("M20 16 Q24 21 29 17 M44 16 Q40 21 35 17", "#f1c27a", 1, "1.4 1.2").line("M20.4 53 H28.2 M35.8 53 H45.2", light(c, .25), 1)
        return i.dots([(32, 13)], "#e9b44c", 1.3)
    if key == "slacks":
        c = "#7b7f8c"; i = Icon(key).shape(WIDE, c).line(WAIST, dark(c), 1.3)
        return i.line("M24 17 L22 55 M40 17 L42 55", light(c, .25), 1.1).line("M32 14 V24", dark(c, .35), 1.1)
    if key == "cargo":
        c = "#9aa27a"; i = pants(key, c)
        return i.fill("M17.6 31 H25 V40 H17.3 Z", dark(c, .1), w=1.2).fill("M39 31 H46.4 L46.7 40 H39 Z", dark(c, .1), w=1.2).line("M17.6 33.5 H25 M39 33.5 H46.4", dark(c, .35), 1)
    if key == "jogger":
        c = "#3f4555"; i = Icon(key).shape(TAPER, c).line("M18.1 14 H45.9", light(c, .3), 1.3)
        i.fill("M19.2 52 H28.8 V56 Q28.8 57.5 27.3 57.5 H20.7 Q19.2 57.5 19.2 56 Z", dark(c, .2), w=1.2)
        i.fill("M35.2 52 H44.8 V56 Q44.8 57.5 43.3 57.5 H36.7 Q35.2 57.5 35.2 56 Z", dark(c, .2), w=1.2)
        return i.line("M18.5 22 L19.4 50 M45.5 22 L44.6 50", "#ffffff", 1.2).line("M30.5 14 L30 19 M33.5 14 L34 19", "#ffffff", 1)
    if key == "warm_pants":
        c = "#8c7a6b"; i = Icon(key).shape(WIDE, c).line(WAIST, dark(c), 1.3)
        for x in (21, 25, 39, 43): i.line(f"M{x} 17 L{x - (2 if x < 32 else -2)} 55", dark(c, .2), 1.2)
        return i
    if key == "leggings":
        c = "#2f333d"; i = Icon(key).shape("M21 10 L43 10 Q44 10 44 12 L41.5 56 Q41.4 57.5 40 57.5 L35.5 57.5 Q34 57.5 34 56 L32 26 L30 56 Q30 57.5 28.5 57.5 L24 57.5 Q22.6 57.5 22.5 56 L20 12 Q20 10 21 10 Z", c)
        return i.line("M20.2 14 H43.8", light(c, .3), 1.3).line("M22 22 L24 54 M42 22 L40 54", "#b9a6e3", 1.2)
    if key == "skirt_mini":
        c = "#f3bcc8"; i = Icon(key).shape(skirt(36), c).line("M21.3 16 H42.7", dark(c), 1.2)
        return i.line("M27 17 L25 37 M37 17 L39 37", dark(c, .2), 1)
    if key == "pleats":
        c = "#f2f2f2"; i = Icon(key).shape(skirt(38), c).line("M21.3 16 H42.7", dark(c, .4), 1.2)
        for x0, x1 in ((24.5, 19), (28, 25.5), (32, 32), (36, 38.5), (39.5, 45)): i.line(f"M{x0} 17 L{x1} 39.5", dark(c, .3), 1)
        return i.line("M14.5 36.5 H49.5", "#7aa7d9", 1.4)
    if key == "skirt_midi":
        c = "#bdd3e8"; i = Icon(key).shape(skirt(48), c).line("M21.3 16 H42.7", dark(c), 1.2)
        return i.line("M26 17 Q22 33 19 49 M38 17 Q42 33 45 49", dark(c, .2), 1)
    if key == "skirt_long":
        c = "#c9a98c"; i = Icon(key).shape(skirt(56), c).line("M21.3 16 H42.7", dark(c), 1.2)
        return i.line("M26 17 Q21 37 17 57 M32 17 V57.5 M38 17 Q43 37 47 57", dark(c, .2), 1)
    if key == "leather_skirt":
        c = "#7a4a33"; i = Icon(key).shape(skirt(48), c).line("M21.3 16 H42.7", dark(c), 1.2)
        return i.line("M24 20 Q22 32 21 44", "#ffffff", 1.6).line("M38 17 L39 47", dark(c, .4), 1).dots([(38, 21)], "#e9c46a", 1.2)
    # 원피스류
    if key == "dress_sleeveless":
        c = "#fbe1a6"; i = Icon(key).shape("M25 7 L27.5 7 Q29 15 32 15 Q35 15 36.5 7 L39 7 Q39 17 41 24 L52 56 Q52.5 58 50.5 58 L13.5 58 Q11.5 58 12 56 L23 24 Q25 17 25 7 Z", c)
        return i.line("M23 24 H41", dark(c, .3), 1.3).line("M27 26 Q23 42 19 57 M37 26 Q41 42 45 57", dark(c, .18), 1)
    if key == "dress_short":
        c = "#cfe2f1"; i = Icon(key).shape("M21 11 L27 8 Q32 14 37 8 L43 11 L52 20 L47 26 L43 22.5 L42.5 26 L51 56 Q51.5 58 49.5 58 L14.5 58 Q12.5 58 13 56 L21.5 26 L21 22.5 L17 26 L12 20 Z", c)
        i.line("M27 8.5 Q32 15.5 37 8.5", dark(c), 1.4).line("M21.5 27 Q32 29.5 42.5 27", dark(c, .3), 1.3)
        return i.fill("M29.5 26.5 L32 29 L34.5 26.5 L32 25 Z", "#f3a6b6", w=1)
    if key == "dress_long":
        c = "#a9c9a4"; i = Icon(key).shape("M21 10 L27 7 L32 15 L37 7 L43 10 L51 18 L46 24 L43 21 L43 25 L50 59 Q50.5 61 48.5 61 L15.5 61 Q13.5 61 14 59 L21 25 L21 21 L18 24 L13 18 Z", c)
        collar(i, c); buttons(i, c, [21, 28, 35, 42, 49]); return i.line("M21 30 H43", dark(c, .35), 1.6)
    if key == "dress_knit":
        c = "#dcc3a6"; i = Icon(key).shape("M21 11 L27 8 Q32 14 37 8 L43 11 Q48 13 51 19 Q55 32 57 46 Q57.5 49 55 49.5 L51 50 Q49 50 48.5 48 L44.5 30 L46.5 57 Q46.6 59 44.5 59 L19.5 59 Q17.4 59 17.5 57 L19.5 30 L15.5 48 Q15 50 13 50 L9 49.5 Q6.5 49 7 46 Q9 32 13 19 Q16 13 21 11 Z", c)
        i.line("M27 8.5 Q32 15.5 37 8.5", dark(c), 1.4).line("M48.6 45 L56.6 44.6 M7.4 44.6 L15.4 45", dark(c), 1.3)
        for x in (24, 28, 32, 36, 40): i.line(f"M{x} 18 V56", dark(c, .15), 1)
        return i
    if key == "bustier_dress":
        c = "#8fb0d6"; i = Icon(key).fill(TEE_S.replace("L44.5 54 Q44.5 56 42.5 56 L21.5 56 Q19.5 56 19.5 54", "L44.5 30 L19.5 30"), "#ffffff", w=1.8)
        i.shape("M22 20 Q32 23 42 20 L42 30 L50 57 Q50.5 59 48.5 59 L15.5 59 Q13.5 59 14 57 L22 30 Z", c)
        return i.line("M24 21 L23 8.5 M40 21 L41 8.5", dark(c), 2).line("M22 30 H42", dark(c, .3), 1.3)
    if key == "jumpsuit":
        c = "#7fa0c9"; i = Icon(key).shape(PANTS.replace("M19 10 L45 10 Q46 10 46 12", "M19 26 L45 26 Q46 26 46 28").replace("L18 12 Q18 10 19 10 Z", "L18 28 Q18 26 19 26 Z"), c)
        i.shape("M23 9 H41 V28 H23 Z", c).line("M23 10 L20 3 M41 10 L44 3", dark(c), 2)
        return i.dots([(25.5, 12), (38.5, 12)], "#f1c27a", 1.6).fill("M28 14 H36 V21 H28 Z", dark(c, .12), w=1.1)
    # 아우터
    if key == "cardigan":
        c = "#dccff0"; i = Icon(key).fill("M27 8 L32 14 L37 8 L37 56 L27 56 Z", "#ffffff", w=1.2).shape(TEE_L.replace("L27 8 Q32 14 37 8", "L27 8 L30.5 22 L30.5 56 M33.5 56 L33.5 22 L37 8"), c)
        i.line(CUFFS_L, dark(c), 1.3).line(HEM, dark(c, .25), 1.1)
        return i.dots([(29, 29), (29, 37), (29, 45)], dark(c, .45), 1.3)
    if key == "windbreaker":
        c = "#8fd0d8"; i = Icon(key).shape(HOOD, dark(c, .08)).shape(JACKET.replace("L32 17", "L32 12"), c)
        i.line("M32 12 V52", OUT, 1.4).line("M13 30 Q20 34 19 40 M51 30 Q44 34 45 40", "#ffffff", 1.6)
        return i.fill("M8 44 L15.6 45 L15 49.8 L9 49.5 Q6.5 49 7 46 Z", dark(c, .2), w=1.1).fill("M56 44 L48.4 45 L49 49.8 L55 49.5 Q57.5 49 57 46 Z", dark(c, .2), w=1.1)
    if key == "zipup":
        c = "#b6c1cf"; i = Icon(key).shape(HOOD, dark(c, .1)).shape(TEE_L, c)
        i.line("M32 15 V56", OUT, 1.5).line("M31 20 L33 22 M31 28 L33 30", "#ffffff", 1).line(CUFFS_L, dark(c), 1.3)
        return i.fill("M20 40 L28 40 L29.5 49 L20 49 Z", dark(c, .1), w=1.1).fill("M44 40 L36 40 L34.5 49 L44 49 Z", dark(c, .1), w=1.1)
    if key == "jacket_casual":
        c = "#b7a77a"; i = Icon(key).shape(JACKET, c); collar(i, c); buttons(i, c, [24, 32, 40, 48])
        return i.fill("M21 24 H28 V31 H21 Z", dark(c, .08), w=1.1).fill("M36 24 H43 V31 H36 Z", dark(c, .08), w=1.1).fill("M20.5 37 H28.5 V46 H20.5 Z", dark(c, .08), w=1.1)
    if key == "blazer":
        c = "#59657d"; i = Icon(key).fill("M27 8 L32 17 L37 8 Z", "#ffffff", w=1).shape(JACKET, c)
        i.fill("M27 8 L30 21 L32 17 Z", light(c, .2), w=1.2).fill("M37 8 L34 21 L32 17 Z", light(c, .2), w=1.2)
        return i.line("M32 17 L32 52", dark(c, .4), 1.1).dots([(33.6, 34), (33.6, 41)], "#e9c46a", 1.3).line("M37.5 26 H42.5", light(c, .3), 1.2)
    if key == "denim_jacket":
        c = "#7d9fcc"; i = Icon(key).shape(JACKET, c); collar(i, c); buttons(i, c, [22, 30, 38, 46])
        i.line("M20 27 Q25 29 30 27 M34 27 Q39 29 44 27", "#f1c27a", 1, "1.4 1.2")
        return i.fill("M21.5 29 H28.5 V35 H21.5 Z", dark(c, .1), w=1).fill("M35.5 29 H42.5 V35 H35.5 Z", dark(c, .1), w=1).line("M19.2 47 H44.8", "#f1c27a", 1, "1.4 1.2")
    if key == "leather_jacket":
        c = "#3c3a40"; i = Icon(key).shape(JACKET, c)
        i.fill("M27 8 L21 18 L28 24 L32 17 Z", light(c, .12), w=1.2).fill("M37 8 L43 18 L38 22 L32 17 Z", light(c, .12), w=1.2)
        return i.line("M35 20 L28 50", "#c9ccd3", 1.4).line("M38 32 L43 31 M21 36 L26 36", "#c9ccd3", 1.1).line("M14 26 Q16 32 15 38", "#ffffff", 1.2)
    if key == "blouson":
        c = "#3e5a7a"; i = Icon(key).shape(JACKET.replace("L45 50 Q45 52 43 52 L21 52 Q19 52 19 50", "L45 46 Q45 48 43 48 L21 48 Q19 48 19 46"), c)
        i.fill("M19 44 H45 V48 Q45 50 43 50 H21 Q19 50 19 48 Z", dark(c, .25), w=1.2).fill("M27 8 L32 14 L37 8 L35 6.5 Q32 9 29 6.5 Z", dark(c, .25), w=1.2)
        return i.line("M32 14 V44", "#c9ccd3", 1.3).fill("M7.6 44 L15.6 45 L15 49.8 L9 49.5 Q6.5 49 7 46 Z", dark(c, .25), w=1.1).fill("M56.4 44 L48.4 45 L49 49.8 L55 49.5 Q57.5 49 57 46 Z", dark(c, .25), w=1.1).fill("M38 22 H43 V27 H38 Z", "#e98a3a", w=1)
    if key == "trench":
        c = "#d8bd8e"
        return coat(key, c, extra=lambda i: i.fill("M18.3 35 H45.8 V39 H18.3 Z", dark(c, .12), w=1.2).fill("M30 34.5 H34 V39.5 H30 Z", "#ffffff", w=1).dots([(27, 26), (37, 26), (27, 46), (37, 46)], dark(c, .45), 1.3))
    if key == "coat_short":
        c = "#b8865e"
        return coat(key, c, COAT_S, lambda i: i.dots([(35.5, 27), (35.5, 35), (35.5, 43), (28.5, 27), (28.5, 35), (28.5, 43)], dark(c, .45), 1.4).line("M32 17 V57", dark(c, .3), 1))
    if key == "coat_long":
        c = "#cfa577"
        return coat(key, c, extra=lambda i: i.line("M32 17 L32 61", dark(c, .35), 1.1).dots([(34, 30), (34, 40)], dark(c, .5), 1.5).fill("M21 42 L27 42 L27.5 46 L21 46 Z", dark(c, .12), w=1).fill("M43 42 L37 42 L36.5 46 L43 46 Z", dark(c, .12), w=1))
    if key == "light_padding":
        c = "#9fc6b2"; i = Icon(key).shape(JACKET.replace("L32 17", "L32 12"), c)
        for y in (20, 27, 34, 41, 48): i.line(f"M19.4 {y} H44.6", dark(c, .28), 1.1)
        return i.line("M32 12 V52", OUT, 1.3).line("M9.5 32 L15.5 33 M48.5 33 L54.5 32 M8.5 40 L15 41 M49 41 L55.5 40", dark(c, .28), 1)
    if key == "padding":
        c = "#3e4556"; d = ("M18 12 Q24 7 27 8 L32 12 L37 8 Q40 7 46 12 Q52 15 54 21 Q58 34 58 50 Q58 53 55 53 L51 53 Q48.5 53 48.5 50 "
                            "L47 35 Q48.5 47 47 59 Q47 61 45 61 L19 61 Q17 61 17 59 Q15.5 47 17 35 L15.5 50 Q15.5 53 13 53 L9 53 Q6 53 6 50 Q6 34 10 21 Q12 15 18 12 Z")
        i = Icon(key).shape(d, c).fill("M24 6 Q32 2 40 6 L40 13 Q32 16 24 13 Z", dark(c, .15), w=1.4)
        for y in (21, 30, 39, 48): i.line(f"M17.5 {y} Q32 {y + 3.5} 46.5 {y}", light(c, .35), 1.4)
        return i.line("M32 13 V61", light(c, .45), 1.3).line("M7 35 Q11 37 15.5 36 M57 35 Q53 37 48.5 36", light(c, .35), 1.2)
    if key == "fur":
        c = "#b78a62"; i = coat(key, c, COAT_S)
        i.fill("M21 10 Q24 6 27 7 L32 17 L29 22 Q24 18 21 10 Z", "#f4ead9", w=1.3).fill("M43 10 Q40 6 37 7 L32 17 L35 22 Q40 18 43 10 Z", "#f4ead9", w=1.3)
        return i.fill("M48.6 47 L56.8 46.4 Q57.4 51 55 51.5 L51 52 Q49 52 48.6 50 Z", "#f4ead9", w=1.1).fill("M15.4 47 L7.2 46.4 Q6.6 51 9 51.5 L13 52 Q15 52 15.4 50 Z", "#f4ead9", w=1.1).fill("M18 52 H46 V55 Q46 57 44 57 H20 Q18 57 18 55 Z", "#f4ead9", w=1.1)
    if key == "rain":
        c = "#ffd36a"; i = Icon(key).shape(HOOD, dark(c, .08)).shape(JACKET.replace("L32 17", "L32 13"), c)
        i.line("M32 13 V52", OUT, 1.4).dots([(34, 22), (34, 30), (34, 38), (34, 46)], dark(c, .45), 1.2)
        for x, y in ((55, 8), (10, 6), (58, 22)):
            i.fill(f"M{x} {y} Q{x + 3} {y + 5} {x} {y + 7} Q{x - 3} {y + 5} {x} {y} Z", "#86bfee", w=1)
        return i
    # 신발
    if key == "sneakers":
        return shoe(key, "#f3f3f6", extra=lambda i: i.line("M18 33 L22 37 M22 31.5 L26 35.5", OUT, 1.2).line("M9 42 Q20 41 30 37", "#9fb8d8", 1.6).fill("M7.5 40 Q7.5 34 12 33 L13 41 Z", "#c7d6ea", w=1))
    if key == "mesh_sneakers":
        return shoe(key, "#bfe7d9", extra=lambda i: [i.dots([(x, y) for x in (12, 16, 20, 36, 40, 44, 48) for y in (38, 42) if not (x < 24 and y == 38 and x < 12)], dark("#bfe7d9", .3), .8), i.line("M18 33 L22 37 M22 31.5 L26 35.5", OUT, 1.2)][0])
    if key == "loafers":
        c = "#7b4f36"
        return Icon(key).shape(LOAFER, c).shape("M7.5 47.5 L57.5 47.5 Q58 50.5 55 50.5 L10 50.5 Q7 50.5 7.5 47.5 Z", "#3b2a22", shade=False, sw=1.6).fill("M24 39 Q31 37.5 38 40 L37 43 Q31 41 25 42 Z", dark(c, .25), w=1.1).line("M14 43 Q20 40 26 41", "#ffffff", 1.1)
    if key == "boots":
        c = "#5a4232"
        return Icon(key).shape(BOOT, c).shape(SOLE, "#2e231d", shade=False, sw=1.6).line("M17.3 15 H33.7", dark(c, .3), 1.3).line("M33.5 18 V34", light(c, .25), 1.1).line("M20 20 Q19 30 20 40", "#ffffff", 1.1)
    if key == "rain_sneakers":
        return shoe(key, "#79acd9", "#e8eef5", extra=lambda i: i.fill("M45 12 Q50 20 45 24 Q40 20 45 12 Z", "#86bfee", w=1).line("M18 33 L22 37 M22 31.5 L26 35.5", "#ffffff", 1.2))
    if key == "winter_boots":
        c = "#a9744a"; i = Icon(key).shape(BOOT, c).shape(SOLE, "#3a2b22", shade=False, sw=1.6)
        i.fill("M17 10 Q17 8 19 8 L32 8 Q34 8 34 10 L34 17 L17 17 Z", "#f4ead9", w=1.3)
        return i.line("M21 22 L30 22 M21 27 L30 27 M21 32 L30 32", OUT, 1.1).line("M18 49.3 H56", "#ffffff", .8, "2 2")
    if key == "thermal":
        c = "#f3c3b8"; i = tee_long(key, c)
        return i.line("M21 32 Q26.5 28 32 32 Q37.5 36 43 32 M21 42 Q26.5 38 32 42 Q37.5 46 43 42", dark(c, .2), 1.2).line(HEM, dark(c, .3), 1.2)
    raise KeyError(key)


# 그림의 위·아래 끝 (없으면 7~57 = 상의·아우터·긴 하의)
BOUNDS = {"sneakers": (30, 51), "mesh_sneakers": (30, 51), "rain_sneakers": (30, 51), "loafers": (37, 50.5),
          "boots": (10, 51), "winter_boots": (8, 51), "shorts": (13, 39), "sport_shorts": (13, 39),
          "skirt_mini": (12, 38), "pleats": (12, 40), "skirt_midi": (12, 50), "leather_skirt": (12, 50),
          "sport_top": (12, 39), "strap_top": (8, 54), "dress_long": (7, 61), "coat_long": (7, 61),
          "trench": (7, 61), "padding": (4, 61)}


def svg(key):
    return build(key).svg(*BOUNDS.get(key, (7, 57)))


KEYS = ["tee_short", "sport_tee", "collar_tee", "shirt_short", "knit_thin", "tee_long",
        "shirt", "check_shirt", "blouse", "sweatshirt", "hoodie", "knit", "turtleneck", "knit_vest", "pajama",
        "shorts", "sport_shorts", "jeans", "slacks", "cargo", "jogger", "warm_pants", "leggings",
        "skirt_mini", "pleats", "skirt_midi", "skirt_long", "leather_skirt",
        "dress_sleeveless", "dress_short", "dress_long", "dress_knit", "bustier_dress", "jumpsuit",
        "cardigan", "windbreaker", "zipup", "jacket_casual", "blazer", "denim_jacket", "leather_jacket", "blouson",
        "trench", "coat_short", "coat_long", "light_padding", "padding", "fur", "rain",
        "sneakers", "mesh_sneakers", "loafers", "boots", "rain_sneakers", "winter_boots", "thermal"]
