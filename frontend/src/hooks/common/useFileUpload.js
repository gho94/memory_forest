import { useState } from 'react';

const useFileUpload = () => {
    const [isUploading, setIsUploading] = useState(false);

    const uploadFile = async (file) => {
        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${window.API_BASE_URL}/api/files/upload`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log('파일 업로드 성공:', result);
                return result.fileId;
            } else {
                console.error('파일 업로드 실패');
                alert('파일 업로드에 실패했습니다.');
                return null;
            }
        } catch (error) {
            console.error('파일 업로드 실패:', error);
            alert('파일 업로드 중 오류가 발생했습니다.');
            return null;
        } finally {
            setIsUploading(false);
        }
    };

    return { uploadFile, isUploading };
};

export default useFileUpload;