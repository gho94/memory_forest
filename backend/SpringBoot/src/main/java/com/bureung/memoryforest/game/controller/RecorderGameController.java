package com.bureung.memoryforest.game.controller;

import com.bureung.memoryforest.game.application.GameQueryService;
import com.bureung.memoryforest.game.dto.response.GameRecorderDashboardResponseDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/recorder/game")
@RequiredArgsConstructor
public class RecorderGameController {

    private final GameQueryService gameQueryService;

    @GetMapping("/dashboard")
    public ResponseEntity<GameRecorderDashboardResponseDto> getDashboard(HttpServletRequest request) {
        // 세션에서 user_id 가져오기
        HttpSession session = request.getSession();
        String recorderId = (String) session.getAttribute("user_id");
        String userName = (String) session.getAttribute("user_name");

        recorderId = "U0002"; //leb. I'll change user id of session

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
}
