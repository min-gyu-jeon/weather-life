"""추천 착장 세트 목록 (여 20 · 남 16). build_map.py · make_outfit_sets.py · 요청문 만들기가 모두 이 목록을 쓴다.

동업자 결정(10-14): 「추천 착장세트를 더 만들어달라는 뜻」 · 개수 = 여 20 · 남 16 (여름을 더 많이) ·
나누는 기준 = 기온 + 용도(일상·출근·운동) + 비 — 「불쾌지수도 들어가는데 너무 어렵게는 안해도되고 어짜피 백엔드쪽에서 기준을 줄 것」 ·
여자 머리 = 계절별 그대로 · 남자 = 1명 통일 · 나시·스포츠 탑 등 노출 많은 옷은 쓰지 않음(「건전해야해」).

items = 그 세트를 이루는 카탈로그 id (칸별). 백엔드 결과와 가장 많이 겹치는 세트를 고른다.
src  = 이미 있는 그림(폴더 이름, 파일 앞부분) · 없으면 새로 만들 세트(그림 = 착장세트_20261014/outfit_<key>_340*).
draw = Gemini에 줄 옷 설명(영어) — 새 세트만.
"""

SEASON_KO = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
OCC_KO = {"DAILY": "일상", "OFFICE": "출근", "EXERCISE": "운동", "RAIN": "비"}

