"""
Memory Forest 모델 관리 유틸리티
Word2Vec 모델의 상태 확인, 백업, 복원 등 관리 기능
"""

import os
import shutil
import logging
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelManager:
    """Word2Vec 모델 관리 클래스"""
    
    def __init__(self):
        self.models_dir = Path("/opt/airflow/models")
        self.backup_dir = Path("/opt/airflow/models/backups")
        self.main_model_path = self.models_dir / "word2vec_custom.model"
        self.backup_model_path = self.models_dir / "word2vec_custom_backup.model"
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")
        
        # 디렉토리 생성
        self.models_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
    
    def get_model_info(self) -> Dict:
        """현재 모델 정보 조회"""
        try:
            if not self.main_model_path.exists():
                return {
                    "status": "no_model",
                    "message": "모델 파일이 존재하지 않습니다.",
                    "path": str(self.main_model_path)
                }
            
            # 파일 정보
            stat = self.main_model_path.stat()
            file_size_mb = round(stat.st_size / (1024 * 1024), 2)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            model_info = {
                "status": "exists",
                "path": str(self.main_model_path),
                "size_mb": file_size_mb,
                "modified_at": modified_time.isoformat(),
                "modified_at_readable": modified_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # AI 서비스에서 모델 상세 정보 가져오기
            try:
                response = requests.get(f"{self.ai_service_url}/model/info", timeout=10)
                if response.status_code == 200:
                    ai_info = response.json()
                    model_info.update({
                        "ai_service_status": ai_info.get("status", "unknown"),
                        "vocab_size": ai_info.get("vocab_size", 0),
                        "vector_size": ai_info.get("vector_size", 0)
                    })
            except Exception as e:
                logger.warning(f"AI 서비스 모델 정보 조회 실패: {e}")
                model_info["ai_service_status"] = "unavailable"
            
            return model_info
            
        except Exception as e:
            logger.error(f"모델 정보 조회 실패: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict:
        """모델 백업 생성"""
        try:
            if not self.main_model_path.exists():
                return {
                    "success": False,
                    "message": "백업할 모델이 존재하지 않습니다."
                }
            
            # 백업 이름 생성
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"word2vec_backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.model"
            
            # 백업 수행
            if self.main_model_path.is_dir():
                shutil.copytree(self.main_model_path, backup_path)
            else:
                shutil.copy2(self.main_model_path, backup_path)
            
            # 백업 정보 저장
            backup_info = {
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "created_at": datetime.now().isoformat(),
                "original_model_info": self.get_model_info()
            }
            
            info_file = self.backup_dir / f"{backup_name}_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"모델 백업 생성 완료: {backup_path}")
            
            return {
                "success": True,
                "backup_name": backup_name,
                "backup_path": str(backup_path),
                "backup_info": backup_info
            }
            
        except Exception as e:
            logger.error(f"모델 백업 실패: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def list_backups(self) -> List[Dict]:
        """백업 목록 조회"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.model"):
                backup_name = backup_file.stem
                info_file = self.backup_dir / f"{backup_name}_info.json"
                
                backup_info = {
                    "backup_name": backup_name,
                    "backup_path": str(backup_file),
                    "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                }
                
                # 상세 정보 파일이 있으면 추가 정보 로드
                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            detailed_info = json.load(f)
                            backup_info.update(detailed_info)
                    except Exception as e:
                        logger.warning(f"백업 정보 파일 로드 실패: {info_file} - {e}")
                
                backups.append(backup_info)
            
            # 생성 시간순으로 정렬 (최신순)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"백업 목록 조회 실패: {e}")
            return []
    
    def restore_backup(self, backup_name: str) -> Dict:
        """백업에서 모델 복원"""
        try:
            backup_path = self.backup_dir / f"{backup_name}.model"
            
            if not backup_path.exists():
                return {
                    "success": False,
                    "message": f"백업 파일을 찾을 수 없습니다: {backup_name}"
                }
            
            # 현재 모델을 임시 백업 (복원 실패 시 복구용)
            temp_backup_result = self.create_backup("temp_before_restore")
            if not temp_backup_result["success"]:
                logger.warning("임시 백업 생성 실패, 계속 진행")
            
            # 현재 모델 삭제
            if self.main_model_path.exists():
                if self.main_model_path.is_dir():
                    shutil.rmtree(self.main_model_path)
                else:
                    self.main_model_path.unlink()
            
            # 백업에서 복원
            if backup_path.is_dir():
                shutil.copytree(backup_path, self.main_model_path)
            else:
                shutil.copy2(backup_path, self.main_model_path)
            
            # AI 서비스에 모델 리로드 요청
            reload_success = self.request_model_reload()
            
            logger.info(f"모델 복원 완료: {backup_name}")
            
            return {
                "success": True,
                "restored_backup": backup_name,
                "model_path": str(self.main_model_path),
                "ai_reload_success": reload_success
            }
            
        except Exception as e:
            logger.error(f"모델 복원 실패: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def request_model_reload(self) -> bool:
        """AI 서비스에 모델 리로드 요청"""
        try:
            response = requests.post(
                f"{self.ai_service_url}/reload-model", 
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("AI 서비스 모델 리로드 성공")
                return True
            else:
                logger.warning(f"AI 서비스 리로드 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"AI 서비스 리로드 요청 실패: {e}")
            return False
    
    def check_ai_service_health(self) -> Dict:
        """AI 서비스 상태 확인"""
        try:
            response = requests.get(f"{self.ai_service_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "details": health_data
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unavailable",
                "message": str(e)
            }
    
    def cleanup_old_backups(self, keep_count: int = 10) -> Dict:
        """오래된 백업 정리 (최신 N개만 유지)"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return {
                    "success": True,
                    "message": f"정리할 백업 없음 (현재: {len(backups)}개, 유지: {keep_count}개)",
                    "deleted_count": 0
                }
            
            # 삭제할 백업들 (오래된 순)
            backups_to_delete = backups[keep_count:]
            deleted_count = 0
            
            for backup in backups_to_delete:
                try:
                    backup_path = Path(backup["backup_path"])
                    info_file = self.backup_dir / f"{backup['backup_name']}_info.json"
                    
                    # 백업 파일 삭제
                    if backup_path.exists():
                        if backup_path.is_dir():
                            shutil.rmtree(backup_path)
                        else:
                            backup_path.unlink()
                    
                    # 정보 파일 삭제
                    if info_file.exists():
                        info_file.unlink()
                    
                    deleted_count += 1
                    logger.info(f"오래된 백업 삭제: {backup['backup_name']}")
                    
                except Exception as e:
                    logger.warning(f"백업 삭제 실패: {backup['backup_name']} - {e}")
            
            return {
                "success": True,
                "message": f"{deleted_count}개 오래된 백업 삭제 완료",
                "deleted_count": deleted_count,
                "remaining_count": len(backups) - deleted_count
            }
            
        except Exception as e:
            logger.error(f"백업 정리 실패: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_model_statistics(self) -> Dict:
        """모델 관련 통계 정보"""
        try:
            model_info = self.get_model_info()
            backups = self.list_backups()
            ai_health = self.check_ai_service_health()
            
            # 디스크 사용량 계산
            total_size = 0
            if self.main_model_path.exists():
                total_size += self.main_model_path.stat().st_size
            
            for backup in backups:
                backup_path = Path(backup["backup_path"])
                if backup_path.exists():
                    total_size += backup_path.stat().st_size
            
            statistics = {
                "model_status": model_info.get("status", "unknown"),
                "total_backups": len(backups),
                "total_disk_usage_mb": round(total_size / (1024 * 1024), 2),
                "ai_service_status": ai_health["status"],
                "last_updated": datetime.now().isoformat()
            }
            
            if model_info.get("status") == "exists":
                statistics.update({
                    "vocab_size": model_info.get("vocab_size", 0),
                    "vector_size": model_info.get("vector_size", 0),
                    "model_size_mb": model_info.get("size_mb", 0)
                })
            
            return statistics
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }

# 전역 모델 매니저 인스턴스
model_manager = ModelManager()

# 편의 함수들
def get_current_model_info() -> Dict:
    """현재 모델 정보 조회"""
    return model_manager.get_model_info()

def create_model_backup(backup_name: Optional[str] = None) -> Dict:
    """모델 백업 생성"""
    return model_manager.create_backup(backup_name)

def list_model_backups() -> List[Dict]:
    """백업 목록 조회"""
    return model_manager.list_backups()

def restore_model_from_backup(backup_name: str) -> Dict:
    """백업에서 모델 복원"""
    return model_manager.restore_backup(backup_name)

def reload_ai_service_model() -> bool:
    """AI 서비스 모델 리로드"""
    return model_manager.request_model_reload()

def check_system_health() -> Dict:
    """시스템 전체 상태 확인"""
    return {
        "model_info": model_manager.get_model_info(),
        "ai_service": model_manager.check_ai_service_health(),
        "statistics": model_manager.get_model_statistics()
    }