package com.weatherlife.service;

public class NoOutfitException extends RuntimeException {
    public NoOutfitException() {
        super("성별·선호 조건에 맞는 등록된 의상 세트가 없습니다. 선호 조건을 완화하거나 해당 캐릭터 세트를 추가하세요.");
    }
}
