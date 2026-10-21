from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
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