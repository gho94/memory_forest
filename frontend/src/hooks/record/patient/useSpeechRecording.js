import { useState, useRef } from 'react';
import useFileUpload from '@/hooks/common/useFileUpload';

const useSpeechRecording = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [transcriptText, setTranscriptText] = useState('');
    const { uploadFile } = useFileUpload();
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const timerRef = useRef(null);
    const recognitionRef = useRef(null);

    // 녹음 시작
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];
            setTranscriptText('');

            // 음성 파일 녹음
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                setAudioBlob(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            // Web Speech API로 실시간 텍스트 변환
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();

                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'ko-KR';

                recognition.onresult = (event) => {
                    let finalTranscript = '';
                    for (let i = 0; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        }
                    }
                    if (finalTranscript) {
                        setTranscriptText(prev => prev + finalTranscript + ' ');
                    }
                };

                recognition.onerror = (event) => {
                    console.warn('음성 인식 오류:', event.error);

                    if (event.error === 'no-speech') {
                        console.log('음성이 감지되지 않았습니다.');
                        // 조용한 경우는 오류로 처리하지 않음
                    } else if (event.error === 'audio-capture') {
                        alert('마이크에 문제가 있습니다. 재녹음해주세요.');
                    } else if (event.error === 'not-allowed') {
                        alert('마이크 권한이 필요합니다. 재녹음해주세요.');
                    } else if (event.error === 'network') {
                        alert('네트워크 오류가 발생했습니다. 재녹음해주세요.');
                    } else {
                        alert('음성 인식에 문제가 발생했습니다. 재녹음을 권장합니다.');
                    }
                };

                recognitionRef.current = recognition;
                recognition.start();
            }

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

        } catch (error) {
            console.error('마이크 접근 오류:', error);
            alert('마이크 권한이 필요합니다.');
        }
    };

    // 녹음 중지
    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();

            // 음성 인식 중지
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }

            setIsRecording(false);

            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
            }
        }
    };

    // WebM을 WAV로 변환
    const convertToWav = async (webmBlob) => {
        return new Promise((resolve) => {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const fileReader = new FileReader();

            fileReader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                    const wavBuffer = audioBufferToWav(audioBuffer);
                    const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
                    resolve(wavBlob);
                } catch (error) {
                    resolve(webmBlob);
                }
            };

            fileReader.readAsArrayBuffer(webmBlob);
        });
    };

    const audioBufferToWav = (buffer) => {
        const length = buffer.length;
        const numberOfChannels = buffer.numberOfChannels;
        const sampleRate = buffer.sampleRate;
        const bytesPerSample = 2;
        const blockAlign = numberOfChannels * bytesPerSample;
        const byteRate = sampleRate * blockAlign;
        const dataSize = length * blockAlign;
        const bufferSize = 44 + dataSize;

        const arrayBuffer = new ArrayBuffer(bufferSize);
        const view = new DataView(arrayBuffer);

        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, bufferSize - 8, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numberOfChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bytesPerSample * 8, true);
        writeString(36, 'data');
        view.setUint32(40, dataSize, true);

        let offset = 44;
        for (let i = 0; i < buffer.length; i++) {
            for (let channel = 0; channel < numberOfChannels; channel++) {
                const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
                view.setInt16(offset, sample * 0x7FFF, true);
                offset += 2;
            }
        }

        return arrayBuffer;
    };

    // 서버로 전송 (2단계: 파일 업로드 → 레코드 저장)
    const uploadToServer = async () => {
        if (!audioBlob) {
            alert('녹음된 파일이 없습니다.');
            return;
        }

        setIsUploading(true);

        try {
            // 1단계: 파일 업로드
            const wavBlob = await convertToWav(audioBlob);
            const fileId = await uploadFile(wavBlob);

            if (!fileId) {
                throw new Error('파일 업로드에 실패했습니다.');
            }

            // 2단계: 레코드 저장
            const response = await fetch(`${window.API_BASE_URL}/recorder/record/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    fileId: fileId,
                    text: transcriptText.trim(),
                    duration: recordingTime
                }),
            });

            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }

            const result = await response.text();
            if (result === 'success') {
                return true;
            }
            return false;

        } catch (error) {
            console.error('파일 업로드 오류:', error);
            alert('파일 업로드 중 오류가 발생했습니다.');
            return false;
        } finally {
            setIsUploading(false);
        }
    };

    // 초기화
    const resetRecording = () => {
        setAudioBlob(null);
        setTranscriptText('');
        setRecordingTime(0);
    };

    return {
        isRecording,
        audioBlob,
        isUploading,
        recordingTime,
        transcriptText,
        startRecording,
        stopRecording,
        uploadToServer,
        resetRecording
    };
};

export default useSpeechRecording;