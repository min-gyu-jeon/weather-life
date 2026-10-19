package com.weatherlife.service;

import com.weatherlife.dto.Garment;
import tools.jackson.databind.json.JsonMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;

/** 시작할 때 한 번 읽습니다. 매 요청마다 파일을 읽지 않으며 JAR 내부 리소스도 지원합니다. */
@Component
public class ClothingCatalog {
    public record Data(String version, String description, List<Garment> items) { }
    private final Data data;

    public ClothingCatalog(JsonMapper mapper,
            @Value("${outfit.catalog-location:classpath:data/clothing-catalog.json}") Resource resource)
            throws IOException {
        try (var input = resource.getInputStream()) {
            var parsed = mapper.readValue(input, Data.class);
            if (parsed.version() == null || parsed.items() == null || parsed.items().isEmpty()) {
                throw new IllegalStateException("의류 목록 또는 버전이 없습니다.");
            }
            var ids = new HashSet<String>();
            for (var item : parsed.items()) {
                if (item == null || !ids.add(item.id())) {
                    throw new IllegalStateException("의류 ID가 중복되었거나 항목이 비어 있습니다.");
                }
            }
            data = new Data(parsed.version(), parsed.description(), List.copyOf(parsed.items()));
        }
    }

    public Data data() { return data; }

    public Garment item(String id) {
        return data.items().stream().filter(g -> g.id().equals(id)).findFirst()
                .orElseThrow(() -> new IllegalStateException("등록되지 않은 옷 ID: " + id));
    }
}
