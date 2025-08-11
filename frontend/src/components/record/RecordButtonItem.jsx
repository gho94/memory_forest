const recordImagePath = '/images/record_icon.svg';

const RecordButtonItem = ({
                          isRecording,
                          audioBlob,
                          isUploading,
                          onRecordClick
                      }) => {
    return (
        <div
            className={`game-icon record ${isRecording ? 'recording' : ''} ${audioBlob && !isRecording ? 'hidden' : ''}`}
            style={{
                backgroundImage: (audioBlob && !isRecording) ? 'none' : `url(${recordImagePath})`,
                cursor: 'pointer',
                opacity: isUploading ? 0.5 : 1,
                transform: isRecording ? 'scale(1.1)' : 'scale(1)',
                border: (audioBlob && !isRecording) ? 'none' : (isRecording ? '15px solid #ff8578' : '15px solid #ffe8c0')
            }}
            onClick={onRecordClick}
        />
    );
};

export default RecordButtonItem;