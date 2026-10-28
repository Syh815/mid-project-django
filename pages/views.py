import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import Course, Enrollment, UserProfile
from .utils import init_demo_data, create_student_account

# 依據圖片第二張完整時段排程
PERIOD_INFO = [
    {'period': 1, 'time': '08:10 - 09:00', 'name': '第一節'},
    {'period': 2, 'time': '09:10 - 10:00', 'name': '第二節'},
    {'period': 3, 'time': '10:10 - 11:00', 'name': '第三節'},
    {'period': 4, 'time': '11:10 - 12:00', 'name': '第四節'},
    {'period': 5, 'time': '13:30 - 14:20', 'name': '第五節'},
    {'period': 6, 'time': '14:25 - 15:15', 'name': '第六節'},
    {'period': 7, 'time': '15:25 - 16:15', 'name': '第七節'},
    {'period': 8, 'time': '16:20 - 17:10', 'name': '第八節'},
    {'period': 9, 'time': '17:15 - 18:05', 'name': '第九節'},
]

DAYS_INFO = [
    {'day': 1, 'name': '一', 'full_name': '星期一'},
    {'day': 2, 'name': '二', 'full_name': '星期二'},
    {'day': 3, 'name': '三', 'full_name': '星期三'},
    {'day': 4, 'name': '四', 'full_name': '星期四'},
    {'day': 5, 'name': '五', 'full_name': '星期五'},
]

def check_time_conflict(course_a, course_b):
    """檢查兩門課是否有時間衝堂"""
    if course_a.id == course_b.id:
        return False
    if course_a.day_of_week != course_b.day_of_week:
        return False
    return max(course_a.start_period, course_b.start_period) <= min(course_a.end_period, course_b.end_period)


def index(request, tab=None):
    """選課系統首頁 / 課表與維護入口"""
    # 確保基本示範資料存在
    if not User.objects.filter(username__in=['admin', 'student']).exists() or not Course.objects.exists():
        init_demo_data()

    # 未登入者一律強制重導向至 /login/
    if not request.user.is_authenticated:
        return redirect('pages:login')

    is_admin = request.user.is_staff or request.user.username == 'admin'

    # 若使用舊式 query string ?tab=...，自動 302 重新導向至乾淨語意化目錄路徑 (Clean Directory URLs)
    query_tab = request.GET.get('tab')
    if query_tab:
        tab_redirect_map = {
            'enrolled': 'pages:enrolled',
            'electives': 'pages:electives',
            'timetable': 'pages:timetable',
            'admin_courses': 'pages:manage_courses',
            'students_roster': 'pages:students_roster',
        }
        if query_tab in tab_redirect_map:
            return redirect(tab_redirect_map[query_tab])

    active_tab = tab or ('admin_courses' if is_admin else 'timetable')

    # 取得所有課程與選課紀錄
    all_courses = Course.objects.all().prefetch_related('enrollments')

    # 學生已選課程
    if not is_admin:
        user_enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
        enrolled_courses = [e.course for e in user_enrollments]
        enrolled_course_ids = {c.id for c in enrolled_courses}
    else:
        enrolled_courses = list(all_courses)
        enrolled_course_ids = {c.id for c in all_courses}

    # 建立課表網格 [period][day]
    timetable = {p['period']: {d['day']: None for d in DAYS_INFO} for p in PERIOD_INFO}

    courses_to_plot = enrolled_courses if not is_admin else [c for c in all_courses if c.category == 'REQUIRED']

    for course in courses_to_plot:
        day = course.day_of_week
        start_p = course.start_period
        end_p = course.end_period
        span = end_p - start_p + 1

        if start_p in timetable and day in timetable[start_p]:
            timetable[start_p][day] = {
                'type': 'course',
                'course': course,
                'rowspan': span,
                'is_start': True,
            }
            # 將跨節次的後續格子標記為 occupied
            for p in range(start_p + 1, end_p + 1):
                if p in timetable and day in timetable[p]:
                    timetable[p][day] = {'type': 'occupied'}

    # 學生選修課程清單處理（計算衝堂狀態、選課狀態）
    elective_courses_data = []
    for c in all_courses:
        is_enrolled = c.id in enrolled_course_ids
        conflict_with = None
        if not is_enrolled and not is_admin:
            for ec in enrolled_courses:
                if check_time_conflict(c, ec):
                    conflict_with = ec
                    break

        elective_courses_data.append({
            'course': c,
            'is_enrolled': is_enrolled,
            'is_open': c.is_open_for_enrollment,
            'conflict_with': conflict_with,
            'is_full': c.current_enrolled_count >= c.max_students,
        })

    # 學分統計（學生端）
    total_credits = sum(c.credits for c in enrolled_courses)
    required_credits = sum(c.credits for c in enrolled_courses if c.category == 'REQUIRED')
    elective_credits = sum(c.credits for c in enrolled_courses if c.category == 'ELECTIVE')

    # 管理員端統計數據（總課程數、開放選修中課程數）
    total_courses_count = all_courses.count()
    open_courses_count = all_courses.filter(is_open_for_enrollment=True).count()

    # 取得現有與預設所有教師名單（供新增/編輯課程時打字或下拉選擇）
    default_teachers = [
        '黃燕萍', '李俞麟', '唐日新', '林俊杰', '丁慧瑩',
        '謝文欽', '陳秋良', '許佩玉', '顏嬿真', '王嬿惠',
        '葉明貴', '郭怡君'
    ]
    db_teachers = list(Course.objects.values_list('teacher', flat=True).distinct())
    teachers_list = sorted(list({t.strip() for t in (default_teachers + db_teachers) if t and t.strip()}))

    # 學生名冊（管理員端查看與管理資管一甲學生）
    students_list = []
    if is_admin:
        students_query = User.objects.filter(is_staff=False).select_related('profile').prefetch_related('enrollments__course').order_by('username')
        for stu in students_query:
            enr_courses = [e.course for e in stu.enrollments.all()]
            req_c = sum(c.credits for c in enr_courses if c.category == 'REQUIRED')
            elec_c = sum(c.credits for c in enr_courses if c.category == 'ELECTIVE')
            students_list.append({
                'user': stu,
                'profile': getattr(stu, 'profile', None),
                'total_credits': req_c + elec_c,
                'required_credits': req_c,
                'elective_credits': elec_c,
                'course_count': len(enr_courses),
                'enrolled_courses': enr_courses,
            })

    context = {
        'is_admin': is_admin,
        'period_info': PERIOD_INFO,
        'days_info': DAYS_INFO,
        'timetable': timetable,
        'all_courses': all_courses,
        'enrolled_courses': enrolled_courses,
        'elective_courses_data': elective_courses_data,
        'total_credits': total_credits,
        'required_credits': required_credits,
        'elective_credits': elective_credits,
        'course_count': len(enrolled_courses),
        'total_courses_count': total_courses_count,
        'open_courses_count': open_courses_count,
        'teachers_list': teachers_list,
        'students_list': students_list,
        'tab': active_tab,
    }
    return render(request, 'index.html', context)


