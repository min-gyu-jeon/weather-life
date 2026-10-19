package com.weatherlife.service;

import com.weatherlife.dto.RegionShort;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 서울 25개 자치구의 CSV 행정구역 대표격자 좌표를 재사용합니다. */
@Service
public class SeoulDistrictService {
    private static final List<String> NAMES = List.of(
            "종로구", "중구", "용산구", "성동구", "광진구",
            "동대문구", "중랑구", "성북구", "강북구", "도봉구",
            "노원구", "은평구", "서대문구", "마포구", "양천구",
            "강서구", "구로구", "금천구", "영등포구", "동작구",
            "관악구", "서초구", "강남구", "송파구", "강동구");

    private final OfficialRegionService regionService;

    public record District(String gu, String regionName, int gridX, int gridY) { }

    public SeoulDistrictService(OfficialRegionService regionService) {
        this.regionService = regionService;
    }

    public List<District> allDistricts() {
        List<District> districts = new ArrayList<>(NAMES.size());
        for (String gu : NAMES) {
            String full = "서울특별시 " + gu;
            RegionShort grid = regionService.getShortRegion(full);
            if (grid == null) {
                throw new IllegalStateException("서울 자치구 CSV 격자 누락: " + full);
            }
            districts.add(new District(gu, full, grid.nx(), grid.ny()));
        }
        return List.copyOf(districts);
    }

    /** 동일 격자를 공유하는 구는 한 번만 기상청에 요청합니다. */
    public List<District> uniqueGridRepresentatives() {
        Map<String, District> grids = new LinkedHashMap<>();
        for (District district : allDistricts()) {
            grids.putIfAbsent(district.gridX() + ":" + district.gridY(), district);
        }
        return List.copyOf(grids.values());
    }

    /** 구 단축명은 CSV에 존재하는 서울특별시 자치구 정식 명칭으로 정규화합니다. */
    public String normalizeRegionName(String input) {
        if (input == null || input.isBlank()) {
            throw new IllegalArgumentException("지역명(regionName 또는 gu)이 필요합니다.");
        }
        String region = input.strip().replaceAll("\\s+", " ");
        for (String gu : NAMES) {
            if (region.equals(gu) || region.equals("서울특별시 " + gu) || region.equals("서울 " + gu)) {
                return "서울특별시 " + gu;
            }
        }
        // 기존 동 단위 조회 경로의 하위 호환성 유지.
        return region;
    }
}
