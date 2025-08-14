const PDF_STYLES = `
  .patient-activity-con { 
    display: grid; 
    grid-template-columns: 1fr 1fr; 
    gap: 20px; 
    margin: 30px 0; 
    font-size: 16px;
    font-weight: 500;
  }
  
  .patient-activity-con .col-6 {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
  }
  
  .patient-activity-con .col-6 span {
    font-weight: bold;
    color: #007bff;
    font-size: 18px;
  }
  
  .chart { 
    margin: 30px 0;
    min-height: 450px !important;
  }
  
  .chart #chart, .chart svg {
    min-height: 450px !important;
    width: 100% !important;
  }
  
  .game-item { 
    border: 1px solid #ddd; 
    padding: 15px; 
    margin: 15px 0; 
    border-radius: 8px; 
    background: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .option-btn {
    display: inline-block;
    padding: 10px 15px;
    margin: 5px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: #f9f9f9;
    font-weight: 500;
  }
  
  .correct-selected { 
    background: #d4edda; 
    border-color: #28a745;
    color: #155724;
  }
  
  .wrong-selected { 
    background: #f8d7da; 
    border-color: #dc3545;
    color: #721c24;
  }
  
  .correct-answer { 
    background: #d1ecf1; 
    border-color: #17a2b8;
    color: #0c5460;
  }
  
  .detail-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 2px solid #007bff;
  }
  
  .game-date {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 20px;
  }
  
  .apexcharts-toolbar { 
    display: none !important; 
  }
  
  @media print {
    .icon-btn, .search-btn, .date-picker-wrapper { 
      display: none !important; 
    }
    .apexcharts-toolbar { 
      display: none !important; 
    }
    .chart, .chart #chart, .chart svg {
      min-height: 400px !important;
    }
  }
`;

export const usePDFGenerator = () => {
    const handlePrintToPDF = () => {
        const element = document.querySelector('.content-area.guardian-con');
        if (!element) return;

        // 원본 요소를 복사해서 작업용 복사본 생성
        const clonedElement = element.cloneNode(true);

        // 복사본에서 탭 메뉴 제거
        const tabMenu = clonedElement.querySelector('ul.menu-tab-con.nav.nav-tabs.mb-2');
        if (tabMenu) {
            tabMenu.remove();
        }

        const printWindow = window.open('', '_blank');
        const printHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>활동 리포트</title>
        <style>${PDF_STYLES}</style>
      </head>
      <body>
        ${clonedElement.innerHTML}
        <script>
          window.onload = function() {
            setTimeout(() => {
              const chartElements = document.querySelectorAll('.chart svg');
              chartElements.forEach(chart => {
                chart.setAttribute('height', '450');
              });
              
              window.print();
              window.onafterprint = function() {
                window.close();
              }
            }, 1000);
          }
        </script>
      </body>
      </html>
    `;

        printWindow.document.write(printHTML);
        printWindow.document.close();
    };

    return {handlePrintToPDF};
};