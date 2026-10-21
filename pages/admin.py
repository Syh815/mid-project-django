from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'teacher', 'classroom', 'day_of_week', 'start_period', 'end_period', 'credits', 'is_open_for_enrollment')
    list_filter = ('category', 'day_of_week', 'is_open_for_enrollment')
    search_fields = ('code', 'name', 'teacher', 'classroom')
    list_editable = ('is_open_for_enrollment',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('course__category', 'course')
    search_fields = ('user__username', 'course__name')
