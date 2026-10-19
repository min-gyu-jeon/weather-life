package com.weatherlife.dto;

/** 요청과 카탈로그에서 쓰는 고정된 값들. 임의 문자열 대신 enum으로 오타를 잡습니다. */
public final class OutfitTypes {
    private OutfitTypes() { }
    public enum Gender { MALE, FEMALE, UNISEX }
    public enum Season { SPRING, SUMMER, AUTUMN, WINTER }
    public enum AirQuality { GOOD, NORMAL, BAD, VERY_BAD }
    public enum Occasion { DAILY, OFFICE, EXERCISE, HOME }
    public enum Preference { ANY, PANTS, SKIRT, ONE_PIECE }
    public enum ThermalPreference { NORMAL, FEEL_COLD, FEEL_HOT }
    public enum Sky { SUNNY, PARTLY_CLOUDY, CLOUDY }
    public enum Precipitation { NONE, RAIN, SNOW, MIXED }
    public enum Slot { TOP, BOTTOM, ONE_PIECE, OUTER, BASE_LAYER, SHOES }
    public enum BottomType { NONE, PANTS, SHORTS, SKIRT }
    public enum Style { CASUAL, SMART, SPORT, HOME }
    public enum Structure { SEPARATES, ONE_PIECE, LAYERED_ONE_PIECE }
    public enum OuterUsage { NONE, WEAR, CARRY }
}
