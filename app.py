import atexit
import os
import uuid
import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
from posthog import Posthog

load_dotenv()
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment=os.getenv('FLASK_ENV', 'development')
)

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from posthog import Posthog


posthog_client = Posthog(
    os.getenv('POSTHOG_PROJECT_TOKEN', ''),
    host=os.getenv('POSTHOG_HOST', 'https://eu.i.posthog.com'),
    enable_exception_autocapture=True,
)
atexit.register(posthog_client.shutdown)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dealership.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
app.config['POSTHOG_PROJECT_TOKEN'] = os.getenv('POSTHOG_PROJECT_TOKEN', '')
app.config['POSTHOG_HOST'] = os.getenv('POSTHOG_HOST', 'https://eu.i.posthog.com')

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "5000 per hour"]
)

def get_distinct_id():
    if 'distinct_id' not in session:
        session['distinct_id'] = str(uuid.uuid4())
    return session['distinct_id']

@app.errorhandler(Exception)
def handle_exception(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    import sentry_sdk
    sentry_sdk.capture_exception(e)
    posthog_client.capture_exception(e)
    return '<h1>500 — Server Error</h1><p>Something went wrong. We\'ve been notified.</p>', 500
import json as _json

@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return _json.loads(value) if value else []
    except:
        return []

# ─── MODELS ───────────────────────────────────────────────────────────────────

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # in KES
    mileage = db.Column(db.Integer, nullable=False)  # in km
    fuel_type = db.Column(db.String(20), nullable=False)  # Petrol, Diesel, Hybrid, Electric
    transmission = db.Column(db.String(20), nullable=False)  # Automatic, Manual
    body_type = db.Column(db.String(30), nullable=False)  # Sedan, SUV, Hatchback, Pickup, Van
    color = db.Column(db.String(30), nullable=False)
    engine_cc = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    features = db.Column(db.Text, nullable=True)  # JSON string
    images = db.Column(db.Text, nullable=True)    # JSON string of image URLs
    is_featured = db.Column(db.Boolean, default=False)
    is_sold = db.Column(db.Boolean, default=False)
    condition = db.Column(db.String(20), default='Used')  # New, Used, Certified
    import_country = db.Column(db.String(30), nullable=True)  # Japan, UK, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'price': self.price,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'body_type': self.body_type,
            'color': self.color,
            'engine_cc': self.engine_cc,
            'description': self.description,
            'features': json.loads(self.features) if self.features else [],
            'images': json.loads(self.images) if self.images else [],
            'is_featured': self.is_featured,
            'is_sold': self.is_sold,
            'condition': self.condition,
            'import_country': self.import_country,
        }

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=True)
    inquiry_type = db.Column(db.String(30), default='general')  # general, test_drive, financing
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    car = db.relationship('Car', backref='inquiries')

# ─── SEED DATA ────────────────────────────────────────────────────────────────

