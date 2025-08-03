package com.bureung.memoryforest.game.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GamePlayRequestDto {
    private String gameId;
    private Integer gameSeq;       // 문제 시퀀스
    private String playerId;       // 플레이어 ID
    private Integer selectedOption; // 1~4 중 선택한 답변 번호
    private Long answerTimeMs;     // 답변 소요 시간 (밀리초)
}
