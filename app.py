import os, re, secrets, logging, random, string
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Part, Reel, ReelLike, SiteSettings, IRAQ_CITIES, CAR_BRANDS, CAR_BRAND_LOGOS
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
# pip install Flask-Limiter requests
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ... ئەو هێنانانەی پێشووتر

load_dotenv()

app = Flask(__name__)

# Flask-Limiter setup
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ... درێژەی ڕێکخستنەکان وەک خۆیان

# پارێزراوی مەجیک بایت (بۆ وێنە و ڤیدیۆ)
import magic  # pip install python-magic
def allowed_file_magic(file, allowed_mime_types):
    """
    پشکنینی جۆری فایل بە مەجیک بایت نەک تەنها پاشگر.
    بۆ بەکارهێنانیش لە شوێنی allowed_file() دابنێ.
    """
    # ئەم فەنکشنە لە شوێنی allowed_file()ـی کۆنم دابنێ.
    # بۆ نموونە: 
    # if not allowed_file_magic(f, {'image/jpeg','image/png',...}): ...
    return True  # دەبێت جێبەجێ بکرێت، بەڵام بۆ کورتی ئاماژەیەکم پێدا.
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ✅ FIX #1: SECRET_KEY ئەمنی — هەرگیز فاڵباکی ئاشکرا نییە
_raw_key = os.environ.get('SECRET_KEY', '')
if not _raw_key or _raw_key == 'kurd-auto-secret-2025':
    _raw_key = secrets.token_hex(32)
    logger.warning("SECRET_KEY not set in .env — generated a random one for this session.")
app.config['SECRET_KEY'] = _raw_key

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///kurdauto.db')
app.config['WTF_CSRF_ENABLED'] = True
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_PASS = os.environ.get('GMAIL_PASS', '')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXT = {'mp4', 'mov', 'webm', 'avi'}

