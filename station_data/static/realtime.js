/**
 * 簡單定期刷新 - 每 5 秒自動更新頁面數據
 */

let updateCount = 0;
let chartInstance = null;  // 保存圖表實例

function updateData() {
    console.log('[realtime] 開始更新 #' + (updateCount + 1));
    
    // 加入時間戳記避免快取
    const url = window.location.href.includes('?') 
        ? window.location.href + '&t=' + Date.now()
        : window.location.href + '?t=' + Date.now();
    
    console.log('[realtime] 拉取 URL:', url);
    
    fetch(url)
        .then(response => {
            console.log('[realtime] 響應狀態:', response.status);
            return response.text();
        })
        .then(html => {
            console.log('[realtime] HTML 長度:', html.length);
            
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            
            // 需要監控的所有元素 ID
            const elementIds = [
                'latest-timestamp',
                'latest-temperature',
                'latest-ph',
                'latest-oxygen',
                'latest-salinity',
                'latest-conductivity',
                'latest-pressure',
                'latest-fluorescence',
                'latest-turbidity',
                'total-reading-count',
                'stat-temperature-min',
                'stat-temperature-avg',
                'stat-temperature-max',
                'stat-ph-min',
                'stat-ph-avg',
                'stat-ph-max',
                'stat-oxygen-min',
                'stat-oxygen-avg',
                'stat-oxygen-max',
                'stat-salinity-min',
                'stat-salinity-avg',
                'stat-salinity-max',
            ];
            
            let changeCount = 0;
            
            // 更新每個元素
            elementIds.forEach(id => {
                const oldEl = document.getElementById(id);
                const newEl = newDoc.getElementById(id);
                
                if (oldEl && newEl) {
                    const oldText = oldEl.textContent.trim();
                    const newText = newEl.textContent.trim();
                    
                    // 如果內容改變，更新並加上黃色閃爍效果
                    if (oldText !== newText) {
                        console.log(`[realtime] ${id} 改變: "${oldText}" → "${newText}"`);
                        oldEl.textContent = newText;
                        
                        // 黃色閃爍效果 - 更明顯
                        oldEl.style.backgroundColor = '#ffd54f';
                        oldEl.style.transition = 'background-color 0.3s ease';
                        oldEl.style.fontWeight = 'bold';
                        
                        changeCount++;
                        setTimeout(() => {
                            oldEl.style.backgroundColor = '';
                            oldEl.style.fontWeight = 'normal';
                        }, 1500);  // 延長到 1.5 秒
                    }
                } else {
                    if (!oldEl) console.warn(`[realtime] 找不到舊元素 #${id}`);
                    if (!newEl) console.warn(`[realtime] 新 HTML 沒有 #${id}`);
                }
            });
            
            // 更新表格
            updateTable(newDoc);
            
            // 更新圖表
            updateChart(newDoc);
            
            // 增加更新計數
            updateCount++;
            
            console.log(`[realtime] 更新完成 #${updateCount}，改變 ${changeCount} 個元素`);
            
            // 更新狀態顯示
            const statusEl = document.getElementById('status-text');
            if (statusEl) {
                statusEl.textContent = `監控中 (更新: ${updateCount}次)`;
            }
        })
        .catch(error => {
            console.error('[realtime] 更新失敗:', error);
        });
}

// 更新表格
function updateTable(newDoc) {
    const newTbody = newDoc.querySelector('table tbody');
    const oldTbody = document.querySelector('table tbody');
    
    if (newTbody && oldTbody) {
        const oldHTML = oldTbody.innerHTML;
        const newHTML = newTbody.innerHTML;
        
        if (oldHTML !== newHTML) {
            console.log('[realtime] 表格內容已改變，更新中...');
            oldTbody.innerHTML = newHTML;
            
            // 高亮整個表格
            oldTbody.style.backgroundColor = '#fffacd';
            setTimeout(() => {
                oldTbody.style.backgroundColor = '';
            }, 1500);
        }
    }
}

// 更新圖表 - 從 DOM 中提取最新數據加入
function updateChart(newDoc) {
    if (!chartInstance) {
        console.warn('[realtime] 圖表實例不存在，跳過更新');
        return;
    }
    
    try {
        // 從 DOM 中直接獲取最新數據
        const latestTemp = document.getElementById('latest-temperature');
        const latestPH = document.getElementById('latest-ph');
        const latestOxygen = document.getElementById('latest-oxygen');
        const latestSalinity = document.getElementById('latest-salinity');
        const latestTimestamp = document.getElementById('latest-timestamp');
        
        if (!latestTemp || !latestPH || !latestOxygen || !latestSalinity || !latestTimestamp) {
            console.warn('[realtime] 無法找到必要的 DOM 元素');
            return;
        }
        
        // 提取數值（移除單位）
        const tempVal = parseFloat(latestTemp.textContent);
        const phVal = parseFloat(latestPH.textContent);
        const oxygenVal = parseFloat(latestOxygen.textContent);
        const salinityVal = parseFloat(latestSalinity.textContent);
        const timeVal = latestTimestamp.textContent.trim();
        
        // 檢查是否已經有這個時間戳的數據（避免重複）
        if (chartInstance.data.labels.length > 0) {
            const lastLabel = chartInstance.data.labels[chartInstance.data.labels.length - 1];
            if (lastLabel === timeVal) {
                console.log('[realtime] 圖表已是最新，跳過更新');
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
        console.log('[realtime] 圖表已加入新數據點');
        
    } catch (e) {
        console.error('[realtime] 圖表更新出錯:', e);
    }
}

// 頁面加載完成後啟動
document.addEventListener('DOMContentLoaded', () => {
    console.log('[realtime] DOMContentLoaded 觸發');
    
    // 取得圖表實例（在 HTML script 標籤中定義）
    chartInstance = window.chartInstance || null;
    if (chartInstance) {
        console.log('[realtime] 找到圖表實例');
    } else {
        console.warn('[realtime] 未找到圖表實例');
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
                    background-color: #4CAF50;
                    display: inline-block;
                    margin-right: 8px;
                "></span>
                <span id="status-text">監控中</span>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', statusHTML);
        console.log('[realtime] 狀態指示器已建立');
    }
    
    // 立即更新一次
    console.log('[realtime] 開始首次更新');
    updateData();
    
    // 每 5 秒更新一次
    console.log('[realtime] 設定 5 秒定期更新');
    setInterval(updateData, 5000);
    
    console.log('[realtime] 初始化完成');
});
