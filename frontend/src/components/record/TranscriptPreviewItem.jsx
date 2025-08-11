const TranscriptPreviewItem = ({ transcriptText }) => {
    if (!transcriptText.trim()) return null;

    return (
        <div style={{
            margin: '20px 0',
            padding: '15px',
            backgroundColor: 'rgba(255,255,255,0.9)',
            borderRadius: '10px',
            textAlign: 'left'
        }}>
            <h3 style={{margin: '0 0 10px 0', color: '#2d5a27'}}>인식된 텍스트:</h3>
            <p style={{margin: '10px 0', lineHeight: '1.5'}}>{transcriptText}</p>
        </div>
    );
};

export default TranscriptPreviewItem;