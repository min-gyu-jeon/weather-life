package com.weatherlife.controller;

import com.weatherlife.service.AccessoryCatalog;
import com.weatherlife.service.OutfitSetCatalog;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/outfits")
public class OutfitCatalogController {
    private final OutfitSetCatalog sets;
    private final AccessoryCatalog accessories;
    public OutfitCatalogController(OutfitSetCatalog sets, AccessoryCatalog accessories) {
        this.sets = sets;
        this.accessories = accessories;
    }
    @GetMapping("/sets") public OutfitSetCatalog.Data sets() { return sets.data(); }
    @GetMapping("/accessories") public AccessoryCatalog.Data accessories() { return accessories.data(); }
}
