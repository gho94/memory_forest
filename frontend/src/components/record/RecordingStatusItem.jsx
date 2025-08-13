const RecordingStatusItem = ({ isRecording, recordingTime }) => {
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    if (!isRecording) return null;

    return (
        <div className="record-con">
            🔴 {formatTime(recordingTime)}
        </div>
    );
};

export default RecordingStatusItem;