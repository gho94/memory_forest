package com.bureung.memoryforest.game.application.impl;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.game.application.GameMasterService;
import com.bureung.memoryforest.game.application.GameService;
import com.bureung.memoryforest.game.dto.request.GameCreateReqDto;
import com.bureung.memoryforest.game.dto.request.GameDetailDto;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GamePlayer;
import com.bureung.memoryforest.game.domain.GamePlayerAnswer;
import com.bureung.memoryforest.game.domain.GamePlayerAnswerId;
import com.bureung.memoryforest.game.domain.GamePlayerId;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import com.bureung.memoryforest.game.repository.GamePlayerAnswerRepository;
import com.bureung.memoryforest.game.repository.GamePlayerRepository;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.common.application.CommonCodeService;
import com.bureung.memoryforest.game.dto.response.GameListResponseDto;
import com.bureung.memoryforest.user.domain.User;
import com.bureung.memoryforest.user.repository.UserRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class GameServiceImpl implements GameService {

    private final GameMasterRepository gameMasterRepository;
    private final GamePlayerRepository gamePlayerRepository;  
    private final GameDetailRepository gameDetailRepository;
    private final GamePlayerAnswerRepository gamePlayerAnswerRepository;
    private final CommonCodeService commonCodeService;
    private final UserRepository userRepository;
    private final GameMasterService gameMasterService;


    @Override
    public List<GameMaster> getAllGame() {
        return gameMasterRepository.findAll();
    }

    @Override
    public List<GameDetail> getGameDetail(String gameId) {
        return gameDetailRepository.findByGameIdOrderByGameSeq(gameId);
    }

    @Override
    public GameMaster createGame(GameCreateReqDto gameCreateReqDto) {
        String gameId = generateGameId();
        
        GameMaster gameMaster = GameMaster.builder()
                .gameId(gameId)
                .gameName(gameCreateReqDto.getGameName())
                .gameCount(gameCreateReqDto.getTotalProblems())
                .difficultyLevelCode(getDifficultyLevelCode())
                .creationStatusCode(getCreationStatusCode())
                .createdBy(gameCreateReqDto.getCreatedBy())
                .updatedAt(null)
                .build();
                
        gameMasterRepository.save(gameMaster);
        createGamePlayer(gameId, gameCreateReqDto.getSelectedPatients());

        // 게임 디테일 생성
        createGameDetail(gameId, gameCreateReqDto);

        // TODO: 게임 생성 이후에 AI 분석 요청
        // AI 관련 컬럼값 변경 
        // gameDetail 테이블 변경점 wrong_option_1, wrong_option_2, wrong_option_3, wrong_score_1, wrong_score_2, wrong_score_3, ai_status_code, ai_processed_at
        // gameMaster 테이블 변경점 creation_status_code (완료 or 실패)

        try {
            CompletableFuture<Void> aiAnalysisFuture = gameMasterService.processAIAnalysis(gameId);
            
            aiAnalysisFuture.thenRun(() -> {
                try {
                    GameMaster updatedGameMaster = gameMasterRepository.findById(gameId).orElse(null);
                    if (updatedGameMaster != null) {
                        log.info("AI 분석 완료 후 GameMaster 상태: gameId={}, creationStatusCode={}", 
                                gameId, updatedGameMaster.getCreationStatusCode());
                    }
                } catch (Exception e) {
                    log.error("AI 분석 완료 후 GameMaster 상태 확인 실패: gameId={}", gameId, e);
                }
            });            
            log.info("gameId : " + gameId + "AI 분석이 시작되었습니다.");
        } catch (Exception e) {
            log.error("AI 분석 요청 실패: gameId={}", gameId, e);
        }

        return gameMaster;
    }

    @Override
    public List<GameListResponseDto> getGameListInfo() {
        List<GameMaster> games = gameMasterRepository.findAll();
        
        return games.stream()
                .map(game -> {
                    // 각 게임에 참여한 플레이어 정보 조회 (User 객체 직접)
                    List<User> players = gamePlayerRepository
                            .findByIdGameId(game.getGameId())
                            .stream()
                            .map(gamePlayer -> userRepository.findById(gamePlayer.getId().getPlayerId()).orElse(null))
                            .filter(user -> user != null) // null 제거
                            .collect(Collectors.toList());                    
                    return new GameListResponseDto(game, players);
                })
                .collect(Collectors.toList());
    }
    
    private void createGamePlayer(String gameId, List<String> selectedPatients) {
        for (String patientId : selectedPatients) {
            GamePlayer gamePlayer = GamePlayer.builder()
                .id(new GamePlayerId(gameId, patientId))
                .gameStatusCode(getGameStatusCode())
                .build();
            gamePlayerRepository.save(gamePlayer);
        }
    }

    private void createGameDetail(String gameId, GameCreateReqDto gameCreateReqDto) {
        List<GameDetailDto> gameDetails = gameCreateReqDto.getGameDetails();
        int gameSeq = 1;
        for (GameDetailDto gameDetail : gameDetails) {
            GameDetail gameDetailEntity = GameDetail.builder()
                .gameId(gameId)
                .gameSeq(gameSeq)
                .gameOrder(gameSeq)
                .gameTitle(gameDetail.getGameTitle())
                .gameDesc(gameDetail.getGameDesc())
                .fileId(gameDetail.getFileId())
                .answerText(gameDetail.getAnswerText())
                .aiStatusCode(getAiStatusCode()) // 통일된 AI 상태 코드 사용
                .build();

            gameDetailRepository.save(gameDetailEntity);
            createGamePlayerAnswer(gameId, gameDetailEntity, gameCreateReqDto.getSelectedPatients());
            gameSeq++;
        }
    }

    private void createGamePlayerAnswer(String gameId, GameDetail gameDetail, List<String> selectedPatients) {
        for (String patientId : selectedPatients) {
            GamePlayerAnswer gamePlayerAnswer = GamePlayerAnswer.builder()
                .id(new GamePlayerAnswerId(gameId, gameDetail.getGameSeq(), patientId))
                .selectedOption(0)
                .isCorrect("N")
                .build();
            gamePlayerAnswerRepository.save(gamePlayerAnswer);
        }
    }

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

    private String getDifficultyLevelCode() {
        // 난이도 코드: B20001(초급), B20002(중급), B20003(고급), B20004(전문가)
        // 기본값으로 초급 사용
        return "B20001"; // 초급으로 고정 (CommonCode 조회 대신 직접 설정)
    }

    private String getCreationStatusCode() {
        // 게임 생성 상태 코드: B20005(대기중), B20006(생성중), B20007(완료), B20008(실패)
        // 게임 생성 시 대기중 상태로 설정
        return "B20005"; // 대기중으로 고정 (CommonCode 조회 대신 직접 설정)
    }

    private String getGameStatusCode() {
        // 게임 진행 상태 코드: B20010(대기), B20011(진행중), B20012(완료), B20013(중단), B20014(오류)
        // 게임 생성 시 대기 상태로 설정
        return "B20010"; // 대기로 고정 (CommonCode 조회 대신 직접 설정)
    }

    private String getAiStatusCode() {
        // AI 상태 코드를 게임 생성 상태 코드와 통일
        // B20005(대기중), B20006(생성중), B20007(완료), B20008(실패)
        // AI 분석 대기 상태로 설정
        return "B20005"; // 대기중으로 고정 (다른 팀원 코드와 통일)
    }

    /**
     * @deprecated 공통코드 조회 방식 대신 직접 코드값 사용으로 변경
     * CommonCode 팀원의 작업과 충돌을 피하기 위해 사용 중지
     */
    @Deprecated
    private String getCommonCode(String parentCodeId) {
        String codeId = null;
        try {
            var commonCodes = commonCodeService.getCommonCodesByParentCodeId(parentCodeId);
            if (!commonCodes.isEmpty()) {
                codeId = commonCodes.get(0).getCodeId();
            }
        } catch (Exception e) {
            log.error("공통 코드 조회 실패", e);
        }
        return codeId;
    }
}