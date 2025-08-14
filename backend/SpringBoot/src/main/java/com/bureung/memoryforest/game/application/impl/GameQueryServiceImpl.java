package com.bureung.memoryforest.game.application.impl;

import com.bureung.memoryforest.game.application.*;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.dto.request.GameDashboardRequestDto;
import com.bureung.memoryforest.game.dto.response.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class GameQueryServiceImpl implements GameQueryService {
    private final GamePlayerService gamePlayerService;
    private final GameMasterService gameMasterService;
    private final GamePlayerAnswerService gamePlayerAnswerService;
    private final GameDetailService gameDetailService;

    @Override
    public GameDashboardResponseDto getDashboardStats(GameDashboardRequestDto request) {
        String userId = request.getUserId();

        // endDate 우선순위: 1. param의 endDate, 2. gameId의 end_time, 3. 오늘 날짜
        Map<String, LocalDate> dates = determineDates(request, userId);

        return GameDashboardResponseDto.builder()
                .stats(buildDashboardStats(userId))
                .weeklyChart(gamePlayerService.getWeeklyAccuracyChart(userId, dates.get("startDate"), dates.get("endDate")))
                .gameList(gamePlayerAnswerService.getTodayGameAnswers(userId, dates.get("endDate")))
                .searchDate(dates.get("endDate").format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일", Locale.KOREAN)))
                .build();
    }

    /**
     * endDate 결정 로직
     * 1. request.endDate가 있으면 → request.endDate
     * 2. request.gameId가 있으면 → 해당 게임의 end_time
     * 3. 둘 다 없으면 → 오늘 날짜
     */
    private LocalDate determineEndDate(GameDashboardRequestDto request, String userId) {
        // 1순위: param의 endDate
        if (request.getEndDate() != null) {
            return request.getEndDate();
        }

        // 2순위: gameId가 있으면 해당 게임의 종료일
        if (request.getGameId() != null && !request.getGameId().isEmpty()) {
            LocalDate gameEndDate = gamePlayerService.getGameEndDate(userId, request.getGameId());
            if (gameEndDate != null) {
                return gameEndDate;
            }
        }

        // 3순위: 오늘 날짜
        return LocalDate.now(ZoneId.of("Asia/Seoul"));
    }

    private GameDashboardStatsResponseDto buildDashboardStats(String userId) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));
        LocalDate yesterday = today.minusDays(1);

        return GameDashboardStatsResponseDto.builder()
                .todayScore(gamePlayerService.getTotalScoreByDate(userId, today))
                .todayAccuracy(gamePlayerService.getAccuracyRateByDate(userId, today))
                .yesterdayScore(gamePlayerService.getTotalScoreByDate(userId, yesterday))
                .yesterdayAccuracy(gamePlayerService.getAccuracyRateByDate(userId, yesterday))
                .weeklyAccuracy(gamePlayerService.getWeeklyAverageAccuracy(userId, today))
                .weeklyParticipation(gamePlayerService.getWeeklyParticipationRate(userId, today))
                .overallAccuracy(gamePlayerService.getOverallAccuracyRate(userId))
                .weeklyAccuracyDiff(calculateWeeklyAccuracyDiff(userId, today))
                .build();
    }

    /**
     * 주간 정답률 차이 계산
     * 이번주(endDate 기준 7일) vs 저번주(그 이전 7일) 정답률 차이
     */
    private BigDecimal calculateWeeklyAccuracyDiff(String userId, LocalDate endDate) {
        // 이번주 정답률 (endDate 기준으로 7일간)
        LocalDate thisWeekStart = endDate.minusDays(6);
        BigDecimal thisWeekAccuracy = Optional.ofNullable(gamePlayerService.getWeeklyAverageAccuracy(userId, endDate)).orElse(BigDecimal.ZERO);

        // 저번주 정답률 (그 이전 7일간)
        LocalDate lastWeekEnd = thisWeekStart.minusDays(1);
        LocalDate lastWeekStart = lastWeekEnd.minusDays(6);
        BigDecimal lastWeekAccuracy = Optional.ofNullable(gamePlayerService.getWeeklyAverageAccuracyBetween(userId, lastWeekStart, lastWeekEnd)).orElse(BigDecimal.ZERO);

        // 차이 계산 (이번주 - 저번주)
        return thisWeekAccuracy.subtract(lastWeekAccuracy);
    }


    @Override
    public GameRecorderDashboardResponseDto getRecorderDashboardData(String recorderId, String userName) {
        // 1. 먼저 진행중인 게임이 있는지 확인
        Optional<GamePlayer> inProgressGame = gamePlayerService.getInProgressGameByPlayerId(recorderId);
        log.info("1번: {}", inProgressGame);
        if (inProgressGame.isPresent()) {
            // 진행중인 게임이 있는 경우
            return buildDashboard(inProgressGame.get(), "IN_PROGRESS", userName, null);
        }

        // 2. 진행중인 게임이 없으면, 안 푼 게임 중 가장 오래된 것 찾기
        Optional<GamePlayer> unplayedGame = gamePlayerService.getOldestUnplayedGameByPlayerId(recorderId);
        log.info("2번: {}", unplayedGame);
        if (unplayedGame.isPresent()) {
            // 새로운 게임이 있는 경우
            return buildDashboard(unplayedGame.get(), "NEW_GAME", userName, null);
        }

        // 3. 모든 게임을 다 푼 경우, 가장 최근에 푼 게임을 보여주기
        Optional<GamePlayer> mostRecentCompletedGame = gamePlayerService.getMostRecentCompletedGameByPlayerId(recorderId);

        log.info("3번: {}", mostRecentCompletedGame);
        if (mostRecentCompletedGame.isPresent()) {
            return buildDashboard(mostRecentCompletedGame.get(), "COMPLETED", userName, mostRecentCompletedGame.get().getAccuracyRate());
        }

        // 4. 게임이 아예 없는 경우 (예외 상황)
        throw new RuntimeException("사용 가능한 게임이 없습니다.");
    }

    private GameRecorderDashboardResponseDto buildDashboard(GamePlayer gamePlayer, String status, String userName, BigDecimal recentAccuracyRate) {
        try {
            log.info("기록: {}, 상태 : {}, 이름:{}", gamePlayer, status, userName);
            String gameId;
            int totalQuestions;
            int answeredQuestions = 0;
            Integer beforeDays = null;
            boolean isNewGame = false;

            // 진행중 또는 완료된 게임
            gameId = gamePlayer.getId().getGameId();
            totalQuestions = gameMasterService.getGameCountByGameId(gameId);
            answeredQuestions = gamePlayerAnswerService.getCountByGameIdAndPlayerId(gameId, gamePlayer.getId().getPlayerId());

            // 완료된 게임인 경우 날짜 계산
            if ("COMPLETED".equals(status)) {
                LocalDateTime now = LocalDateTime.now(ZoneId.of("Asia/Seoul"));
                LocalDateTime gameCompletedDate = gamePlayer.getEndTime();
                beforeDays = (int) ChronoUnit.DAYS.between(gameCompletedDate.toLocalDate(), now.toLocalDate());
            }

            if (recentAccuracyRate == null && gamePlayer != null) {
                recentAccuracyRate = gamePlayerService
                        .getMostRecentCompletedGameByPlayerId(gamePlayer.getId().getPlayerId())
                        .map(GamePlayer::getAccuracyRate)
                        .orElse(BigDecimal.ZERO);
            }

            return GameRecorderDashboardResponseDto.builder()
                    .gameId(gameId)
                    .currentProgress(answeredQuestions)
                    .totalQuestions(totalQuestions)
                    .isNewGame(isNewGame)
                    .beforeDays(beforeDays)
                    .status(status)
                    .userName(userName)
                    .recentAccuracyRate(recentAccuracyRate)
                    .build();

        } catch (Exception e) {
            log.error("실패다임ㅁ마!!: {}", e.getMessage());
            throw new RuntimeException(e);
        }
    }

    @Override
    public GameStageResponseDto getGameStageData(String playerId, String gameId) {
        gamePlayerService.updateStartTimeIfNull(playerId, gameId);
        int currentProgress = gamePlayerAnswerService.getCountByGameIdAndPlayerId(gameId, playerId);
        int totalQuestions = gameMasterService.getGameCountByGameId(gameId);
        log.info("currentProgress : {}, totalQuestions : {}", currentProgress, totalQuestions);
        if (currentProgress >= totalQuestions) {
            throw new RuntimeException("이용 가능한 게임이 없습니다.");
        }

        Integer gameSeq = gamePlayerAnswerService.getMaxGameSeqByGameIdAndPlayerId(gameId, playerId) + 1;
        GameDetail gameDetail = gameDetailService.getGameDetailByGameIdAndGameSeq(gameId, gameSeq).orElseThrow(() -> new RuntimeException("게임을 찾을 수 없습니다: " + gameId));

        return GameStageResponseDto.builder()
                .gameId(gameId)
                .gameSeq(gameSeq)
                .fileId(gameDetail.getFileId())
                .answerText(gameDetail.getAnswerText())
                .wrongOption1(gameDetail.getWrongOption1())
                .wrongOption2(gameDetail.getWrongOption2())
                .wrongOption3(gameDetail.getWrongOption3())
                .currentProgress(currentProgress)
                .totalQuestions(totalQuestions)
                .build();
    }

    public Map<String, LocalDate> determineDates(GameDashboardRequestDto request, String playerId) {
        LocalDate endDate = determineEndDate(request, playerId);
        LocalDate startDate = request.getStartDate() != null ? request.getStartDate() : endDate.minusDays(6);
        return Map.of("startDate", startDate, "endDate", endDate);
    }

    @Override
    public GameDashboardResponseDto getWeeklyAccuracyChartForRecorder(String gameId, String playerId) {
        GameDashboardRequestDto request = new GameDashboardRequestDto();
        request.setGameId(gameId);
        Map<String, LocalDate> dates = determineDates(request, playerId);
        return GameDashboardResponseDto.builder()
                .weeklyChart(gamePlayerService.getWeeklyAccuracyChart(playerId, dates.get("startDate"), dates.get("endDate")))
                .searchDate(dates.get("endDate").format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일", Locale.KOREAN)))
                .build();
    }
}
