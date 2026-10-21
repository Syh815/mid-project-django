from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('REQUIRED', '必修'),
        ('ELECTIVE', '選修'),
    ]

    DAY_CHOICES = [
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name="課程代碼")
    name = models.CharField(max_length=100, verbose_name="課程名稱")
    teacher = models.CharField(max_length=50, verbose_name="授課教師")
    classroom = models.CharField(max_length=50, verbose_name="上課教室")
    credits = models.PositiveIntegerField(default=2, verbose_name="學分數")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='ELECTIVE', verbose_name="課程屬性")
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES, default=1, verbose_name="上課星期")
    start_period = models.PositiveSmallIntegerField(default=1, verbose_name="開始節次")
    end_period = models.PositiveSmallIntegerField(default=1, verbose_name="結束節次")
    is_open_for_enrollment = models.BooleanField(default=True, verbose_name="開放學生選修")
    max_students = models.PositiveIntegerField(default=50, verbose_name="選課人數上限")
    description = models.TextField(blank=True, default="", verbose_name="課程描述")
    color_tag = models.CharField(max_length=30, default="indigo", verbose_name="代表顏色")

    class Meta:
        ordering = ['day_of_week', 'start_period', 'code']
        verbose_name = "課程"
        verbose_name_plural = "課程列表"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name} ({self.get_day_of_week_display()} 第{self.start_period}-{self.end_period}節)"

    @property
    def periods_list(self):
        return list(range(self.start_period, self.end_period + 1))

    @property
    def period_display(self):
        day_str = dict(self.DAY_CHOICES).get(self.day_of_week, '')
        if self.start_period == self.end_period:
            return f"{day_str} 第 {self.start_period} 節"
        return f"{day_str} 第 {self.start_period}~{self.end_period} 節"

    @property
    def current_enrolled_count(self):
        return self.enrollments.count()


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name="選課學生")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="選修課程")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="選課時間")

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "選課紀錄"
        verbose_name_plural = "選課紀錄列表"

    def __str__(self):
        return f"{self.user.username} -> {self.course.name}"
