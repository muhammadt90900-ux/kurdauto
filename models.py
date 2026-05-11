# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

IRAQ_CITIES = [
    'هەولێر', 'سلێمانی', 'دهۆک', 'کەرکووک', 'هەڵەبجە',
    'بغداد', 'موسڵ', 'بەسرە', 'نەجەف', 'کەربەلا',
    'تکریت', 'کووت', 'دیالە', 'ڕامادی', 'فەلووجە',
    'سامەڕا', 'بابیل', 'دیوانیە', 'عەماره', 'ناسریه'
]

CAR_BRANDS = [
    'Toyota', 'Kia', 'Hyundai', 'BMW', 'Mercedes-Benz',
    'Volkswagen', 'Audi', 'Honda', 'Nissan', 'Chevrolet',
    'Ford', 'Mitsubishi', 'Suzuki', 'Mazda', 'Peugeot',
    'Renault', 'Land Rover', 'Jeep', 'Lexus', 'Isuzu',
    'Opel', 'Dodge', 'Porsche', 'Volvo', 'Subaru',
    'Infiniti', 'Cadillac', 'Chrysler', 'GMC', 'Hummer',
    'BYD', 'Chery', 'Geely', 'MG', 'Haval',
    'JAC', 'Changan', 'BAIC', 'Lifan', 'Brilliance',
    'Daihatsu', 'Fiat', 'Alfa Romeo', 'Ferrari', 'Lamborghini',
    'Maserati', 'Bentley', 'Rolls-Royce', 'Aston Martin', 'McLaren'
]

CAR_BRAND_LOGOS = {
    'Toyota':        'https://logo.clearbit.com/toyota.com',
    'Kia':           'https://logo.clearbit.com/kia.com',
    'Hyundai':       'https://logo.clearbit.com/hyundai.com',
    'BMW':           'https://logo.clearbit.com/bmw.com',
    'Mercedes-Benz': 'https://logo.clearbit.com/mercedes-benz.com',
    'Volkswagen':    'https://logo.clearbit.com/vw.com',
    'Audi':          'https://logo.clearbit.com/audi.com',
    'Honda':         'https://logo.clearbit.com/honda.com',
    'Nissan':        'https://logo.clearbit.com/nissan.com',
    'Chevrolet':     'https://logo.clearbit.com/chevrolet.com',
    'Ford':          'https://logo.clearbit.com/ford.com',
    'Mitsubishi':    'https://logo.clearbit.com/mitsubishi.com',
    'Suzuki':        'https://logo.clearbit.com/suzuki.com',
    'Mazda':         'https://logo.clearbit.com/mazda.com',
    'Peugeot':       'https://logo.clearbit.com/peugeot.com',
    'Renault':       'https://logo.clearbit.com/renault.com',
    'Land Rover':    'https://logo.clearbit.com/landrover.com',
    'Jeep':          'https://logo.clearbit.com/jeep.com',
    'Lexus':         'https://logo.clearbit.com/lexus.com',
    'Isuzu':         'https://logo.clearbit.com/isuzu.com',
    'Opel':          'https://logo.clearbit.com/opel.com',
    'Dodge':         'https://logo.clearbit.com/dodge.com',
    'Porsche':       'https://logo.clearbit.com/porsche.com',
    'Volvo':         'https://logo.clearbit.com/volvocars.com',
    'Subaru':        'https://logo.clearbit.com/subaru.com',
    'Infiniti':      'https://logo.clearbit.com/infiniti.com',
    'Cadillac':      'https://logo.clearbit.com/cadillac.com',
    'Chrysler':      'https://logo.clearbit.com/chrysler.com',
    'GMC':           'https://logo.clearbit.com/gmc.com',
    'BYD':           'https://logo.clearbit.com/byd.com',
    'Chery':         'https://logo.clearbit.com/chery.net',
    'Geely':         'https://logo.clearbit.com/geely.com',
    'MG':            'https://logo.clearbit.com/mgmotor.com',
    'Haval':         'https://logo.clearbit.com/haval.com',
    'Hummer':        'https://logo.clearbit.com/hummer.com',
    'Fiat':          'https://logo.clearbit.com/fiat.com',
    'Alfa Romeo':    'https://logo.clearbit.com/alfaromeo.com',
    'Ferrari':       'https://logo.clearbit.com/ferrari.com',
    'Lamborghini':   'https://logo.clearbit.com/lamborghini.com',
    'Maserati':      'https://logo.clearbit.com/maserati.com',
    'Bentley':       'https://logo.clearbit.com/bentley.com',
    'Rolls-Royce':   'https://logo.clearbit.com/rolls-roycemotorcars.com',
}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # seller / buyer / admin
    phone = db.Column(db.String(20), default='')
    whatsapp = db.Column(db.String(20), default='')
    telegram = db.Column(db.String(80), default='')
    city = db.Column(db.String(50), default='')
    profile_image = db.Column(db.String(300), nullable=True)
    plan = db.Column(db.String(10), default='free')
    plan_expires = db.Column(db.DateTime, nullable=True)
    free_img_limit = db.Column(db.Integer, default=3)
    free_vid_limit = db.Column(db.Integer, default=2)
    email_verified = db.Column(db.Boolean, default=False)
    is_active_account = db.Column(db.Boolean, default=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parts = db.relationship('Part', backref='seller', lazy=True)
    reels = db.relationship('Reel', backref='owner', lazy=True)
    # چات
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    # ئاگادارکردنەوە
    notifications = db.relationship('Notification', backref='user', lazy=True)


class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    car_model = db.Column(db.String(80))
    car_brand = db.Column(db.String(80), default='')
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(50), default='')
    image_url = db.Column(db.String(300))
    media_type = db.Column(db.String(10), default='image')
    condition = db.Column(db.String(20), default='used')  # new / used
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # نرخدان
    reviews = db.relationship('Review', backref='part', lazy=True)

    @property
    def avg_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)


class Reel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    video_url = db.Column(db.String(300), nullable=False)
    thumbnail_url = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class ReelLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reel_id = db.Column(db.Integer, db.ForeignKey('reel.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('reel_id', 'ip_address', name='uq_reel_ip'),)


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    default_free_img_limit = db.Column(db.Integer, default=3)
    default_free_vid_limit = db.Column(db.Integer, default=2)
    vip_price_usd = db.Column(db.Integer, default=25)
    vip_months = db.Column(db.Integer, default=6)


# ═══════════════════════════════════════════════
# 💬 چات و پەیام
# ═══════════════════════════════════════════════
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def time_ago(self):
        diff = datetime.utcnow() - self.created_at
        if diff.seconds < 60:
            return 'ئێستا'
        elif diff.seconds < 3600:
            return f'{diff.seconds // 60} خولەک'
        elif diff.seconds < 86400:
            return f'{diff.seconds // 3600} کاتژمێر'
        else:
            return f'{diff.days} ڕۆژ'


# ═══════════════════════════════════════════════
# ⭐ نرخدان و کۆمێنت
# ═══════════════════════════════════════════════
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='reviews')
    __table_args__ = (db.UniqueConstraint('part_id', 'user_id', name='uq_part_user_review'),)


# ═══════════════════════════════════════════════
# 🔔 ئاگادارکردنەوە
# ═══════════════════════════════════════════════
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notif_type = db.Column(db.String(30), default='info')  # info / message / review / system
    link = db.Column(db.String(300), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
