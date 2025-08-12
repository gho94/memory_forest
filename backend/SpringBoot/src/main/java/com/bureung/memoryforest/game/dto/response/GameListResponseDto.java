package com.bureung.memoryforest.game.dto.response;

import lombok.*;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.user.domain.User;
import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameListResponseDto {    
    private String gameId;
    private String gameName;
    private String gameDesc;
    private Integer gameCount;
    private String difficultyLevelCode;
    private String creationStatusCode;
    private String createdBy;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    private List<User> players;
    
    public GameListResponseDto(GameMaster gameMaster, List<User> players) {
        this.gameId = gameMaster.getGameId();
        this.gameName = gameMaster.getGameName();
        this.gameDesc = gameMaster.getGameDesc();
        this.gameCount = gameMaster.getGameCount();
        this.difficultyLevelCode = gameMaster.getDifficultyLevelCode();
        this.creationStatusCode = gameMaster.getCreationStatusCode();
        this.createdBy = gameMaster.getCreatedBy();
        this.createdAt = gameMaster.getCreatedAt();
        this.updatedAt = gameMaster.getUpdatedAt();
        this.players = players;
    }
}
