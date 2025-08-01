package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.domain.GameMaster;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/companion/game")
public class CompanionGameController {
    private final GameMasterService gameMasterService;

    public CompanionGameController(GameMasterService gameMasterService) {
        this.gameMasterService = gameMasterService;
    }

    @GetMapping("/search/by-name")
    public ResponseEntity<List<GameMaster>> searchByName(@RequestParam String name) {
        System.out.println("검색어: " + name);
        return ResponseEntity.ok(gameMasterService.getGamesByGameName(name));
    }

//    @GetMapping("/search/by-answer")
//    public ResponseEntity<List<GameMaster>> searchByAnswer(@RequestParam String answer) {
//        return ResponseEntity.ok(gameMasterService.getGamesByGameAnswer(answer));
//    }

//    @GetMapping("/search/by-content")
//    public ResponseEntity<List<GameMaster>> searchByContent(@RequestParam String content) {
//        return ResponseEntity.ok(gameMasterService.getGamesByGameContent(content));
//    }
}
