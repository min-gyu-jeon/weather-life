package com.weatherlife.service;

import com.weatherlife.dto.*;
import com.weatherlife.dto.OutfitResponse.*;
import com.weatherlife.service.OutfitSetCatalog.Definition;
import jakarta.validation.ConstraintViolationException;
import jakarta.validation.Validator;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.time.LocalTime;
import java.util.*;

import static com.weatherlife.dto.OutfitTypes.*;

@Service
public class OutfitService {
    private final ClothingCatalog catalog;
    private final OutfitSetCatalog sets;
    private final AccessoryService accessories;
    private final Validator validator;

    public OutfitService(
            ClothingCatalog catalog,
            OutfitSetCatalog sets,
            AccessoryService accessories,
            Validator validator) {
        this.catalog = catalog;
        this.sets = sets;
        this.accessories = accessories;
        this.validator = validator;
    }

    // 기존 호출 방식 유지
    public OutfitResponse recommend(OutfitRequest request) {
        return recommend(request, null);
    }

    public OutfitResponse recommend(
            OutfitRequest request,
            LocalTime forecastTime) {

        Objects.requireNonNull(request, "request");

        var violations = validator.validate(request);
        if (!violations.isEmpty()) {
            throw new ConstraintViolationException(violations);
        }

        var ctx = WeatherRules.evaluate(request);
        var random = new Random(request.seed());
        var warnings = new LinkedHashSet<>(ctx.warnings());

        var candidates = sets.sets().stream()
                .filter(s -> request.gender() == Gender.UNISEX
                        || s.gender() == request.gender())
                .filter(s -> matchesPreference(s, request.preference()))
                .toList();

        if (candidates.isEmpty()) {
            throw new NoOutfitException();
        }

        var fitting = candidates.stream()
                .filter(s -> distance(
                        ctx.temperature(),
                        s.minTemperature(),
                        s.maxTemperature()) == 0)
                .toList();

        if (fitting.isEmpty()) {
            double closest = candidates.stream()
                    .mapToDouble(s -> distance(
                            ctx.temperature(),
                            s.minTemperature(),
                            s.maxTemperature()))
                    .min()
                    .orElseThrow();

            fitting = candidates.stream()
                    .filter(s -> distance(
                            ctx.temperature(),
                            s.minTemperature(),
                            s.maxTemperature()) == closest)
                    .toList();

            warnings.add(
                    "등록된 세트의 권장 기온 범위 밖이어서 가장 가까운 세트를 반환했습니다. 착용 적합성을 확인하세요.");
        }

        record Ranked(Definition set, double score) {}

        var ranked = fitting.stream()
                .map(s -> new Ranked(
                        s, scoreSet(s, ctx) + random.nextDouble() * 0.2))
                .sorted(
                        Comparator.comparingDouble(Ranked::score)
                                .reversed()
                                .thenComparing(x -> x.set().key()))
                .limit(request.count())
                .toList();

        var outfits = new ArrayList<Outfit>();

        for (var entry : ranked) {
            outfits.add(assemble(
                    entry.set(), ctx, random, warnings, forecastTime));
        }

        if (outfits.size() < request.count()) {
            warnings.add(
                    "조건에 맞는 서로 다른 세트가 적어 "
                            + outfits.size() + "개만 반환했습니다.");
        }

        if (request.gender() == Gender.UNISEX) {
            warnings.add(
                    "성별 미지정/UNISEX는 남녀 세트를 모두 후보로 사용합니다. 캐릭터 성별을 고정하려면 MALE 또는 FEMALE을 전달하세요.");
        }

        return new OutfitResponse(
                "RULE_BASED",
                catalog.data().version(),
                request,
                ctx.temperature(),
                ctx.outerTemperature(),
                List.copyOf(outfits),
                ctx.advice(),
                List.copyOf(warnings));
    }

