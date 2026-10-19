package com.weatherlife.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import tools.jackson.databind.json.JsonMapper;
import java.io.IOException;
import java.util.*;

@Component
public class AccessoryCatalog {
    public record Accessory(String key, String name, String iconPath) { }
    public record Data(String version, List<Accessory> items) { }
    private final Data data;
    public AccessoryCatalog(JsonMapper mapper,
            @Value("${outfit.accessory-location:classpath:data/accessory-catalog.json}") Resource resource) throws IOException {
        try (var input = resource.getInputStream()) {
            var parsed = mapper.readValue(input, Data.class);
            if (parsed == null || parsed.version() == null || parsed.items() == null || parsed.items().isEmpty())
                throw new IllegalStateException("소품 목록이 없습니다.");
            var keys = new HashSet<String>();
            for (var item : parsed.items()) {
                if (item == null || item.key() == null || item.key().isBlank() || !keys.add(item.key())
                        || item.name() == null || item.name().isBlank()
                        || item.iconPath() == null || item.iconPath().isBlank())
                    throw new IllegalStateException("소품 key/이름/아이콘 오류");
            }
            data = new Data(parsed.version(), List.copyOf(parsed.items()));
        }
    }
    public Data data() { return data; }
    public Accessory item(String key) {
        return data.items().stream().filter(a -> a.key().equals(key)).findFirst()
                .orElseThrow(() -> new IllegalStateException("등록되지 않은 소품: " + key));
    }
}
