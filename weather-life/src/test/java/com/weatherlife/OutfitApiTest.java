package com.weatherlife;

import com.weatherlife.service.*;
import com.weatherlife.dto.OutfitRequest;
import com.weatherlife.dto.OutfitResponse.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import java.time.LocalDate;
import java.util.*;
import static com.weatherlife.dto.OutfitTypes.*;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/** 세트 이미지와 세부 의류의 일치, 날씨 우선 순위, 조건부 소품 및 API 계약을 검증합니다. */
@SpringBootTest
@AutoConfigureMockMvc
class OutfitApiTest {
    @Autowired MockMvc mvc;
    @Autowired OutfitService service;
    @Autowired ClothingCatalog catalog;
    @Autowired OutfitSetCatalog sets;
    @Autowired AccessoryCatalog accessories;
    @MockitoBean OfficialWeatherService weatherService;

    private OutfitRequest request(double t, Gender gender, Precipitation rain, double wind,
                                  Occasion occasion, Preference preference) {
        return new OutfitRequest(t, 60.0, wind, Sky.CLOUDY, rain, gender, occasion, preference,
                ThermalPreference.NORMAL, null, null, 3, 42L,
                LocalDate.of(2026, 10, 15), null, null, null);
    }

    @Test void validApiAndAllCatalogs() throws Exception {
        mvc.perform(post("/api/outfits/recommend").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"temperature\":24,\"humidity\":65,\"gender\":\"FEMALE\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.recommendationType").value("RULE_BASED"))
                .andExpect(jsonPath("$.outfits.length()").value(1))
                .andExpect(jsonPath("$.outfits[0].setKey").isString())
                .andExpect(jsonPath("$.outfits[0].setGender").value("FEMALE"))
                .andExpect(jsonPath("$.outfits[0].visual.videoPath").isString())
                .andExpect(jsonPath("$.outfits[0].shoes.iconKey").isString());
        mvc.perform(get("/api/outfits/catalog")).andExpect(status().isOk())
                .andExpect(jsonPath("$.items.length()").value(56));
        mvc.perform(get("/api/outfits/sets")).andExpect(status().isOk())
                .andExpect(jsonPath("$.sets.length()").value(36));
        mvc.perform(get("/api/outfits/accessories")).andExpect(status().isOk())
                .andExpect(jsonPath("$.items.length()").value(19));
    }

    @Test void everyReturnedOutfitUsesOnlyItsRegisteredPiecesAcrossWeatherAndGenders() {
        for (var gender : Gender.values()) for (double t : new double[]{-20,-5,5,15,25,34})
            for (var rain : new Precipitation[]{Precipitation.NONE,Precipitation.RAIN})
                for (double wind : new double[]{0,10}) {
                    var result = service.recommend(request(t,gender,rain,wind,Occasion.DAILY,Preference.ANY));
                    assertThat(result.outfits()).isNotEmpty();
                    assertThat(result.outfits().stream().map(Outfit::setKey)).doesNotHaveDuplicates();
                    for (var o : result.outfits()) {
                        var s = sets.sets().stream().filter(x -> x.key().equals(o.setKey())).findFirst().orElseThrow();
                        if (gender != Gender.UNISEX) assertThat(o.setGender()).isEqualTo(gender);
                        Map<String,Item> parts = new LinkedHashMap<>();
                        parts.put("top",o.top()); parts.put("bottom",o.bottom()); parts.put("outer",o.outer());
                        parts.put("onePiece",o.onePiece()); parts.put("innerTop",o.innerTop()); parts.put("shoes",o.shoes());
                        parts.forEach((part,item) -> {
                            if (s.ids(part).isEmpty()) assertThat(item).isNull();
                            else { assertThat(item).isNotNull(); assertThat(s.ids(part)).contains(item.id()); }
                        });
                        if (o.structure() == Structure.SEPARATES) {
                            assertThat(o.top()).isNotNull(); assertThat(o.bottom()).isNotNull(); assertThat(o.onePiece()).isNull();
                        } else { assertThat(o.onePiece()).isNotNull(); assertThat(o.top()).isNull(); assertThat(o.bottom()).isNull(); }
                        var ids = parts.values().stream().filter(Objects::nonNull).map(Item::id).toList();
                        assertThat(ids).doesNotHaveDuplicates();
                        for (var item : parts.values()) if (item != null) {
                            assertThat(item.iconKey()).isEqualTo(item.id());
                            assertThat(item.iconPath()).endsWith("/"+item.id()+".svg");
                        }
                        assertThat(o.visual().videoPath()).endsWith("/"+o.setKey()+"_340.mp4");
                        if (rain != Precipitation.NONE) assertThat(catalog.item(o.shoes().id()).waterResistance()).isPositive();
                        if (result.selectionTemperature() <= 5) assertThat(o.baseLayer().id()).isEqualTo("thermal");
                        for (var extra : o.accessoryItems()) assertThat(accessories.item(extra.key()).name()).isEqualTo(extra.name());
                    }
                }
    }

    @Test void coldSummerAndHotAutumnFollowWeatherRatherThanCalendar() {
        for (var gender : List.of(Gender.FEMALE,Gender.MALE)) {
            var cold = new OutfitRequest(13.0,60.0,2.0,Sky.CLOUDY,Precipitation.NONE,gender,
                    Occasion.DAILY,Preference.ANY,ThermalPreference.NORMAL,null,null,1,0L,LocalDate.of(2026,7,15),null,null,null);
            var coolSet = service.recommend(cold).outfits().getFirst();
            assertThat(coolSet.season()).isIn(Season.SPRING,Season.AUTUMN);
            var hot = new OutfitRequest(32.0,60.0,2.0,Sky.CLOUDY,Precipitation.NONE,gender,
                    Occasion.OFFICE,Preference.ANY,ThermalPreference.NORMAL,null,null,1,0L,LocalDate.of(2026,10,15),null,null,null);
            var hotSet = service.recommend(hot).outfits().getFirst();
            assertThat(hotSet.season()).isEqualTo(Season.SUMMER);
            assertThat(hotSet.outer()).isNull();
            assertThat(catalog.item(hotSet.bottom().id()).bottomType()).isEqualTo(BottomType.SHORTS);
        }
    }

    @Test void occasionDoesNotRestrictOrWarmTheRecommendation() {
        var base = service.recommend(request(28,Gender.FEMALE,Precipitation.NONE,2,Occasion.DAILY,Preference.ANY));
        for (var occasion : Occasion.values()) {
            var result = service.recommend(request(28,Gender.FEMALE,Precipitation.NONE,2,occasion,Preference.ANY));
            assertThat(result.outfits()).isEqualTo(base.outfits());
            assertThat(result.selectionTemperature()).isEqualTo(base.selectionTemperature());
        }
    }

    @Test void preferencesStillStayInsideExistingSets() {
        var pants = service.recommend(request(25,Gender.FEMALE,Precipitation.NONE,0,Occasion.DAILY,Preference.PANTS));
        assertThat(pants.outfits()).allSatisfy(o -> {
            assertThat(o.onePiece()).isNull();
            assertThat(catalog.item(o.bottom().id()).bottomType()).isIn(BottomType.PANTS,BottomType.SHORTS);
        });
        var dresses = service.recommend(request(25,Gender.FEMALE,Precipitation.NONE,0,Occasion.DAILY,Preference.ONE_PIECE));
        assertThat(dresses.outfits()).allSatisfy(o -> {
            assertThat(o.onePiece()).isNotNull(); assertThat(o.top()).isNull(); assertThat(o.bottom()).isNull();
        });
    }

    @Test void snowUsesGripAndThermalWithoutChangingTheSet() {
        var result = service.recommend(request(-5,Gender.FEMALE,Precipitation.SNOW,3,Occasion.DAILY,Preference.ANY));
        assertThat(result.outfits()).allSatisfy(o -> {
            assertThat(o.shoes().id()).isEqualTo("winter_boots");
            assertThat(o.baseLayer().id()).isEqualTo("thermal");
            assertThat(o.accessoryItems().stream().map(AccessoryItem::key)).doesNotContain("umbrella","folding_umbrella");
        });
    }

    @Test void mildWeatherHasNoForcedAccessories() {
        var result = service.recommend(request(20,Gender.FEMALE,Precipitation.NONE,0,Occasion.DAILY,Preference.ANY));
        assertThat(result.outfits()).allSatisfy(o -> {
            assertThat(o.accessories()).isEmpty(); assertThat(o.accessoryItems()).isEmpty();
        });
    }

    @Test void rainProbabilityDustAndAmountDriveOnlyTheirAccessories() {
        var dry = new OutfitRequest(26.0,60.0,0.0,Sky.CLOUDY,Precipitation.NONE,Gender.FEMALE,
                null,null,null,null,null,1,0L,LocalDate.of(2026,10,15),60.0,null,null);
        var dryKeys = service.recommend(dry).outfits().getFirst().accessoryItems().stream().map(AccessoryItem::key).toList();
        assertThat(dryKeys).contains("folding_umbrella").doesNotContain("umbrella","mask","rain_boots");
        var wet = new OutfitRequest(26.0,60.0,0.0,Sky.CLOUDY,Precipitation.RAIN,Gender.FEMALE,
                null,null,null,null,null,1,0L,LocalDate.of(2026,10,15),90.0,10.0,AirQuality.BAD);
        var outfit = service.recommend(wet).outfits().getFirst();
        assertThat(outfit.setKey()).isEqualTo("f_summer_rain");
        assertThat(outfit.accessoryItems().stream().map(AccessoryItem::key)).contains("umbrella","rain_boots","mask").doesNotContain("folding_umbrella");
        var keys = outfit.accessoryItems().stream().map(AccessoryItem::key).toList();
        assertThat(keys).doesNotHaveDuplicates();
    }

    @Test void largeDailyRangeSuggestsCarryingWithoutAddingAnUnpicturedOuter() {
        var req = new OutfitRequest(32.0,50.0,0.0,Sky.CLOUDY,Precipitation.NONE,Gender.FEMALE,
                null,null,null,16.0,32.0,1,1L,LocalDate.of(2026,10,15),null,null,null);
        var o = service.recommend(req).outfits().getFirst();
        assertThat(o.season()).isEqualTo(Season.SUMMER);
        assertThat(o.outer()).isNull();
        assertThat(o.accessoryItems().stream().map(AccessoryItem::key)).contains("light_outer");
    }

    @Test void coldAndHotAccessoriesRespondToWeatherAndWind() {
        var cold = service.recommend(request(-8,Gender.MALE,Precipitation.NONE,9,Occasion.DAILY,Preference.ANY)).outfits().getFirst();
        assertThat(cold.accessoryItems().stream().map(AccessoryItem::key)).contains("scarf","gloves","beanie","earmuffs","hotpack","thermos");
        var hot = new OutfitRequest(32.0,80.0,0.0,Sky.SUNNY,Precipitation.NONE,Gender.FEMALE,null,null,null,null,null,1,0L);
        assertThat(service.recommend(hot).outfits().getFirst().accessoryItems().stream().map(AccessoryItem::key))
                .contains("parasol","sunglasses","sunscreen","cap","fan","water_bottle","cool_sleeve").doesNotContain("mask");
        var wind = service.recommend(request(26,Gender.FEMALE,Precipitation.RAIN,12,Occasion.DAILY,Preference.ANY)).outfits().getFirst();
        assertThat(wind.accessoryItems().stream().map(AccessoryItem::key)).doesNotContain("umbrella","folding_umbrella","parasol");
    }

    @Test void sameSeedIsRepeatableAndExplicitCountReturnsDistinctSets() {
        var req = request(24,Gender.FEMALE,Precipitation.NONE,0,Occasion.DAILY,Preference.ANY);
        assertThat(service.recommend(req)).isEqualTo(service.recommend(req));
        assertThat(service.recommend(req).outfits()).hasSize(3);
    }

    @Test void malformedAndInvalidRequestsReturn400() throws Exception {
        for (String json : List.of("{}", "{\"temperature\":20,\"humidity\":101}",
                "{\"temperature\":20,\"humidity\":60,\"count\":0}",
                "{\"temperature\":20,\"humidity\":60,\"gender\":\"OTHER\"}",
                "{\"temperature\":20,\"humidity\":60,\"minTemperature\":25}",
                "{\"temperature\":20,\"humidity\":60,\"typo\":1}",
                "{\"temperature\":20,\"humidity\":60,\"precipitationProbability\":101}",
                "{\"temperature\":20,\"humidity\":60,\"precipitationAmount\":-1}",
                "{\"temperature\":20,\"humidity\":60,\"date\":\"bad\"}",
                "{\"temperature\":\"NaN\",\"humidity\":60}")) {
            mvc.perform(post("/api/outfits/recommend").contentType(MediaType.APPLICATION_JSON).content(json))
                    .andExpect(status().isBadRequest());
        }
    }

    @Test void unsupportedGenderPreferenceReturns422InsteadOfInventingANewImage() throws Exception {
        mvc.perform(post("/api/outfits/recommend").contentType(MediaType.APPLICATION_JSON)
                .content("{\"temperature\":22,\"humidity\":60,\"gender\":\"MALE\",\"preference\":\"SKIRT\"}"))
                .andExpect(status().is(422)).andExpect(jsonPath("$.code").value("NO_MATCHING_OUTFIT"));
    }
    @Test void existingWeatherEndpointsRemainAvailable() throws Exception {
        given(weatherService.getShortRangeForecast("테스트 지역")).willReturn("{\"forecast\":\"short\"}");
        given(weatherService.getMediumLandForecast("11B00000")).willReturn("{\"forecast\":\"land\"}");
        given(weatherService.getMediumTemperatureForecast("11B10101")).willReturn("{\"forecast\":\"temperature\"}");
        mvc.perform(get("/api/short").param("regionName", "테스트 지역"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.forecast").value("short"));
        mvc.perform(get("/api/medium/land").param("regId", "11B00000"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.forecast").value("land"));
        mvc.perform(get("/api/medium/temperature").param("regId", "11B10101"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.forecast").value("temperature"));
    }

}