def login_view(request):
    """手動登入頁面與身分驗證"""
    # 若已登入直接轉至首頁
    if request.user.is_authenticated:
        return redirect('pages:index')

    if request.method == 'POST':
        uname = request.POST.get('username', '').strip()
        pwd = request.POST.get('password', '').strip()
        user = authenticate(request, username=uname, password=pwd)
        if user:
            login(request, user)
            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"登入成功！歡迎 {display_name} 進入系統。")
            if user.is_staff or user.username == 'admin':
                return redirect('pages:manage_courses')
            else:
                return redirect('pages:timetable')
        else:
            messages.error(request, "帳號或密碼輸入錯誤，請重新登入！(學生: student / student123；管理員: admin / admin123)")

    return render(request, 'login.html')


def logout_view(request):
    """登出帳號並返回登入頁"""
    logout(request)
    messages.info(request, "您已成功登出系統。")
    return redirect('pages:login')


@login_required
@require_POST
def enroll_course(request, course_id):
    """學生加選額外課程"""
    course = get_object_or_404(Course, id=course_id)

    # 檢查是否開放選修
    if not course.is_open_for_enrollment:
        messages.error(request, f"選課失敗：【{course.name}】目前教務端未開放學生選修！")
        return redirect('pages:electives')

    # 檢查是否已經選修
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, f"您已經選修過【{course.name}】囉！")
        return redirect('pages:electives')

    # 檢查人數上限
    if course.current_enrolled_count >= course.max_students:
        messages.error(request, f"選課失敗：【{course.name}】修課人數已額滿（上限 {course.max_students} 人）！")
        return redirect('pages:electives')

    # 檢查時間衝突 (衝堂)
    current_enrolled = [e.course for e in Enrollment.objects.filter(user=request.user).select_related('course')]
    for ec in current_enrolled:
        if check_time_conflict(course, ec):
            messages.error(
                request,
                f"選課失敗：【{course.name}】（{course.period_display}）與您已選的【{ec.name}】（{ec.period_display}）時段衝突！"
            )
            return redirect('pages:electives')

    # 建立選課紀錄
    Enrollment.objects.create(user=request.user, course=course)
    messages.success(request, f"成功加選【{course.name}】（{course.credits} 學分），已排入您的週課表！")
    return redirect('pages:timetable')


