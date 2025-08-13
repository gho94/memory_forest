const RecordDescriptionItem = ({ isRecording }) => {
    return (
        <div className="record_desc_con">
      <span className="dark-green-color">
        {isRecording ? '녹음 중입니다...' : '위 녹음 버튼 클릭 후'}
      </span>
            <span className="light-green-color">
        <br />
        기분, 날씨, 음식, 장소
        <br />
        등등<br />
        오늘 하루를 편하게
        <br />
        말씀해주세요!
      </span>
        </div>
    );
};

export default RecordDescriptionItem;