def seed_cars():
    if Car.query.count() > 0:
        return
    cars = [
        Car(make='Toyota', model='Land Cruiser Prado', year=2019, price=7500000,
            mileage=52000, fuel_type='Diesel', transmission='Automatic',
            body_type='SUV', color='Pearl White', engine_cc=2800,
            condition='Used', import_country='Japan', is_featured=True,
            description='Immaculate Prado TX in pristine condition. Full-time 4WD, leather seats, factory navigation. One owner, full service history available. Perfect for both city driving and off-road excursions.',
            features=json.dumps(['4WD', 'Leather Seats', 'Sunroof', 'Navigation', 'Reverse Camera', 'Bluetooth', 'Cruise Control', 'Keyless Entry']),
            images=json.dumps(['https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=800&q=80'])),

        Car(make='Toyota', model='Axio', year=2017, price=1650000,
            mileage=78000, fuel_type='Petrol', transmission='Automatic',
            body_type='Sedan', color='Silver', engine_cc=1500,
            condition='Used', import_country='Japan', is_featured=True,
            description='Reliable and fuel-efficient Axio hybrid. Perfect for daily commuting in Nairobi. Low fuel consumption at 18km/L. Recently serviced with new tyres.',
            features=json.dumps(['Hybrid Engine', 'Fuel Efficient', 'ABS', 'Airbags', 'Electric Windows', 'Central Locking', 'Bluetooth']),
            images=json.dumps(['https://images.unsplash.com/photo-1590362891991-f776e747a588?w=800&q=80'])),

        Car(make='Mazda', model='CX-5', year=2020, price=3800000,
            mileage=31000, fuel_type='Petrol', transmission='Automatic',
            body_type='SUV', color='Soul Red', engine_cc=2000,
            condition='Used', import_country='Japan', is_featured=True,
            description='Stunning Soul Red CX-5 with i-Activ AWD. Near-new condition with only 31,000km. Full Mazda service history. Heads-up display, Bose audio, 360 camera system.',
            features=json.dumps(['AWD', 'Heads-Up Display', 'Bose Audio', '360 Camera', 'Lane Assist', 'Blind Spot Monitor', 'Heated Seats', 'Apple CarPlay']),
            images=json.dumps(['https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&q=80'])),

        Car(make='Mercedes-Benz', model='C200', year=2018, price=5200000,
            mileage=45000, fuel_type='Petrol', transmission='Automatic',
            body_type='Sedan', color='Obsidian Black', engine_cc=1991,
            condition='Used', import_country='Germany',
            description='Executive C200 AMG Line in impeccable condition. Full Mercedes service history from authorized dealer. Panoramic sunroof, Burmester sound system, ambient lighting.',
            features=json.dumps(['AMG Line', 'Panoramic Sunroof', 'Burmester Audio', 'Ambient Lighting', 'Memory Seats', 'Parking Sensors', 'Wireless Charging']),
            images=json.dumps(['https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=800&q=80'])),

        Car(make='Subaru', model='Forester', year=2018, price=2900000,
            mileage=61000, fuel_type='Petrol', transmission='Automatic',
            body_type='SUV', color='Dark Blue', engine_cc=2000,
            condition='Used', import_country='Japan',
            description='EyeSight equipped Forester XT Turbo. Subaru\'s legendary AWD with active safety suite. Great for upcountry travel and Nairobi traffic alike.',
            features=json.dumps(['EyeSight Safety', 'Turbo Engine', 'Symmetrical AWD', 'Heated Seats', 'Panoramic Sunroof', 'Push Start', 'Reverse Camera']),
            images=json.dumps(['https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&q=80'])),

        Car(make='Toyota', model='Hilux Double Cab', year=2021, price=5900000,
            mileage=28000, fuel_type='Diesel', transmission='Manual',
            body_type='Pickup', color='Graphite', engine_cc=2800,
            condition='Used', import_country='Japan', is_featured=True,
            description='2021 Hilux GD-6 Revo in near-showroom condition. The workhorse that never lets you down. Ideal for business use or weekend adventures. 4x4 with diff-lock.',
            features=json.dumps(['4x4', 'Diff Lock', 'Tow Bar', 'Canopy Ready', 'ABS+EBD', 'Airbags x6', 'Rear Camera', 'Apple CarPlay']),
            images=json.dumps(['https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80'])),

        Car(make='Honda', model='Vezel', year=2019, price=2450000,
            mileage=42000, fuel_type='Hybrid', transmission='Automatic',
            body_type='SUV', color='Passion Red', engine_cc=1500,
            condition='Used', import_country='Japan',
            description='Popular Honda Vezel Hybrid RS in sporty Passion Red. Excellent fuel economy, spacious interior. Honda Sensing safety package included.',
            features=json.dumps(['Hybrid', 'Honda Sensing', 'Lane Watch', 'Collision Mitigation', 'LED Headlights', 'Touchscreen', 'USB Ports x4']),
            images=json.dumps(['https://images.unsplash.com/photo-1581362072978-14998d01fdaa?w=800&q=80'])),

        Car(make='BMW', model='X3 xDrive20d', year=2019, price=6100000,
            mileage=38000, fuel_type='Diesel', transmission='Automatic',
            body_type='SUV', color='Alpine White', engine_cc=1995,
            condition='Used', import_country='UK',
            description='G01 X3 xDrive in executive trim. Live Cockpit Professional, Harman Kardon, panoramic glass roof. One careful owner, full BMW service history verified.',
            features=json.dumps(['xDrive AWD', 'Live Cockpit Pro', 'Harman Kardon', 'Panoramic Roof', 'Driving Assistant', 'Head-Up Display', 'Gesture Control']),
            images=json.dumps(['https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80'])),
    ]
    for car in cars:
        db.session.add(car)
    db.session.commit()

