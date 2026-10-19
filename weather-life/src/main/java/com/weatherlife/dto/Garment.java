package com.weatherlife.dto;

import java.util.Set;
import static com.weatherlife.dto.OutfitTypes.*;

/**
 * 실제 상품이 아닌 의류 종류 한 가지입니다.
 * 온도는 이 프로젝트에서 정한 추천 기준이며 공인된 의복·체감온도 기준이 아닙니다.
 * 통풍성: 0~5, 방수/방풍: 0~2. JSON 수정 후 재시작하면 반영됩니다.
 */
public record Garment(
        String id, String name, String iconPath, Slot slot,
        Set<Gender> genders, Set<Occasion> occasions, Style style,
        double minTemperature, double maxTemperature, double idealTemperature,
        int breathability, int waterResistance, int windResistance,
        BottomType bottomType, boolean requiresInnerTop, Set<String> tags) {
    public Garment {
        if (id == null || id.isBlank() || name == null || name.isBlank()
                || iconPath == null || iconPath.isBlank()
                || slot == null || style == null || bottomType == null
                || genders == null || genders.isEmpty() || occasions == null || occasions.isEmpty()
                || tags == null || !Double.isFinite(minTemperature) || !Double.isFinite(maxTemperature)
                || !Double.isFinite(idealTemperature) || minTemperature > maxTemperature
                || idealTemperature < minTemperature || idealTemperature > maxTemperature
                || breathability < 0 || breathability > 5 || waterResistance < 0 || waterResistance > 2
                || windResistance < 0 || windResistance > 2) {
            throw new IllegalArgumentException("의류 카탈로그 값이 올바르지 않습니다: " + id);
        }
        if ((slot == Slot.BOTTOM) != (bottomType != BottomType.NONE)) {
            throw new IllegalArgumentException("하의에만 bottomType을 지정하세요: " + id);
        }
        if (requiresInnerTop && slot != Slot.TOP && slot != Slot.ONE_PIECE) {
            throw new IllegalArgumentException("이너가 필요한 의류는 TOP 또는 ONE_PIECE입니다: " + id);
        }
        genders = Set.copyOf(genders);
        occasions = Set.copyOf(occasions);
        tags = Set.copyOf(tags);
    }
}