    private boolean matchesPreference(Definition set, Preference preference) {
        boolean dress = !set.ids("onePiece").isEmpty();

        return switch (preference) {
            case ANY -> true;
            case ONE_PIECE -> dress;
            case PANTS -> !dress && set.ids("bottom").stream()
                    .allMatch(id ->
                            catalog.item(id).bottomType() != BottomType.SKIRT);
            case SKIRT -> !dress && set.ids("bottom").stream()
                    .allMatch(id ->
                            catalog.item(id).bottomType() == BottomType.SKIRT);
        };
    }

    private double scoreSet(Definition set, WeatherRules.Context ctx) {
        double score =
                100 - Math.abs(ctx.temperature() - set.idealTemperature()) * 4;

        score -= distance(
                ctx.temperature(),
                set.minTemperature(),
                set.maxTemperature()) * 12;

        if (ctx.wet()) {
            if (set.tags().contains("RAIN")) score += 24;
            if (set.ids("outer").contains("leather_jacket")) score -= 15;
        } else if (set.tags().contains("RAIN")) {
            score -= 18;
        }

        if (ctx.windy()) {
            if (set.tags().contains("WIND")) score += 8;
            if (set.tags().contains("WIND_SENSITIVE")) score -= 20;
        }

        // 봄·가을처럼 기온대가 겹치는 날에는 달력 계절을 보조 기준으로 사용합니다.
        // 한여름·한겨울에 가까운 날씨라면 기존 기온·강수·바람 점수를 우선합니다.
        score += seasonalScore(set, ctx);

        return score;
    }

    private double seasonalScore(Definition set, WeatherRules.Context ctx) {
        Season currentSeason = season(ctx.request().date().getMonthValue());
        Season setSeason = set.season();
        double temperature = ctx.temperature();
        double humidity = ctx.request().humidity();

        boolean isSpringOrAutumn = currentSeason == Season.SPRING
                || currentSeason == Season.AUTUMN;
        boolean isTransitionalSet = setSeason == Season.SPRING
                || setSeason == Season.AUTUMN;
        boolean isMildWeather = temperature >= 10 && temperature <= 23;
        boolean isSummerLike = temperature >= 22 && humidity >= 75;

        if (!isSpringOrAutumn || !isTransitionalSet
                || !isMildWeather || isSummerLike) {
            return 0;
        }

        return currentSeason == setSeason ? 10 : -10;
    }

    private Outfit assemble(
            Definition set,
            WeatherRules.Context ctx,
            Random random,
            Set<String> warnings,
            LocalTime forecastTime) {

        Garment top = pick(set, "top", ctx, random);
        Garment bottom = pick(set, "bottom", ctx, random);
        Garment dress = pick(set, "onePiece", ctx, random);
        Garment inner = pick(set, "innerTop", ctx, random);
        Garment outer = pick(set, "outer", ctx, random);
        Garment shoes = pick(set, "shoes", ctx, random);
        Garment base = ctx.baseLayerRequired()
                ? catalog.item("thermal") : null;

        OuterUsage usage =
                outer == null ? OuterUsage.NONE : OuterUsage.WEAR;

        var extras = accessories.select(ctx, set, usage, forecastTime);

        var reasons = new ArrayList<String>();
        reasons.add("기온·습도·바람·강수에 맞춰 이미지가 있는 고정 세트를 선택했습니다.");
        reasons.add(
                "세부 의류는 " + set.key() + "에 허용된 조합 안에서만 선택했습니다.");

        if (set.season() != season(ctx.request().date().getMonthValue())) {
            reasons.add("달력 계절보다 전달된 날씨를 우선했습니다.");
        }

        if (base != null) {
            reasons.add(
                    "추운 날씨에 대비해 겉으로 보이는 세트를 바꾸지 않는 발열 내의를 추가했습니다.");
        }

        if (ctx.wet() && (outer == null || outer.waterResistance() == 0)) {
            warnings.add(
                    "선택된 세트의 일반 겉옷을 방수 의류로 간주하지 않습니다. 비·눈 대비는 신발·소품 및 별도 안내를 확인하세요.");
        }

        if (ctx.windy() && set.tags().contains("WIND_SENSITIVE")) {
            warnings.add(
                    "선택한 세트에 바람에 날릴 수 있는 치마·원피스가 포함되어 있습니다.");
        }

        var structure = dress == null
                ? Structure.SEPARATES
                : inner == null
                ? Structure.ONE_PIECE
                : Structure.LAYERED_ONE_PIECE;

        String signature = set.key() + "|" + String.join(
                "|", id(top), id(bottom), id(dress),
                id(inner), id(outer), id(base), id(shoes));

        String outfitId = UUID.nameUUIDFromBytes(
                signature.getBytes(StandardCharsets.UTF_8)).toString();

        return new Outfit(
                outfitId,
                set.key(),
                set.name(),
                set.gender(),
                set.season(),
                Visual.of(set.key()),
                structure,
                Item.of(top),
                Item.of(bottom),
                Item.of(dress),
                Item.of(inner),
                Item.of(outer),
                usage,
                Item.of(base),
                Item.of(shoes),
                extras.stream().map(AccessoryItem::name).toList(),
                extras,
                List.copyOf(reasons));
    }

