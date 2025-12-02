from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from functools import wraps
from data_ingestion.models import Station, Reading
from apps.core.accounts.models import User
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


def staff_required(view_func):
    """自訂裝飾器：要求使用者為 staff，否則顯示錯誤並重定向"""
    @wraps(view_func)
    @login_required(login_url='/login/')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, '您沒有權限訪問管理後台，請使用管理員帳號登入。')
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_logout(request):
    """管理員登出"""
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('/login/')


@staff_required
def dashboard(request):
    """儀表板"""
    # 統計資料
    total_stations = Station.objects.count()
    total_readings = Reading.objects.count()
    total_users = User.objects.count()

    # 近7天的數據筆數
    week_ago = timezone.now() - timedelta(days=7)
    recent_readings = Reading.objects.filter(timestamp__gte=week_ago).count()

    # 測站數據統計
    station_stats = Station.objects.annotate(
        reading_count=Count('readings')
    ).order_by('-reading_count')[:5]

    # 最新數據
    latest_readings = Reading.objects.select_related('station').order_by('-timestamp')[:10]

    context = {
        'total_stations': total_stations,
        'total_readings': total_readings,
        'total_users': total_users,
        'recent_readings': recent_readings,
        'station_stats': station_stats,
        'latest_readings': latest_readings,
    }

    return render(request, 'admin_panel/dashboard.html', context)


@staff_required
def station_list(request):
    """測站列表"""
    stations = Station.objects.annotate(
        reading_count=Count('readings')
    ).order_by('-install_date')

    context = {
        'stations': stations,
    }

    return render(request, 'admin_panel/station_list.html', context)


@staff_required
def station_create(request):
    """新增測站"""
    if request.method == 'POST':
        station_name = request.POST.get('station_name')
        device_model = request.POST.get('device_model')
        location = request.POST.get('location')
        install_date = request.POST.get('install_date')

        Station.objects.create(
            station_name=station_name,
            device_model=device_model,
            location=location,
            install_date=install_date
        )

        messages.success(request, f'測站 "{station_name}" 已成功新增!')
        return redirect('admin_panel:station_list')

    return render(request, 'admin_panel/station_form.html', {'action': '新增'})


@staff_required
def station_edit(request, pk):
    """編輯測站"""
    station = get_object_or_404(Station, pk=pk)

    if request.method == 'POST':
        station.station_name = request.POST.get('station_name')
        station.device_model = request.POST.get('device_model')
        station.location = request.POST.get('location')
        station.install_date = request.POST.get('install_date')
        station.save()

        messages.success(request, f'測站 "{station.station_name}" 已更新!')
        return redirect('admin_panel:station_list')

    context = {
        'station': station,
        'action': '編輯'
    }

    return render(request, 'admin_panel/station_form.html', context)


@staff_required
def station_delete(request, pk):
    """刪除測站"""
    station = get_object_or_404(Station, pk=pk)

    if request.method == 'POST':
        station_name = station.station_name
        station.delete()
        messages.warning(request, f'測站 "{station_name}" 已刪除!')
        return redirect('admin_panel:station_list')

    context = {
        'station': station,
    }

    return render(request, 'admin_panel/station_delete.html', context)


@staff_required
def reading_list(request):
    """數據記錄列表"""
    readings = Reading.objects.select_related('station').order_by('-timestamp')[:100]

    context = {
        'readings': readings,
    }

    return render(request, 'admin_panel/reading_list.html', context)


@staff_required
def user_list(request):
    """使用者列表"""
    users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users,
    }

    return render(request, 'admin_panel/user_list.html', context)


# ==========================================
# Celery 定時任務管理
# ==========================================

@staff_required
def periodic_task_list(request):
    """定時任務列表"""
    tasks = PeriodicTask.objects.all().order_by('-enabled', 'name')

    # 統計資訊
    total_tasks = tasks.count()
    enabled_tasks = tasks.filter(enabled=True).count()
    disabled_tasks = total_tasks - enabled_tasks

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'enabled_tasks': enabled_tasks,
        'disabled_tasks': disabled_tasks,
    }

    return render(request, 'admin_panel/periodic_task_list.html', context)


