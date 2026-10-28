from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from pages.models import Course, Enrollment
from pages.utils import init_demo_data, create_student_account

class CourseSelectionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user, self.student_user = init_demo_data()

    def test_demo_initialization(self):
        """驗證預設帳號與課程建立"""
        self.assertTrue(User.objects.filter(username='admin').exists())
        self.assertTrue(User.objects.filter(username='student').exists())
        self.assertEqual(self.student_user.first_name, '張家豪')
        self.assertGreaterEqual(Course.objects.count(), 10)
        # 課表必修科目數為 10 門
        self.assertEqual(Course.objects.filter(category='REQUIRED').count(), 10)

    def test_unauthenticated_redirects_to_login(self):
        """未登入使用者造訪首頁時應自動跳轉至 /login/"""
        response = self.client.get(reverse('pages:index'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('pages:login')))

    def test_student_login_and_enroll_open_course(self):
        """學生登入並成功加選開放中的選修課程 (如 Linux基礎教學)"""
        login_res = self.client.post(reverse('pages:login'), {'username': 'student', 'password': 'student123'}, follow=True)
        self.assertEqual(login_res.status_code, 200)

        # EL201 Linux基礎教學 (葉明貴老師)
        linux_course = Course.objects.get(code='EL201')
        self.assertEqual(linux_course.teacher, '葉明貴')
        self.assertTrue(linux_course.is_open_for_enrollment)

        response = self.client.post(reverse('pages:enroll_course', args=[linux_course.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enrollment.objects.filter(user=self.student_user, course=linux_course).exists())

    def test_student_cannot_enroll_closed_course(self):
        """學生無法選修管理員關閉中的課程 (如 EL205 人工智慧通識導論)"""
        self.client.force_login(self.student_user)
        ai_course = Course.objects.get(code='EL205')
        self.assertFalse(ai_course.is_open_for_enrollment)

        response = self.client.post(reverse('pages:enroll_course', args=[ai_course.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Enrollment.objects.filter(user=self.student_user, course=ai_course).exists())

    def test_student_time_conflict_prevention(self):
        """學生選課若與現有時段衝堂應被阻擋"""
        self.client.force_login(self.student_user)
        # 建立一門與週一 2-4 節（資訊管理導論）衝堂的選修課
        conflict_course = Course.objects.create(
            code='CONF01',
            name='衝堂測試課',
            teacher='測試師',
            classroom='電708',
            credits=2,
            category='ELECTIVE',
            day_of_week=1,
            start_period=3,
            end_period=4,
            is_open_for_enrollment=True,
            max_students=30
        )
        response = self.client.post(reverse('pages:enroll_course', args=[conflict_course.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Enrollment.objects.filter(user=self.student_user, course=conflict_course).exists())

    def test_student_drop_course(self):
        """學生退選選修課程"""
        self.client.force_login(self.student_user)
        # 加選後退選
        c = Course.objects.get(code='EL202')
        Enrollment.objects.create(user=self.student_user, course=c)
        self.assertTrue(Enrollment.objects.filter(user=self.student_user, course=c).exists())

        response = self.client.post(reverse('pages:drop_course', args=[c.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Enrollment.objects.filter(user=self.student_user, course=c).exists())

    def test_student_cannot_drop_required_course(self):
        """學生不可退選資管一甲必修課程"""
        self.client.force_login(self.student_user)
        req_course = Course.objects.filter(category='REQUIRED').first()
        response = self.client.post(reverse('pages:drop_course', args=[req_course.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        # 依然存在
        self.assertTrue(Enrollment.objects.filter(user=self.student_user, course=req_course).exists())

    def test_admin_toggle_course_status(self):
        """管理員切換課程是否開放選修"""
        self.client.force_login(self.admin_user)
        ai_course = Course.objects.get(code='EL205')
        self.assertFalse(ai_course.is_open_for_enrollment)

        # 切換為開放
        response = self.client.post(reverse('pages:toggle_course_status', args=[ai_course.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        ai_course.refresh_from_db()
        self.assertTrue(ai_course.is_open_for_enrollment)

        # 再切換回關閉
        response = self.client.post(reverse('pages:toggle_course_status', args=[ai_course.id]), follow=True)
        ai_course.refresh_from_db()
        self.assertFalse(ai_course.is_open_for_enrollment)

    def test_admin_add_course(self):
        """管理員新增課程"""
        self.client.force_login(self.admin_user)
        data = {
            'code': 'NEW101',
            'name': '人工智慧商務應用',
            'teacher': '黃教授',
            'classroom': '管401',
            'credits': 3,
            'category': 'ELECTIVE',
            'day_of_week': 3,
            'start_period': 7,
            'end_period': 8,
            'is_open_for_enrollment': 'on',
            'max_students': 40,
            'description': 'AI 商業實例解析',
            'color_tag': 'emerald',
        }
        response = self.client.post(reverse('pages:add_course'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Course.objects.filter(code='NEW101').exists())

    def test_admin_edit_course(self):
        """管理員編輯課程資訊與節次"""
        self.client.force_login(self.admin_user)
        c = Course.objects.get(code='EL201')
        data = {
            'name': '進階Linux雲端伺服器架設',
            'teacher': '葉明貴',
            'classroom': '電708(承曦樓)',
            'credits': 3,
            'category': 'ELECTIVE',
            'day_of_week': 5,
            'start_period': 5,
            'end_period': 7,
            'is_open_for_enrollment': 'on',
            'max_students': 50,
            'description': 'Linux 伺服器進階應用',
            'color_tag': 'emerald',
        }
        response = self.client.post(reverse('pages:edit_course', args=[c.id]), data, follow=True)
        self.assertEqual(response.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.name, '進階Linux雲端伺服器架設')
        self.assertEqual(c.credits, 3)
        self.assertEqual(c.end_period, 7)

    def test_teachers_list_in_index_context(self):
        """驗證管理員首頁提供教師名單供選取與自動補全"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('pages:index'))
        self.assertEqual(response.status_code, 200)
        teachers_list = response.context['teachers_list']
        self.assertIn('葉明貴', teachers_list)
        self.assertIn('黃燕萍', teachers_list)
        self.assertIn('丁慧瑩', teachers_list)
        self.assertNotIn('丁慧堂', teachers_list)
        self.assertNotIn('佐藤愛子', teachers_list)
        # 驗證模板中包含 teacherOptionsList datalist 與下拉選單
        content = response.content.decode('utf-8')
        self.assertIn('id="teacherOptionsList"', content)
        self.assertIn('id="addTeacherInput"', content)
        self.assertIn('id="editTeacher"', content)
        self.assertIn('▼ 快速選擇', content)

    def test_semantic_directory_urls_and_tab_redirect(self):
        """驗證語意化目錄路徑（/enrolled/、/electives/、/timetable/）與舊式 ?tab= 重導向"""
        self.client.force_login(self.student_user)

        # 1. 直接造訪 /enrolled/
        res_enrolled = self.client.get(reverse('pages:enrolled'))
        self.assertEqual(res_enrolled.status_code, 200)
        self.assertEqual(res_enrolled.context['tab'], 'enrolled')
        self.assertIn('/enrolled/', res_enrolled.content.decode('utf-8'))

        # 2. 直接造訪 /electives/
        res_electives = self.client.get(reverse('pages:electives'))
        self.assertEqual(res_electives.status_code, 200)
        self.assertEqual(res_electives.context['tab'], 'electives')

        # 3. 直接造訪 /timetable/
        res_timetable = self.client.get(reverse('pages:timetable'))
        self.assertEqual(res_timetable.status_code, 200)
        self.assertEqual(res_timetable.context['tab'], 'timetable')

        # 4. 造訪舊式 ?tab=enrolled，應自動 302 導向至 /enrolled/
        res_legacy = self.client.get('/?tab=enrolled')
        self.assertEqual(res_legacy.status_code, 302)
        self.assertEqual(res_legacy.url, reverse('pages:enrolled'))

        # 5. 管理員造訪 /manage/courses/
        self.client.force_login(self.admin_user)
        res_admin = self.client.get(reverse('pages:manage_courses'))
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.context['tab'], 'admin_courses')

    def test_student_gender_and_add_student_feature(self):
        """驗證張家豪為男生、性別欄位存在，以及管理員新增資管一甲學生帳號功能"""
        # 1. 驗證張家豪性別為男，班級為資管一甲
        profile = self.student_user.profile
        self.assertEqual(profile.gender, 'M')
        self.assertEqual(profile.get_gender_display(), '男')
        self.assertEqual(profile.student_class, '資管一甲')

        # 2. 測試管理員新增資管一甲學生帳號 (例如: 林美美, 女生)
        self.client.force_login(self.admin_user)
        new_student_data = {
            'username': 'student2',
            'name': '林美美',
            'gender': 'F',
            'student_id': 'B11305002',
            'password': 'student123',
        }
        response = self.client.post(reverse('pages:add_student'), new_student_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 驗證新學生已建立
        new_stu = User.objects.get(username='student2')
        self.assertEqual(new_stu.first_name, '林美美')
        self.assertEqual(new_stu.profile.gender, 'F')
        self.assertEqual(new_stu.profile.get_gender_display(), '女')
        self.assertEqual(new_stu.profile.student_class, '資管一甲')

        # 驗證新學生自動預載資管一甲的 10 門必修課
        enrolled_required_count = Enrollment.objects.filter(user=new_stu, course__category='REQUIRED').count()
        self.assertEqual(enrolled_required_count, 10)

        # 3. 測試非管理員無法新增學生
        self.client.force_login(self.student_user)
        res_forbidden = self.client.post(reverse('pages:add_student'), new_student_data)
        self.assertEqual(res_forbidden.status_code, 403)

    def test_admin_edit_student_id_feature(self):
        """驗證管理員可成功修改學生學號、權限校驗與重複/空白學號之防護機制"""
        # 1. 驗證張家豪原始學號
        self.student_user.profile.refresh_from_db()
        self.assertEqual(self.student_user.profile.student_id, 'B11305001')

        # 2. 管理員成功修改學號為 B11305088
        self.client.force_login(self.admin_user)
        url = reverse('pages:edit_student_id', args=[self.student_user.id])
        response = self.client.post(url, {'student_id': 'B11305088'}, follow=True)
        self.assertEqual(response.status_code, 200)

        # 驗證資料庫已更新
        self.student_user.profile.refresh_from_db()
        self.assertEqual(self.student_user.profile.student_id, 'B11305088')

        # 驗證學生登入後首頁即時顯示新學號
        self.client.force_login(self.student_user)
        res_index = self.client.get(reverse('pages:index'))
        self.assertContains(res_index, 'B11305088')

        # 3. 測試管理員不能將學號改為空白
        self.client.force_login(self.admin_user)
        res_empty = self.client.post(url, {'student_id': '   '}, follow=True)
        self.assertContains(res_empty, '學生學號不可為空白')
        self.student_user.profile.refresh_from_db()
        self.assertEqual(self.student_user.profile.student_id, 'B11305088')

        # 4. 測試防止學號與其他學生重複
        # 先建立另一名學生 student2 (學號: B11305002)
        create_student_account(
            username='student2',
            name='李小明',
            gender='M',
            password='student123',
            student_id='B11305002'
        )
        res_dup = self.client.post(url, {'student_id': 'B11305002'}, follow=True)
        self.assertContains(res_dup, '已被其他學生使用')
        self.student_user.profile.refresh_from_db()
        self.assertEqual(self.student_user.profile.student_id, 'B11305088')

        # 5. 測試非管理員(一般學生)無法修改他人學號
        self.client.force_login(self.student_user)
        res_forbidden = self.client.post(url, {'student_id': 'B11305999'})
        self.assertEqual(res_forbidden.status_code, 403)
        self.student_user.profile.refresh_from_db()
        self.assertEqual(self.student_user.profile.student_id, 'B11305088')




