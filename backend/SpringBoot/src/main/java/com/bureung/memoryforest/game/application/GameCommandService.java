package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.ai.AIAnalysisRequest;
import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class GameCommandService {

    private final GameDetailRepository gameDetailRepository;
    private final GameMasterRepository gameMasterRepository;
    private final AIClientService aiClientService;

    private static final String UPLOAD_DIR = "/app/uploads/";

    /**
     * 게임 생성 (파일 업로드와 함께)
     */
    public String createGame(String categoryCode, MultipartFile file, String answerText,
                             String gameName, String gameDesc, String difficultyLevel, String createdBy) throws IOException {

        String gameId = generateGameId();

        // 난이도 코드 매핑
        String difficultyCode = mapDifficultyLevelToCode(difficultyLevel);

        // GameMaster 생성
        GameMaster gameMaster = GameMaster.builder()
                .gameId(gameId)
                .gameName(gameName)
                .gameDesc(gameDesc)
                .gameCount(1)
                .difficultyLevelCode(difficultyCode)
                .creationStatusCode("CREATING")
                .createdBy(createdBy)
                .build();

        gameMasterRepository.save(gameMaster);

        // 파일 저장
        String fileName = saveFile(file);
        Path filePath = Paths.get(UPLOAD_DIR + fileName);

        // GameDetail 생성
        GameDetail gameDetail = GameDetail.builder()
                .gameId(gameId)
                .gameSeq(1)
                .gameOrder(1)
                .categoryCode(categoryCode)
                .originalName(file.getOriginalFilename())
                .fileName(fileName)
                .filePath(filePath.toString())
                .fileSize(file.getSize())
                .mimeType(file.getContentType())
                .answerText(answerText)
                .aiStatus("PENDING")
                .build();

        gameDetailRepository.save(gameDetail);

        // AI 분석 비동기 요청
        requestAIAnalysis(gameId, 1, answerText, difficultyLevel);

        log.info("게임 생성 완료: gameId={}, gameName={}", gameId, gameName);
        return gameId;
    }

    /**
     * AI 분석 비동기 요청
     */
    @Async("aiTaskExecutor")
    public CompletableFuture<Void> requestAIAnalysis(String gameId, int gameSeq, String answerText, String difficultyLevel) {
        try {
            log.info("AI 분석 요청: gameId={}, gameSeq={}, difficulty={}", gameId, gameSeq, difficultyLevel);

            // GameDetail 조회 및 상태 업데이트
            Optional<GameDetail> gameDetailOpt = gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
            if (gameDetailOpt.isPresent()) {
                GameDetail gameDetail = gameDetailOpt.get();
                gameDetail.markAIAnalyzing();
                gameDetailRepository.save(gameDetail);

                // AI 분석 요청 객체 생성
                AIAnalysisRequest request = new AIAnalysisRequest();
                request.setGameId(gameId);
                request.setGameSeq(gameSeq);
                request.setAnswerText(answerText);
                request.setDifficultyLevel(difficultyLevel);

                // AI 서비스 호출 (난이도별 분석)
                aiClientService.analyzeAnswerWithDifficulty(gameId, gameSeq, answerText, difficultyLevel);

                log.info("AI 분석 요청 완료: gameId={}, gameSeq={}", gameId, gameSeq);
            } else {
                log.warn("GameDetail을 찾을 수 없음: gameId={}, gameSeq={}", gameId, gameSeq);
            }

        } catch (Exception e) {
            log.error("AI 분석 요청 실패: gameId={}, gameSeq={}", gameId, gameSeq, e);

            // 실패 시 상태 업데이트
            Optional<GameDetail> gameDetailOpt = gameDetailRepository.findByGameIdAndGameSeq(gameId, gameSeq);
            if (gameDetailOpt.isPresent()) {
                GameDetail gameDetail = gameDetailOpt.get();
                gameDetail.markAIAnalysisFailed("AI 분석 요청 중 오류 발생: " + e.getMessage());
                gameDetailRepository.save(gameDetail);
            }
        }

        return CompletableFuture.completedFuture(null);
    }

    /**
     * 게임 ID 생성
     */
    private String generateGameId() {
        String dateStr = LocalDate.now().format(DateTimeFormatter.ofPattern("yyMMdd"));
        String maxGameId = gameMasterRepository.findMaxGameIdByDate(dateStr);

        int nextSeq = 1;
        if (maxGameId != null && maxGameId.length() >= 10) {
            String seqStr = maxGameId.substring(7);
            nextSeq = Integer.parseInt(seqStr) + 1;
        }

        return String.format("G%s%03d", dateStr, nextSeq);
    }

    /**
     * 파일 저장
     */
    private String saveFile(MultipartFile file) throws IOException {
        Files.createDirectories(Paths.get(UPLOAD_DIR));
        String fileExtension = getFileExtension(file.getOriginalFilename());
        String fileName = UUID.randomUUID() + "." + fileExtension;
        Path targetLocation = Paths.get(UPLOAD_DIR).resolve(fileName);
        Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
        return fileName;
    }

    /**
     * 파일 확장자 추출
     */
    private String getFileExtension(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".") + 1);
    }

    /**
     * 난이도 문자열을 코드로 매핑
     */
    private String mapDifficultyLevelToCode(String difficultyLevel) {
        switch (difficultyLevel.toUpperCase()) {
            case "EASY": return "D10001";
            case "NORMAL": return "D10002";
            case "HARD": return "D10003";
            case "EXPERT": return "D10004";
            default: return "D10002"; // 기본값: NORMAL
        }
    }
}
