package com.bureung.memoryforest.game.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RestController;

import com.bureung.memoryforest.game.application.GameService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.dto.request.GameCreateReqDto;
import com.bureung.memoryforest.game.dto.response.GameListResponseDto;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequiredArgsConstructor
@RestController
public class GameController {
    
    private final GameService gameService;    

    @GetMapping("/companion/dashboard")
    public ResponseEntity<List<GameListResponseDto>> getAllGame() {
        List<GameListResponseDto> games = gameService.getGameListInfo();
        return ResponseEntity.ok(games);
    }

    @GetMapping("/companion/games/list")
    public ResponseEntity<List<GameDetail>> getGameDetail(@RequestParam String gameId) {
        List<GameDetail> gameDetails = gameService.getGameDetail(gameId);
        return ResponseEntity.ok(gameDetails);
    }   

    @PostMapping("/api/game")
    public ResponseEntity<GameMaster> createGame(@RequestBody GameCreateReqDto requestDto) {
        log.info("게임 생성 API 호출: {}", requestDto);
        try {   
            GameMaster gameMaster = gameService.createGame(requestDto);
            return ResponseEntity.ok(gameMaster);
        } catch (Exception e) {
            log.error("게임 생성 실패", e);
            return ResponseEntity.badRequest().build();
        }
    }
}
