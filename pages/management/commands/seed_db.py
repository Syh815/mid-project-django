from django.core.management.base import BaseCommand
from pages.utils import init_demo_data

class Command(BaseCommand):
    help = '初始化資管一甲課表與 student / admin 帳號'

    def handle(self, *args, **options):
        admin_user, student_user = init_demo_data()
        self.stdout.write(self.style.SUCCESS(f"成功初始化資料！"))
        self.stdout.write(self.style.SUCCESS(f"管理員帳號: {admin_user.username} (密碼: admin123)"))
        self.stdout.write(self.style.SUCCESS(f"學生帳號: {student_user.username} (密碼: student123)"))