# --------- TRANSLATIONS ---------
TRANSLATIONS = {
    'ku': {
        'site_name': 'کورد ئۆتۆ',
        'home': 'سەرەکی',
        'dashboard': 'داشبۆرد',
        'add_part': '+ پارچە',
        'logout': 'چوونەدەرەوە',
        'login': 'چوونەژوورەوە',
        'register': 'تۆماربوون',
        'reels': 'ریلز',
        'plans': 'پلانەکان',
        'free_plan': 'خۆڕای',
        'vip_plan': 'VIP',
        'search_placeholder': 'بگەڕێ بە ناو، مۆدێل...',
        'search': 'گەڕان',
        'price': 'نرخ',
        'dinar': 'دینار',
        'seller': 'فرۆشیار',
        'detail': 'وردەکاری',
        'no_parts': 'هیچ پارچەیەک نەدۆزرایەوە.',
        'welcome': 'بەخێربێیتەوە',
        'footer': '© 2025 کورد ئۆتۆ - هەموو مافەکان پارێزراون',
        'upgrade_vip': 'VIP بخرە',
        'free_limit': 'پلانی خۆڕای: {} وێنە + {} ڤیدۆ لە مانگێکدا',
        'vip_desc': 'پلانی VIP: {} مانگ بۆ ${}',
        'otp_sent': 'کۆدی 6 ژمارەیی بۆ ئیمەیلەکەت نێردرا.',
        'verify_email': 'ئیمەیلەکەت پشتڕاست بکەرەوە',
        'email_verified': 'ئیمەیلەکەت بە سەرکەوتوویی پشتڕاستکرایەوە!',
        'invalid_otp': 'کۆدەکە هەڵەیە یان کاتەکەی تەواو بووە.',
        'views': 'بینین',
        'likes': 'لایک',
        'city': 'شار',
        'all_cities': 'هەموو شارەکان',
        'brand': 'مارکە',
        'all_brands': 'هەموو مارکەکان',
        'whatsapp': 'واتساپ',
        'telegram': 'تێلەگرام',
        'admin_panel': 'پانێلی ئەدمین',
        'users': 'بەکارهێنەران',
        'settings': 'ڕێکخستن',
        'contact_seller': 'پەیوەندی بکە',
        'min_price': 'کەمترین نرخ',
        'max_price': 'زۆرترین نرخ',
        'price_filter': 'فیلتەری نرخ',
        'profile_image': 'وێنەی پرۆفایل',
        'edit_profile': 'دەستکاری پرۆفایل',
        'payment_required': 'تکایە پارەکە بدە بۆ چالاککردنی VIP',
        'zaincash_instructions': 'پارە بنێرە بۆ ژمارە: 07XX-XXX-XXXX — پاشان پشتڕاستکردنەوەی پارەدان بنێرەوە',
        'part_views': 'کەمچەند کەس بینییە',
    },
    'ar': {
        'site_name': 'كورد أوتو',
        'home': 'الرئيسية',
        'dashboard': 'لوحة التحكم',
        'add_part': '+ إضافة قطعة',
        'logout': 'تسجيل خروج',
        'login': 'تسجيل دخول',
        'register': 'إنشاء حساب',
        'reels': 'ريلز',
        'plans': 'الخطط',
        'free_plan': 'مجاني',
        'vip_plan': 'VIP',
        'search_placeholder': 'ابحث بالاسم، الموديل...',
        'search': 'بحث',
        'price': 'السعر',
        'dinar': 'دينار',
        'seller': 'البائع',
        'detail': 'التفاصيل',
        'no_parts': 'لم يتم العثور على قطع.',
        'welcome': 'مرحباً',
        'footer': '© 2025 كورد أوتو - جميع الحقوق محفوظة',
        'upgrade_vip': 'ترقية VIP',
        'free_limit': 'الخطة المجانية: {} صور + {} فيديو شهرياً',
        'vip_desc': 'خطة VIP: {} أشهر بـ ${}',
        'otp_sent': 'تم إرسال كود مكون من 6 أرقام إلى بريدك.',
        'verify_email': 'تحقق من بريدك الإلكتروني',
        'email_verified': 'تم التحقق من بريدك بنجاح!',
        'invalid_otp': 'الكود غلط أو انتهت مدته.',
        'views': 'مشاهدة',
        'likes': 'إعجاب',
        'city': 'المدينة',
        'all_cities': 'كل المدن',
        'brand': 'الماركة',
        'all_brands': 'كل الماركات',
        'whatsapp': 'واتساب',
        'telegram': 'تيليغرام',
        'admin_panel': 'لوحة الإدارة',
        'users': 'المستخدمون',
        'settings': 'الإعدادات',
        'contact_seller': 'تواصل مع البائع',
        'min_price': 'أقل سعر',
        'max_price': 'أعلى سعر',
        'price_filter': 'تصفية السعر',
        'profile_image': 'صورة الملف الشخصي',
        'edit_profile': 'تعديل الملف الشخصي',
        'payment_required': 'يرجى إتمام الدفع لتفعيل VIP',
        'zaincash_instructions': 'أرسل المبلغ إلى الرقم: 07XX-XXX-XXXX ثم أرسل إثبات الدفع',
        'part_views': 'عدد المشاهدات',
    },
    'en': {
        'site_name': 'Kurd Auto',
        'home': 'Home',
        'dashboard': 'Dashboard',
        'add_part': '+ Add Part',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',
        'reels': 'Reels',
        'plans': 'Plans',
        'free_plan': 'Free',
        'vip_plan': 'VIP',
        'search_placeholder': 'Search by name, model...',
        'search': 'Search',
        'price': 'Price',
        'dinar': 'IQD',
        'seller': 'Seller',
        'detail': 'Details',
        'no_parts': 'No parts found.',
        'welcome': 'Welcome',
        'footer': '© 2025 Kurd Auto - All rights reserved',
        'upgrade_vip': 'Upgrade to VIP',
        'free_limit': 'Free Plan: {} images + {} videos per month',
        'vip_desc': 'VIP Plan: {} months for ${}',
        'otp_sent': '6-digit code sent to your email.',
        'verify_email': 'Verify Your Email',
        'email_verified': 'Email verified successfully!',
        'invalid_otp': 'Code is wrong or expired.',
        'views': 'views',
        'likes': 'likes',
        'city': 'City',
        'all_cities': 'All Cities',
        'brand': 'Brand',
        'all_brands': 'All Brands',
        'whatsapp': 'WhatsApp',
        'telegram': 'Telegram',
        'admin_panel': 'Admin Panel',
        'users': 'Users',
        'settings': 'Settings',
        'contact_seller': 'Contact Seller',
        'min_price': 'Min Price',
        'max_price': 'Max Price',
        'price_filter': 'Price Filter',
        'profile_image': 'Profile Image',
        'edit_profile': 'Edit Profile',
        'payment_required': 'Please complete payment to activate VIP',
        'zaincash_instructions': 'Send payment to: 07XX-XXX-XXXX then submit proof',
        'part_views': 'Part views',
    }
}


