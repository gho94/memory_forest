const AudioPreview = ({ audioBlob, onReRecord }) => {
    if (!audioBlob) return null;

    return (
        <div className="re-record-con">
            <audio controls src={URL.createObjectURL(audioBlob)} className="mb-2"/>
            <button onClick={onReRecord}>
                재녹음
            </button>
        </div>
    );
};

export default AudioPreview;