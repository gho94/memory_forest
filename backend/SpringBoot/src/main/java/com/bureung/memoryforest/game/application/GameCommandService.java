package com.bureung.memoryforest.game.application;

import com.bureung.memoryforest.ai.AIClientService;
import com.bureung.memoryforest.game.domain.GameDetail;
import com.bureung.memoryforest.game.domain.GameMaster;
import com.bureung.memoryforest.game.repository.GameDetailRepository;
import com.bureung.memoryforest.game.repository.GameMasterRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class GameCommandService {

    private final GameDetailRepository gameDetailRepository;
    private final GameMasterRepository gameMasterRepository;
    private final AIClientService aiClientService;

    private static final String UPLOAD_DIR = "/app/uploads/";

    public String createGame(String categoryCode, MultipartFile file, String answerText,
                             String gameName, String gameDesc, String difficultyLevel, String createdBy) throws IOException {

        String gameId = generateGameId();

        GameMaster gameMaster = GameMaster.builder()
                .gameId(gameId)
                .gameName(gameName)
                .gameDesc(gameDesc)
                .gameCount(1)
                .difficultyLevel(difficultyLevel)
                .creationStatusCode("CREATING")
                .createdBy(createdBy)
                .build();

        gameMasterRepository.save(gameMaster);

        String fileName = saveFile(file);
        Path filePath = Paths.get(UPLOAD_DIR + fileName);

        GameDetail gameDetail = GameDetail.builder()
                .gameId(gameId)
                .gameSeq(1)
                .gameOrder(1)
                .categoryCode(categoryCode)
                .originalName(file.getOriginalFilename())
                .fileName(fileName)
                .filePath(filePath.toString())
                .fileSize(file.getSize())
                .mimeType(file.getContentType())
                .answerText(answerText)
                .aiStatus("PENDING")
                .build();

        gameDetailRepository.save(gameDetail);

        return gameId;
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

    private String saveFile(MultipartFile file) throws IOException {
        Files.createDirectories(Paths.get(UPLOAD_DIR));
        String fileExtension = getFileExtension(file.getOriginalFilename());
        String fileName = UUID.randomUUID() + "." + fileExtension;
        Path targetLocation = Paths.get(UPLOAD_DIR).resolve(fileName);
        Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
        return fileName;
    }

    private String getFileExtension(String filename) {
        return filename.substring(filename.lastIndexOf(".") + 1);
    }
}
