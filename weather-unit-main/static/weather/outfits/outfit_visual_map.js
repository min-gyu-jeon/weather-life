window.OUTFIT_VISUAL_MAP = {
 "version": "2026-10-14",
 "source": "clothing-catalog.json v1.0.0",
 "howTo": "API outfits[0]와 sets(같은 성별)의 items를 비교해 점수가 가장 높은 세트의 그림을 보여 준다 (outfit_visual.js). 점수 = 아우터 종류·하의 모양 같음 각 4 · 운동/비 같음 각 3 · 칸별 아이콘 같음(상의·하의·원피스·아우터 2, 신발 1) · 완전히 같은 id +1. 아우터가 없거나 outerUsage가 WEAR가 아니면 아우터 없음. 칸마다 icons[items[id].icon]과 items[id].short(짧은 이름)를 보여 준다.",
 "notRecommended": {
  "note": "노출이 많은 옷 — 화면에는 반팔·운동용 상의로 바꿔 보여 준다. 백엔드 추천에서 빼 주기를 요청.",
  "items": {
   "C006": "민소매 러닝",
   "C007": "나시",
   "C072": "스트랩 나시",
   "C073": "끈나시",
   "C146": "헬스 나시",
   "C147": "스포츠 브라",
   "C148": "요가 탑"
  }
 },
 "icons": {
  "tee_short": {
   "label": "반팔 티",
   "file": "assets/icons/tee_short.svg"
  },
  "sport_tee": {
   "label": "기능성 티",
   "file": "assets/icons/sport_tee.svg"
  },
  "collar_tee": {
   "label": "카라티",
   "file": "assets/icons/collar_tee.svg"
  },
  "shirt_short": {
   "label": "반팔 셔츠",
   "file": "assets/icons/shirt_short.svg"
  },
  "knit_thin": {
   "label": "여름 니트",
   "file": "assets/icons/knit_thin.svg"
  },
  "tee_long": {
   "label": "긴팔 티",
   "file": "assets/icons/tee_long.svg"
  },
  "shirt": {
   "label": "셔츠",
   "file": "assets/icons/shirt.svg"
  },
  "check_shirt": {
   "label": "체크·데님 셔츠",
   "file": "assets/icons/check_shirt.svg"
  },
  "blouse": {
   "label": "블라우스",
   "file": "assets/icons/blouse.svg"
  },
  "sweatshirt": {
   "label": "맨투맨",
   "file": "assets/icons/sweatshirt.svg"
  },
  "hoodie": {
   "label": "후드티",
   "file": "assets/icons/hoodie.svg"
  },
  "knit": {
   "label": "니트",
   "file": "assets/icons/knit.svg"
  },
  "turtleneck": {
   "label": "터틀넥",
   "file": "assets/icons/turtleneck.svg"
  },
  "knit_vest": {
   "label": "조끼·뷔스티에",
   "file": "assets/icons/knit_vest.svg"
  },
  "pajama": {
   "label": "잠옷·라운지웨어",
   "file": "assets/icons/pajama.svg"
  },
  "shorts": {
   "label": "반바지",
   "file": "assets/icons/shorts.svg"
  },
  "sport_shorts": {
   "label": "운동 반바지",
   "file": "assets/icons/sport_shorts.svg"
  },
  "jeans": {
   "label": "청바지",
   "file": "assets/icons/jeans.svg"
  },
  "slacks": {
   "label": "슬랙스·면바지",
   "file": "assets/icons/slacks.svg"
  },
  "cargo": {
   "label": "카고 팬츠",
   "file": "assets/icons/cargo.svg"
  },
  "jogger": {
   "label": "조거·트레이닝",
   "file": "assets/icons/jogger.svg"
  },
  "warm_pants": {
   "label": "기모·울 바지",
   "file": "assets/icons/warm_pants.svg"
  },
  "leggings": {
   "label": "레깅스",
   "file": "assets/icons/leggings.svg"
  },
  "skirt_mini": {
   "label": "미니 스커트",
   "file": "assets/icons/skirt_mini.svg"
  },
  "pleats": {
   "label": "플리츠 스커트",
   "file": "assets/icons/pleats.svg"
  },
  "skirt_midi": {
   "label": "미디 스커트",
   "file": "assets/icons/skirt_midi.svg"
  },
  "skirt_long": {
   "label": "롱스커트",
   "file": "assets/icons/skirt_long.svg"
  },
  "leather_skirt": {
   "label": "가죽 스커트",
   "file": "assets/icons/leather_skirt.svg"
  },
  "dress_sleeveless": {
   "label": "민소매 원피스",
   "file": "assets/icons/dress_sleeveless.svg"
  },
  "dress_short": {
   "label": "반팔 원피스",
   "file": "assets/icons/dress_short.svg"
  },
  "dress_long": {
   "label": "롱·셔츠 원피스",
   "file": "assets/icons/dress_long.svg"
  },
  "dress_knit": {
   "label": "니트 원피스",
   "file": "assets/icons/dress_knit.svg"
  },
  "bustier_dress": {
   "label": "뷔스티에·멜빵치마",
   "file": "assets/icons/bustier_dress.svg"
  },
  "jumpsuit": {
   "label": "점프수트·멜빵바지",
   "file": "assets/icons/jumpsuit.svg"
  },
  "cardigan": {
   "label": "가디건",
   "file": "assets/icons/cardigan.svg"
  },
  "windbreaker": {
   "label": "바람막이",
   "file": "assets/icons/windbreaker.svg"
  },
  "zipup": {
   "label": "집업",
   "file": "assets/icons/zipup.svg"
  },
  "jacket_casual": {
   "label": "사파리·야상",
   "file": "assets/icons/jacket_casual.svg"
  },
  "blazer": {
   "label": "블레이저",
   "file": "assets/icons/blazer.svg"
  },
  "denim_jacket": {
   "label": "데님 재킷",
   "file": "assets/icons/denim_jacket.svg"
  },
  "leather_jacket": {
   "label": "가죽 재킷",
   "file": "assets/icons/leather_jacket.svg"
  },
  "blouson": {
   "label": "블루종·항공점퍼",
   "file": "assets/icons/blouson.svg"
  },
  "trench": {
   "label": "트렌치코트",
   "file": "assets/icons/trench.svg"
  },
  "coat_short": {
   "label": "숏코트",
   "file": "assets/icons/coat_short.svg"
  },
  "coat_long": {
   "label": "롱코트",
   "file": "assets/icons/coat_long.svg"
  },
  "light_padding": {
   "label": "경량패딩·플리스",
   "file": "assets/icons/light_padding.svg"
  },
  "padding": {
   "label": "패딩",
   "file": "assets/icons/padding.svg"
  },
  "fur": {
   "label": "무스탕·퍼",
   "file": "assets/icons/fur.svg"
  },
  "rain": {
   "label": "레인재킷",
   "file": "assets/icons/rain.svg"
  },
  "sneakers": {
   "label": "운동화",
   "file": "assets/icons/sneakers.svg"
  },
  "mesh_sneakers": {
   "label": "통풍 운동화",
   "file": "assets/icons/mesh_sneakers.svg"
  },
  "loafers": {
   "label": "로퍼",
   "file": "assets/icons/loafers.svg"
  },
  "boots": {
   "label": "앵클부츠",
   "file": "assets/icons/boots.svg"
  },
  "rain_sneakers": {
   "label": "방수 운동화",
   "file": "assets/icons/rain_sneakers.svg"
  },
  "winter_boots": {
   "label": "방한화",
   "file": "assets/icons/winter_boots.svg"
  },
  "thermal": {
   "label": "따뜻한 상하의",
   "file": "assets/icons/thermal.svg"
  }
 },
 "items": {
  "C001": {
   "name": "기본 반소매 티셔츠",
   "short": "반팔 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C002": {
   "name": "오버핏 반소매 티셔츠",
   "short": "오버핏 반팔티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C003": {
   "name": "카라 반소매 티셔츠",
   "short": "카라티",
   "replaced": false,
   "slot": "TOP",
   "icon": "collar_tee",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C004": {
   "name": "린넨 반소매 셔츠",
   "short": "린넨 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C005": {
   "name": "하와이안 셔츠",
   "short": "하와이안 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C006": {
   "name": "민소매 러닝",
   "short": "시원한 반팔",
   "replaced": true,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C007": {
   "name": "나시",
   "short": "시원한 반팔",
   "replaced": true,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C008": {
   "name": "기본 롱슬리브",
   "short": "긴팔 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_long",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C009": {
   "name": "헨리넥 롱슬리브",
   "short": "헨리넥 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_long",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C010": {
   "name": "얇은 카라 티셔츠",
   "short": "얇은 카라티",
   "replaced": false,
   "slot": "TOP",
   "icon": "collar_tee",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C011": {
   "name": "드레스 셔츠",
   "short": "드레스 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C012": {
   "name": "옥스퍼드 셔츠",
   "short": "옥스퍼드 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C013": {
   "name": "캐주얼 셔츠",
   "short": "캐주얼 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C014": {
   "name": "린넨 긴소매 셔츠",
   "short": "린넨 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C015": {
   "name": "데님 셔츠",
   "short": "데님 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "check_shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C016": {
   "name": "플라넬 체크 셔츠",
   "short": "체크 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "check_shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C017": {
   "name": "맨투맨",
   "short": "맨투맨",
   "replaced": false,
   "slot": "TOP",
   "icon": "sweatshirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C018": {
   "name": "세미오버 맨투맨",
   "short": "맨투맨",
   "replaced": false,
   "slot": "TOP",
   "icon": "sweatshirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C019": {
   "name": "후드 티셔츠",
   "short": "후드 티셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "hoodie",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C020": {
   "name": "여름용 쿨니트",
   "short": "쿨니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_thin",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C021": {
   "name": "린넨 니트",
   "short": "린넨 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_thin",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C022": {
   "name": "라운드넥 니트",
   "short": "니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C023": {
   "name": "V넥 니트",
   "short": "V넥 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C024": {
   "name": "모크넥 니트",
   "short": "모크넥 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C025": {
   "name": "터틀넥 니트",
   "short": "터틀넥 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "turtleneck",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C026": {
   "name": "굵은 케이블 니트",
   "short": "케이블 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "turtleneck",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C027": {
   "name": "니트 조끼",
   "short": "니트 조끼",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_vest",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C028": {
   "name": "숏 팬츠",
   "short": "숏 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C029": {
   "name": "버뮤다 반바지",
   "short": "버뮤다 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C030": {
   "name": "린넨 반바지",
   "short": "린넨 반바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C031": {
   "name": "트레이닝 반바지",
   "short": "운동 반바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "sport_shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C032": {
   "name": "생지 데님",
   "short": "생지 데님",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C033": {
   "name": "워싱 청바지",
   "short": "워싱 청바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C034": {
   "name": "스트레이트 청바지",
   "short": "일자 청바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C035": {
   "name": "와이드 청바지",
   "short": "와이드 청바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C036": {
   "name": "기모 청바지",
   "short": "기모 청바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "warm_pants",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C037": {
   "name": "여름용 쿨데님",
   "short": "쿨데님",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C038": {
   "name": "사계절 슬랙스",
   "short": "슬랙스",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "slacks",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C039": {
   "name": "치노 팬츠",
   "short": "치노 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "slacks",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C040": {
   "name": "쿨슬랙스",
   "short": "쿨슬랙스",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "slacks",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C041": {
   "name": "얇은 린넨 긴바지",
   "short": "린넨 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "slacks",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C042": {
   "name": "기모 슬랙스",
   "short": "기모 슬랙스",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "warm_pants",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C043": {
   "name": "울 와이드 팬츠",
   "short": "울 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "warm_pants",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C044": {
   "name": "카고 팬츠",
   "short": "카고 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "cargo",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C045": {
   "name": "조거 팬츠",
   "short": "조거 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jogger",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C046": {
   "name": "코듀로이 바지",
   "short": "코듀로이 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "warm_pants",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C047": {
   "name": "바람막이",
   "short": "바람막이",
   "replaced": false,
   "slot": "OUTER",
   "icon": "windbreaker",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C048": {
   "name": "사파리 재킷",
   "short": "사파리 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "jacket_casual",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C049": {
   "name": "셔츠형 재킷",
   "short": "셔츠형 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "jacket_casual",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C050": {
   "name": "트랙 재킷",
   "short": "트랙 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "zipup",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C051": {
   "name": "집업 후드티",
   "short": "집업 후드티",
   "replaced": false,
   "slot": "OUTER",
   "icon": "zipup",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C052": {
   "name": "가디건",
   "short": "가디건",
   "replaced": false,
   "slot": "OUTER",
   "icon": "cardigan",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C053": {
   "name": "테일러드 블레이저",
   "short": "블레이저",
   "replaced": false,
   "slot": "OUTER",
   "icon": "blazer",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C054": {
   "name": "데님 재킷",
   "short": "데님 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "denim_jacket",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C055": {
   "name": "트러커 재킷",
   "short": "트러커 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "denim_jacket",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C056": {
   "name": "가죽 라이더 재킷",
   "short": "라이더 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "leather_jacket",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C057": {
   "name": "MA-1 항공점퍼",
   "short": "항공점퍼",
   "replaced": false,
   "slot": "OUTER",
   "icon": "blouson",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C058": {
   "name": "블루종",
   "short": "블루종",
   "replaced": false,
   "slot": "OUTER",
   "icon": "blouson",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C059": {
   "name": "트렌치코트",
   "short": "트렌치코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "trench",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C060": {
   "name": "울 숏코트",
   "short": "울 숏코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_short",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C061": {
   "name": "체스터필드 롱코트",
   "short": "롱코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_long",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C062": {
   "name": "더플코트",
   "short": "더플코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_short",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C063": {
   "name": "피코트",
   "short": "피코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_short",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C064": {
   "name": "경량 패딩 재킷",
   "short": "경량 패딩",
   "replaced": false,
   "slot": "OUTER",
   "icon": "light_padding",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C065": {
   "name": "경량 패딩 조끼",
   "short": "패딩 조끼",
   "replaced": false,
   "slot": "OUTER",
   "icon": "light_padding",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C066": {
   "name": "숏패딩",
   "short": "숏패딩",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C067": {
   "name": "롱패딩",
   "short": "롱패딩",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C068": {
   "name": "다운 파카",
   "short": "다운 파카",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C069": {
   "name": "무스탕",
   "short": "무스탕",
   "replaced": false,
   "slot": "OUTER",
   "icon": "fur",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C070": {
   "name": "플리스 재킷",
   "short": "플리스 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "light_padding",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C071": {
   "name": "발열 내의 상하의",
   "short": "따뜻한 상하의",
   "replaced": false,
   "slot": "BASE_LAYER",
   "icon": "thermal",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C072": {
   "name": "스트랩 나시",
   "short": "시원한 반팔",
   "replaced": true,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C073": {
   "name": "끈나시",
   "short": "시원한 반팔",
   "replaced": true,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C074": {
   "name": "크롭 반소매 티셔츠",
   "short": "크롭 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C075": {
   "name": "루즈핏 반소매 티셔츠",
   "short": "루즈핏 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C076": {
   "name": "린넨 반소매 블라우스",
   "short": "린넨 블라우스",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt_short",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C077": {
   "name": "뷔스티에",
   "short": "뷔스티에",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_vest",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C078": {
   "name": "시스루 긴소매 티셔츠",
   "short": "시스루 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_long",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C079": {
   "name": "오프숄더 긴소매 티셔츠",
   "short": "오프숄더 티",
   "replaced": false,
   "slot": "TOP",
   "icon": "tee_long",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C080": {
   "name": "오버핏 셔츠",
   "short": "오버핏 셔츠",
   "replaced": false,
   "slot": "TOP",
   "icon": "shirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C081": {
   "name": "시폰 블라우스",
   "short": "시폰 블라우스",
   "replaced": false,
   "slot": "TOP",
   "icon": "blouse",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C082": {
   "name": "레이스 블라우스",
   "short": "레이스 블라우스",
   "replaced": false,
   "slot": "TOP",
   "icon": "blouse",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C083": {
   "name": "프릴 블라우스",
   "short": "프릴 블라우스",
   "replaced": false,
   "slot": "TOP",
   "icon": "blouse",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C084": {
   "name": "실크 블라우스",
   "short": "실크 블라우스",
   "replaced": false,
   "slot": "TOP",
   "icon": "blouse",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C085": {
   "name": "크롭 맨투맨",
   "short": "크롭 맨투맨",
   "replaced": false,
   "slot": "TOP",
   "icon": "sweatshirt",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C086": {
   "name": "여름용 그물 니트",
   "short": "그물 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_thin",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C087": {
   "name": "반소매 니트",
   "short": "반소매 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit_thin",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C088": {
   "name": "오프숄더 니트",
   "short": "오프숄더 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C089": {
   "name": "골지 니트",
   "short": "골지 니트",
   "replaced": false,
   "slot": "TOP",
   "icon": "knit",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C090": {
   "name": "핫팬츠",
   "short": "핫팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C091": {
   "name": "5부 반바지",
   "short": "5부 반바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C092": {
   "name": "스키니진",
   "short": "스키니진",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C093": {
   "name": "부츠컷 팬츠",
   "short": "부츠컷 팬츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jeans",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C094": {
   "name": "와이드 슬랙스",
   "short": "와이드 슬랙스",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "slacks",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C095": {
   "name": "미니스커트",
   "short": "미니스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_mini",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C096": {
   "name": "데님 스커트",
   "short": "데님 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_mini",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C097": {
   "name": "미디스커트",
   "short": "미디스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_midi",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C098": {
   "name": "A라인 스커트",
   "short": "A라인 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_midi",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C099": {
   "name": "H라인 스커트",
   "short": "H라인 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_midi",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C100": {
   "name": "롱스커트",
   "short": "롱스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_long",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C101": {
   "name": "플리츠 스커트",
   "short": "플리츠 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pleats",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C102": {
   "name": "밴딩 스커트",
   "short": "밴딩 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_long",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C103": {
   "name": "울 미디스커트",
   "short": "울 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_midi",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C104": {
   "name": "코듀로이 롱스커트",
   "short": "코듀로이 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "skirt_long",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C105": {
   "name": "가죽 스커트",
   "short": "가죽 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "leather_skirt",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": false
  },
  "C106": {
   "name": "끈나시 원피스",
   "short": "여름 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_sleeveless",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C107": {
   "name": "반소매 원피스",
   "short": "반팔 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_short",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C108": {
   "name": "린넨 원피스",
   "short": "린넨 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_sleeveless",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C109": {
   "name": "시폰 원피스",
   "short": "시폰 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_short",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C110": {
   "name": "롱 원피스",
   "short": "롱 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_long",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C111": {
   "name": "미니 원피스",
   "short": "미니 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_short",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C112": {
   "name": "셔츠 원피스",
   "short": "셔츠 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_long",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C113": {
   "name": "니트 원피스",
   "short": "니트 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_knit",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C114": {
   "name": "트위드 원피스",
   "short": "트위드 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "dress_knit",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C115": {
   "name": "뷔스티에 원피스",
   "short": "뷔스티에 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "bustier_dress",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C116": {
   "name": "멜빵치마",
   "short": "멜빵치마",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "bustier_dress",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C117": {
   "name": "점프수트",
   "short": "점프수트",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "jumpsuit",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C118": {
   "name": "멜빵바지",
   "short": "멜빵바지",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "jumpsuit",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C119": {
   "name": "시스루 가디건",
   "short": "시스루 가디건",
   "replaced": false,
   "slot": "OUTER",
   "icon": "cardigan",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C120": {
   "name": "크롭 가디건",
   "short": "크롭 가디건",
   "replaced": false,
   "slot": "OUTER",
   "icon": "cardigan",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C121": {
   "name": "볼레로 가디건",
   "short": "볼레로 가디건",
   "replaced": false,
   "slot": "OUTER",
   "icon": "cardigan",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C122": {
   "name": "크롭 후드 집업",
   "short": "크롭 집업",
   "replaced": false,
   "slot": "OUTER",
   "icon": "zipup",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C123": {
   "name": "트랙 집업",
   "short": "트랙 집업",
   "replaced": false,
   "slot": "OUTER",
   "icon": "zipup",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C124": {
   "name": "트위드 재킷",
   "short": "트위드 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "blazer",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C125": {
   "name": "야상 재킷",
   "short": "야상 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "jacket_casual",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C126": {
   "name": "가죽 트렌치코트",
   "short": "가죽 트렌치",
   "replaced": false,
   "slot": "OUTER",
   "icon": "leather_jacket",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C127": {
   "name": "핸드메이드 코트",
   "short": "핸드메이드 코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_long",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C128": {
   "name": "울 롱코트",
   "short": "울 롱코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_long",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C129": {
   "name": "숏코트",
   "short": "숏코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "coat_short",
   "lower": null,
   "outerKind": "COAT",
   "sport": false
  },
  "C130": {
   "name": "퍼 코트",
   "short": "퍼 코트",
   "replaced": false,
   "slot": "OUTER",
   "icon": "fur",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C131": {
   "name": "크롭 패딩",
   "short": "크롭 패딩",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C132": {
   "name": "헤비 다운",
   "short": "헤비 다운",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C133": {
   "name": "경량 패딩 베스트",
   "short": "패딩 조끼",
   "replaced": false,
   "slot": "OUTER",
   "icon": "light_padding",
   "lower": null,
   "outerKind": "JACKET",
   "sport": false
  },
  "C134": {
   "name": "후드형 초경량 방수 레인재킷",
   "short": "레인재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "rain",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C135": {
   "name": "후드형 방수 방풍 재킷",
   "short": "방풍 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "rain",
   "lower": null,
   "outerKind": "THIN",
   "sport": false
  },
  "C136": {
   "name": "후드형 발수 다운 파카",
   "short": "다운 파카",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": false
  },
  "C137": {
   "name": "통풍 운동화",
   "short": "통풍 운동화",
   "replaced": false,
   "slot": "SHOES",
   "icon": "mesh_sneakers",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C138": {
   "name": "기본 운동화",
   "short": "기본 운동화",
   "replaced": false,
   "slot": "SHOES",
   "icon": "sneakers",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C139": {
   "name": "로퍼",
   "short": "로퍼",
   "replaced": false,
   "slot": "SHOES",
   "icon": "loafers",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C140": {
   "name": "보온 앵클부츠",
   "short": "앵클부츠",
   "replaced": false,
   "slot": "SHOES",
   "icon": "boots",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C141": {
   "name": "방수 운동화",
   "short": "방수 운동화",
   "replaced": false,
   "slot": "SHOES",
   "icon": "rain_sneakers",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C142": {
   "name": "접지력 있는 방수 방한화",
   "short": "방한화",
   "replaced": false,
   "slot": "SHOES",
   "icon": "winter_boots",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C143": {
   "name": "기능성 반소매 티셔츠",
   "short": "기능성 반팔",
   "replaced": false,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C144": {
   "name": "기능성 긴소매 티셔츠",
   "short": "기능성 긴팔",
   "replaced": false,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C145": {
   "name": "겨울용 기능성 긴소매",
   "short": "보온 긴팔",
   "replaced": false,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C146": {
   "name": "헬스 나시",
   "short": "운동용 반팔",
   "replaced": true,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C147": {
   "name": "스포츠 브라",
   "short": "운동용 상의",
   "replaced": true,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C148": {
   "name": "요가 탑",
   "short": "운동용 상의",
   "replaced": true,
   "slot": "TOP",
   "icon": "sport_tee",
   "lower": null,
   "outerKind": null,
   "sport": true
  },
  "C149": {
   "name": "러닝 쇼츠",
   "short": "러닝 쇼츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "sport_shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": true
  },
  "C150": {
   "name": "바이커 쇼츠",
   "short": "바이커 쇼츠",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "sport_shorts",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": true
  },
  "C151": {
   "name": "운동용 레깅스",
   "short": "레깅스",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "leggings",
   "lower": "PANTS",
   "outerKind": null,
   "sport": true
  },
  "C152": {
   "name": "얇은 트레이닝 긴바지",
   "short": "트레이닝 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jogger",
   "lower": "PANTS",
   "outerKind": null,
   "sport": true
  },
  "C153": {
   "name": "기모 트레이닝 팬츠",
   "short": "기모 트레이닝",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "jogger",
   "lower": "PANTS",
   "outerKind": null,
   "sport": true
  },
  "C154": {
   "name": "테니스 스커트",
   "short": "테니스 스커트",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pleats",
   "lower": "SKIRT",
   "outerKind": null,
   "sport": true
  },
  "C155": {
   "name": "운동용 바람막이",
   "short": "바람막이",
   "replaced": false,
   "slot": "OUTER",
   "icon": "windbreaker",
   "lower": null,
   "outerKind": "THIN",
   "sport": true
  },
  "C156": {
   "name": "운동용 보온 재킷",
   "short": "보온 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "blouson",
   "lower": null,
   "outerKind": "JACKET",
   "sport": true
  },
  "C157": {
   "name": "운동용 방한 재킷",
   "short": "방한 재킷",
   "replaced": false,
   "slot": "OUTER",
   "icon": "padding",
   "lower": null,
   "outerKind": "PADDING",
   "sport": true
  },
  "C158": {
   "name": "반소매 파자마 상의",
   "short": "잠옷 상의",
   "replaced": false,
   "slot": "TOP",
   "icon": "pajama",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C159": {
   "name": "얇은 라운지 반소매",
   "short": "라운지 반팔",
   "replaced": false,
   "slot": "TOP",
   "icon": "pajama",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C160": {
   "name": "긴소매 파자마 상의",
   "short": "잠옷 상의",
   "replaced": false,
   "slot": "TOP",
   "icon": "pajama",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C161": {
   "name": "라운지 긴소매",
   "short": "라운지 긴팔",
   "replaced": false,
   "slot": "TOP",
   "icon": "pajama",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C162": {
   "name": "보온 수면 상의",
   "short": "수면 상의",
   "replaced": false,
   "slot": "TOP",
   "icon": "pajama",
   "lower": null,
   "outerKind": null,
   "sport": false
  },
  "C163": {
   "name": "파자마 반바지",
   "short": "잠옷 반바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pajama",
   "lower": "SHORTS",
   "outerKind": null,
   "sport": false
  },
  "C164": {
   "name": "얇은 파자마 긴바지",
   "short": "잠옷 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pajama",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C165": {
   "name": "파자마 긴바지",
   "short": "잠옷 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pajama",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C166": {
   "name": "라운지 긴바지",
   "short": "라운지 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pajama",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C167": {
   "name": "보온 수면바지",
   "short": "수면 바지",
   "replaced": false,
   "slot": "BOTTOM",
   "icon": "pajama",
   "lower": "PANTS",
   "outerKind": null,
   "sport": false
  },
  "C168": {
   "name": "반소매 원피스 잠옷",
   "short": "원피스 잠옷",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "pajama",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C169": {
   "name": "긴소매 원피스 잠옷",
   "short": "원피스 잠옷",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "pajama",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  },
  "C170": {
   "name": "보온 원피스 잠옷",
   "short": "수면 원피스",
   "replaced": false,
   "slot": "ONE_PIECE",
   "icon": "pajama",
   "lower": "ONEPIECE",
   "outerKind": null,
   "sport": false
  }
 },
 "sets": {
  "f_spring_basic": {
   "gender": "F",
   "season": "spring",
   "occasion": "DAILY",
   "label": "여 · 봄 일상 · 라벤더 가디건 + 흰 원피스",
   "items": {
    "outer": "C120",
    "onePiece": "C111",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/f_spring_basic_340_poster.png",
   "mp4": "assets/characters/f_spring_basic_340.mp4",
   "gif": "assets/characters/f_spring_basic_340.gif"
  },
  "f_spring_campus": {
   "gender": "F",
   "season": "spring",
   "occasion": "DAILY",
   "label": "여 · 봄 일상 · 후드집업 + 스웨트 팬츠",
   "items": {
    "outer": "C122",
    "top": "C001",
    "bottom": "C045",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/f_spring_campus_340_poster.png",
   "mp4": "assets/characters/f_spring_campus_340.mp4",
   "gif": "assets/characters/f_spring_campus_340.gif"
  },
  "f_spring_trench": {
   "gender": "F",
   "season": "spring",
   "occasion": "OFFICE",
   "label": "여 · 봄 출근 · 트렌치코트 + 블라우스 + 슬랙스",
   "items": {
    "outer": "C059",
    "top": "C081",
    "bottom": "C094",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/f_spring_trench_340_poster.png",
   "mp4": "assets/characters/f_spring_trench_340.mp4",
   "gif": "assets/characters/f_spring_trench_340.gif"
  },
  "f_spring_rain": {
   "gender": "F",
   "season": "spring",
   "occasion": "RAIN",
   "label": "여 · 봄 비 · 봄비 · 방풍 재킷 + 청바지",
   "items": {
    "outer": "C135",
    "top": "C008",
    "bottom": "C033",
    "shoes": "C141"
   },
   "status": "ready",
   "poster": "assets/characters/f_spring_rain_340_poster.png",
   "mp4": "assets/characters/f_spring_rain_340.mp4",
   "gif": "assets/characters/f_spring_rain_340.gif"
  },
  "f_summer_basic": {
   "gender": "F",
   "season": "summer",
   "occasion": "DAILY",
   "label": "여 · 여름 일상 · 라벤더 티 + 돌핀팬츠",
   "items": {
    "top": "C001",
    "bottom": "C028",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_basic_340_poster.png",
   "mp4": "assets/characters/f_summer_basic_340.mp4",
   "gif": "assets/characters/f_summer_basic_340.gif"
  },
  "f_summer_athleisure": {
   "gender": "F",
   "season": "summer",
   "occasion": "EXERCISE",
   "label": "여 · 여름 운동 · 애슬레저 (기능성 반팔 + 러닝 쇼츠)",
   "items": {
    "top": "C143",
    "bottom": "C149",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_athleisure_340_poster.png",
   "mp4": "assets/characters/f_summer_athleisure_340.mp4",
   "gif": "assets/characters/f_summer_athleisure_340.gif"
  },
  "f_summer_onepiece": {
   "gender": "F",
   "season": "summer",
   "occasion": "DAILY",
   "label": "여 · 여름 일상 · 반팔 원피스",
   "items": {
    "onePiece": "C107",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_onepiece_340_poster.png",
   "mp4": "assets/characters/f_summer_onepiece_340.mp4",
   "gif": "assets/characters/f_summer_onepiece_340.gif"
  },
  "f_summer_office": {
   "gender": "F",
   "season": "summer",
   "occasion": "OFFICE",
   "label": "여 · 여름 출근 · 린넨 블라우스 + 쿨슬랙스",
   "items": {
    "top": "C076",
    "bottom": "C040",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_office_340_poster.png",
   "mp4": "assets/characters/f_summer_office_340.mp4",
   "gif": "assets/characters/f_summer_office_340.gif"
  },
  "f_summer_linen": {
   "gender": "F",
   "season": "summer",
   "occasion": "DAILY",
   "label": "여 · 여름 일상 · 린넨 셔츠 + 버뮤다 반바지",
   "items": {
    "top": "C004",
    "bottom": "C091",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_linen_340_poster.png",
   "mp4": "assets/characters/f_summer_linen_340.mp4",
   "gif": "assets/characters/f_summer_linen_340.gif"
  },
  "f_summer_skirt": {
   "gender": "F",
   "season": "summer",
   "occasion": "DAILY",
   "label": "여 · 여름 일상 · 루즈핏 반팔 + 롱스커트",
   "items": {
    "top": "C075",
    "bottom": "C100",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_skirt_340_poster.png",
   "mp4": "assets/characters/f_summer_skirt_340.mp4",
   "gif": "assets/characters/f_summer_skirt_340.gif"
  },
  "f_summer_denim": {
   "gender": "F",
   "season": "summer",
   "occasion": "DAILY",
   "label": "여 · 여름 일상 · 오버핏 반팔 + 쿨데님",
   "items": {
    "top": "C002",
    "bottom": "C037",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_denim_340_poster.png",
   "mp4": "assets/characters/f_summer_denim_340.mp4",
   "gif": "assets/characters/f_summer_denim_340.gif"
  },
  "f_summer_rain": {
   "gender": "F",
   "season": "summer",
   "occasion": "RAIN",
   "label": "여 · 여름 비 · 장마 · 레인재킷 + 반바지",
   "items": {
    "outer": "C134",
    "top": "C001",
    "bottom": "C029",
    "shoes": "C141"
   },
   "status": "ready",
   "poster": "assets/characters/f_summer_rain_340_poster.png",
   "mp4": "assets/characters/f_summer_rain_340.mp4",
   "gif": "assets/characters/f_summer_rain_340.gif"
  },
  "f_autumn_basic": {
   "gender": "F",
   "season": "autumn",
   "occasion": "DAILY",
   "label": "여 · 가을 일상 · 아이보리 긴팔 + 청바지",
   "items": {
    "top": "C008",
    "bottom": "C034",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/f_autumn_basic_340_poster.png",
   "mp4": "assets/characters/f_autumn_basic_340.mp4",
   "gif": "assets/characters/f_autumn_basic_340.gif"
  },
  "f_autumn_leather": {
   "gender": "F",
   "season": "autumn",
   "occasion": "DAILY",
   "label": "여 · 가을 일상 · 레더 재킷 + 미디 스커트",
   "items": {
    "outer": "C056",
    "top": "C011",
    "bottom": "C097",
    "shoes": "C140"
   },
   "status": "ready",
   "poster": "assets/characters/f_autumn_leather_340_poster.png",
   "mp4": "assets/characters/f_autumn_leather_340.mp4",
   "gif": "assets/characters/f_autumn_leather_340.gif"
  },
  "f_autumn_office": {
   "gender": "F",
   "season": "autumn",
   "occasion": "OFFICE",
   "label": "여 · 가을 출근 · 블레이저 + 셔츠 + 와이드 슬랙스",
   "items": {
    "outer": "C053",
    "top": "C012",
    "bottom": "C094",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/f_autumn_office_340_poster.png",
   "mp4": "assets/characters/f_autumn_office_340.mp4",
   "gif": "assets/characters/f_autumn_office_340.gif"
  },
  "f_autumn_knit": {
   "gender": "F",
   "season": "autumn",
   "occasion": "DAILY",
   "label": "여 · 가을 일상 · 니트 + A라인 스커트",
   "items": {
    "top": "C022",
    "bottom": "C098",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/f_autumn_knit_340_poster.png",
   "mp4": "assets/characters/f_autumn_knit_340.mp4",
   "gif": "assets/characters/f_autumn_knit_340.gif"
  },
  "f_winter_padding": {
   "gender": "F",
   "season": "winter",
   "occasion": "DAILY",
   "label": "여 · 겨울 일상 · 숏패딩 + 맨투맨 + 울 팬츠",
   "items": {
    "outer": "C066",
    "top": "C017",
    "bottom": "C043",
    "shoes": "C142"
   },
   "status": "ready",
   "poster": "assets/characters/f_winter_padding_340_poster.png",
   "mp4": "assets/characters/f_winter_padding_340.mp4",
   "gif": "assets/characters/f_winter_padding_340.gif"
  },
  "f_winter_halfcoat": {
   "gender": "F",
   "season": "winter",
   "occasion": "DAILY",
   "label": "여 · 겨울 일상 · 하프코트 + 버건디 스커트",
   "items": {
    "outer": "C129",
    "top": "C022",
    "bottom": "C103",
    "shoes": "C140"
   },
   "status": "ready",
   "poster": "assets/characters/f_winter_halfcoat_340_poster.png",
   "mp4": "assets/characters/f_winter_halfcoat_340.mp4",
   "gif": "assets/characters/f_winter_halfcoat_340.gif"
  },
  "f_winter_longcoat": {
   "gender": "F",
   "season": "winter",
   "occasion": "OFFICE",
   "label": "여 · 겨울 출근 · 롱코트 + 터틀넥 + 슬랙스",
   "items": {
    "outer": "C128",
    "top": "C025",
    "bottom": "C042",
    "shoes": "C140"
   },
   "status": "ready",
   "poster": "assets/characters/f_winter_longcoat_340_poster.png",
   "mp4": "assets/characters/f_winter_longcoat_340.mp4",
   "gif": "assets/characters/f_winter_longcoat_340.gif"
  },
  "f_winter_longpadding": {
   "gender": "F",
   "season": "winter",
   "occasion": "DAILY",
   "label": "여 · 겨울 일상 · 한파 · 롱패딩 + 기모 청바지",
   "items": {
    "outer": "C067",
    "top": "C019",
    "bottom": "C036",
    "shoes": "C142"
   },
   "status": "ready",
   "poster": "assets/characters/f_winter_longpadding_340_poster.png",
   "mp4": "assets/characters/f_winter_longpadding_340.mp4",
   "gif": "assets/characters/f_winter_longpadding_340.gif"
  },
  "m_spring_zipup": {
   "gender": "M",
   "season": "spring",
   "occasion": "DAILY",
   "label": "남 · 봄 일상 · 후드집업 + 조거",
   "items": {
    "outer": "C051",
    "top": "C001",
    "bottom": "C045",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/m_spring_zipup_340_poster.png",
   "mp4": "assets/characters/m_spring_zipup_340.mp4",
   "gif": "assets/characters/m_spring_zipup_340.gif"
  },
  "m_spring_shirt": {
   "gender": "M",
   "season": "spring",
   "occasion": "OFFICE",
   "label": "남 · 봄 출근 · 옥스퍼드 셔츠 + 치노",
   "items": {
    "top": "C012",
    "bottom": "C039",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/m_spring_shirt_340_poster.png",
   "mp4": "assets/characters/m_spring_shirt_340.mp4",
   "gif": "assets/characters/m_spring_shirt_340.gif"
  },
  "m_spring_denim": {
   "gender": "M",
   "season": "spring",
   "occasion": "DAILY",
   "label": "남 · 봄 일상 · 데님 재킷 + 카고 팬츠",
   "items": {
    "outer": "C054",
    "top": "C001",
    "bottom": "C044",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/m_spring_denim_340_poster.png",
   "mp4": "assets/characters/m_spring_denim_340.mp4",
   "gif": "assets/characters/m_spring_denim_340.gif"
  },
  "m_summer_tee": {
   "gender": "M",
   "season": "summer",
   "occasion": "DAILY",
   "label": "남 · 여름 일상 · 반팔 + 버뮤다 반바지",
   "items": {
    "top": "C001",
    "bottom": "C029",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_tee_340_poster.png",
   "mp4": "assets/characters/m_summer_tee_340.mp4",
   "gif": "assets/characters/m_summer_tee_340.gif"
  },
  "m_summer_athleisure": {
   "gender": "M",
   "season": "summer",
   "occasion": "EXERCISE",
   "label": "남 · 여름 운동 · 애슬레저",
   "items": {
    "top": "C143",
    "bottom": "C149",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_athleisure_340_poster.png",
   "mp4": "assets/characters/m_summer_athleisure_340.mp4",
   "gif": "assets/characters/m_summer_athleisure_340.gif"
  },
  "m_summer_office": {
   "gender": "M",
   "season": "summer",
   "occasion": "OFFICE",
   "label": "남 · 여름 출근 · 카라 반팔 + 쿨슬랙스",
   "items": {
    "top": "C003",
    "bottom": "C040",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_office_340_poster.png",
   "mp4": "assets/characters/m_summer_office_340.mp4",
   "gif": "assets/characters/m_summer_office_340.gif"
  },
  "m_summer_linen": {
   "gender": "M",
   "season": "summer",
   "occasion": "DAILY",
   "label": "남 · 여름 일상 · 린넨 반팔 셔츠 + 린넨 바지",
   "items": {
    "top": "C004",
    "bottom": "C041",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_linen_340_poster.png",
   "mp4": "assets/characters/m_summer_linen_340.mp4",
   "gif": "assets/characters/m_summer_linen_340.gif"
  },
  "m_summer_denim": {
   "gender": "M",
   "season": "summer",
   "occasion": "DAILY",
   "label": "남 · 여름 일상 · 오버핏 반팔 + 쿨데님",
   "items": {
    "top": "C002",
    "bottom": "C037",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_denim_340_poster.png",
   "mp4": "assets/characters/m_summer_denim_340.mp4",
   "gif": "assets/characters/m_summer_denim_340.gif"
  },
  "m_summer_hawaiian": {
   "gender": "M",
   "season": "summer",
   "occasion": "DAILY",
   "label": "남 · 여름 일상 · 하와이안 셔츠 + 린넨 반바지",
   "items": {
    "top": "C005",
    "bottom": "C030",
    "shoes": "C137"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_hawaiian_340_poster.png",
   "mp4": "assets/characters/m_summer_hawaiian_340.mp4",
   "gif": "assets/characters/m_summer_hawaiian_340.gif"
  },
  "m_summer_rain": {
   "gender": "M",
   "season": "summer",
   "occasion": "RAIN",
   "label": "남 · 여름 비 · 장마 · 레인재킷 + 반바지",
   "items": {
    "outer": "C134",
    "top": "C001",
    "bottom": "C028",
    "shoes": "C141"
   },
   "status": "ready",
   "poster": "assets/characters/m_summer_rain_340_poster.png",
   "mp4": "assets/characters/m_summer_rain_340.mp4",
   "gif": "assets/characters/m_summer_rain_340.gif"
  },
  "m_autumn_sweat": {
   "gender": "M",
   "season": "autumn",
   "occasion": "DAILY",
   "label": "남 · 가을 일상 · 맨투맨 + 청바지",
   "items": {
    "top": "C017",
    "bottom": "C033",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/m_autumn_sweat_340_poster.png",
   "mp4": "assets/characters/m_autumn_sweat_340.mp4",
   "gif": "assets/characters/m_autumn_sweat_340.gif"
  },
  "m_autumn_blouson": {
   "gender": "M",
   "season": "autumn",
   "occasion": "DAILY",
   "label": "남 · 가을 일상 · 블루종 + 치노",
   "items": {
    "outer": "C058",
    "top": "C001",
    "bottom": "C039",
    "shoes": "C138"
   },
   "status": "ready",
   "poster": "assets/characters/m_autumn_blouson_340_poster.png",
   "mp4": "assets/characters/m_autumn_blouson_340.mp4",
   "gif": "assets/characters/m_autumn_blouson_340.gif"
  },
  "m_autumn_office": {
   "gender": "M",
   "season": "autumn",
   "occasion": "OFFICE",
   "label": "남 · 가을 출근 · 블레이저 + 셔츠 + 슬랙스",
   "items": {
    "outer": "C053",
    "top": "C012",
    "bottom": "C038",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/m_autumn_office_340_poster.png",
   "mp4": "assets/characters/m_autumn_office_340.mp4",
   "gif": "assets/characters/m_autumn_office_340.gif"
  },
  "m_winter_coat": {
   "gender": "M",
   "season": "winter",
   "occasion": "OFFICE",
   "label": "남 · 겨울 출근 · 롱코트 + 니트 + 슬랙스",
   "items": {
    "outer": "C061",
    "top": "C022",
    "bottom": "C042",
    "shoes": "C139"
   },
   "status": "ready",
   "poster": "assets/characters/m_winter_coat_340_poster.png",
   "mp4": "assets/characters/m_winter_coat_340.mp4",
   "gif": "assets/characters/m_winter_coat_340.gif"
  },
  "m_winter_padding": {
   "gender": "M",
   "season": "winter",
   "occasion": "DAILY",
   "label": "남 · 겨울 일상 · 숏패딩 + 기모 청바지",
   "items": {
    "outer": "C066",
    "top": "C019",
    "bottom": "C036",
    "shoes": "C142"
   },
   "status": "ready",
   "poster": "assets/characters/m_winter_padding_340_poster.png",
   "mp4": "assets/characters/m_winter_padding_340.mp4",
   "gif": "assets/characters/m_winter_padding_340.gif"
  },
  "m_winter_duffle": {
   "gender": "M",
   "season": "winter",
   "occasion": "DAILY",
   "label": "남 · 겨울 일상 · 더플코트 + 터틀넥",
   "items": {
    "outer": "C062",
    "top": "C025",
    "bottom": "C043",
    "shoes": "C140"
   },
   "status": "ready",
   "poster": "assets/characters/m_winter_duffle_340_poster.png",
   "mp4": "assets/characters/m_winter_duffle_340.mp4",
   "gif": "assets/characters/m_winter_duffle_340.gif"
  }
 },
 "accessories": {
  "note": "소품 20개 + 추천 기준 초안(백엔드가 최종 기준을 정함). 카탈로그에는 아직 소품이 없음. 날씨 값으로 고르는 함수 = outfit_visual.js pickAccessories(weather, outfit, map). 미세먼지(pm)는 팀 자료가 없어 값이 올 때만 동작.",
  "items": {
   "umbrella": {
    "label": "우산",
    "rule": "비가 올 때 (pty가 비/비눈/빗방울 — 눈만 올 때는 아님)",
    "file": "assets/icons/acc_umbrella.svg"
   },
   "folding_umbrella": {
    "label": "접이식 우산",
    "rule": "비는 안 오지만 강수확률 40% 이상",
    "file": "assets/icons/acc_folding_umbrella.svg"
   },
   "rain_boots": {
    "label": "장화",
    "rule": "강수량 10mm 이상",
    "file": "assets/icons/acc_rain_boots.svg"
   },
   "parasol": {
    "label": "양산",
    "rule": "맑고 28℃ 이상",
    "file": "assets/icons/acc_parasol.svg"
   },
   "sunglasses": {
    "label": "선글라스",
    "rule": "맑고 20℃ 이상",
    "file": "assets/icons/acc_sunglasses.svg"
   },
   "sunscreen": {
    "label": "선크림",
    "rule": "맑거나 구름 많고 18℃ 이상",
    "file": "assets/icons/acc_sunscreen.svg"
   },
   "cap": {
    "label": "모자",
    "rule": "맑고 25℃ 이상",
    "file": "assets/icons/acc_cap.svg"
   },
   "fan": {
    "label": "휴대용 선풍기",
    "rule": "30℃ 이상 또는 불쾌지수 80 이상",
    "file": "assets/icons/acc_fan.svg"
   },
   "water_bottle": {
    "label": "물병",
    "rule": "28℃ 이상 또는 운동복 추천",
    "file": "assets/icons/acc_water_bottle.svg"
   },
   "cool_sleeve": {
    "label": "쿨토시",
    "rule": "30℃ 이상",
    "file": "assets/icons/acc_cool_sleeve.svg"
   },
   "light_outer": {
    "label": "겉옷 챙기기",
    "rule": "아우터를 입지 않았는데 일교차 10℃ 이상, 또는 아우터를 '챙기기'로 추천",
    "file": "assets/icons/acc_light_outer.svg"
   },
   "scarf": {
    "label": "목도리",
    "rule": "5℃ 이하",
    "file": "assets/icons/acc_scarf.svg"
   },
   "gloves": {
    "label": "장갑",
    "rule": "0℃ 이하",
    "file": "assets/icons/acc_gloves.svg"
   },
   "beanie": {
    "label": "비니",
    "rule": "0℃ 이하, 또는 5℃ 이하에 바람 5m/s 이상",
    "file": "assets/icons/acc_beanie.svg"
   },
   "earmuffs": {
    "label": "귀마개",
    "rule": "-5℃ 이하, 또는 3℃ 이하에 바람 8m/s 이상",
    "file": "assets/icons/acc_earmuffs.svg"
   },
   "hotpack": {
    "label": "핫팩",
    "rule": "-5℃ 이하",
    "file": "assets/icons/acc_hotpack.svg"
   },
   "thermos": {
    "label": "보온 텀블러",
    "rule": "3℃ 이하",
    "file": "assets/icons/acc_thermos.svg"
   },
   "lip_balm": {
    "label": "립밤",
    "rule": "습도 35% 이하",
    "file": "assets/icons/acc_lip_balm.svg"
   },
   "mask": {
    "label": "KF94 마스크",
    "rule": "미세먼지 '나쁨' 이상 (미세먼지 자료가 있을 때만)",
    "file": "assets/icons/acc_mask.svg"
   }
  }
 }
};
