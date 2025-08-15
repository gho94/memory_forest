package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.game.application.GamePlayerAnswerService;
import com.bureung.memoryforest.game.application.GamePlayerService;
import com.bureung.memoryforest.game.application.GameQueryService;
import com.bureung.memoryforest.game.dto.request.CreateGamePlayerAnswerRequestDto;
import com.bureung.memoryforest.game.dto.response.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/recorder/game")
@RequiredArgsConstructor
public class RecorderGameController {

    private final GameQueryService gameQueryService;
    private final GamePlayerAnswerService gamePlayerAnswerService;
    private final GamePlayerService gamePlayerService;

    @GetMapping("/dashboard")
    public ResponseEntity<GameRecorderDashboardResponseDto> getDashboard(HttpServletRequest request) {
        // 세션에서 user_id 가져오기
        HttpSession session = request.getSession();
        String recorderId = (String) session.getAttribute("userId");
        String userName = (String) session.getAttribute("userName");

        if (recorderId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }

        try {
            GameRecorderDashboardResponseDto dashboardData = gameQueryService.getRecorderDashboardData(recorderId, userName);
            return ResponseEntity.ok(dashboardData);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/play/{gameId}")
    public ResponseEntity<GameStageResponseDto> getGameStageData(@PathVariable String gameId, HttpServletRequest request) {
        try {
            log.info("게임 플레이 요청 - gameId: {}", gameId);
            HttpSession session = request.getSession();
            String playerId = (String) session.getAttribute("userId");
            GameStageResponseDto stageData = gameQueryService.getGameStageData(playerId, gameId);
            return ResponseEntity.ok(stageData);
        } catch (Exception e) {
            log.error("게임 스테이지별 데이터 조회 오류", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @PostMapping("/play")
    public ResponseEntity<Integer> createGamePlayerAnswer(@RequestBody CreateGamePlayerAnswerRequestDto request, HttpServletRequest httpRequest) {
        try {
            HttpSession session = httpRequest.getSession();
            String playerId = (String) session.getAttribute("userId");
            Integer score = gamePlayerAnswerService.createGamePlayerAnswer(request, playerId);
            return ResponseEntity.ok(score);
        } catch (Exception e) {
            log.error("게임 플레이 오류", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/result/{gameId}")
    public ResponseEntity<GamePlayResultResponseDto> getGamePlayResult(@PathVariable String gameId, HttpServletRequest httpRequest) {
        try {
            HttpSession session = httpRequest.getSession();
            String playerId = (String) session.getAttribute("userId");
            GamePlayResultResponseDto gamePlayResult = gamePlayerService.getGamePlayResult(gameId, playerId);
            return ResponseEntity.ok(gamePlayResult);
        } catch (Exception e) {
            log.error("게임 결과 오류", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/chart/stats")
    public ResponseEntity<Map<String, Object>> getPlayerStats(HttpServletRequest httpRequest) {
        try {
            HttpSession session = httpRequest.getSession();
            String playerId = (String) session.getAttribute("userId");
            Map<String, Object> response = gamePlayerService.getPlayerStats(playerId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("기본 통계 결과 오류", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/chart/weekly-chart")
    public ResponseEntity<GameDashboardResponseDto> getWeeklyChart(@RequestParam(required = false) String gameId, HttpServletRequest httpRequest) {
        try {
            HttpSession session = httpRequest.getSession();
            String playerId = (String) session.getAttribute("userId");
            GameDashboardResponseDto response = gameQueryService.getWeeklyAccuracyChartForRecorder(gameId, playerId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("차트 결과 오류", e);
            return ResponseEntity.badRequest().build();
        }
    }
}
