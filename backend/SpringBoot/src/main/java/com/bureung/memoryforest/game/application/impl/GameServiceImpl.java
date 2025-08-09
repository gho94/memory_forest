package com.bureung.memoryforest.game.application.impl;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.bureung.memoryforest.game.application.GameService;
import com.bureung.memoryforest.game.dto.request.GameCreateReqDto;
import com.bureung.memoryforest.game.dto.request.GameDetailDto;
import com.bureung.memoryforest.game.domain.GameDetail2;
import com.bureung.memoryforest.game.repository.GameDetail2Repository;
import com.bureung.memoryforest.game.repository.GameMaster2Repository;
import com.bureung.memoryforest.game.domain.GameMaster2;
import com.bureung.memoryforest.common.application.CommonCodeService;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@Transactional
public class GameServiceImpl implements GameService {

    @Autowired
    GameMaster2Repository gameMasterRepository;

    @Autowired
    GameDetail2Repository gameDetailRepository;

    @Autowired
    CommonCodeService commonCodeService;

    @Override
    public List<GameMaster2> getAllGame() {
        return gameMasterRepository.findAll();
    }

    @Override
    public List<GameDetail2> getGameDetail(String gameId) {
        return gameDetailRepository.findByGameId(gameId);
    }

    @Override
    public GameMaster2 createGame(GameCreateReqDto gameCreateReqDto) {
        String gameId = generateGameId();
        
        GameMaster2 gameMaster = GameMaster2.builder()
                .gameId(gameId)
                .gameName(gameCreateReqDto.getGameName())
                .gameDesc(gameCreateReqDto.getGameDesc())
                .gameCount(gameCreateReqDto.getTotalProblems())
                .difficultyLevelCode(getDifficultyLevelCode())
                .creationStatusCode(getCreationStatusCode())
                .createdBy("ADMIN") // TODO: 로그인 기능 추가 후 수정
                .build();
                
        gameMasterRepository.save(gameMaster);

        // 게임 디테일 생성
        createGameDetail(gameId, gameCreateReqDto.getGameDetails());

        // TODO: 게임 생성 이후에 AI 분석 요청
        // AI 관련 컬럼값 변경 
        // gameDetail 테이블 변경점 wrong_option_1, wrong_option_2, wrong_option_3, wrong_score_1, wrong_score_2, wrong_score_3, ai_status_code, ai_processed_at
        // gameMaster 테이블 변경점 creation_status_code (완료 or 실패)

        return gameMaster;
    }

    private void createGameDetail(String gameId, List<GameDetailDto> gameDetails) {
        int gameSeq = 1;
        for (GameDetailDto gameDetail : gameDetails) {
            GameDetail2 gameDetail2 = GameDetail2.builder()
                .gameId(gameId)
                .gameSeq(gameSeq)
                .gameOrder(gameSeq)
                .fileId(gameDetail.getFileId())
                .answerText(gameDetail.getAnswerText())
                .description(gameDetail.getDescription())
                .aiStatusCode(getAiStatusCode())
                .build();

            gameDetailRepository.save(gameDetail2);
            gameSeq++;
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