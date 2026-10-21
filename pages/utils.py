from django.contrib.auth.models import User
from pages.models import Course, Enrollment

def init_demo_data():
    """建立預設帳號與資管一甲課程示範資料（參考實際課表資訊）"""
    # 建立或更新 admin 帳號
    admin_user, _ = User.objects.get_or_create(username='admin')
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.first_name = '教務處管理員'
    admin_user.save()

    # 建立或更新 student 帳號，學生姓名設定為「張家豪」
    student_user, _ = User.objects.get_or_create(username='student')
    student_user.set_password('student123')
    student_user.is_staff = False
    student_user.is_superuser = False
    student_user.first_name = '張家豪'
    student_user.save()

    # 清除舊課程資料以確保完全符合課表
    Enrollment.objects.all().delete()
    Course.objects.all().delete()

    # 資管一甲標準課表課程（完全依據課表圖片第二張之課程、教師、教室與節次）
    demo_courses = [
        # --- 必修課程 (週一至週五固定課表) ---
        {
            'code': 'IM101',
            'name': '資訊管理導論',
            'teacher': '黃燕萍',
            'classroom': '電708(承曦樓)',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 1,
            'start_period': 2,
            'end_period': 4,
            'is_open_for_enrollment': False,
            'max_students': 60,
            'description': '資管核心基礎課程，探討資訊管理架構、數位轉型與企業資訊科技應用。',
            'color_tag': 'blue'
        },
        {
            'code': 'PE101',
            'name': '體育三(上)',
            'teacher': '李俞麟',
            'classroom': '藝406',
            'credits': 1,
            'category': 'REQUIRED',
            'day_of_week': 1,
            'start_period': 5,
            'end_period': 6,
            'is_open_for_enrollment': False,
            'max_students': 60,
            'description': '健康體適能與球類運動訓練。',
            'color_tag': 'teal'
        },
        {
            'code': 'IM102',
            'name': '電子商務',
            'teacher': '唐日新',
            'classroom': '藝406',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 2,
            'start_period': 2,
            'end_period': 4,
            'is_open_for_enrollment': False,
            'max_students': 55,
            'description': '網路商業經營模式、網路金流、平台經濟與跨境電商策略。',
            'color_tag': 'indigo'
        },
        {
            'code': 'IM103',
            'name': '網站應用程式設計與實習',
            'teacher': '林俊杰',
            'classroom': '電708(承曦樓)',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 2,
            'start_period': 5,
            'end_period': 7,
            'is_open_for_enrollment': False,
            'max_students': 50,
            'description': 'Web 應用程式架構、前端互動界面與後端資料庫串接實習。',
            'color_tag': 'sky'
        },
        {
            'code': 'IM104',
            'name': '系統分析與設計(上)與實習',
            'teacher': '丁慧堂',
            'classroom': '藝406',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 3,
            'start_period': 2,
            'end_period': 4,
            'is_open_for_enrollment': False,
            'max_students': 55,
            'description': '物件導向系統分析方法（UML）、軟體開發生命週期與系統需求規格書製作。',
            'color_tag': 'indigo'
        },
        {
            'code': 'IM105',
            'name': '電腦網路(上)',
            'teacher': '謝文欽',
            'classroom': '資401',
            'credits': 2,
            'category': 'REQUIRED',
            'day_of_week': 3,
            'start_period': 5,
            'end_period': 6,
            'is_open_for_enrollment': False,
            'max_students': 50,
            'description': 'TCP/IP 網路協定、區域網路拓撲、路由器配置與網路安全架構。',
            'color_tag': 'blue'
        },
        {
            'code': 'MA101',
            'name': '微積分(上)',
            'teacher': '陳秋良',
            'classroom': '藝406',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 3,
            'start_period': 7,
            'end_period': 9,
            'is_open_for_enrollment': False,
            'max_students': 60,
            'description': '極限、微分技巧及其在管理數學與工程問題中的分析與求解。',
            'color_tag': 'violet'
        },
        {
            'code': 'GE101',
            'name': '國文(三)(上)',
            'teacher': '許佩玉',
            'classroom': '藝406',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 4,
            'start_period': 2,
            'end_period': 4,
            'is_open_for_enrollment': False,
            'max_students': 55,
            'description': '文學思維與批判性閱讀，提升公文寫作與人文素養。',
            'color_tag': 'amber'
        },
        {
            'code': 'GE102',
            'name': '英語會話(二)(上)與實習',
            'teacher': '顏嬿真',
            'classroom': '藝406',
            'credits': 2,
            'category': 'REQUIRED',
            'day_of_week': 4,
            'start_period': 5,
            'end_period': 6,
            'is_open_for_enrollment': False,
            'max_students': 50,
            'description': '職場專業會話演練、英語口語聽力與國際簡報技巧。',
            'color_tag': 'purple'
        },
        {
            'code': 'GE103',
            'name': '英文(三)(上)',
            'teacher': '王嬿惠',
            'classroom': '藝406',
            'credits': 3,
            'category': 'REQUIRED',
            'day_of_week': 5,
            'start_period': 2,
            'end_period': 4,
            'is_open_for_enrollment': False,
            'max_students': 55,
            'description': '實用中高階商務英語閱讀與寫作。',
            'color_tag': 'blue'
        },

        # --- 額外選修課程清單（Linux老師指定為葉明貴） ---
        {
            'code': 'EL201',
            'name': 'Linux基礎教學',
            'teacher': '葉明貴',
            'classroom': '電708(承曦樓)',
            'credits': 2,
            'category': 'ELECTIVE',
            'day_of_week': 5,
            'start_period': 5,
            'end_period': 6,
            'is_open_for_enrollment': True,
            'max_students': 40,
            'description': 'Linux 核心指令、Shell Script 編寫、系統使用者管理與伺服器架設入門。',
            'color_tag': 'emerald'
        },
        {
            'code': 'EL202',
            'name': '基礎日文(一)',
            'teacher': '佐藤愛子',
            'classroom': '藝406',
            'credits': 2,
            'category': 'ELECTIVE',
            'day_of_week': 4,
            'start_period': 7,
            'end_period': 8,
            'is_open_for_enrollment': True,
            'max_students': 40,
            'description': '五十音平假名/片假名入門、基礎生活問候日語與日本文化概覽。',
            'color_tag': 'rose'
        },
        {
            'code': 'EL203',
            'name': '多媒體導論',
            'teacher': '郭怡君',
            'classroom': '電708(承曦樓)',
            'credits': 2,
            'category': 'ELECTIVE',
            'day_of_week': 2,
            'start_period': 8,
            'end_period': 9,
            'is_open_for_enrollment': True,
            'max_students': 45,
            'description': '數位音訊與影像處理技術、UI/UX 介面設計原則與多媒體素材整合。',
            'color_tag': 'cyan'
        },
        {
            'code': 'EL204',
            'name': '多益輔導與聽力測驗',
            'teacher': '王嬿惠',
            'classroom': '藝406',
            'credits': 2,
            'category': 'ELECTIVE',
            'day_of_week': 5,
            'start_period': 7,
            'end_period': 8,
            'is_open_for_enrollment': True,
            'max_students': 45,
            'description': '新制 TOEIC 聽力解題技巧、職場模擬情境訓練與文法高分攻略。',
            'color_tag': 'amber'
        },
        {
            'code': 'EL205',
            'name': '人工智慧通識導論',
            'teacher': '謝文欽',
            'classroom': '資401',
            'credits': 2,
            'category': 'ELECTIVE',
            'day_of_week': 3,
            'start_period': 1,
            'end_period': 1,
            'is_open_for_enrollment': False,  # 示範由管理員手動開啟選修之課程
            'max_students': 50,
            'description': '現代機器學習思維、生成式 AI 應用與演算法倫理探討。（管理員預設暫未開放）',
            'color_tag': 'orange'
        },
    ]

    for item in demo_courses:
        Course.objects.create(**item)

    # 將預設必修課全數登記給張家豪 (student)
    required_courses = Course.objects.filter(category='REQUIRED')
    for rc in required_courses:
        Enrollment.objects.get_or_create(user=student_user, course=rc)

    return admin_user, student_user
