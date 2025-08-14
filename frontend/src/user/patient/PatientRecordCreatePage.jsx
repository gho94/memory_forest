import '@/assets/css/common.css';
import '@/assets/css/patient.css';
import PatientHeader from "@/components/layout/header/PatientHeader";
import PatientFooter from "@/components/layout/footer/PatientFooter";
import RecordButtonItem from "@/components/record/RecordButtonItem";
import RecordingStatusItem from "@/components/record/RecordingStatusItem";
import AudioPreviewItem from "@/components/record/AudioPreviewItem";
import RecordDescriptionItem from "@/components/record/RecordDescriptionItem";
import useSpeechRecording from "@/hooks/record/patient/useSpeechRecording";
import useTodayRecordCheck from "@/hooks/record/patient/useTodayRecordCheck";
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

function PatientRecordCreatePage() {
  const navigate = useNavigate();
  const {
    isRecording,
    audioBlob,
    isUploading,
    recordingTime,
    transcriptText,
    startRecording,
    stopRecording,
    uploadToServer,
    resetRecording
  } = useSpeechRecording();


  const { todayRecordExists, checkTodayRecord } = useTodayRecordCheck();

  // 컴포넌트 마운트 시 오늘 기록 확인
  useEffect(() => {
    const checkAndRedirect = async () => {
      const exists = await checkTodayRecord();
      if (exists) {
        alert('오늘은 이미 기록을 하였습니다.');
        navigate('/recorder/record/list');
      }
    };

    checkAndRedirect();
  }, [checkTodayRecord, navigate]);

  const handleRecordClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleComplete = async () => {
    const success = await uploadToServer();
    if (success) {
      alert('저장되었습니다.');
      navigate('/recorder/record/list');
    }
  };

  const handleReRecord = () => {
    resetRecording();
  };

  return (
      <div className="app-container d-flex flex-column">
        <PatientHeader />
        <main className="content-area patient-con">
          <div className="greeting">
            오늘 하루는
            <br />
            어땠나요?
          </div>

          <section className="content-con">
            <div className="game-icon-con">
              <RecordButtonItem
                  isRecording={isRecording}
                  audioBlob={audioBlob}
                  isUploading={isUploading}
                  onRecordClick={handleRecordClick}
              />

              <RecordingStatusItem
                  isRecording={isRecording}
                  recordingTime={recordingTime}
              />

              {audioBlob && !isRecording && (
                  <AudioPreviewItem
                      audioBlob={audioBlob}
                      onReRecord={handleReRecord}
                  />
              )}
            </div>
          </section>

          <RecordDescriptionItem isRecording={isRecording} />

          <button
              className="btn btn-patient"
              onClick={handleComplete}
              disabled={!audioBlob || isUploading || isRecording}
              style={{
                opacity: (!audioBlob || isUploading || isRecording) ? 0.5 : 1
              }}
          >
            {isUploading ? '저장 중...' : '완료'}
          </button>
        </main>
        <PatientFooter />
      </div>
  );
}

export default PatientRecordCreatePage;