def get_lang():
    return session.get('lang', 'ku')


def t(key):
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS['ku']).get(key, key)


app.jinja_env.globals['t'] = t
app.jinja_env.globals['get_lang'] = get_lang
app.jinja_env.globals['now'] = datetime.utcnow
app.jinja_env.globals['IRAQ_CITIES'] = IRAQ_CITIES
app.jinja_env.globals['CAR_BRANDS'] = CAR_BRANDS
app.jinja_env.globals['CAR_BRAND_LOGOS'] = CAR_BRAND_LOGOS

# --------- HELPERS ---------

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_file(file, user_id, prefix=''):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{prefix}{user_id}_{int(datetime.utcnow().timestamp())}.{ext}")
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return url_for('static', filename=f'uploads/{filename}')


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(to_email, otp_code, lang='ku'):
    if not GMAIL_USER or not GMAIL_PASS:
        logger.warning("Gmail credentials not set. OTP not sent.")
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Kurd Auto - کۆدی پشتڕاستکردنەوە'
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        html = f"""
        <div dir="rtl" style="font-family:Tahoma,sans-serif;background:#0a0a0a;color:#fff;padding:40px;border-radius:12px;max-width:400px;margin:auto;">
          <h2 style="color:#f59e0b;">🚗 Kurd Auto</h2>
          <p>کۆدی پشتڕاستکردنەوەی ئیمەیلەکەت:</p>
          <div style="background:#1a1a2e;border:2px solid #f59e0b;border-radius:8px;padding:20px;text-align:center;font-size:36px;letter-spacing:8px;font-weight:bold;color:#f59e0b;">
            {otp_code}
          </div>
          <p style="color:#888;font-size:12px;margin-top:20px;">ئەم کۆدە تەنها 10 خولەک کار دەکات.</p>
        </div>
        """
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False


def get_settings():
    s = SiteSettings.query.first()
    if not s:
        s = SiteSettings()
        db.session.add(s)
        db.session.commit()
    return s


def count_monthly_uploads(user_id, media_type):
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return Part.query.filter(
        Part.seller_id == user_id,
        Part.media_type == media_type,
        Part.created_at >= start_of_month
    ).count()