SETS = [
    # ---------------- 여성 (20) ----------------
    # 봄 4
    dict(key="f_spring_basic", g="F", season="spring", occ="DAILY", label="라벤더 가디건 + 흰 원피스",
         items=dict(outer="C120", onePiece="C111", shoes="C138"), src=("최종_4계절_추천복장_20261013", "outfit_spring_340")),
    dict(key="f_spring_campus", g="F", season="spring", occ="DAILY", label="후드집업 + 스웨트 팬츠",
         items=dict(outer="C122", top="C001", bottom="C045", shoes="C138"), src=("추가착장_4계절_20261014", "outfit_spring_campus_340")),
    dict(key="f_spring_trench", g="F", season="spring", occ="OFFICE", label="트렌치코트 + 블라우스 + 슬랙스",
         items=dict(outer="C059", top="C081", bottom="C094", shoes="C139"),
         draw="beige trench coat (open, belt tied at the back) over a white chiffon blouse, light grey wide slacks, brown loafers"),
    dict(key="f_spring_rain", g="F", season="spring", occ="RAIN", label="봄비 · 방풍 재킷 + 청바지",
         items=dict(outer="C135", top="C008", bottom="C033", shoes="C141"),
         draw="light mint hooded rain jacket (hood down, zipped halfway) over a white long-sleeve T-shirt, light-blue jeans, navy waterproof sneakers"),
    # 여름 8
    dict(key="f_summer_basic", g="F", season="summer", occ="DAILY", label="라벤더 티 + 돌핀팬츠",
         items=dict(top="C001", bottom="C028", shoes="C138"), src=("최종_4계절_추천복장_20261013", "outfit_summer_340")),
    dict(key="f_summer_athleisure", g="F", season="summer", occ="EXERCISE", label="애슬레저 (기능성 반팔 + 러닝 쇼츠)",
         items=dict(top="C143", bottom="C149", shoes="C137"), src=("추가착장_4계절_20261014", "outfit_summer_athleisure_340")),
    dict(key="f_summer_onepiece", g="F", season="summer", occ="DAILY", label="반팔 원피스",
         items=dict(onePiece="C107", shoes="C137"),
         draw="light yellow short-sleeve knee-length cotton dress with a round neck, white canvas sneakers"),
    dict(key="f_summer_office", g="F", season="summer", occ="OFFICE", label="린넨 블라우스 + 쿨슬랙스",
         items=dict(top="C076", bottom="C040", shoes="C139"),
         draw="sky-blue short-sleeve linen blouse tucked in, navy straight light slacks, black loafers"),
    dict(key="f_summer_linen", g="F", season="summer", occ="DAILY", label="린넨 셔츠 + 버뮤다 반바지",
         items=dict(top="C004", bottom="C091", shoes="C137"),
         draw="white short-sleeve linen shirt, beige knee-length bermuda shorts, white mesh sneakers"),
    dict(key="f_summer_skirt", g="F", season="summer", occ="DAILY", label="루즈핏 반팔 + 롱스커트",
         items=dict(top="C075", bottom="C100", shoes="C137"),
         draw="loose pastel pink short-sleeve T-shirt, long light-green flowy skirt to the ankles, white sneakers"),
    dict(key="f_summer_denim", g="F", season="summer", occ="DAILY", label="오버핏 반팔 + 쿨데님",
         items=dict(top="C002", bottom="C037", shoes="C137"),
         draw="oversized white short-sleeve T-shirt, light-blue thin summer straight jeans, white sneakers"),
    dict(key="f_summer_rain", g="F", season="summer", occ="RAIN", label="장마 · 레인재킷 + 반바지",
         items=dict(outer="C134", top="C001", bottom="C029", shoes="C141"),
         draw="thin yellow hooded rain jacket (open) over a white T-shirt, navy knee-length shorts, blue waterproof sneakers"),
    # 가을 4
    dict(key="f_autumn_basic", g="F", season="autumn", occ="DAILY", label="아이보리 긴팔 + 청바지",
         items=dict(top="C008", bottom="C034", shoes="C138"), src=("최종_4계절_추천복장_20261013", "outfit_autumn_340")),
    dict(key="f_autumn_leather", g="F", season="autumn", occ="DAILY", label="레더 재킷 + 미디 스커트",
         items=dict(outer="C056", top="C011", bottom="C097", shoes="C140"), src=("추가착장_4계절_20261014", "outfit_autumn_leather_skirt_340")),
    dict(key="f_autumn_office", g="F", season="autumn", occ="OFFICE", label="블레이저 + 셔츠 + 와이드 슬랙스",
         items=dict(outer="C053", top="C012", bottom="C094", shoes="C139"),
         draw="charcoal grey tailored blazer (open) over a white button shirt, beige wide slacks, brown loafers"),
    dict(key="f_autumn_knit", g="F", season="autumn", occ="DAILY", label="니트 + A라인 스커트",
         items=dict(top="C022", bottom="C098", shoes="C139"),
         draw="mustard yellow round-neck knit sweater, dark brown knee-length A-line skirt, black loafers with white socks"),
    # 겨울 4
    dict(key="f_winter_padding", g="F", season="winter", occ="DAILY", label="햄스터 모자 + 패딩",
         items=dict(outer="C066", top="C017", bottom="C043", shoes="C142"), src=("최종_4계절_추천복장_20261013", "outfit_winter_340")),
    dict(key="f_winter_halfcoat", g="F", season="winter", occ="DAILY", label="하프코트 + 버건디 스커트",
         items=dict(outer="C129", top="C022", bottom="C103", shoes="C140"), src=("추가착장_4계절_20261014", "outfit_winter_halfcoat_340")),
    dict(key="f_winter_longcoat", g="F", season="winter", occ="OFFICE", label="롱코트 + 터틀넥 + 슬랙스",
         items=dict(outer="C128", top="C025", bottom="C042", shoes="C140"),
         draw="long camel wool coat (open, to below the knees) over a cream turtleneck knit, black warm slacks, black ankle boots"),
    dict(key="f_winter_longpadding", g="F", season="winter", occ="DAILY", label="한파 · 롱패딩 + 기모 청바지",
         items=dict(outer="C067", top="C019", bottom="C036", shoes="C142"),
         draw="long navy puffy down padding coat (zipped, to the knees) with the hood down, a plain knit scarf, dark blue jeans, brown winter boots"),

    # ---------------- 남성 (16) ----------------
    # 봄 3
    dict(key="m_spring_zipup", g="M", season="spring", occ="DAILY", label="후드집업 + 조거",
         items=dict(outer="C051", top="C001", bottom="C045", shoes="C138"),
         draw="open grey zip-up hoodie over a white T-shirt, black jogger pants, white sneakers"),
    dict(key="m_spring_shirt", g="M", season="spring", occ="OFFICE", label="옥스퍼드 셔츠 + 치노",
         items=dict(top="C012", bottom="C039", shoes="C139"),
         draw="light blue oxford button shirt, beige chino pants, brown loafers"),
    dict(key="m_spring_denim", g="M", season="spring", occ="DAILY", label="데님 재킷 + 카고 팬츠",
         items=dict(outer="C054", top="C001", bottom="C044", shoes="C138"),
         draw="blue denim jacket (open) over a white T-shirt, khaki cargo pants, white sneakers"),
    # 여름 7
    dict(key="m_summer_tee", g="M", season="summer", occ="DAILY", label="반팔 + 버뮤다 반바지",
         items=dict(top="C001", bottom="C029", shoes="C138"),
         draw="light sky-blue short-sleeve T-shirt, beige knee-length bermuda shorts, white sneakers"),
    dict(key="m_summer_athleisure", g="M", season="summer", occ="EXERCISE", label="애슬레저",
         items=dict(top="C143", bottom="C149", shoes="C137"),
         draw="white athletic short-sleeve T-shirt, black running shorts, grey mesh sneakers with a small lime accent"),
    dict(key="m_summer_office", g="M", season="summer", occ="OFFICE", label="카라 반팔 + 쿨슬랙스",
         items=dict(top="C003", bottom="C040", shoes="C139"),
         draw="navy short-sleeve polo shirt with a collar, light grey slacks, brown loafers"),
    dict(key="m_summer_linen", g="M", season="summer", occ="DAILY", label="린넨 반팔 셔츠 + 린넨 바지",
         items=dict(top="C004", bottom="C041", shoes="C137"),
         draw="white short-sleeve linen shirt, light beige linen long pants, white mesh sneakers"),
    dict(key="m_summer_denim", g="M", season="summer", occ="DAILY", label="오버핏 반팔 + 쿨데님",
         items=dict(top="C002", bottom="C037", shoes="C137"),
         draw="oversized black short-sleeve T-shirt, light-blue straight summer jeans, white sneakers"),
    dict(key="m_summer_hawaiian", g="M", season="summer", occ="DAILY", label="하와이안 셔츠 + 린넨 반바지",
         items=dict(top="C005", bottom="C030", shoes="C137"),
         draw="short-sleeve hawaiian shirt with a simple big leaf pattern (mint and white), cream linen shorts, white sneakers"),
    dict(key="m_summer_rain", g="M", season="summer", occ="RAIN", label="장마 · 레인재킷 + 반바지",
         items=dict(outer="C134", top="C001", bottom="C028", shoes="C141"),
         draw="thin navy hooded rain jacket (open, hood down) over a white T-shirt, grey shorts, blue waterproof sneakers"),
    # 가을 3
    dict(key="m_autumn_sweat", g="M", season="autumn", occ="DAILY", label="맨투맨 + 청바지",
         items=dict(top="C017", bottom="C033", shoes="C138"),
         draw="ivory crew-neck sweatshirt, medium-blue straight jeans, brown canvas sneakers"),
    dict(key="m_autumn_blouson", g="M", season="autumn", occ="DAILY", label="블루종 + 치노",
         items=dict(outer="C058", top="C001", bottom="C039", shoes="C138"),
         draw="short navy blouson jacket (zipped halfway) over a white T-shirt, beige chino pants, white sneakers"),
    dict(key="m_autumn_office", g="M", season="autumn", occ="OFFICE", label="블레이저 + 셔츠 + 슬랙스",
         items=dict(outer="C053", top="C012", bottom="C038", shoes="C139"),
         draw="charcoal tailored blazer (open) over a white button shirt, dark grey slacks, black loafers"),
    # 겨울 3
    dict(key="m_winter_coat", g="M", season="winter", occ="OFFICE", label="롱코트 + 니트 + 슬랙스",
         items=dict(outer="C061", top="C022", bottom="C042", shoes="C139"),
         draw="knee-length camel wool coat (open) over a dark grey knit sweater, charcoal warm slacks, black loafers"),
    dict(key="m_winter_padding", g="M", season="winter", occ="DAILY", label="숏패딩 + 기모 청바지",
         items=dict(outer="C066", top="C019", bottom="C036", shoes="C142"),
         draw="puffy black short down padding jacket (zipped) over a grey hoodie with the hood out, dark blue jeans, brown winter boots"),
    dict(key="m_winter_duffle", g="M", season="winter", occ="DAILY", label="더플코트 + 터틀넥",
         items=dict(outer="C062", top="C025", bottom="C043", shoes="C140"),
         draw="navy duffle coat with toggle buttons (closed), cream turtleneck showing at the neck, grey wool wide pants, brown ankle boots"),
]


def new_sets(g, season):
    """그림을 새로 만들어야 하는 세트 (Gemini 한 장에 그릴 순서)."""
    return [s for s in SETS if s["g"] == g and s["season"] == season and not s.get("src")]
