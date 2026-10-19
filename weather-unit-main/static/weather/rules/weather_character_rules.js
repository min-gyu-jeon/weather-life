// 자동 생성 파일 — 고치지 마세요. 원본 = weather_character_rules.json → py -I make_rules_js.py
// 더블클릭으로 연 화면(file://)에서도 기준표를 읽게 하려고 JSON과 같은 내용을 담아 둠.
window.WEATHER_CHARACTER_RULES = {
  "version": "2026-10-15",
  "status": "참고용 초안: 실제 조합은 팀의 백엔드·화면 담당이 결정",
  "input": {
    "month": "1~12 정수: 생략하면 오늘 날짜의 월",
    "temp": "섭씨 기온 숫자: 필수",
    "pty": "강수형태 글자 또는 기상청 PTY 코드: 생략하면 없음",
    "sky": "맑음/구름많음/흐림 또는 기상청 SKY 코드: 생략하면 맑음",
    "di": "불쾌지수 숫자: 생략하면 normal(보통) 단계",
    "gender": "F 또는 M: 생략하면 F",
    "occasion": "선택: 일상/출근/운동, 생략하면 일상",
    "uv": "선택: 자외선지수 숫자, 없으면 선글라스 판단에 쓰지 않음",
    "pm": "선택: 미세먼지 등급 글자, 예: 좋음/보통/나쁨/매우나쁨",
    "humidity": "선택: 상대습도 0~100 숫자, 없으면 하늘 상태로 빨래를 판단"
  },
  "input_defaults": {
    "month": "today",
    "pty": "없음",
    "sky": "맑음",
    "di": null,
    "gender": "F",
    "occasion": "일상",
    "uv": null,
    "pm": "",
    "humidity": null,
    "note": "month=today는 실행 당일의 월을 사용한다. di=null이면 스티커 표정은 normal을 사용하며 불쾌지수 수치 조건은 적용하지 않는다. temp는 필수다."
  },
  "kma_codes": {
    "SKY": {
      "1": "맑음",
      "3": "구름많음",
      "4": "흐림"
    },
    "PTY": {
      "0": "없음",
      "1": "비",
      "2": "비/눈",
      "3": "눈",
      "4": "소나기",
      "5": "빗방울",
      "6": "빗방울눈날림",
      "7": "눈날림"
    }
  },
  "order": [
    "① 월에서 봄·여름·가을·겨울을 고른다.",
    "② 28℃ 이상은 여름 겉모습, 5℃ 이하는 겨울 겉모습으로 바꾼다. 여름인데 23℃ 미만이면 월에 따라 봄·가을 착장과 액티비티를 고른다.",
    "③ 강수형태에 비·소나기·뇌우·천둥이 있는지 확인한다.",
    "④ 비용 착장이 있으면 우선하고, 없으면 기온·용도로 착장을 고른다.",
    "⑤ 활동은 비·천둥, 미세먼지 나쁨, 폭염, 한파 예외를 먼저 보고 계절 활동을 고른다.",
    "⑥ 스티커는 불쾌지수 표정을 먼저 고르고, 비면 같은 표정의 우산, 맑고 더우거나 자외선이 강하면 선글라스를 고른다.",
    "⑦ 빨래는 -5℃ 이하 얼음 → 비 → 습도 70% 이상 → 습도 없고 흐림 → 그 밖은 잘 마름 순서로 고른다."
  ],
  "season": {
    "months": {
      "spring": [
        3,
        4,
        5
      ],
      "summer": [
        6,
        7,
        8
      ],
      "autumn": [
        9,
        10,
        11
      ],
      "winter": [
        12,
        1,
        2
      ]
    },
    "summer_if_temp_at_least": 28,
    "winter_if_temp_at_most": 5,
    "cool_summer_outfit": {
      "below_temp": 23,
      "spring_months": [
        3,
        4,
        5,
        6
      ],
      "autumn_months": [
        7,
        8,
        9,
        10,
        11
      ]
    }
  },
  "rain": {
    "pty_contains_any": [
      "비",
      "빗방울",
      "소나기",
      "뇌우",
      "천둥"
    ],
    "activity": {
      "F": "summer_rain",
      "M": "m_rain_game"
    },
    "outfit_if_available": {
      "spring": {
        "F": "f_spring_rain"
      },
      "summer": {
        "F": "f_summer_rain",
        "M": "m_summer_rain"
      },
      "autumn": {
        "F": "f_spring_rain"
      }
    },
    "note": "비용 착장이 없는 성별·계절은 일상 기본 착장. 우산은 기존 소품 규칙에서 고른다."
  },
  "outfit": {
    "daily_first_match": {
      "spring": [
        {
          "when": {
            "min_temp": 18
          },
          "F": "f_spring_basic",
          "M": "m_spring_denim"
        },
        {
          "when": {},
          "F": "f_spring_campus",
          "M": "m_spring_zipup"
        }
      ],
      "summer": [
        {
          "when": {},
          "F": "f_summer_basic",
          "M": "m_summer_tee"
        }
      ],
      "autumn": [
        {
          "when": {
            "min_temp": 18
          },
          "F": "f_autumn_basic",
          "M": "m_autumn_sweat"
        },
        {
          "when": {},
          "F": "f_autumn_knit",
          "M": "m_autumn_blouson"
        }
      ],
      "winter": [
        {
          "when": {
            "min_temp_exclusive": 0
          },
          "F": "f_winter_halfcoat",
          "M": "m_winter_duffle"
        },
        {
          "when": {
            "min_temp_exclusive": -10
          },
          "F": "f_winter_padding",
          "M": "m_winter_padding"
        },
        {
          "when": {},
          "F": "f_winter_longpadding",
          "M": "m_winter_padding"
        }
      ]
    },
    "occasion_if_dry": {
      "출근": {
        "spring": {
          "F": "f_spring_trench",
          "M": "m_spring_shirt"
        },
        "summer": {
          "F": "f_summer_office",
          "M": "m_summer_office"
        },
        "autumn": {
          "F": "f_autumn_office",
          "M": "m_autumn_office"
        },
        "winter": {
          "F": "f_winter_longcoat",
          "M": "m_winter_coat"
        }
      },
      "운동": {
        "summer": {
          "F": "f_summer_athleisure",
          "M": "m_summer_athleisure"
        }
      }
    },
    "variety_optional": {
      "f_summer_basic": [
        "f_summer_onepiece",
        "f_summer_linen",
        "f_summer_skirt",
        "f_summer_denim"
      ],
      "m_summer_tee": [
        "m_summer_linen",
        "m_summer_denim",
        "m_summer_hawaiian"
      ],
      "f_autumn_knit": [
        "f_autumn_leather"
      ]
    },
    "variety_note": "화면에서 날짜별로 바꾸고 싶을 때만 사용. 기본 결과는 daily_first_match의 키."
  },
  "activity": {
    "fine_dust": {
      "pm_contains": "나쁨",
      "activity": {
        "F": "home_ac",
        "M": "m_home_ac"
      }
    },
    "heat_wave": {
      "min_temp": 33,
      "min_di": 80,
      "activity": {
        "F": "home_ac",
        "M": "m_home_ac"
      },
      "note": "기온 또는 불쾌지수 중 하나만 기준 이상이면 적용"
    },
    "by_season": {
      "spring": {
        "F": "spring_jump",
        "M": "m_spring_bike"
      },
      "summer": {
        "F": "summer_swim",
        "M": "m_summer_surf"
      },
      "autumn": {
        "F": "autumn_walk",
        "M": "m_autumn_hike"
      }
    },
    "winter_first_match": [
      {
        "when": {
          "max_temp": -5
        },
        "F": "winter_cold",
        "M": "m_winter_cold"
      },
      {
        "when": {
          "min_temp_exclusive": -5,
          "max_temp": 0,
          "sky": "맑음"
        },
        "F": "winter_onsen",
        "M": "m_winter_ski"
      },
      {
        "when": {},
        "F": "winter_chilly",
        "M": "m_winter_jog"
      }
    ],
    "known_keys": [
      "spring_jump",
      "m_spring_bike",
      "summer_swim",
      "m_summer_surf",
      "autumn_walk",
      "m_autumn_hike",
      "winter_cold",
      "m_winter_cold",
      "winter_onsen",
      "m_winter_ski",
      "winter_chilly",
      "m_winter_jog",
      "summer_rain",
      "m_rain_game",
      "home_ac",
      "m_home_ac"
    ]
  },
  "sticker": {
    "rain": "umbrella_{stage}",
    "sunny": {
      "sky": "맑음",
      "min_temp": 30,
      "min_uv": 8,
      "stage": "sunglasses",
      "note": "맑음이고 기온 또는 자외선지수 중 하나만 기준 이상이면 적용"
    },
    "first_match": [
      {
        "when": {
          "di_below": 68
        },
        "stage": "comfort",
        "label": "쾌적 · 아주 행복한 미소"
      },
      {
        "when": {
          "di_below": 75
        },
        "stage": "normal",
        "label": "보통 · 미소"
      },
      {
        "when": {
          "di_below": 80
        },
        "stage": "bad",
        "label": "나쁨 · 무표정"
      },
      {
        "when": {},
        "stage": "very_bad",
        "label": "매우 나쁨 · 화남"
      }
    ]
  },
  "laundry": {
    "frozen_if_temp_at_most": -5,
    "rain_uses": "rain.pty_contains_any",
    "damp_if_humidity_at_least": 70,
    "damp_if_humidity_missing_and_sky": "흐림",
    "default": "dry",
    "known_keys": [
      "dry",
      "damp",
      "frozen"
    ]
  },
  "labels": {
    "activity": {
      "spring_jump": "봄날 점프",
      "m_spring_bike": "봄 자전거",
      "summer_swim": "여름 수영",
      "m_summer_surf": "여름 서핑",
      "autumn_walk": "가을 산책",
      "m_autumn_hike": "가을 등산",
      "winter_cold": "추위에 떨기",
      "m_winter_cold": "추위에 떨기",
      "winter_onsen": "따뜻한 족욕",
      "m_winter_ski": "겨울 스키",
      "winter_chilly": "쌀쌀한 겨울",
      "m_winter_jog": "겨울 조깅",
      "summer_rain": "비 오는 날 집에서 쉬기",
      "m_rain_game": "비 오는 날 집에서 게임하기",
      "home_ac": "에어컨 켜고 쉬기",
      "m_home_ac": "에어컨 켜고 쉬기"
    },
    "sticker": {
      "comfort": "쾌적 · 아주 행복한 미소",
      "normal": "보통 · 부드러운 미소",
      "bad": "나쁨 · 지친 무표정",
      "very_bad": "매우 나쁨 · 귀엽게 화남",
      "umbrella_comfort": "비 · 쾌적한 미소",
      "umbrella_normal": "비 · 부드러운 미소",
      "umbrella_bad": "비 · 지친 무표정",
      "umbrella_very_bad": "비 · 귀엽게 화남",
      "sunglasses": "맑고 뜨거운 날 · 선글라스"
    },
    "laundry": {
      "dry": "잘 마른 빨래",
      "damp": "축축한 빨래",
      "frozen": "얼어붙은 빨래"
    }
  },
  "files": {
    "outfit": {
      "poster": "outfits/assets/characters/{key}_340_poster.png",
      "mp4": "outfits/assets/characters/{key}_340.mp4",
      "gif": "outfits/assets/characters/{key}_340.gif"
    },
    "activity": {
      "poster": "activities/activity_{key}_340_poster.png",
      "mp4": "activities/activity_{key}_340.mp4",
      "gif": "activities/activity_{key}_340.gif"
    },
    "sticker": {
      "poster": "stickers/{gender}_{sticker}.png"
    },
    "laundry": {
      "poster": "laundry/laundry_{key}.png"
    }
  }
};
