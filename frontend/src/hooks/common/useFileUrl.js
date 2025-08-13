import { useState, useCallback } from 'react';

const useFileUrl = () => {
    const [isLoading, setIsLoading] = useState(false);

    const fetchFileUrl = useCallback(async (fileId) => {
        if (!fileId) return null;

        setIsLoading(true);

        try {
            const response = await fetch(`${window.API_BASE_URL}/api/files/${fileId}`);
            if (!response.ok) {
                console.error('파일 조회 실패:', fileId);
                return null;
            }
            const fileData = await response.json();
            return fileData.s3Url;
        } catch (error) {
            console.error('파일 URL 조회 오류:', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, []);

    return { fetchFileUrl, isLoading };
};

export default useFileUrl;