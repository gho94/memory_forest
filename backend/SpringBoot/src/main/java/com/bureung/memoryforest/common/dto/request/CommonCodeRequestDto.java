package com.bureung.memoryforest.common.dto.request;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CommonCodeRequestDto {    
    private String codeName;
    private String parentCodeID;
    private String useYn;
}
