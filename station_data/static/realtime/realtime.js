/**
 * WebSocket 即時更新 - 使用 WebSocket 連接接收即時資料
 */

let updateCount = 0;
let chartInstance = null;  // 保存圖表實例
let socket = null;  // WebSocket 連接
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function getWebSocketURL() {
    // 從當前頁面 URL 判斷是哪個頁面
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    // 如果是測站詳情頁面，連接到特定測站的 WebSocket
    const stationMatch = window.location.pathname.match(/\/stations\/(\d+)\//);
    if (stationMatch) {
        const stationId = stationMatch[1];
        return `${protocol}//${host}/ws/stations/${stationId}/`;
    }

    // 否則連接到所有測站的 WebSocket
    return `${protocol}//${host}/ws/stations/readings/`;
}

function connectWebSocket() {
    const wsUrl = getWebSocketURL();
    console.log('[WebSocket] 正在連接:', wsUrl);

    socket = new WebSocket(wsUrl);

    socket.onopen = function(e) {
        console.log('[WebSocket] 連接成功');
        reconnectAttempts = 0;
        updateStatusIndicator('已連線', '#4CAF50');
    };

    socket.onmessage = function(event) {
        console.log('[WebSocket] 收到訊息:', event.data);

        try {
            const message = JSON.parse(event.data);

            if (message.type === 'initial_data') {
                // 初始資料
                console.log('[WebSocket] 收到初始資料');
                updateDataFromWebSocket(message.data);
            } else if (message.type === 'sensor_reading_update') {
                // 即時更新
                console.log('[WebSocket] 收到即時更新');
                updateDataFromWebSocket(message.data);
                updateCount++;
            } else if (message.type === 'error') {
                console.error('[WebSocket] 錯誤:', message.message);
            }

            updateStatusIndicator(`已連線 (更新: ${updateCount}次)`, '#4CAF50');
        } catch (error) {
            console.error('[WebSocket] 解析訊息失敗:', error);
        }
    };

    socket.onerror = function(error) {
        console.error('[WebSocket] 錯誤:', error);
        updateStatusIndicator('連線錯誤', '#f44336');
    };

    socket.onclose = function(event) {
        console.log('[WebSocket] 連線關閉:', event.code, event.reason);
        updateStatusIndicator('連線中斷', '#ff9800');

        // 嘗試重新連接
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            console.log(`[WebSocket] 將在 3 秒後重新連接 (第 ${reconnectAttempts} 次)`);
            setTimeout(connectWebSocket, 3000);
        } else {
            console.error('[WebSocket] 超過最大重連次數，停止重連');
            updateStatusIndicator('連線失敗', '#f44336');
        }
    };
}

function updateDataFromWebSocket(data) {
    if (!data) return;

    // 如果是陣列（多個測站）
    if (Array.isArray(data)) {
        // 可以在這裡處理多個測站的資料
        console.log('[WebSocket] 收到多個測站資料:', data.length);
        return;
    }

    // 單一測站資料
    console.log('[WebSocket] 更新測站資料:', data);

    // 更新各個數值
    updateElement('latest-timestamp', data.timestamp);
    updateElement('latest-temperature', formatValue(data.temperature, '°C'));
    updateElement('latest-ph', formatValue(data.ph));
    updateElement('latest-oxygen', formatValue(data.dissolved_oxygen, 'mg/L'));
    updateElement('latest-salinity', formatValue(data.salinity, 'PSU'));
    updateElement('latest-conductivity', formatValue(data.conductivity, 'mS/cm'));
    updateElement('latest-pressure', formatValue(data.pressure, 'dbar'));
    updateElement('latest-fluorescence', formatValue(data.fluorescence, 'µg/L'));
    updateElement('latest-turbidity', formatValue(data.turbidity, 'NTU'));

    // 更新圖表
    updateChartWithWebSocketData(data);
}

function updateElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const oldValue = element.textContent.trim();
    const newValue = value ? String(value) : '-';

    if (oldValue !== newValue) {
        element.textContent = newValue;

        // 黃色閃爍效果
        element.style.backgroundColor = '#ffd54f';
        element.style.transition = 'background-color 0.3s ease';
        element.style.fontWeight = 'bold';

        setTimeout(() => {
            element.style.backgroundColor = '';
            element.style.fontWeight = 'normal';
        }, 1500);
    }
}

function formatValue(value, unit = '') {
    if (value === null || value === undefined) return '-';
    const formatted = typeof value === 'number' ? value.toFixed(2) : value;
    return unit ? `${formatted} ${unit}` : formatted;
}

// 更新圖表 - 使用 WebSocket 傳來的資料
function updateChartWithWebSocketData(data) {
    if (!chartInstance) {
        console.warn('[WebSocket] 圖表實例不存在，跳過更新');
        return;
    }

    try {
        const timeVal = data.timestamp;
        const tempVal = data.temperature;
        const phVal = data.ph;
        const oxygenVal = data.dissolved_oxygen;
        const salinityVal = data.salinity;

        // 檢查是否已經有這個時間戳的數據（避免重複）
        if (chartInstance.data.labels.length > 0) {
            const lastLabel = chartInstance.data.labels[chartInstance.data.labels.length - 1];
            if (lastLabel === timeVal) {
                console.log('[WebSocket] 圖表已是最新，跳過更新');
                return;
            }
        }

        // 只保留最近 30 個數據點
        const maxPoints = 30;
        if (chartInstance.data.labels.length >= maxPoints) {
            chartInstance.data.labels.shift();
            chartInstance.data.datasets.forEach(ds => ds.data.shift());
        }

        // 加入新數據
        chartInstance.data.labels.push(timeVal);
        chartInstance.data.datasets[0].data.push(tempVal);      // 溫度
        chartInstance.data.datasets[1].data.push(phVal);        // pH
        chartInstance.data.datasets[2].data.push(oxygenVal);    // 溶氧
        chartInstance.data.datasets[3].data.push(salinityVal);  // 鹽度

        // 重新繪製
        chartInstance.update('none');
        console.log('[WebSocket] 圖表已加入新數據點');

    } catch (e) {
        console.error('[WebSocket] 圖表更新出錯:', e);
    }
}

function updateStatusIndicator(text, color) {
    const statusText = document.getElementById('status-text');
    const statusDot = document.querySelector('#realtime-status span');

    if (statusText) {
        statusText.textContent = text;
    }

    if (statusDot) {
        statusDot.style.backgroundColor = color;
    }
}

// 頁面加載完成後啟動
document.addEventListener('DOMContentLoaded', () => {
    console.log('[WebSocket] DOMContentLoaded 觸發');

    // 取得圖表實例（在 HTML script 標籤中定義）
    chartInstance = window.chartInstance || null;
    if (chartInstance) {
        console.log('[WebSocket] 找到圖表實例');
    } else {
        console.warn('[WebSocket] 未找到圖表實例');
    }

    // 確保狀態指示器存在
    if (!document.getElementById('realtime-status')) {
        const statusHTML = `
            <div id="realtime-status" style="
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 15px;
                border-radius: 5px;
                background-color: #f0f0f0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                font-size: 14px;
                z-index: 1000;
            ">
                <span style="
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background-color: #ff9800;
                    display: inline-block;
                    margin-right: 8px;
                "></span>
                <span id="status-text">連線中...</span>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', statusHTML);
        console.log('[WebSocket] 狀態指示器已建立');
    }

    // 建立 WebSocket 連接
    console.log('[WebSocket] 開始建立連接');
    connectWebSocket();

    console.log('[WebSocket] 初始化完成');

    // 當頁面關閉時，關閉 WebSocket 連接
    window.addEventListener('beforeunload', () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    });
});
