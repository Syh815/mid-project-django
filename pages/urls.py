from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # 首頁與乾淨語意化目錄路徑 (Clean Semantic Directory URLs)
    path('', views.index, name='index'),
    path('timetable/', views.index, {'tab': 'timetable'}, name='timetable'),
    path('electives/', views.index, {'tab': 'electives'}, name='electives'),
    path('enrolled/', views.index, {'tab': 'enrolled'}, name='enrolled'),

    # 教務管理語意化目錄路徑
    path('manage/courses/', views.index, {'tab': 'admin_courses'}, name='manage_courses'),
    path('manage/students/', views.index, {'tab': 'students_roster'}, name='students_roster'),

    # 快捷別名相容
    path('admin-courses/', views.index, {'tab': 'admin_courses'}, name='admin_courses'),
    path('students-roster/', views.index, {'tab': 'students_roster'}, name='students_roster_alias'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/drop/', views.drop_course, name='drop_course'),
    # 教務管理路徑（使用 manage/ 前綴，避免與 django admin.site.urls 衝突）
    path('manage/course/<int:course_id>/toggle/', views.toggle_course_status, name='toggle_course_status'),
    path('manage/course/add/', views.add_course, name='add_course'),
    path('manage/course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('manage/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('manage/reset-database/', views.reset_database, name='reset_database'),
]