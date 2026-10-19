package com.weatherlife.dto;

import java.util.List;
import static com.weatherlife.dto.OutfitTypes.*;

public record OutfitResponse(
        String recommendationType, String catalogVersion, OutfitRequest input,
        double selectionTemperature, double outerSelectionTemperature,
        List<Outfit> outfits, List<String> advice, List<String> warnings) {

    /** id와 iconKey는 확정된 56개 아이콘 key입니다. 구 C001 등의 ID는 사용하지 않습니다. */
    public record Item(String id, String name, Slot slot, String iconKey, String iconPath) {
        public static Item of(Garment g) {
            return g == null ? null : new Item(g.id(), g.name(), g.slot(), g.id(), g.iconPath());
        }
    }
    public record AccessoryItem(String key, String name, String iconPath, String reason) { }
    public record Visual(String posterPath, String videoPath, String gifPath) {
        public static Visual of(String key) {
            String base = "/weather/outfits/assets/characters/" + key + "_340";
            return new Visual(base + "_poster.png", base + ".mp4", base + ".gif");
        }
    }
    public record Outfit(
            String id, String setKey, String setName, Gender setGender, Season season, Visual visual,
            Structure structure, Item top, Item bottom, Item onePiece, Item innerTop,
            Item outer, OuterUsage outerUsage, Item baseLayer, Item shoes,
            List<String> accessories, List<AccessoryItem> accessoryItems, List<String> reasons) { }
}
