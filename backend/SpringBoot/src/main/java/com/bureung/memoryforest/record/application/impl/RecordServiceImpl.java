package com.bureung.memoryforest.record.application.impl;

import com.bureung.memoryforest.ai.application.EmotionAnalysisService;
import com.bureung.memoryforest.record.application.RecordService;
import com.bureung.memoryforest.record.dto.request.RecordDashboardRequestDto;
import com.bureung.memoryforest.record.dto.response.RecordDashboardResponseDto;
import com.bureung.memoryforest.record.dto.response.RecordDashboardStatsResponseDto;
import com.bureung.memoryforest.record.dto.response.RecordListResponseDto;
import com.bureung.memoryforest.record.dto.response.RecordWeeklyScoreChartDto;
import com.bureung.memoryforest.record.repository.RecordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.bureung.memoryforest.record.domain.Record;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class RecordServiceImpl implements RecordService {
    private final RecordRepository recordRepository;
    private final EmotionAnalysisService emotionAnalysisService;

    @Override
    @Transactional
    public void saveRecord(Integer fileId, String text, Integer duration, String userId) {
        log.info("레코드 저장 시작: fileId={}, userId={}, duration={}", fileId, userId, duration);

        try {
            Integer score = emotionAnalysisService.analyzeEmotion(text);
            log.info("감정 분석 결과: score={}", score);

            Record record = Record.builder()
                    .score(score)
                    .userId(userId)
                    .fileId(fileId)
                    .text(text)
                    .duration(duration)
                    .build();

            Record savedRecord = recordRepository.save(record);
            log.info("레코드 저장 완료: recordId={}", savedRecord.getRecordId());

        } catch (Exception e) {
            log.error("레코드 저장 실패: fileId={}, userId={}", fileId, userId, e);
            throw new RuntimeException("레코드 저장에 실패했습니다.", e);
        }
    }

    @Override
    public List<RecordListResponseDto> getRecordsByYearMonth(String userId, int year, int month) {
        // 해당 년도/월의 시작일과 마지막일 계산
        LocalDateTime startDate = LocalDate.of(year, month, 1).atStartOfDay();
        LocalDateTime endDate = startDate.withDayOfMonth(startDate.toLocalDate().lengthOfMonth());

        log.info("기록 조회 - 사용자: {}, 기간: {} ~ {}", userId, startDate, endDate);

        List<Record> records = recordRepository.findByUserIdAndCreatedAtBetweenOrderByCreatedAtDesc(
                userId, startDate, endDate);

        return records.stream()
                .map(this::convertToListDto)
                .collect(Collectors.toList());
    }

    @Override
    public boolean hasRecordToday(String userId) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));
        return recordRepository.existsByUserIdAndCreatedAt(userId, today) > 0;
    }

    private RecordListResponseDto convertToListDto(Record record) {
        return RecordListResponseDto.builder()
                .recordId(record.getRecordId())
                .fileId(record.getFileId())
                .text(record.getText())
                .duration(record.getDuration())
                .createdAt(record.getCreatedAt())
                .build();
    }

    @Override
    public RecordDashboardResponseDto getDashboardStats(RecordDashboardRequestDto request) {
        String userId = request.getUserId();
        Map<String, LocalDate> dates = determineDates(request);

        return RecordDashboardResponseDto.builder()
                .stats(buildDashboardStats(userId))
                .weeklyChart(getWeeklyScoreChart(userId, dates.get("startDate"), dates.get("endDate")))
                .record(recordRepository.getRecordEntities(userId, dates.get("endDate")))
                .searchDate(dates.get("endDate").format(DateTimeFormatter.ofPattern("yyyy년 MM월 dd일", Locale.KOREAN)))
                .build();
    }

    @Override
    public List<RecordWeeklyScoreChartDto> getWeeklyScoreChart(String userId, LocalDate startDate, LocalDate endDate) {
        log.info("주간 차트 인자: startDate={}, endDate={}, userId={}",
                startDate, endDate, userId);
        List<Object[]> rawResults = recordRepository.findWeeklyScoreChartRaw(userId, startDate, endDate);
        return rawResults.stream()
                .map(row -> {
                    LocalDate date = ((java.sql.Date) row[0]).toLocalDate();
                    Integer score = (Integer) row[1];
                    return new RecordWeeklyScoreChartDto(date, score);
                })
                .collect(Collectors.toList());
    }

    public Map<String, LocalDate> determineDates(RecordDashboardRequestDto request) {
        LocalDate endDate = request.getEndDate() != null ? request.getEndDate() : LocalDate.now(ZoneId.of("Asia/Seoul"));
        LocalDate startDate = request.getStartDate() != null ? request.getStartDate() : endDate.minusDays(6);
        return Map.of("startDate", startDate, "endDate", endDate);
    }

    private RecordDashboardStatsResponseDto buildDashboardStats(String userId) {
        LocalDate today = LocalDate.now(ZoneId.of("Asia/Seoul"));
        LocalDate yesterday = today.minusDays(1);

        return RecordDashboardStatsResponseDto.builder()
                .todayScore(recordRepository.findScoreByDate(userId, today).orElse(0))
                .yesterdayScore(recordRepository.findScoreByDate(userId, yesterday).orElse(0))
                .weeklyScore(
                        Optional.ofNullable(
                                recordRepository.findWeeklyAverageScore(
                                        userId, today.minusDays(6), today
                                )
                            ).orElse(BigDecimal.ZERO))
                .weeklyParticipation(
                        Optional.ofNullable(
                                recordRepository.findWeeklyParticipationRate(
                                        userId, today.minusDays(today.getDayOfWeek().getValue() % 7),today
                                )
                            ).orElse(BigDecimal.ZERO))
                .overallScore(recordRepository.findAverageScoreByUserId(userId))
                .weeklyScoreDiff(calculateWeeklyScoreDiff(userId, today))
                .build();
    }

    private BigDecimal calculateWeeklyScoreDiff(String userId, LocalDate endDate) {
        // 이번주 정답률 (endDate 기준으로 7일간)
        LocalDate thisWeekStart = endDate.minusDays(6);
        BigDecimal thisWeekAccuracy =
                Optional.ofNullable(
                        recordRepository.findWeeklyAverageScore(
                                userId, thisWeekStart, endDate
                        )).orElse(BigDecimal.ZERO);

        // 저번주 정답률 (그 이전 7일간)
        LocalDate lastWeekEnd = thisWeekStart.minusDays(1);
        LocalDate lastWeekStart = lastWeekEnd.minusDays(6);
        BigDecimal lastWeekAccuracy =
                Optional.ofNullable(
                        recordRepository.findWeeklyAverageScore(
                                userId, lastWeekStart, lastWeekEnd
                        )).orElse(BigDecimal.ZERO);


        // 차이 계산 (이번주 - 저번주)
        return thisWeekAccuracy.subtract(lastWeekAccuracy);
    }

}
