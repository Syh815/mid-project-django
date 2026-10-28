from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Course, Enrollment, UserProfile

DEFAULT_TEACHERS = [
    '黃燕萍', '李俞麟', '唐日新', '林俊杰', '丁慧瑩',
    '謝文欽', '陳秋良', '許佩玉', '顏嬿真', '王嬿惠',
    '葉明貴', '郭怡君'
]

def get_teacher_list():
    try:
        db_teachers = list(Course.objects.values_list('teacher', flat=True).distinct())
    except Exception:
        db_teachers = []
    return sorted(list({t.strip() for t in (DEFAULT_TEACHERS + db_teachers) if t and t.strip()}))

class TeacherDatalistWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        widget_id = attrs.get('id', f"id_{name}")
        list_id = f"{widget_id}_datalist"
        attrs['list'] = list_id
        attrs['placeholder'] = "可打字輸入或由右側/清單挑選老師"
        attrs['autocomplete'] = "off"
        html = super().render(name, value, attrs, renderer)
        teachers = get_teacher_list()
        options = "".join(f'<option value="{t}">' for t in teachers)
        select_options = "".join(f'<option value="{t}">{t}</option>' for t in teachers)
        helper_html = f'''
        <select style="margin-left: 8px; vertical-align: middle; padding: 4px 8px; border-radius: 4px; border: 1px solid #ccc; font-size: 13px; background: #f8fafc; cursor: pointer;"
                onchange="if(this.value){{ document.getElementById('{widget_id}').value = this.value; this.value=''; document.getElementById('{widget_id}').focus(); }}">
            <option value="">▼ 快速選擇老師</option>
            {select_options}
        </select>
        <datalist id="{list_id}">{options}</datalist>
        <span style="display: block; margin-top: 4px; font-size: 12px; color: #64748b;">
            💡 提示：可直接於文字框打字輸入教師名稱，或點選右側下拉選單快速挑選。
        </span>
        '''
        return mark_safe(f'<div style="display: inline-block;">{html}{helper_html}</div>')

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'teacher': TeacherDatalistWidget(),
        }

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('code', 'name', 'category', 'teacher', 'classroom', 'day_of_week', 'start_period', 'end_period', 'credits', 'is_open_for_enrollment')
    list_filter = ('category', 'day_of_week', 'is_open_for_enrollment')
    search_fields = ('code', 'name', 'teacher', 'classroom')
    list_editable = ('is_open_for_enrollment',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    list_filter = ('course__category', 'course')
    search_fields = ('user__username', 'course__name')


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "學生個人資訊 / 學號設定"
    verbose_name_plural = "學生個人資訊 / 學號設定"

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'get_student_id', 'get_gender', 'is_staff')

    @admin.display(description="學號")
    def get_student_id(self, obj):
        return getattr(obj.profile, 'student_id', '') if hasattr(obj, 'profile') else ''

    @admin.display(description="性別")
    def get_gender(self, obj):
        return obj.profile.get_gender_display() if hasattr(obj, 'profile') else ''

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'student_class', 'gender', 'updated_at')
    list_editable = ('student_id',)
    search_fields = ('user__username', 'user__first_name', 'student_id')
    list_filter = ('student_class', 'gender')


