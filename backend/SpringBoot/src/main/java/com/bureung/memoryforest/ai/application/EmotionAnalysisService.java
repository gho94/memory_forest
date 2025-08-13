package com.bureung.memoryforest.ai.application;
import com.bureung.memoryforest.ai.dto.request.GPTRequest;
import com.bureung.memoryforest.ai.dto.response.GPTResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import java.util.List;

import org.springframework.web.reactive.function.client.WebClientResponseException;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmotionAnalysisService {

    private final WebClient webClient;

    @Value("${openai.api.key}")
    private String apiKey;

    @Value("${openai.api.url}")
    private String apiUrl;

    @Value("${openai.api.model}")
    private String model;

    public Integer analyzeEmotion(String text) {
        try {
            log.info("감정 분석 시작: text={}", text);
            log.info("사용 모델: {}", model);

            // 공식문서 그대로!
            GPTRequest request = GPTRequest.builder()
                    .model(model)  // gpt-5-nano
                    .messages(List.of(
                            GPTRequest.Message.builder()
                                    .role("developer")
                                    .content("You are a helpful assistant. Analyze emotion and respond with only a number 0-100.")
                                    .build(),
                            GPTRequest.Message.builder()
                                    .role("user")
                                    .content("Analyze this text emotion (0-100): " + text)
                                    .build()
                    ))
                    .build();

            log.info("요청 데이터: {}", request);

            GPTResponse response = webClient.post()
                    .uri(apiUrl)
                    .header("Authorization", "Bearer " + apiKey)
                    .header("Content-Type", "application/json")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(GPTResponse.class)
                    .block();

            if (response != null && !response.getChoices().isEmpty()) {
                String content = response.getChoices().get(0).getMessage().getContent();
                log.info("GPT 원본 응답: '{}'", content);

                if (content == null || content.trim().isEmpty()) {
                    log.warn("GPT 응답이 비어있음");
                    return 50;
                }

                String trimmedContent = content.trim();

                try {
                    Integer score = Integer.parseInt(trimmedContent);
                    score = Math.max(0, Math.min(100, score));

                    log.info("감정 분석 완료: score={}, reasoning_tokens={}",
                            score,
                            response.getUsage().getCompletionTokensDetails().getReasoningTokens());
                    return score;
                } catch (NumberFormatException e) {
                    log.warn("GPT 응답 파싱 실패. 응답내용: '{}', 숫자 추출 시도", trimmedContent);

                    String numbersOnly = trimmedContent.replaceAll("[^0-9]", "");
                    if (!numbersOnly.isEmpty()) {
                        Integer score = Integer.parseInt(numbersOnly);
                        score = Math.max(0, Math.min(100, score));
                        log.info("숫자 추출 성공: score={}", score);
                        return score;
                    }

                    return 50;
                }
            }

            log.warn("GPT 응답이 비어있음");
            return 50;

        } catch (WebClientResponseException e) {
            log.error("OpenAI API 에러 응답: {}", e.getResponseBodyAsString());
            log.error("HTTP 상태 코드: {}", e.getStatusCode());
            return 50;
        } catch (Exception e) {
            log.error("감정 분석 실패: {}", e.getMessage(), e);
            return 50;
        }
    }
}
