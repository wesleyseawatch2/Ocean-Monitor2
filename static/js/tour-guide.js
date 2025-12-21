/**
 * 網頁導覽教學功能
 * 使用 Driver.js 實現互動式導覽
 */

// 首頁導覽配置
const homeTourSteps = [
    {
        element: 'nav',
        popover: {
            title: '歡迎使用海洋監測系統 🌊',
            description: '這是系統的主選單，您可以在這裡切換不同的功能頁面。',
            side: "bottom",
            align: 'start'
        }
    },
    {
        element: 'a[href*="stations"]',
        popover: {
            title: '測站列表',
            description: '查看所有測站的基本資訊、位置和數據筆數。',
            side: "bottom"
        }
    },
    {
        element: 'a[href*="readings"]',
        popover: {
            title: '數據記錄',
            description: '瀏覽所有測站的完整數據記錄和 GPS 軌跡地圖。',
            side: "bottom"
        }
    },
    {
        element: 'a[href*="reports"]',
        popover: {
            title: '報告管理',
            description: '管理系統自動生成的各類報告，包括每日統計、數據更新等。',
            side: "bottom"
        }
    }
];

// 測站列表導覽配置
const stationListTourSteps = [
    {
        popover: {
            title: '測站列表頁面 📍',
            description: '這裡顯示所有海洋監測測站的資訊和位置。讓我們一起了解如何使用這個頁面！'
        }
    },
    {
        element: '.stations-grid',
        popover: {
            title: '測站卡片',
            description: '每個卡片代表一個測站，顯示測站名稱、設備型號、裝設日期和位置資訊。',
            side: "top"
        }
    },
    {
        element: '.station-map',
        popover: {
            title: '測站地圖',
            description: '互動式地圖顯示測站的確切位置。您可以點擊標記查看詳細資訊。',
            side: "top"
        }
    },
    {
        element: '.btn-detail',
        popover: {
            title: '查看詳細數據',
            description: '點擊此按鈕可以查看該測站的完整監測數據、統計圖表和 GPS 軌跡。',
            side: "top"
        }
    }
];

// 測站詳情導覽配置
const stationDetailTourSteps = [
    {
        popover: {
            title: '測站詳情頁面 🌡️',
            description: '這裡顯示測站的完整監測數據和分析圖表。讓我帶您了解各個功能！'
        }
    },
    {
        element: '.stats-grid',
        popover: {
            title: '統計數據卡片',
            description: '即時顯示溫度、pH值、溶氧量和鹽度的最新值、平均值和變化範圍。',
            side: "bottom"
        }
    },
    {
        element: 'canvas#dataChart',
        popover: {
            title: '數據趨勢圖表',
            description: '互動式圖表顯示各項參數隨時間的變化趨勢。您可以勾選/取消勾選圖例來顯示/隱藏不同參數。',
            side: "top"
        }
    },
    {
        element: '#trajectory-map',
        popover: {
            title: 'GPS 軌跡地圖',
            description: '顯示儀器的移動軌跡（最新 100 個 GPS 點）。綠色標記是起點，紅色標記是最新位置。',
            side: "top"
        }
    },
    {
        element: '#tableContainer2',
        popover: {
            title: '完整數據記錄',
            description: '顯示最新 100 筆完整數據記錄。使用左右箭頭或滑動查看所有欄位。',
            side: "top"
        }
    }
];

// 報告管理導覽配置
const reportListTourSteps = [
    {
        popover: {
            title: '報告管理中心 📊',
            description: '管理系統自動生成的各類報告。讓我們看看如何使用這個頁面！'
        }
    },
    {
        element: '.stat-card',
        popover: {
            title: '報告統計',
            description: '快速查看不同類型報告的數量統計。',
            side: "bottom"
        }
    },
    {
        element: '#reportTypeFilter',
        popover: {
            title: '報告篩選',
            description: '選擇報告類型來篩選顯示的報告。可以選擇每日統計、數據更新、異常檢查等類型。',
            side: "bottom"
        }
    },
    {
        element: 'button[onclick="deleteAllReports()"]',
        popover: {
            title: '刪除全部報告',
            description: '⚠️ 此按鈕會刪除所有報告，使用時請特別小心！系統會要求您二次確認。',
            side: "left"
        }
    },
    {
        element: 'table',
        popover: {
            title: '報告列表',
            description: '顯示所有報告的詳細資訊。您可以查看、刪除單個報告，或使用 AI 生成洞察分析。',
            side: "top"
        }
    }
];

// 初始化導覽功能
function initTourGuide() {
    // 檢查是否已安裝 Driver.js
    if (typeof driver === 'undefined') {
        console.warn('Driver.js 未載入，導覽功能無法使用');
        return null;
    }

    // 根據當前頁面選擇導覽步驟
    const currentPath = window.location.pathname;
    let steps = [];

    if (currentPath === '/') {
        steps = homeTourSteps;
    } else if (currentPath.includes('/stations/') && currentPath.match(/\/stations\/\d+\/$/)) {
        steps = stationDetailTourSteps;
    } else if (currentPath.includes('/stations/') && !currentPath.includes('/readings') && !currentPath.includes('/reports')) {
        steps = stationListTourSteps;
    } else if (currentPath.includes('/reports/')) {
        steps = reportListTourSteps;
    }

    if (steps.length === 0) {
        return null;
    }

    // 創建 Driver.js 實例
    const driverObj = driver({
        showProgress: true,
        steps: steps,
        nextBtnText: '下一步',
        prevBtnText: '上一步',
        doneBtnText: '完成',
        progressText: '{{current}} / {{total}}',
        onDestroyStarted: () => {
            // 保存已完成導覽的狀態
            localStorage.setItem('tour_completed_' + currentPath, 'true');
            driverObj.destroy();
        }
    });

    return driverObj;
}

// 檢查是否需要自動啟動導覽
function checkAutoStartTour() {
    const currentPath = window.location.pathname;
    const tourCompleted = localStorage.getItem('tour_completed_' + currentPath);
    const autoTourDisabled = localStorage.getItem('auto_tour_disabled');

    // 如果用戶禁用自動導覽或已完成此頁面導覽，則不自動啟動
    if (autoTourDisabled === 'true' || tourCompleted === 'true') {
        return false;
    }

    return true;
}

// 啟動導覽
function startTour() {
    const driverObj = initTourGuide();
    if (driverObj) {
        driverObj.drive();
    } else {
        alert('此頁面暫無導覽教學');
    }
}

// 重置導覽狀態
function resetTourProgress() {
    const keys = Object.keys(localStorage).filter(key => key.startsWith('tour_completed_'));
    keys.forEach(key => localStorage.removeItem(key));
    alert('導覽進度已重置！重新載入頁面後將再次顯示導覽。');
}

// 禁用/啟用自動導覽
function toggleAutoTour(enable) {
    if (enable) {
        localStorage.removeItem('auto_tour_disabled');
    } else {
        localStorage.setItem('auto_tour_disabled', 'true');
    }
}

// 頁面載入時檢查是否需要自動啟動導覽
document.addEventListener('DOMContentLoaded', function() {
    // 延遲 1 秒後檢查，確保頁面完全載入
    setTimeout(() => {
        if (checkAutoStartTour()) {
            const driverObj = initTourGuide();
            if (driverObj) {
                // 首次訪問時自動啟動導覽
                driverObj.drive();
            }
        }
    }, 1000);
});

// 導出函數供外部使用
window.tourGuide = {
    start: startTour,
    reset: resetTourProgress,
    toggleAuto: toggleAutoTour
};
