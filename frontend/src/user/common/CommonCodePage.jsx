import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

const CommonCodePage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const parentCodeID = searchParams.get('parentCodeID');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [commonCodeData, setCommonCodeData] = useState([]);
    const [codeName, setCodeName] = useState('');
    const [editingCode, setEditingCode] = useState(null);
    const [isEditMode, setIsEditMode] = useState(false);
    
    useEffect(() => {
        fetchData();
    }, [parentCodeID]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const url = parentCodeID 
                ? `${window.API_BASE_URL}/api/common-codes?parentCodeID=${parentCodeID}`
                : `${window.API_BASE_URL}/api/common-codes`;            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('데이터를 가져오는데 실패했습니다.');
            }
            const data = await response.json();
            setCommonCodeData(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };
    
    const handleAddCode = async (e) => {
        e.preventDefault();
        if (codeName) {
            try {
                const response = await fetch(`${window.API_BASE_URL}/api/common-codes`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        codeName: codeName,
                        parentCodeID: parentCodeID
                    })
                });
                if (!response.ok) {
                    throw new Error('코드 추가 실패');
                }
                const data = await response.json();
                setCommonCodeData([...commonCodeData, data]);
                setCodeName('');
                fetchData();
            } catch (err) {
                console.error('코드 추가 오류:', err);
            }
        }
    }

    const handleCodeClick = (codeId) => {
        navigate(`/common-code?parentCodeID=${codeId}`);
    };

    const handleBackClick = () => {
        navigate('/common-code');
    };

    const handleEditClick = (code, e) => {
        e.stopPropagation();
        setEditingCode(code);
        setCodeName(code.codeName);
        setIsEditMode(true);
    };

    const handleUpdateCode = async (e) => {
        e.preventDefault();
        if (codeName && editingCode) {
            try {
                const response = await fetch(`${window.API_BASE_URL}/api/common-codes/${editingCode.codeId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        codeName: codeName
                    })
                });
                if (!response.ok) {
                    throw new Error('코드 수정 실패');
                }
                // 수정 후 데이터를 다시 가져와서 UI 업데이트
                await fetchData();
                setCodeName('');
                setEditingCode(null);
                setIsEditMode(false);
            } catch (err) {
                console.error('코드 수정 오류:', err);
            }
        }
    };

    const handleCancelEdit = () => {
        setCodeName('');
        setEditingCode(null);
        setIsEditMode(false);
    };



    if (loading) {
        return (
            <div className="app-container d-flex flex-column">
                <FamilyHeader />
                <main className="content-area guardian-con">
                    <div className="patient-activity-con row">
                        <div className="text-center">
                            <p>데이터를 불러오는 중...</p>
                        </div>
                    </div>
                </main>
                <FamilyFooter />
            </div>
        );
    }

    return (
        <div className="app-container d-flex flex-column"> 
            <FamilyHeader />
            <main className="content-area guardian-con">
                <div className="menu-title">
                    <div>
                        {parentCodeID ? `공통코드 리스트 (${parentCodeID})` : '공통코드 리스트'}
                        {parentCodeID && (
                            <button type="button" className="btn btn-login" onClick={handleBackClick}>뒤로가기</button>
                        )}
                    </div>
                </div>
                <div className="game-list-wrap">
                    <div className="game-list-con">                        
                            {commonCodeData.map((code) => (
                             <div className="game-item" key={code.codeId}>
                                 <div className="game-number">{commonCodeData.indexOf(code) + 1}</div>
                                 <div className="game-box" onClick={() => handleCodeClick(code.codeId)} style={{ cursor: 'pointer' }}>                                     
                                     <div className="game-title">{code.codeName}</div>
                                     <div className="game-title">{code.parentCodeId}</div>
                                     <div className="game-answer">{code.useYn}</div>
                                     <div className="game-texts"></div>
                                     <button className="game-edit-btn" onClick={(e) => handleEditClick(code, e)}>수정</button>
                                 </div>
                             </div>
                         ))}
                    </div>
                </div>
                <form className="signup-form game-signup-form" onSubmit={isEditMode ? handleUpdateCode : handleAddCode}>
                    <div className="form-control-con">
                        <input
                            type="text"
                            id="codeName"
                            className="form-control"
                            value={codeName}
                            onChange={(e) => setCodeName(e.target.value)}
                            placeholder={isEditMode ? "수정할 코드 이름을 입력하세요" : "코드 이름을 입력하세요"}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-login">{isEditMode ? '수정' : '추가'}</button>
                    {isEditMode && (<button type="button" className="btn btn-login" onClick={handleCancelEdit}>취소</button>)}
                </form>
            </main>
            <FamilyFooter />
        </div>
    );
};      

export default CommonCodePage;
