package com.bureung.memoryforest.common.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CommonCodeResDto {
    private String codeId;
    private String codeName;
    private String parentCodeId;
    private String useYn;
}
