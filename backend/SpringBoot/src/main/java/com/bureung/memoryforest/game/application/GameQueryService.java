package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.game.dto.request.GameDashboardRequestDto;
import com.bureung.memoryforest.game.dto.response.GameDashboardResponseDto;
import com.bureung.memoryforest.game.dto.response.GameRecorderDashboardResponseDto;
import com.bureung.memoryforest.game.dto.response.GameStageResponseDto;

//leb. Recorder/Companion이 게임 정보를 조회할 때 조회성 로직
public interface GameQueryService {

    /**
     * 대시보드 전체 통계 데이터 조회
     * @param request 조회 조건 (userId, startDate, endDate)
     * @return 대시보드 통계 정보
     */
    GameDashboardResponseDto getDashboardStats(GameDashboardRequestDto request);
    GameRecorderDashboardResponseDto getRecorderDashboardData(String recorderId, String userName);
    GameStageResponseDto getGameStageData(String playerId, String gameId);
}
