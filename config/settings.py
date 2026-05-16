import os
import sys
from dotenv import load_dotenv

class Passwords:
    """
    محطة الطاقة المركزية للمشروع (Security & Config).
    تقوم بعزل البيانات الحساسة عن كود المصدر لضمان الأمان والاحترافية.
    """
    
    def __init__(self):
        # 1. التحميل الذاتي (Self-Loading)
        self._load_env_file()
        # 2. القاموس الداخلي لسرعة الوصول (Data Mapping)
        self.data_map = {}
        self._populate_data()

    def _load_env_file(self):
        """تبحث عن ملف .env وتتأكد من وجوده قبل البدء."""
        if not load_dotenv():
            print("❌ خطأ حرج: ملف .env مفقود في المجلد الرئيسي!")
            print("يرجى إنشاء الملف وتعبئة البيانات قبل تشغيل البرنامج.")
            sys.exit(1) # الخروج من البرنامج فوراً للأمان

    def _populate_data(self):
        """سحب كافة البيانات من البيئة إلى الذاكرة لمرة واحدة فقط."""
        # سنقوم بتعريف كل المفاتيح المتوقع وجودها بناءً على هيكلك المخطط
        expected_keys = [
            'TWITTER_USERNAME', 'TWITTER_PASSWORD',
            'INSTAGRAM_USERNAME', 'INSTAGRAM_PASSWORD',
            'LINKEDIN_USERNAME', 'LINKEDIN_PASSWORD',
            'OPENAI_API_KEY',
            'DB_HOST', 'DB_USER', 'DB_PASS', 'DB_NAME',
            'TWITTER_USER', 'TWITTER_PASS',
            'INSTA_USER', 'INSTA_PASS',
            'LINKED_USER', 'LINKED_PASS',
            'AI_API_KEY'
        ]
        
        for key in expected_keys:
            value = os.getenv(key)
            if value is None:
                # تحدي القيم المفقودة: البرنامج يخبرك أين النقص فوراً
                print(f"⚠️ تنبيه: المتغير الحساس [{key}] غير موجود في ملف .env")
            self.data_map[key] = value

    def get_credential(self, platform, key_type):
        """
        آلية ذكية: تأخذ اسم المنصة ونوع البيانات وتركب الاسم برمجياً.
        مثال: get_credential('INSTA', 'PASS') -> INSTA_PASS
        """
        platform_aliases = {
            "twitter": "TWITTER",
            "insta": "INSTAGRAM",
            "instagram": "INSTAGRAM",
            "linked": "LINKEDIN",
            "linkedin": "LINKEDIN",
        }
        key_aliases = {
            "user": "USERNAME",
            "username": "USERNAME",
            "pass": "PASSWORD",
            "password": "PASSWORD",
        }
        legacy_platform_aliases = {
            "instagram": "INSTA",
            "linkedin": "LINKED",
        }

        normalized_platform = platform.lower()
        normalized_key = key_type.lower()
        platform_key = platform_aliases.get(normalized_platform, platform.upper())
        credential_key = key_aliases.get(normalized_key, key_type.upper())
        constructed_key = f"{platform_key}_{credential_key}"

        legacy_platform = legacy_platform_aliases.get(
            platform_key.lower(),
            platform_key,
        )
        legacy_key = "USER" if credential_key == "USERNAME" else "PASS"
        legacy_constructed_key = f"{legacy_platform}_{legacy_key}"

        return self.data_map.get(constructed_key) or self.data_map.get(legacy_constructed_key)

    def get_db_config(self):
        """دالة مخصصة لجلب إعدادات قاعدة البيانات كقاموس."""
        return {
            'host': self.data_map.get('DB_HOST'),
            'user': self.data_map.get('DB_USER'),
            'password': self.data_map.get('DB_PASS'),
            'database': self.data_map.get('DB_NAME')
        }

    def get_ai_key(self):
        """جلب مفتاح الـ API الخاص بـ Gemini للاستخدام في كلاس Filter."""
        return self.data_map.get('OPENAI_API_KEY') or self.data_map.get('AI_API_KEY')

# --- منطقة الاختبار (Testing) ---
if __name__ == "__main__":
    p = Passwords()
    print("✅ تم تفعيل الحارس الشخصي للمشروع.")
    
    # تجربة جلب بيانات قاعدة البيانات
    db = p.get_db_config()
    print(f"🔗 محاولة الاتصال بـ: {db['host']} (قاعدة البيانات: {db['database']})")
    
    # تجربة الجلب الذكي للمنصات
    twitter_u = p.get_credential('twitter', 'user')
    if twitter_u:
        print(f"👤 مستخدم تويتر المحمل: {twitter_u}")
