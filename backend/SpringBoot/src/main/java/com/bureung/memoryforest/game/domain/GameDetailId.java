package com.bureung.memoryforest.game.domain;

import lombok.*;
import java.io.Serializable;
import java.util.Objects;

/**
 * GameDetail 엔티티의 복합 기본키 클래스
 * JPA에서 복합키 사용 시 @IdClass 어노테이션과 함께 사용
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class GameDetailId implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    private String gameId;
    private Integer gameSeq;
    
    // equals와 hashCode는 복합키에서 매우 중요함
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GameDetailId that = (GameDetailId) o;
        return Objects.equals(gameId, that.gameId) && 
               Objects.equals(gameSeq, that.gameSeq);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(gameId, gameSeq);
    }
}