# ─── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    featured = Car.query.filter_by(is_featured=True, is_sold=False).limit(4).all()
    total_cars = Car.query.filter_by(is_sold=False).count()
    makes = db.session.query(Car.make).distinct().all()
    makes = [m[0] for m in makes]
    return render_template('index.html', featured=featured, total_cars=total_cars, makes=makes)

@app.route('/inventory')
def inventory():
    page = request.args.get('page', 1, type=int)
    make = request.args.get('make', '')
    body_type = request.args.get('body_type', '')
    fuel_type = request.args.get('fuel_type', '')
    transmission = request.args.get('transmission', '')
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 99999999, type=int)
    min_year = request.args.get('min_year', 2000, type=int)
    max_year = request.args.get('max_year', 2025, type=int)
    sort = request.args.get('sort', 'newest')

    query = Car.query.filter_by(is_sold=False)
    if make: query = query.filter(Car.make == make)
    if body_type: query = query.filter(Car.body_type == body_type)
    if fuel_type: query = query.filter(Car.fuel_type == fuel_type)
    if transmission: query = query.filter(Car.transmission == transmission)
    query = query.filter(Car.price >= min_price, Car.price <= max_price)
    query = query.filter(Car.year >= min_year, Car.year <= max_year)

    if sort == 'price_asc': query = query.order_by(Car.price.asc())
    elif sort == 'price_desc': query = query.order_by(Car.price.desc())
    elif sort == 'year_desc': query = query.order_by(Car.year.desc())
    else: query = query.order_by(Car.created_at.desc())

    cars = query.paginate(page=page, per_page=9, error_out=False)
    makes = [m[0] for m in db.session.query(Car.make).distinct().all()]
    filters_active = any([make, body_type, fuel_type, transmission,
                          min_price > 0, max_price < 99999999,
                          min_year > 2000, max_year < 2025, sort != 'newest'])
    if filters_active:
        posthog_client.capture(
            get_distinct_id(),
            'inventory_searched',
            properties={
                'make': make or None,
                'body_type': body_type or None,
                'fuel_type': fuel_type or None,
                'transmission': transmission or None,
                'sort': sort,
                'result_count': cars.total,
            }
        )
    return render_template('inventory.html', cars=cars, makes=makes,
                           filters={'make': make, 'body_type': body_type,
                                    'fuel_type': fuel_type, 'transmission': transmission,
                                    'min_price': min_price, 'max_price': max_price,
                                    'min_year': min_year, 'max_year': max_year, 'sort': sort})

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    similar = Car.query.filter(
        Car.body_type == car.body_type,
        Car.id != car.id,
        Car.is_sold == False
    ).limit(3).all()
    posthog_client.capture(
        get_distinct_id(),
        'car_detail_viewed',
        properties={
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'body_type': car.body_type,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'condition': car.condition,
            'is_featured': car.is_featured,
        }
    )
    return render_template('car_detail.html', car=car, similar=similar)

@app.route('/inquiry', methods=['POST'])
@limiter.limit("5 per minute")
@csrf.exempt
def submit_inquiry():
    data = request.form
    name = data.get('name')
    phone = data.get('phone')
    if not name or not phone:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Name and phone are required.'}), 400
        flash('Name and phone are required.', 'error')
        return redirect(request.referrer or url_for('index'))
    inquiry = Inquiry(
        car_id=data.get('car_id', type=int),
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        message=data.get('message'),
        inquiry_type=data.get('inquiry_type', 'general')
    )
    db.session.add(inquiry)
    db.session.commit()
    posthog_client.capture(
        get_distinct_id(),
        'inquiry_submitted',
        properties={
            'inquiry_type': inquiry.inquiry_type,
            'has_car_id': inquiry.car_id is not None,
            'has_message': bool(inquiry.message and inquiry.message.strip()),
        }
    )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Inquiry received. We\'ll call you within 2 hours.'})
    flash('Your inquiry has been received. We\'ll contact you within 2 hours.', 'success')
    return redirect(url_for('car_detail', car_id=data.get('car_id')) if data.get('car_id') else url_for('index'))

@app.route('/api/cars')
def api_cars():
    cars = Car.query.filter_by(is_sold=False).all()
    return jsonify([c.to_dict() for c in cars])

# ─── ADMIN ROUTES ──────────────────────────────────────────────────────────────



