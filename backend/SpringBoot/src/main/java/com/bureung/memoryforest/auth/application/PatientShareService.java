package com.bureung.memoryforest.auth.application;

public interface PatientShareService {
    String generateShareLink(Long patientId);
    String processPatientAccess(String accessCode);
}
