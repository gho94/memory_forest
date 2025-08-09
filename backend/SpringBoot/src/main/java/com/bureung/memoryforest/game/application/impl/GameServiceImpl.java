package com.bureung.memoryforest.game.application.impl;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

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

    @Override
    public List<GameMaster> getAllGame() {
        return gameMasterRepository.findAll();
    }

    @Override
    public List<GameDetail> getGameDetail(String gameId) {
        return gameDetailRepository.findByGameId(gameId);
    }

    @Override
    public GameMaster createGame(GameCreateReqDto gameCreateReqDto) {
        String gameId = generateGameId();
        
        GameMaster gameMaster = GameMaster.builder()
                .gameId(gameId)
                .gameName(gameCreateReqDto.getGameName())
                .gameDesc(gameCreateReqDto.getGameDesc())
                .gameCount(gameCreateReqDto.getTotalProblems())
                .difficultyLevelCode(getDifficultyLevelCode())
                .creationStatusCode(getCreationStatusCode())
                .createdBy("ADMIN") // TODO: 로그인 기능 추가 후 수정
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

        return gameMaster;
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
                .fileId(gameDetail.getFileId())
                .answerText(gameDetail.getAnswerText())
                .description(gameDetail.getDescription())
                .aiStatusCode(getAiStatusCode())
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
        // TODO: 코드 난이도 설정하는 화면이 있을 때 사용
        // 현재는 기본값으로 초급 코드(B20001) 사용 하고 AI 분석 이후 코드 값 변경        
        // -- 2.1.1 게임 난이도 (DIFFICULTY_LEVEL)
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
        // VALUES ('B10001', '게임 난이도', 'B00001', 'ADMIN');

        // -- 2.1.2 하위 코드들
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
        //                                                                          ('B20001', '초급', 'B10001', 'ADMIN'),
        //                                                                          ('B20002', '중급', 'B10001', 'ADMIN'),
        //                                                                          ('B20003', '고급', 'B10001', 'ADMIN'),
        //                                                                          ('B20004', '전문가', 'B10001', 'ADMIN');
        return getCommonCode("B10001");
    }

    private String getCreationStatusCode() {
        // TODO: 게임 생성 상태
        // 현재는 기본값으로 대기 코드(B20005) 사용 하고 AI 분석 이후 (오답 생성) 코드 값 변경
        // -- 2.2.1 게임 생성 상태 (CREATION_STATUS)
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
        // VALUES ('B10002', '게임 생성 상태', 'B00001', 'ADMIN');

        // -- 2.2.2 하위 코드들
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
        //                                                                          ('B20005', '대기중', 'B10002', 'ADMIN'),
        //                                                                          ('B20006', '생성중', 'B10002', 'ADMIN'),
        //                                                                          ('B20007', '완료', 'B10002', 'ADMIN'),
        //                                                                          ('B20008', '실패', 'B10002', 'ADMIN'),
        return getCommonCode("B10002");
    }

    private String getGameStatusCode() {
        // TODO: 게임 진행 상태
        // -- 2.3.1 게임 진행 상태 (GAME_STATUS)
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
        // VALUES ('B10003', '게임 진행 상태', 'B00001', 'ADMIN');

        // -- 2.3.2 하위 코드들
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
        //                                                                          ('B20010', '대기', 'B10003', 'ADMIN'),
        //                                                                          ('B20011', '진행중', 'B10003', 'ADMIN'),
        //                                                                          ('B20012', '완료', 'B10003', 'ADMIN'),
        //                                                                          ('B20013', '중단', 'B10003', 'ADMIN'),
        //                                                                          ('B20014', '오류', 'B10003', 'ADMIN');
        return getCommonCode("B10003");
    }

    private String getAiStatusCode() {
        // TODO: AI 상태 코드
        // 현재는 기본값으로 대기 코드(B20015) 사용 하고 AI 분석 이후 (오답 생성) 코드 값 변경
        // -- 2.4.1 Ai 상태 코드 (AI_STATUS)
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by)
        // VALUES ('B10004', 'Ai 상태 코드', 'B00001', 'ADMIN');

        // -- 2.4.2 하위 코드들         
        // INSERT INTO common_codes (code_id, code_name, parent_code_id, created_by) VALUES
        //                                                                          ('B20015', '대기', 'B10004', 'ADMIN'),
        //                                                                          ('B20016', '완료', 'B10004', 'ADMIN'),
        //                                                                          ('B20017', '실패', 'B10004', 'ADMIN');
        return getCommonCode("B10004");
    }

    private String getCommonCode(String parendCodeId) {
        String codeId = null;
        try {
            var commonCodes = commonCodeService.getCommonCodesByParentCodeId(parendCodeId);
            if (!commonCodes.isEmpty()) {
                codeId = commonCodes.get(0).getCodeId();
            }
        } catch (Exception e) {
            log.error("공통 코드 조회 실패", e);
        }
        return codeId;
    }
}