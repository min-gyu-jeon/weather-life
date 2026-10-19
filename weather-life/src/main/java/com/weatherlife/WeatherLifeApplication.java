package com.weatherlife;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class WeatherLifeApplication {

    public static void main(String[] args) {
        SpringApplication.run(WeatherLifeApplication.class, args);
    }

}