@staff_required
def periodic_task_create(request):
    """新增定時任務"""
    if request.method == 'POST':
        name = request.POST.get('name')
        task = request.POST.get('task')
        schedule_type = request.POST.get('schedule_type')
        enabled = request.POST.get('enabled') == 'on'

        # 建立定時任務
        periodic_task = PeriodicTask(
            name=name,
            task=task,
            enabled=enabled,
        )

        # 根據排程類型設定
        if schedule_type == 'interval':
            every = int(request.POST.get('interval_every'))
            period = request.POST.get('interval_period')

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=every,
                period=period,
            )
            periodic_task.interval = schedule

        elif schedule_type == 'crontab':
            minute = request.POST.get('crontab_minute', '*')
            hour = request.POST.get('crontab_hour', '*')
            day_of_week = request.POST.get('crontab_day_of_week', '*')
            day_of_month = request.POST.get('crontab_day_of_month', '*')
            month_of_year = request.POST.get('crontab_month_of_year', '*')

            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
            )
            periodic_task.crontab = schedule

        # 處理參數
        kwargs_str = request.POST.get('kwargs', '{}')
        if kwargs_str.strip():
            try:
                periodic_task.kwargs = kwargs_str
            except:
                periodic_task.kwargs = '{}'

        periodic_task.save()

        messages.success(request, f'定時任務 "{name}" 已成功新增！')
        return redirect('admin_panel:periodic_task_list')

    # 取得可用的任務列表
    available_tasks = [
        ('station_data.tasks.update_ocean_data_from_source', '更新海洋數據'),
        ('station_data.tasks.check_ocean_data_alerts', '檢查數據異常'),
        ('station_data.tasks.generate_daily_statistics', '產生每日統計報告'),
        ('station_data.tasks.send_data_alert_notification', '發送數據異常通知'),
    ]

    context = {
        'action': '新增',
        'available_tasks': available_tasks,
    }

    return render(request, 'admin_panel/periodic_task_form.html', context)


@staff_required
def periodic_task_edit(request, pk):
    """編輯定時任務"""
    periodic_task = get_object_or_404(PeriodicTask, pk=pk)

    if request.method == 'POST':
        periodic_task.name = request.POST.get('name')
        periodic_task.task = request.POST.get('task')
        periodic_task.enabled = request.POST.get('enabled') == 'on'

        schedule_type = request.POST.get('schedule_type')

        # 清除舊的排程
        periodic_task.interval = None
        periodic_task.crontab = None

        # 根據排程類型設定
        if schedule_type == 'interval':
            every = int(request.POST.get('interval_every'))
            period = request.POST.get('interval_period')

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=every,
                period=period,
            )
            periodic_task.interval = schedule

        elif schedule_type == 'crontab':
            minute = request.POST.get('crontab_minute', '*')
            hour = request.POST.get('crontab_hour', '*')
            day_of_week = request.POST.get('crontab_day_of_week', '*')
            day_of_month = request.POST.get('crontab_day_of_month', '*')
            month_of_year = request.POST.get('crontab_month_of_year', '*')

            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
            )
            periodic_task.crontab = schedule

        # 處理參數
        kwargs_str = request.POST.get('kwargs', '{}')
        if kwargs_str.strip():
            try:
                periodic_task.kwargs = kwargs_str
            except:
                periodic_task.kwargs = '{}'

        periodic_task.save()

        messages.success(request, f'定時任務 "{periodic_task.name}" 已更新！')
        return redirect('admin_panel:periodic_task_list')

    # 取得可用的任務列表
    available_tasks = [
        ('station_data.tasks.update_ocean_data_from_source', '更新海洋數據'),
        ('station_data.tasks.check_ocean_data_alerts', '檢查數據異常'),
        ('station_data.tasks.generate_daily_statistics', '產生每日統計報告'),
        ('station_data.tasks.send_data_alert_notification', '發送數據異常通知'),
    ]

    # 判斷當前排程類型
    current_schedule_type = None
    if periodic_task.interval:
        current_schedule_type = 'interval'
    elif periodic_task.crontab:
        current_schedule_type = 'crontab'

    context = {
        'action': '編輯',
        'task': periodic_task,
        'available_tasks': available_tasks,
        'current_schedule_type': current_schedule_type,
    }

    return render(request, 'admin_panel/periodic_task_form.html', context)


@staff_required
def periodic_task_delete(request, pk):
    """刪除定時任務"""
    periodic_task = get_object_or_404(PeriodicTask, pk=pk)

    if request.method == 'POST':
        task_name = periodic_task.name
        periodic_task.delete()
        messages.warning(request, f'定時任務 "{task_name}" 已刪除！')
        return redirect('admin_panel:periodic_task_list')

    context = {
        'task': periodic_task,
    }

    return render(request, 'admin_panel/periodic_task_delete.html', context)


@staff_required
def periodic_task_toggle(request, pk):
    """切換定時任務啟用狀態"""
    periodic_task = get_object_or_404(PeriodicTask, pk=pk)
    periodic_task.enabled = not periodic_task.enabled
    periodic_task.save()

    status = '啟用' if periodic_task.enabled else '停用'
    messages.info(request, f'定時任務 "{periodic_task.name}" 已{status}！')

    return redirect('admin_panel:periodic_task_list')