    private Garment pick(
            Definition set,
            String part,
            WeatherRules.Context ctx,
            Random random) {

        var options = set.ids(part).stream()
                .map(catalog::item)
                .toList();

        if (options.isEmpty()) return null;

        if (part.equals("shoes")) {
            var precipitation = ctx.request().precipitation();

            if (precipitation == Precipitation.SNOW
                    || precipitation == Precipitation.MIXED) {
                options = options.stream()
                        .filter(g -> g.tags().contains("GRIP")
                                && g.waterResistance() > 0)
                        .toList();
            } else if (ctx.wet()) {
                options = options.stream()
                        .filter(g -> g.waterResistance() > 0)
                        .toList();
            }

            if (options.isEmpty()) {
                throw new IllegalStateException(
                        "세트의 날씨 대응 신발 후보가 없습니다: " + set.key());
            }
        }

        Garment best = null;
        double bestScore = -Double.MAX_VALUE;

        for (var garment : options) {
            double temperature = ctx.temperature();

            double score =
                    100 - Math.abs(
                            temperature - garment.idealTemperature()) * 2
                            - distance(
                            temperature,
                            garment.minTemperature(),
                            garment.maxTemperature()) * 8;

            if (temperature >= 25) {
                score += garment.breathability()
                        * (ctx.request().humidity() >= 70 ? 3 : 1);
            }

            if (ctx.wet()) {
                score += garment.waterResistance() * 5;
            } else if (garment.id().equals("rain_sneakers")) {
                score -= 10;
            }

            if (ctx.windy()) {
                score += garment.windResistance() * 2;
            }

            if (part.equals("shoes")
                    && set.occasionLabel().equals("출근")
                    && garment.id().equals("loafers")) {
                score += 3;
            }

            if (part.equals("shoes")
                    && set.tags().contains("SPORT")
                    && garment.style() == Style.SPORT) {
                score += 3;
            }

            score += random.nextDouble() * 0.5;

            if (score > bestScore) {
                best = garment;
                bestScore = score;
            }
        }

        return best;
    }

    private static double distance(double temperature, double min, double max) {
        return Math.max(0, Math.max(min - temperature, temperature - max));
    }

    private static String id(Garment garment) {
        return garment == null ? "-" : garment.id();
    }

    private static Season season(int month) {
        return switch (month) {
            case 3, 4, 5 -> Season.SPRING;
            case 6, 7, 8 -> Season.SUMMER;
            case 9, 10, 11 -> Season.AUTUMN;
            default -> Season.WINTER;
        };
    }
}