@login_required
@require_POST
def drop_course(request, course_id):
    """學生退選課程"""
    course = get_object_or_404(Course, id=course_id)

    # 限制必修課不可由學生自行退選
    if course.category == 'REQUIRED':
        messages.error(request, f"退選失敗：【{course.name}】為資管一甲班級必修課程，學生端無法退選！")
        return redirect('pages:timetable')

    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment:
        enrollment.delete()
        messages.success(request, f"已成功退選【{course.name}】（已釋出 {course.credits} 學分）。")
    else:
        messages.warning(request, f"您尚未選修【{course.name}】。")

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('pages:timetable')


@login_required
@require_POST
def toggle_course_status(request, course_id):
    """管理員切換課程是否開放選修"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可調整課程開放狀態。")

    course = get_object_or_404(Course, id=course_id)
    course.is_open_for_enrollment = not course.is_open_for_enrollment
    course.save()

    status_str = "【開放學生選修】" if course.is_open_for_enrollment else "【未開放選修】"
    messages.success(request, f"已更新課程【{course.name}】狀態為：{status_str}")

    return redirect('pages:manage_courses')


@login_required
@require_POST
def add_course(request):
    """管理員新增課程"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可新增課程。")

    code = request.POST.get('code', '').strip().upper()
    name = request.POST.get('name', '').strip()
    teacher = request.POST.get('teacher', '').strip()
    classroom = request.POST.get('classroom', '').strip()
    credits = int(request.POST.get('credits', 2))
    category = request.POST.get('category', 'ELECTIVE')
    day_of_week = int(request.POST.get('day_of_week', 1))
    start_period = int(request.POST.get('start_period', 1))
    end_period = int(request.POST.get('end_period', 1))
    is_open = request.POST.get('is_open_for_enrollment') == 'on'
    max_students = int(request.POST.get('max_students', 50))
    description = request.POST.get('description', '').strip()
    color_tag = request.POST.get('color_tag', 'indigo')

    if not code or not name:
        messages.error(request, "新增失敗：課程代碼與名稱為必填項目！")
        return redirect('pages:manage_courses')

    if end_period < start_period:
        messages.error(request, "新增失敗：結束節次不能小於開始節次！")
        return redirect('pages:manage_courses')

    if Course.objects.filter(code=code).exists():
        messages.error(request, f"新增失敗：課程代碼【{code}】已存在！")
        return redirect('pages:manage_courses')

    Course.objects.create(
        code=code,
        name=name,
        teacher=teacher or "未指定",
        classroom=classroom or "未指定",
        credits=credits,
        category=category,
        day_of_week=day_of_week,
        start_period=start_period,
        end_period=end_period,
        is_open_for_enrollment=is_open,
        max_students=max_students,
        description=description,
        color_tag=color_tag
    )

    messages.success(request, f"成功新增課程：【{name}】（代碼: {code}）！")
    return redirect('pages:manage_courses')


@login_required
@require_POST
def edit_course(request, course_id):
    """管理員編輯課程內容與節次"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可編輯課程。")

    course = get_object_or_404(Course, id=course_id)

    name = request.POST.get('name', '').strip()
    teacher = request.POST.get('teacher', '').strip()
    classroom = request.POST.get('classroom', '').strip()
    credits = int(request.POST.get('credits', course.credits))
    category = request.POST.get('category', course.category)
    day_of_week = int(request.POST.get('day_of_week', course.day_of_week))
    start_period = int(request.POST.get('start_period', course.start_period))
    end_period = int(request.POST.get('end_period', course.end_period))
    is_open = request.POST.get('is_open_for_enrollment') == 'on'
    max_students = int(request.POST.get('max_students', course.max_students))
    description = request.POST.get('description', '').strip()
    color_tag = request.POST.get('color_tag', course.color_tag)

    if not name:
        messages.error(request, "編輯失敗：課程名稱不能為空！")
        return redirect('pages:manage_courses')

    if end_period < start_period:
        messages.error(request, "編輯失敗：結束節次不能小於開始節次！")
        return redirect('pages:manage_courses')

    course.name = name
    course.teacher = teacher or course.teacher
    course.classroom = classroom or course.classroom
    course.credits = credits
    course.category = category
    course.day_of_week = day_of_week
    course.start_period = start_period
    course.end_period = end_period
    course.is_open_for_enrollment = is_open
    course.max_students = max_students
    course.description = description
    course.color_tag = color_tag
    course.save()

    messages.success(request, f"已成功更新課程【{course.name}】的資料與時段！")
    return redirect('pages:manage_courses')


@login_required
@require_POST
def delete_course(request, course_id):
    """管理員刪除課程"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可刪除課程。")

    course = get_object_or_404(Course, id=course_id)
    cname = course.name
    course.delete()
    messages.success(request, f"課程【{cname}】已成功刪除。")
    return redirect('pages:manage_courses')


