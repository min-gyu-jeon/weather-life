"""소품 아이콘 20개 (옷 아이콘과 같은 그림체: icons_svg.Icon). build_map.py 가 불러 쓴다."""
from icons_svg import Icon, OUT, dark, light


def acc(key):
    i = Icon(key)
    if key == "umbrella":
        c = "#7fb2e5"
        i.line("M32 30 V52 Q32 57 27 57 Q23 57 23 53", OUT, 2.4).line("M32 9 V6", OUT, 2.2)
        i.shape("M7 31 Q9 9 32 9 Q55 9 57 31 Q51 26 44.5 31 Q38 26 32 31 Q26 26 19.5 31 Q13 26 7 31 Z", c)
        return i.line("M32 9 Q24 18 19.5 31 M32 9 Q40 18 44.5 31 M32 9 V31", dark(c, .25), 1.2), (6, 57)
    if key == "folding_umbrella":
        c = "#9c8fd9"
        i.line("M42 44 L50 52", OUT, 2.4).fill("M48 49 L55 56 L52 59 L45 52 Z", "#5a4a46", w=1.2)
        i.shape("M14 10 Q26 12 44 40 L40 45 Q18 30 14 10 Z", c)
        return i.line("M18 15 Q30 22 42 42", dark(c, .25), 1.2).fill("M24 24 L30 20 L32 23 L26 27 Z", "#f3e9a8", w=1), (9, 59)
    if key == "rain_boots":
        c = "#f6c945"
        i.shape("M17 12 Q17 10 19 10 L33 10 Q35 10 35 12 L35 37 Q45 38 52 42 Q57 45 56 48 L17 48 Z", c)
        i.shape("M16.5 48 L56.5 48 Q57 52 54 52 L19 52 Q16 52 16.5 48 Z", "#6a5240", shade=False, sw=1.8)
        return i.line("M17.3 15 H34.7", dark(c, .3), 1.3).line("M21 20 Q20 30 21 40", "#ffffff", 1.4), (10, 52)
    if key == "handkerchief":
        c = "#bfe0f2"
        i.shape("M13 17 L50 13 L52 49 L15 51 Z", c)
        i.line("M17 20 L47 17 L48.5 46 L19 47.5 Z", dark(c, .3), 1, "2 1.6")
        return i.dots([(26, 26), (38, 25), (25, 39), (39, 38), (32, 32)], "#f3a6b6", 2), (13, 51)
    if key == "parasol":
        c = "#f6c6d4"
        i.line("M32 30 V52 Q32 57 27 57 Q23 57 23 53", OUT, 2.2).line("M32 9 V6", OUT, 2)
        i.shape("M8 30 Q10 10 32 10 Q54 10 56 30 Z", c)
        for x in (8, 14, 20, 26, 32, 38, 44, 50):
            i.fill(f"M{x} 30 Q{x + 3} 35 {x + 6} 30 Z", "#ffffff", w=1)
        return i.line("M32 10 Q25 18 22 30 M32 10 Q39 18 42 30", dark(c, .2), 1.1), (6, 57)
    if key == "sunglasses":
        i.line("M8 26 L4 22 M56 26 L60 22", OUT, 2.2).line("M27 30 Q32 26 37 30", OUT, 2.2)
        i.shape("M8 26 H27 Q28 40 18 41 Q8 40 8 26 Z", "#3d4a5c").shape("M37 26 H56 Q56 40 46 41 Q36 40 37 26 Z", "#3d4a5c")
        return i.line("M12 29 L16 33 M41 29 L45 33", "#ffffff", 1.4), (22, 41)
    if key == "sunscreen":
        c = "#ffe28a"
        i.shape("M25 8 H39 V15 H25 Z", "#f39a63", shade=False, sw=1.8).shape("M22 15 H42 L40 52 Q32 56 24 52 Z", c)
        i.fill("M32 27 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0", "#f39a63", w=1.2)
        return i.line("M32 18 V20 M32 34 V36 M24 27 H26 M38 27 H40", "#f39a63", 1.4).line("M26 42 H38 M27 46 H37", dark(c, .3), 1.1), (8, 55)
    if key == "cap":
        c = "#8fc0e6"
        i.shape("M42 36 Q55 35 59 41 Q52 44 40 40 Z", dark(c, .12)).shape("M12 38 Q11 16 31 16 Q49 16 50 38 Q31 34 12 38 Z", c)
        return i.fill("M29 14 Q31 12 33 14 Z", dark(c, .3), w=1).line("M31 17 Q30 26 31 36", dark(c, .25), 1.1), (13, 44)
    if key == "fan":
        c = "#a7dccb"
        i.line("M32 34 V54", OUT, 2.6).fill("M28 50 H36 V58 Q32 60 28 58 Z", "#6aa996", w=1.4)
        i.shape("M32 6 m-16 0 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0".replace("M32 6", "M32 22"), c)
        for d in ("M32 22 Q24 12 31 9 Q38 14 32 22", "M32 22 Q42 18 43 26 Q36 31 32 22", "M32 22 Q30 33 23 30 Q22 23 32 22"):
            i.fill(d + " Z", "#ffffff", w=1)
        return i.dots([(32, 22)], OUT, 2), (6, 59)
    if key == "water_bottle":
        c = "#bfe3f6"
        i.shape("M27 6 H37 V12 H27 Z", "#5b8fc4", shade=False, sw=1.8)
        i.shape("M24 12 H40 Q44 12 44 17 L44 52 Q44 57 39 57 L25 57 Q20 57 20 52 L20 17 Q20 12 24 12 Z", c)
        return i.fill("M21 32 Q32 29 43 32 L43 52 Q43 56 39 56 L25 56 Q21 56 21 52 Z", "#7fbfe8", stroke=False).line("M25 18 V27", "#ffffff", 1.6), (6, 57)
    if key == "cool_sleeve":
        c = "#bfe1f4"   # 팔 토시: 위가 넓고 손목 쪽이 좁은 통 · 위아래 밴드
        i.shape("M19 9 Q32 5 45 9 L40 54 Q32 57 24 54 Z", c)
        i.fill("M19 9 Q32 5 45 9 L44.3 15 Q32 11.5 19.7 15 Z", "#7ab3d8", w=1.4)
        i.fill("M24.6 49 Q32 51.5 39.4 49 L40 54 Q32 57 24 54 Z", "#7ab3d8", w=1.4)
        return i.line("M27 20 Q25 34 27 46", "#ffffff", 1.6).line("M36 22 L34.5 44", dark(c, .2), 1, "2 2"), (6, 57)
    if key == "light_outer":
        c = "#dccff0"
        i.line("M32 5 Q35 5 35 8 Q35 11 32 12 V16", OUT, 1.8).line("M32 16 L10 26 H54 Z", OUT, 1.8)
        i.shape("M14 24 L26 21 L32 30 L38 21 L50 24 L52 56 L12 56 Z", c)
        return i.line("M32 30 V56", dark(c, .3), 1.3).dots([(34, 36), (34, 43), (34, 50)], dark(c, .45), 1.2), (5, 56)
    if key == "scarf":
        c = "#e98a7a"
        i.shape("M12 18 Q32 28 52 18 L52 28 Q32 38 12 28 Z", c).shape("M34 31 L40 54 L31 56 L27 33 Z", dark(c, .08))
        for x in (31, 34, 37): i.line(f"M{x + .5} 55.5 L{x + 1} 59", OUT, 1.2)
        return i.line("M16 22 V28 M24 25 V31 M40 25 V31 M48 22 V28", dark(c, .25), 1.1), (18, 59)
    if key == "gloves":
        c = "#7e9fd1"
        i.shape("M19 52 L19 27 Q19 14 30 14 Q41 14 41 27 L41 31 Q47 26 50 32 Q52 38 43 43 L42 52 Z", c)
        i.fill("M18 50 H43 V58 Q43 60 41 60 H20 Q18 60 18 58 Z", "#f4ead9", w=1.4)
        return i.line("M22 24 Q30 21 38 24 M22 31 Q30 28 38 31", "#ffffff", 1.2), (14, 60)
    if key == "beanie":
        c = "#e7a86d"
        i.fill("M32 6 m-5 0 a5 5 0 1 0 10 0 a5 5 0 1 0 -10 0".replace("M32 6", "M32 9"), "#f4ead9", w=1.4)
        i.shape("M13 40 Q13 13 32 13 Q51 13 51 40 Z", c).shape("M11 38 H53 V48 Q53 50 51 50 H13 Q11 50 11 48 Z", dark(c, .12), shade=False, sw=1.8)
        for x in (17, 23, 29, 35, 41, 47): i.line(f"M{x} 39.5 V48.5", dark(c, .35), 1)
        return i, (4, 50)
    if key == "earmuffs":
        c = "#f3b7c9"
        i.line("M14 36 Q14 10 32 10 Q50 10 50 36", OUT, 3.4).line("M14 36 Q14 10 32 10 Q50 10 50 36", "#b78a62", 1.6)
        i.shape("M14 36 m-9 0 a9 10 0 1 0 18 0 a9 10 0 1 0 -18 0", c).shape("M50 36 m-9 0 a9 10 0 1 0 18 0 a9 10 0 1 0 -18 0", c)
        return i.dots([(11, 33), (16, 39), (47, 33), (52, 39)], "#ffffff", 1.4), (9, 46)
    if key == "hotpack":
        c = "#ffb37a"
        i.shape("M14 14 H50 Q53 14 53 17 V49 Q53 52 50 52 H14 Q11 52 11 49 V17 Q11 14 14 14 Z", c)
        i.line("M17 19 H47 V47 H17 Z", dark(c, .25), 1, "2 1.6")
        return i.line("M24 40 Q22 35 25 31 Q28 27 25 22 M32 40 Q30 35 33 31 Q36 27 33 22 M40 40 Q38 35 41 31 Q44 27 41 22", "#e2553e", 1.8), (14, 52)
    if key == "thermos":
        c = "#7f9bc8"
        i.line("M26 6 Q24 3 26 0 M32 6 Q30 3 32 0", "#b8c4d6", 1.4)
        i.shape("M23 8 H41 V16 H23 Z", dark(c, .2), shade=False, sw=1.8)
        i.shape("M22 16 H42 Q44 16 44 19 L44 54 Q44 58 40 58 L24 58 Q20 58 20 54 L20 19 Q20 16 22 16 Z", c)
        return i.line("M20 24 H44 M20 50 H44", dark(c, .3), 1.2).line("M25 28 V44", "#ffffff", 1.6), (6, 58)
    if key == "lip_balm":
        c = "#f6a5bb"
        i.shape("M24 6 Q24 4 26 4 H38 Q40 4 40 6 V24 H24 Z", "#ffffff").shape("M23 24 H41 V56 Q41 58 39 58 H25 Q23 58 23 56 Z", c)
        return i.line("M23 28 H41", dark(c, .3), 1.2).fill("M32 44 Q26 38 29 35 Q31 34 32 36 Q33 34 35 35 Q38 38 32 44 Z", "#ffffff", w=1), (4, 58)
    if key == "mask":
        c = "#f4f6f8"
        i.line("M12 28 Q3 30 6 40 Q8 45 13 41 M52 28 Q61 30 58 40 Q56 45 51 41", OUT, 1.8)
        i.shape("M12 26 Q32 14 52 26 L50 42 Q32 54 14 42 Z", c)
        i.line("M12.5 32 Q32 24 51.5 32 M13 38 Q32 32 51 38", dark(c, .2), 1)
        return i.line("M32 20 V47", dark(c, .35), 1.2), (17, 50)
    raise KeyError(key)


def svg(key):
    i, (top, bottom) = acc(key)
    return i.svg(top, bottom)
