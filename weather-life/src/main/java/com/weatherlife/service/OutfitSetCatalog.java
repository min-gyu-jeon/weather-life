package com.weatherlife.service;

import com.weatherlife.dto.OutfitTypes.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import tools.jackson.databind.json.JsonMapper;
import java.io.IOException;
import java.util.*;

/** 이미지가 존재하는 고정 세트와 슬롯별 허용 의류 목록. 시작 시 잘못된 연결을 차단합니다. */
@Component
public class OutfitSetCatalog {
    public record Definition(String key, String name, Gender gender, Season season, String occasionLabel,
                             double minTemperature, double maxTemperature, double idealTemperature,
                             Map<String, List<String>> pieces, Set<String> tags) {
        public Definition {
            if (key == null || key.isBlank() || name == null || name.isBlank() || gender == null
                    || gender == Gender.UNISEX || season == null || pieces == null || tags == null
                    || !Double.isFinite(minTemperature) || !Double.isFinite(maxTemperature)
                    || !Double.isFinite(idealTemperature) || minTemperature > idealTemperature
                    || idealTemperature > maxTemperature)
                throw new IllegalArgumentException("의상 세트 값 오류: " + key);
            var copy = new LinkedHashMap<String, List<String>>();
            pieces.forEach((k,v) -> copy.put(k, List.copyOf(v)));
            pieces = Collections.unmodifiableMap(copy);
            tags = Set.copyOf(tags);
        }
        public List<String> ids(String part) { return pieces.getOrDefault(part, List.of()); }
    }
    public record Data(String version, String description, List<Definition> sets) { }
    private final Data data;
    public OutfitSetCatalog(JsonMapper mapper, ClothingCatalog clothes,
            @Value("${outfit.set-location:classpath:data/outfit-sets.json}") Resource resource) throws IOException {
        try (var input = resource.getInputStream()) {
            var parsed = mapper.readValue(input, Data.class);
            if (parsed == null || parsed.version() == null || parsed.sets() == null || parsed.sets().isEmpty())
                throw new IllegalStateException("의상 세트 목록이 없습니다.");
            var keys = new HashSet<String>();
            var slots = Map.of("top", Slot.TOP, "innerTop", Slot.TOP, "bottom", Slot.BOTTOM,
                    "onePiece", Slot.ONE_PIECE, "outer", Slot.OUTER, "shoes", Slot.SHOES);
            for (var set : parsed.sets()) {
                if (set == null || !keys.add(set.key())) throw new IllegalStateException("세트 key 중복/누락");
                boolean dress = !set.ids("onePiece").isEmpty();
                if (dress ? !set.ids("top").isEmpty() || !set.ids("bottom").isEmpty()
                        : set.ids("top").isEmpty() || set.ids("bottom").isEmpty())
                    throw new IllegalStateException("상의+하의 또는 원피스로 구성하세요: " + set.key());
                if (set.ids("shoes").isEmpty()) throw new IllegalStateException("신발 후보 누락: " + set.key());
                set.pieces().forEach((part, ids) -> {
                    if (!slots.containsKey(part) || ids.isEmpty() || new HashSet<>(ids).size() != ids.size())
                        throw new IllegalStateException("세트 슬롯 오류: " + set.key() + "/" + part);
                    for (String id : ids) {
                        var garment = clothes.item(id);
                        if (garment.slot() != slots.get(part) || !garment.genders().contains(set.gender()))
                            throw new IllegalStateException("의류 슬롯/성별 불일치: " + set.key() + "/" + id);
                        if (garment.requiresInnerTop() && set.ids("innerTop").isEmpty())
                            throw new IllegalStateException("이너 후보 누락: " + set.key() + "/" + id);
                    }
                });
            }
            data = new Data(parsed.version(), parsed.description(), List.copyOf(parsed.sets()));
        }
    }
    public Data data() { return data; }
    public List<Definition> sets() { return data.sets(); }
}