@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    cars = Car.query.order_by(Car.created_at.desc()).all()
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(10).all()
    unread = Inquiry.query.filter_by(is_read=False).count()
    stats = {
        'total': Car.query.count(),
        'available': Car.query.filter_by(is_sold=False).count(),
        'sold': Car.query.filter_by(is_sold=True).count(),
        'inquiries': Inquiry.query.count(),
        'unread': unread
    }
    return render_template('admin/dashboard.html', cars=cars, inquiries=inquiries, stats=stats)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '').encode()
        stored_hash = os.getenv('ADMIN_PASSWORD_HASH', '').encode()
        if stored_hash and bcrypt.checkpw(password, stored_hash):
            session['admin'] = True
            posthog_client.capture('admin', 'admin_logged_in')
            return redirect(url_for('admin'))
        flash('Incorrect password.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/cars/add', methods=['GET', 'POST'])
def admin_add_car():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        f = request.form
        features = [x.strip() for x in f.get('features', '').split('\n') if x.strip()]
        images = [x.strip() for x in f.get('images', '').split('\n') if x.strip()]
        car = Car(
            make=f['make'], model=f['model'], year=int(f['year']),
            price=int(f['price']), mileage=int(f['mileage']),
            fuel_type=f['fuel_type'], transmission=f['transmission'],
            body_type=f['body_type'], color=f['color'],
            engine_cc=int(f.get('engine_cc') or 0) or None,
            description=f.get('description'), condition=f.get('condition', 'Used'),
            import_country=f.get('import_country'),
            is_featured='is_featured' in f,
            features=json.dumps(features), images=json.dumps(images)
        )
        db.session.add(car)
        db.session.commit()
        posthog_client.capture(
            'admin',
            'car_listing_added',
            properties={
                'make': car.make,
                'body_type': car.body_type,
                'fuel_type': car.fuel_type,
                'condition': car.condition,
                'is_featured': car.is_featured,
            }
        )
        flash(f'{car.year} {car.make} {car.model} added successfully.', 'success')
        return redirect(url_for('admin'))
    return render_template('admin/car_form.html', car=None)

@app.route('/admin/cars/<int:car_id>/edit', methods=['GET', 'POST'])
def admin_edit_car(car_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        f = request.form
        features = [x.strip() for x in f.get('features', '').split('\n') if x.strip()]
        images = [x.strip() for x in f.get('images', '').split('\n') if x.strip()]
        was_sold_before = car.is_sold
        car.make = f['make']; car.model = f['model']; car.year = int(f['year'])
        car.price = int(f['price']); car.mileage = int(f['mileage'])
        car.fuel_type = f['fuel_type']; car.transmission = f['transmission']
        car.body_type = f['body_type']; car.color = f['color']
        car.engine_cc = int(f.get('engine_cc') or 0) or None
        car.description = f.get('description'); car.condition = f.get('condition', 'Used')
        car.import_country = f.get('import_country')
        car.is_featured = 'is_featured' in f
        car.is_sold = 'is_sold' in f
        car.features = json.dumps(features); car.images = json.dumps(images)
        db.session.commit()
        if not was_sold_before and car.is_sold:
            posthog_client.capture(
                'admin',
                'car_listing_marked_sold',
                properties={
                    'make': car.make,
                    'model': car.model,
                    'year': car.year,
                    'body_type': car.body_type,
                }
            )
        flash('Listing updated.', 'success')
        return redirect(url_for('admin'))
    return render_template('admin/car_form.html', car=car)

@app.route('/admin/cars/<int:car_id>/delete', methods=['POST'])
def admin_delete_car(car_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    car = Car.query.get_or_404(car_id)
    posthog_client.capture(
        'admin',
        'car_listing_deleted',
        properties={
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'body_type': car.body_type,
        }
    )
    db.session.delete(car)
    db.session.commit()
    flash('Listing deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/inquiries')
def admin_inquiries():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    Inquiry.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/inquiries.html', inquiries=inquiries)

@app.route('/sitemap.xml')
def sitemap():
    from flask import Response
    cars = Car.query.filter_by(is_sold=False).all()
    pages = []
    pages.append('https://www.apexmotors.co.ke/')
    pages.append('https://www.apexmotors.co.ke/inventory')
    for car in cars:
        pages.append(f'https://www.apexmotors.co.ke/car/{car.id}')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += f'  <url><loc>{page}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    from flask import Response
    txt = 'User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: https://www.apexmotors.co.ke/sitemap.xml'
    return Response(txt, mimetype='text/plain')

