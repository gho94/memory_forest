package com.bureung.memoryforest.game.domain;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
public class GameMasterId implements Serializable {
    private String gameId;
    private Integer gameSeq;
}