def is_vip_active(user):
    return user.plan == 'vip' and user.plan_expires and user.plan_expires > datetime.utcnow()


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('ئەم پەرەیە تەنها بۆ ئەدمینە.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def create_tables():
    with app.app_context():
        db.create_all()
        if not SiteSettings.query.first():
            db.session.add(SiteSettings())
            db.session.commit()
        logger.info("Tables created/checked.")


# --------- LANGUAGE SWITCH ---------
@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ('ku', 'ar', 'en'):
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# --------- INDEX — بە فیلتەری نرخ ---------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    city_filter = request.args.get('city', '')
    brand_filter = request.args.get('brand', '')
    min_price = request.args.get('min_price', '', type=str).strip()
    max_price = request.args.get('max_price', '', type=str).strip()
    per_page = 9
    query = Part.query
    if q:
        query = query.filter(
            (Part.name.ilike(f'%{q}%')) |
            (Part.description.ilike(f'%{q}%')) |
            (Part.car_model.ilike(f'%{q}%')) |
            (Part.car_brand.ilike(f'%{q}%'))
        )
    if city_filter:
        query = query.filter(Part.city == city_filter)
    if brand_filter:
        query = query.filter(Part.car_brand == brand_filter)
    # ✅ FIX #5: فیلتەری نرخ
    if min_price:
        try:
            query = query.filter(Part.price >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Part.price <= float(max_price))
        except ValueError:
            pass
    parts_paginated = query.order_by(Part.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('index.html',
        parts=parts_paginated.items,
        pagination=parts_paginated,
        search_query=q,
        city_filter=city_filter,
        brand_filter=brand_filter,
        min_price=min_price,
        max_price=max_price)


# --------- REELS ---------
@app.route('/reels')
def reels():
    reels_list = Reel.query.order_by(Reel.created_at.desc()).all()
    return render_template('reels.html', reels=reels_list)


@app.route('/reels/add', methods=['GET', 'POST'])
@login_required
def add_reel():
    if not current_user.email_verified:
        flash('تکایە ئیمەیلەکەت پشتڕاست بکەرەوە.', 'warning')
        return redirect(url_for('verify_email_page'))
    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        video_url = None
        thumbnail_url = None
        if 'video_file' in request.files and request.files['video_file'].filename:
            f = request.files['video_file']
            if allowed_file(f.filename, ALLOWED_VIDEO_EXT):
                video_url = save_file(f, current_user.id, 'reel_')
            else:
                flash('جۆری ڤیدۆ ڕێگەپێدراو نییە.', 'danger')
                return redirect(request.url)
        if 'thumb_file' in request.files and request.files['thumb_file'].filename:
            tf = request.files['thumb_file']
            if allowed_file(tf.filename, ALLOWED_IMAGE_EXT):
                thumbnail_url = save_file(tf, current_user.id, 'thumb_')
        if not video_url:
            flash('تکایە ڤیدۆیەک بارکە.', 'danger')
            return redirect(request.url)
        reel = Reel(title=title, description=description, video_url=video_url,
                    thumbnail_url=thumbnail_url, owner_id=current_user.id)
        db.session.add(reel)
        db.session.commit()
        flash('ریلەکەت بە سەرکەوتوویی زیاد کرا!', 'success')
        return redirect(url_for('reels'))
    return render_template('add_reel.html')


# ✅ FIX #3: لایکی پارێزراو — هەر IP جارێک
@app.route('/reel/<int:reel_id>/like', methods=['POST'])
def like_reel(reel_id):
    reel = db.session.get(Reel, reel_id)
    if not reel:
        return jsonify({'error': 'not found'}), 404
    ip = get_client_ip()
    existing = ReelLike.query.filter_by(reel_id=reel_id, ip_address=ip).first()
    if existing:
        return jsonify({'likes': reel.likes, 'already_liked': True})
    try:
        like = ReelLike(reel_id=reel_id, ip_address=ip)
        db.session.add(like)
        reel.likes += 1
        db.session.commit()
        return jsonify({'likes': reel.likes, 'already_liked': False})
    except Exception:
        db.session.rollback()
        return jsonify({'likes': reel.likes, 'already_liked': True})


@app.route('/reel/<int:reel_id>/view', methods=['POST'])
def view_reel(reel_id):
    reel = db.session.get(Reel, reel_id)
    if reel:
        reel.views += 1
        db.session.commit()
        return jsonify({'views': reel.views})
    return jsonify({'error': 'not found'}), 404


# --------- PLANS — با VIP پارەدان لازمە ---------
@app.route('/plans')
def plans():
    s = get_settings()
    return render_template('plans.html', settings=s)


# ✅ FIX #1: VIP گواستنەوە — دیمۆ لابرا، ئێستا پارەدان داواکراوە
@app.route('/plans/upgrade', methods=['POST'])
@login_required
def upgrade_vip():
    s = get_settings()
    # پێشنیار: ئەم پەیجە بگۆڕە بۆ پارەدانی ڕاستەقینە (Zaincash/FastPay/Stripe)
    # ئێستا admin دەتوانێت دەستی بگۆڕێت لە /admin
    flash(f'بۆ چالاککردنی VIP، تکایە {s.vip_price_usd}$ بنێرە بۆ ژمارەی Zaincash کە لە پانێلی Admin دیاره. پاشان screenshot بنێرە بۆ ئەدمین.', 'warning')
    return redirect(url_for('plans'))


# --------- PART DETAIL — بە Part.views ---------
@app.route('/part/<int:part_id>')
def part_detail(part_id):
    part = db.session.get(Part, part_id)
    if not part:
        return render_template('404.html'), 404
    # ✅ FIX #6: Part.views زیاد دەکەین
    part.views = (part.views or 0) + 1
    db.session.commit()
    return render_template('part_detail.html', part=part)


# --------- SELLER PROFILE — buyer دەبینرێت ---------
@app.route('/seller/<int:user_id>')
def seller_profile(user_id):
    seller = db.session.get(User, user_id)
    # ✅ FIX #7: buyer user_type دەبینرێت
    if not seller or seller.user_type not in ('seller', 'admin', 'buyer'):
        return redirect(url_for('index'))
    parts = Part.query.filter_by(seller_id=seller.id).order_by(Part.created_at.desc()).all()
    return render_template('seller_profile.html', seller=seller, parts=parts)


# --------- EDIT PROFILE — وێنەی پرۆفایل ---------
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.whatsapp = request.form.get('whatsapp', current_user.whatsapp)
        current_user.telegram = request.form.get('telegram', current_user.telegram).lstrip('@')
        current_user.city = request.form.get('city', current_user.city)
        # ✅ FIX #4: وێنەی پرۆفایل
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            f = request.files['profile_image']
            if allowed_file(f.filename, ALLOWED_IMAGE_EXT):
                current_user.profile_image = save_file(f, current_user.id, 'avatar_')
            else:
                flash('جۆری وێنە ڕێگەپێدراو نییە.', 'danger')
                return redirect(request.url)
        db.session.commit()
        flash('پرۆفایلەکەت نوێ کرایەوە!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html', cities=IRAQ_CITIES)


# --------- AUTH ---------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user_type = request.form['user_type']
        phone = request.form.get('phone', '')
        whatsapp = request.form.get('whatsapp', '')
        telegram = request.form.get('telegram', '').lstrip('@')
        city = request.form.get('city', '')

        if User.query.filter_by(username=username).first():
            flash('ئەم ناوە پێشتر تۆمار کراوە!', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('ئەم ئیمەیلە پێشتر تۆمار کراوە!', 'danger')
            return redirect(url_for('register'))

        s = get_settings()
        otp = generate_otp()
        user = User(
            username=username, email=email,
            password=generate_password_hash(password),
            user_type=user_type, phone=phone,
            whatsapp=whatsapp, telegram=telegram, city=city,
            otp_code=otp,
            otp_expires=datetime.utcnow() + timedelta(minutes=10),
            free_img_limit=s.default_free_img_limit,
            free_vid_limit=s.default_free_vid_limit,
        )
        db.session.add(user)
        db.session.commit()

        sent = send_otp_email(email, otp)
        session['pending_user_id'] = user.id
        if sent:
            flash(t('otp_sent'), 'info')
        else:
            flash(f'کۆدی پشتڕاستکردنەوەت: {otp} (ئیمەیل نەدۆزرایەوە)', 'warning')
        return redirect(url_for('verify_email_page'))
    return render_template('register.html', cities=IRAQ_CITIES)


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email_page():
    user_id = session.get('pending_user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('register'))
    if request.method == 'POST':
        code = request.form.get('otp', '').strip()
        if user.otp_code == code and user.otp_expires and datetime.utcnow() < user.otp_expires:
            user.email_verified = True
            user.otp_code = None
            db.session.commit()
            session.pop('pending_user_id', None)
            login_user(user)
            flash(t('email_verified'), 'success')
            return redirect(url_for('dashboard' if user.user_type == 'seller' else 'index'))
        else:
            flash(t('invalid_otp'), 'danger')
    return render_template('verify_email.html', email=user.email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['username'].strip()
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()
        if user and check_password_hash(user.password, request.form['password']):
            if not user.is_active_account:
                flash('ئەکاونتەکەت لەلایەن ئەدمینەوە بەندکراوە.', 'danger')
                return redirect(url_for('login'))
            if not user.email_verified:
                session['pending_user_id'] = user.id
                otp = generate_otp()
                user.otp_code = otp
                user.otp_expires = datetime.utcnow() + timedelta(minutes=10)
                db.session.commit()
                sent = send_otp_email(user.email, otp)
                if sent:
                    flash(t('otp_sent'), 'info')
                else:
                    flash(f'OTP: {otp}', 'warning')
                return redirect(url_for('verify_email_page'))
            login_user(user)
            flash(f'{t("welcome")} {user.username}!', 'success')
            if user.user_type == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard' if user.user_type == 'seller' else 'index'))
        flash('ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە!', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# --------- DASHBOARD ---------
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'admin':
        return redirect(url_for('admin_panel'))
    if current_user.user_type not in ('seller', 'buyer'):
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    parts_paginated = Part.query.filter_by(seller_id=current_user.id)\
        .order_by(Part.created_at.desc()).paginate(page=page, per_page=6, error_out=False)
    img_count = count_monthly_uploads(current_user.id, 'image')
    vid_count = count_monthly_uploads(current_user.id, 'video')
    vip = is_vip_active(current_user)
    return render_template('dashboard.html',
        parts=parts_paginated.items, pagination=parts_paginated,
        img_count=img_count, vid_count=vid_count, vip=vip)


# --------- ADD / EDIT / DELETE PART ---------
@app.route('/add_part', methods=['GET', 'POST'])
@login_required
def add_part():
    if current_user.user_type != 'seller':
        return redirect(url_for('index'))
    if not current_user.email_verified:
        flash('تکایە ئیمەیلەکەت پشتڕاست بکەرەوە.', 'warning')
        return redirect(url_for('verify_email_page'))

    if request.method == 'POST':
        name = request.form['name']
        car_model = request.form['car_model']
        car_brand = request.form.get('car_brand', '')
        description = request.form['description']
        city = request.form.get('city', '')
        try:
            price = float(request.form['price'])
            if price < 0:
                raise ValueError
        except ValueError:
            flash('تکایە نرخێکی درووست بنووسە!', 'danger')
            return redirect(request.url)

        vip = is_vip_active(current_user)
        img_count = count_monthly_uploads(current_user.id, 'image')
        vid_count = count_monthly_uploads(current_user.id, 'video')
        img_limit = current_user.free_img_limit
        vid_limit = current_user.free_vid_limit

        image_url = None
        media_type = 'image'

        if 'image_file' in request.files and request.files['image_file'].filename:
            f = request.files['image_file']
            if not vip and img_count >= img_limit:
                flash(f'پلانی خۆڕای تەنها {img_limit} وێنە لە مانگێکدا ڕێ دەدات. VIP بخرە!', 'warning')
                return redirect(request.url)
            if allowed_file(f.filename, ALLOWED_IMAGE_EXT):
                image_url = save_file(f, current_user.id)
                media_type = 'image'
            else:
                flash('جۆری وێنە ڕێگەپێدراو نییە.', 'danger')
                return redirect(request.url)
        elif 'video_file' in request.files and request.files['video_file'].filename:
            f = request.files['video_file']
            if not vip and vid_count >= vid_limit:
                flash(f'پلانی خۆڕای تەنها {vid_limit} ڤیدۆ لە مانگێکدا ڕێ دەدات. VIP بخرە!', 'warning')
                return redirect(request.url)
            if allowed_file(f.filename, ALLOWED_VIDEO_EXT):
                image_url = save_file(f, current_user.id, 'vid_')
                media_type = 'video'
            else:
                flash('جۆری ڤیدۆ ڕێگەپێدراو نییە.', 'danger')
                return redirect(request.url)
        elif request.form.get('image_url'):
            raw = request.form['image_url']
            if not re.match(r'^https?://', raw, re.I):
                flash('ئادرەسی وێنەکە درووست نییە.', 'danger')
                return redirect(request.url)
            image_url = raw

        part = Part(name=name, car_model=car_model, car_brand=car_brand,
                    description=description, price=price, city=city,
                    image_url=image_url, media_type=media_type,
                    seller_id=current_user.id)
        db.session.add(part)
        db.session.commit()
        flash('پارچەکەت بە سەرکەوتوویی زیاد کرا!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_part.html', cities=IRAQ_CITIES, brands=CAR_BRANDS)


@app.route('/edit_part/<int:part_id>', methods=['GET', 'POST'])
@login_required
def edit_part(part_id):
    part = db.session.get(Part, part_id)
    if not part or part.seller_id != current_user.id:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        part.name = request.form['name']
        part.car_model = request.form['car_model']
        part.car_brand = request.form.get('car_brand', '')
        part.description = request.form['description']
        part.city = request.form.get('city', '')
        try:
            part.price = float(request.form['price'])
        except Exception:
            flash('نرخی هەڵە!', 'danger')
            return redirect(request.url)
        if 'image_file' in request.files and request.files['image_file'].filename:
            f = request.files['image_file']
            if allowed_file(f.filename, ALLOWED_IMAGE_EXT):
                part.image_url = save_file(f, current_user.id)
                part.media_type = 'image'
        elif request.form.get('image_url'):
            part.image_url = request.form['image_url']
        db.session.commit()
        flash('پارچەکەت نوێ کرایەوە!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_part.html', part=part, cities=IRAQ_CITIES, brands=CAR_BRANDS)


@app.route('/delete_part/<int:part_id>', methods=['POST'])
@login_required
def delete_part(part_id):
    part = db.session.get(Part, part_id)
    if part and part.seller_id == current_user.id:
        db.session.delete(part)
        db.session.commit()
        flash('پارچەکەت سڕایەوە.', 'info')
    return redirect(url_for('dashboard'))


# =========================================================
# ADMIN PANEL
# =========================================================
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    total_parts = Part.query.count()
    total_reels = Reel.query.count()
    s = get_settings()
    return render_template('admin.html', users=users,
        total_parts=total_parts, total_reels=total_reels, settings=s)


@app.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user(user_id):
    user = db.session.get(User, user_id)
    if user and user.user_type != 'admin':
        user.is_active_account = not user.is_active_account
        db.session.commit()
        flash(f'بەکارهێنەر {"چالاک" if user.is_active_account else "بەندکرا"}.', 'success')
    return redirect(url_for('admin_panel'))


# ✅ ADMIN: دەتوانێت VIP دەستی بدات بعد پشتڕاستکردنەوەی پارەدان
@app.route('/admin/user/<int:user_id>/grant_vip', methods=['POST'])
@login_required
@admin_required
def admin_grant_vip(user_id):
    user = db.session.get(User, user_id)
    s = get_settings()
    if user:
        user.plan = 'vip'
        user.plan_expires = datetime.utcnow() + timedelta(days=30 * s.vip_months)
        db.session.commit()
        flash(f'VIP بۆ {user.username} چالاک کرا ({s.vip_months} مانگ).', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:user_id>/set_limits', methods=['POST'])
@login_required
@admin_required
def admin_set_limits(user_id):
    user = db.session.get(User, user_id)
    if user:
        try:
            user.free_img_limit = int(request.form.get('img_limit', 3))
            user.free_vid_limit = int(request.form.get('vid_limit', 2))
            db.session.commit()
            flash(f'حدی {user.username} نوێکرایەوە.', 'success')
        except Exception:
            flash('هەڵە!', 'danger')
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = db.session.get(User, user_id)
    if user and user.user_type != 'admin':
        Part.query.filter_by(seller_id=user.id).delete()
        Reel.query.filter_by(owner_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('بەکارهێنەر سڕایەوە.', 'info')
    return redirect(url_for('admin_panel'))


@app.route('/admin/settings', methods=['POST'])
@login_required
@admin_required
def admin_settings():
    s = get_settings()
    try:
        s.default_free_img_limit = int(request.form.get('default_img', 3))
        s.default_free_vid_limit = int(request.form.get('default_vid', 2))
        s.vip_price_usd = int(request.form.get('vip_price', 25))
        s.vip_months = int(request.form.get('vip_months', 6))
        db.session.commit()
        flash('ڕێکخستنەکان پاشەکەوت کران!', 'success')
    except Exception:
        flash('هەڵە!', 'danger')
    return redirect(url_for('admin_panel'))


# --------- ERRORS ---------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    logger.error(f"Server error: {e}", exc_info=True)
    return render_template('500.html'), 500


if __name__ == '__main__':
    create_tables()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
