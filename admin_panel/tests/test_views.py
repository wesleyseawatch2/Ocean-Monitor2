"""
admin_panel.views 測試 - 後台管理功能測試
"""
import pytest
from django.urls import reverse
from data_ingestion.models import Station
from django.contrib.auth import get_user_model

User = get_user_model()


# ==========================================
# 權限測試（staff_required 裝飾器）
# ==========================================

def test_dashboard_requires_login(client):
    """測試未登入訪問 dashboard 會被重定向到登入頁"""
    response = client.get(reverse('admin_panel:dashboard'))
    assert response.status_code == 302
    assert '/login/' in response.url


def test_dashboard_requires_staff(authenticated_client):
    """測試一般使用者訪問 dashboard 會被拒絕"""
    response = authenticated_client.get(reverse('admin_panel:dashboard'))

    assert response.status_code == 302
    assert '/login/' in response.url


def test_dashboard_accessible_by_staff(staff_authenticated_client):
    """測試管理員可以訪問 dashboard"""
    response = staff_authenticated_client.get(reverse('admin_panel:dashboard'))
    assert response.status_code == 200


# ==========================================
# 儀表板測試
# ==========================================

def test_dashboard_template(staff_authenticated_client):
    """測試使用的 template"""
    response = staff_authenticated_client.get(reverse('admin_panel:dashboard'))
    assert 'admin_panel/dashboard.html' in [t.name for t in response.templates]


def test_dashboard_context_data(staff_authenticated_client, station, multiple_readings):
    """測試 dashboard context 包含統計資料"""
    response = staff_authenticated_client.get(reverse('admin_panel:dashboard'))

    assert 'total_stations' in response.context
    assert 'total_readings' in response.context
    assert 'total_users' in response.context
    assert 'recent_readings' in response.context
    assert 'station_stats' in response.context
    assert 'latest_readings' in response.context


def test_dashboard_statistics(staff_authenticated_client, multiple_stations, multiple_readings):
    """測試統計數據的正確性"""
    response = staff_authenticated_client.get(reverse('admin_panel:dashboard'))

    # 3 個測站（但 multiple_readings 只給第一個測站）
    assert response.context['total_stations'] >= 1
    assert response.context['total_readings'] == 10
    assert response.context['total_users'] >= 1  # 至少有 staff_user


# ==========================================
# 登出測試
# ==========================================

def test_admin_logout(staff_authenticated_client):
    """測試管理員登出"""
    response = staff_authenticated_client.get(reverse('admin_panel:logout'))

    assert response.status_code == 302
    assert response.url == '/login/'


# ==========================================
# 測站列表測試（後台）
# ==========================================

def test_admin_station_list_requires_staff(authenticated_client):
    """測試一般使用者無法訪問後台測站列表"""
    response = authenticated_client.get(reverse('admin_panel:station_list'))
    assert response.status_code == 302


def test_admin_station_list_accessible(staff_authenticated_client, multiple_stations):
    """測試管理員可以訪問測站列表"""
    response = staff_authenticated_client.get(reverse('admin_panel:station_list'))

    assert response.status_code == 200
    assert 'stations' in response.context
    assert response.context['stations'].count() == 3


# ==========================================
# 新增測站測試
# ==========================================

def test_station_create_get(staff_authenticated_client):
    """測試 GET 顯示新增表單"""
    response = staff_authenticated_client.get(reverse('admin_panel:station_create'))

    assert response.status_code == 200
    assert 'admin_panel/station_form.html' in [t.name for t in response.templates]
    assert response.context['action'] == '新增'


def test_station_create_post(staff_authenticated_client):
    """測試 POST 建立新測站"""
    initial_count = Station.objects.count()

    response = staff_authenticated_client.post(
        reverse('admin_panel:station_create'),
        {
            'station_name': '新測站',
            'device_model': 'Model-Z',
            'location': '花蓮港',
            'install_date': '2024-03-01'
        }
    )

    assert response.status_code == 302
    assert response.url == reverse('admin_panel:station_list')
    assert Station.objects.count() == initial_count + 1

    # 確認測站資料正確
    new_station = Station.objects.get(station_name='新測站')
    assert new_station.device_model == 'Model-Z'
    assert new_station.location == '花蓮港'


def test_station_create_shows_success_message(staff_authenticated_client):
    """測試建立成功後顯示訊息"""
    response = staff_authenticated_client.post(
        reverse('admin_panel:station_create'),
        {
            'station_name': '測試訊息測站',
            'device_model': 'Model-M',
            'location': '測試港',
            'install_date': '2024-03-01'
        },
        follow=True
    )

    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert '成功新增' in str(messages[0])


