import React, { useState, useEffect } from 'react';
import TreeView from './TreeView';
import '@/assets/css/common.css';
import '@/assets/css/login.css';
import '@/assets/css/family.css';
import FamilyHeader from '@/components/layout/header/FamilyHeader';
import FamilyFooter from '@/components/layout/footer/FamilyFooter';

const TreeViewExample = () => {
  const [selectedNode, setSelectedNode] = useState(null);
  const [newCodeName, setNewCodeName] = useState('');
  const [treeData, setTreeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);

  useEffect(() => {
    fetchTreeData();
  }, []);

  const fetchTreeData = async () => {
    try {
      setLoading(true);
      console.log('API 호출 시작');
      
      // 직접 백엔드 호출
      const response = await fetch('http://localhost:8080/api/common-codes/tree');
      console.log('API 응답 상태:', response.status);
      
      if (!response.ok) {
        throw new Error(`트리 데이터를 가져오는데 실패했습니다. (${response.status})`);
      }
      
      const data = await response.json();
      console.log('API 응답 데이터:', data);
      setTreeData(data);
      setError(null);
    } catch (err) {
      console.error('트리 데이터 로딩 오류:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    console.log('선택된 노드:', node);
  };

  const handleAddCode = async (e) => {
    e.preventDefault();
    if (newCodeName) {
      try {
        const response = await fetch('http://localhost:8080/api/common-codes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            codeName: newCodeName,
            parentCodeID: selectedNode ? selectedNode.id : null
          })
        });

        if (response.ok) {
          console.log('새 코드 추가 성공');
          setNewCodeName('');
          setSelectedNode(null);
          // 트리 데이터 새로고침
          fetchTreeData();
        } else {
          console.error('코드 추가 실패:', response.status);
        }
      } catch (err) {
        console.error('코드 추가 오류:', err);
      }
    }
  };

  const handleUpdateCode = async (e) => {
    e.preventDefault();
    if (newCodeName && selectedNode) {
      try {
        const response = await fetch(`http://localhost:8080/api/common-codes/${selectedNode.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            codeName: newCodeName,
            parentCodeID: selectedNode.parentCodeID
          })
        });

        if (response.ok) {
          console.log('코드 수정 성공');
          setNewCodeName('');
          setSelectedNode(null);
          setIsEditMode(false);
          // 트리 데이터 새로고침
          fetchTreeData();
        } else {
          console.error('코드 수정 실패:', response.status);
        }
      } catch (err) {
        console.error('코드 수정 오류:', err);
      }
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (isEditMode) {
      handleUpdateCode(e);
    } else {
      handleAddCode(e);
    }
  };

  const handleAddButtonClick = () => {
    setIsEditMode(false);
  };

  const handleEditButtonClick = () => {
    setIsEditMode(true);
  };

  if (loading) {
    return (
      <div className="app-container d-flex flex-column">
        <FamilyHeader />
        <main className="content-area guardian-con">
          <div className="patient-activity-con row">
            <div className="text-center">
              <p>트리 데이터를 불러오는 중...</p>
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
        <div className="patient-activity-con row">            
          <TreeView 
            data={treeData} 
            onNodeClick={handleNodeClick}
          />  
        </div>
      
        {/* submit 이 코드 추가 인지 코드 수정인지에 따라 다른 함수를 호출하도록 수정 */}
        <form onSubmit={handleFormSubmit} className="signup-form game-signup-form">        
          <div className="form-control-con">
            <input
              type="text"
              id="parentCodeId"
              className="form-control"
              readOnly
              value={selectedNode ? selectedNode.id : ''}
              placeholder="상위 코드 ID"
            />
          </div>
          
          <div className="form-control-con">
            <input
              type="text"
              id="codeName"
              className="form-control"
              value={newCodeName}
              onChange={(e) => setNewCodeName(e.target.value)}
              placeholder={isEditMode ? "수정할 코드 이름을 입력하세요" : "코드 이름을 입력하세요"}
              required
            />
          </div>
          
          <button 
            type="button" 
            className="btn btn-login"
            onClick={handleAddButtonClick}
          >
            코드 추가
          </button>         
          <button 
            type="button" 
            className="btn btn-login"
            onClick={handleEditButtonClick}
          >
            코드 수정
          </button>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={!newCodeName}
          >
            {isEditMode ? '수정 완료' : '추가 완료'}
          </button>         
        </form>    
      </main>
      <FamilyFooter />
    </div>
  );
};

export default TreeViewExample; 