@login_required
@require_POST
def reset_database(request):
    """一鍵重設示範資料為資管一甲標準課表"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可重置系統資料。")

    init_demo_data()
    messages.success(request, "已成功重置為資管一甲標準課表！")
    return redirect('pages:manage_courses')


@login_required
def profile_settings(request):
    """使用者個人設定：修改姓名、上傳頭像、重設密碼（需輸入兩次確認）"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    is_admin = user.is_staff or user.username == 'admin'

    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        avatar_file = request.FILES.get('avatar')

        # 1. 姓名與性別更新
        if name:
            user.first_name = name
            user.save()

        gender = request.POST.get('gender', '').strip()
        if gender in ['M', 'F', 'O']:
            profile.gender = gender
            profile.save()

        # 2. 頭像更新
        if avatar_file:
            profile.avatar = avatar_file
            profile.save()

        # 3. 密碼更新 (若有填寫任一欄位)
        password_changed = False
        if new_password or confirm_password:
            if not new_password:
                messages.error(request, "設定失敗：請輸入新密碼！")
                return render(request, 'profile_settings.html', {'profile': profile, 'is_admin': is_admin})
            if new_password != confirm_password:
                messages.error(request, "設定失敗：兩次輸入的密碼不相符，請重新確認！")
                return render(request, 'profile_settings.html', {'profile': profile, 'is_admin': is_admin})
            if len(new_password) < 4:
                messages.error(request, "設定失敗：新密碼長度至少需 4 個字元以上！")
                return render(request, 'profile_settings.html', {'profile': profile, 'is_admin': is_admin})

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            password_changed = True

        if password_changed:
            messages.success(request, "個人資料與登入密碼已成功更新！")
        else:
            messages.success(request, "個人設定已成功更新！")

        return redirect('pages:profile_settings')

    return render(request, 'profile_settings.html', {'profile': profile, 'is_admin': is_admin})


@login_required
@require_POST
def add_student(request):
    """教務管理員新增資管一甲學生帳號"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可新增學生帳號。")

    username = request.POST.get('username', '').strip()
    name = request.POST.get('name', '').strip()
    gender = request.POST.get('gender', 'M').strip()
    if gender not in ['M', 'F', 'O']:
        gender = 'M'
    password = request.POST.get('password', '').strip() or 'student123'
    student_id = request.POST.get('student_id', '').strip() or username

    if not username or not name:
        messages.error(request, "新增失敗：學生帳號與姓名為必填項目！")
        return redirect('pages:students_roster')

    if User.objects.filter(username=username).exists():
        messages.error(request, f"新增失敗：帳號【{username}】已被使用，請更換帳號或學號！")
        return redirect('pages:students_roster')

    student_user = create_student_account(
        username=username,
        name=name,
        gender=gender,
        password=password,
        student_id=student_id
    )

    gender_display = student_user.profile.get_gender_display()
    messages.success(
        request,
        f"成功新增資管一甲學生：【{name}】（帳號: {username}，性別: {gender_display}）！預設密碼為 {password}，已自動預載資管一甲班級必修課表。"
    )
    return redirect('pages:students_roster')


@login_required
@require_POST
def edit_student_id(request, user_id):
    """教務管理員修改學生學號"""
    if not (request.user.is_staff or request.user.username == 'admin'):
        return HttpResponseForbidden("僅教務管理員可修改學生學號。")

    target_user = get_object_or_404(User, id=user_id)
    new_student_id = request.POST.get('student_id', '').strip()

    if not new_student_id:
        messages.error(request, "修改失敗：學生學號不可為空白！")
        return redirect('pages:students_roster')

    if len(new_student_id) > 20:
        messages.error(request, "修改失敗：學生學號長度不得超過 20 個字元！")
        return redirect('pages:students_roster')

    # 檢查學號是否與其他學生重複
    if UserProfile.objects.filter(student_id=new_student_id).exclude(user=target_user).exists():
        messages.error(request, f"修改失敗：學號【{new_student_id}】已被其他學生使用，請確認後重新輸入！")
        return redirect('pages:students_roster')

    profile, _ = UserProfile.objects.get_or_create(user=target_user)
    old_student_id = profile.student_id or target_user.username
    profile.student_id = new_student_id
    profile.save()

    student_name = target_user.first_name if target_user.first_name else target_user.username
    messages.success(
        request,
        f"成功將學生【{student_name}】（帳號: {target_user.username}）的學號更新為【{new_student_id}】！"
    )
    return redirect('pages:students_roster')