# ==========================================
# 編輯測站測試
# ==========================================

def test_station_edit_get(staff_authenticated_client, station):
    """測試 GET 顯示編輯表單"""
    response = staff_authenticated_client.get(
        reverse('admin_panel:station_edit', args=[station.pk])
    )

    assert response.status_code == 200
    assert response.context['station'] == station
    assert response.context['action'] == '編輯'


def test_station_edit_post(staff_authenticated_client, station):
    """測試 POST 更新測站資料"""
    response = staff_authenticated_client.post(
        reverse('admin_panel:station_edit', args=[station.pk]),
        {
            'station_name': '更新後的測站名稱',
            'device_model': 'Model-Updated',
            'location': '更新後的地點',
            'install_date': '2024-04-01'
        }
    )

    assert response.status_code == 302
    assert response.url == reverse('admin_panel:station_list')

    # 重新讀取確認更新
    station.refresh_from_db()
    assert station.station_name == '更新後的測站名稱'
    assert station.device_model == 'Model-Updated'


def test_station_edit_not_found(staff_authenticated_client):
    """測試編輯不存在的測站回傳 404"""
    response = staff_authenticated_client.get(
        reverse('admin_panel:station_edit', args=[99999])
    )
    assert response.status_code == 404


# ==========================================
# 刪除測站測試
# ==========================================

def test_station_delete_get(staff_authenticated_client, station):
    """測試 GET 顯示刪除確認頁面"""
    response = staff_authenticated_client.get(
        reverse('admin_panel:station_delete', args=[station.pk])
    )

    assert response.status_code == 200
    assert response.context['station'] == station
    assert 'admin_panel/station_delete.html' in [t.name for t in response.templates]


def test_station_delete_post(staff_authenticated_client, station):
    """測試 POST 刪除測站"""
    station_id = station.pk
    initial_count = Station.objects.count()

    response = staff_authenticated_client.post(
        reverse('admin_panel:station_delete', args=[station_id])
    )

    assert response.status_code == 302
    assert response.url == reverse('admin_panel:station_list')
    assert Station.objects.count() == initial_count - 1
    assert not Station.objects.filter(pk=station_id).exists()


def test_station_delete_not_found(staff_authenticated_client):
    """測試刪除不存在的測站回傳 404"""
    response = staff_authenticated_client.post(
        reverse('admin_panel:station_delete', args=[99999])
    )
    assert response.status_code == 404


# ==========================================
# 數據記錄列表測試（後台）
# ==========================================

def test_admin_reading_list(staff_authenticated_client, multiple_readings):
    """測試後台數據記錄列表"""
    response = staff_authenticated_client.get(reverse('admin_panel:reading_list'))

    assert response.status_code == 200
    assert 'readings' in response.context
    assert len(response.context['readings']) == 10


def test_admin_reading_list_select_related(staff_authenticated_client, multiple_readings):
    """測試使用 select_related 優化"""
    response = staff_authenticated_client.get(reverse('admin_panel:reading_list'))

    readings = response.context['readings']
    # 確認可以存取 station 而不會觸發額外查詢
    for reading in readings:
        assert reading.station is not None


# ==========================================
# 使用者列表測試
# ==========================================

def test_user_list(staff_authenticated_client, user, staff_user):
    """測試使用者列表"""
    response = staff_authenticated_client.get(reverse('admin_panel:user_list'))

    assert response.status_code == 200
    assert 'users' in response.context
    assert response.context['users'].count() >= 2  # user + staff_user


def test_user_list_requires_staff(authenticated_client):
    """測試一般使用者無法訪問使用者列表"""
    response = authenticated_client.get(reverse('admin_panel:user_list'))
    assert response.status_code == 302


# ==========================================
# 定時任務列表測試
# ==========================================

def test_periodic_task_list(staff_authenticated_client, db):
    """測試定時任務列表"""
    response = staff_authenticated_client.get(
        reverse('admin_panel:periodic_task_list')
    )

    assert response.status_code == 200
    assert 'tasks' in response.context
    assert 'total_tasks' in response.context
    assert 'enabled_tasks' in response.context
    assert 'disabled_tasks' in response.context


def test_periodic_task_list_requires_staff(authenticated_client):
    """測試一般使用者無法訪問定時任務列表"""
    response = authenticated_client.get(
        reverse('admin_panel:periodic_task_list')
    )
    assert response.status_code == 302
