import pytest
import json
from app import app, db, Car, Inquiry

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    res = client.get('/')
    assert res.status_code == 200

def test_inventory_loads(client):
    res = client.get('/inventory')
    assert res.status_code == 200

def test_car_detail_loads(client):
    res = client.get('/car/1')
    assert res.status_code == 200

def test_car_detail_404(client):
    res = client.get('/car/99999')
    assert res.status_code == 404

def test_api_cars_returns_json(client):
    res = client.get('/api/cars')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert isinstance(data, list)

def test_api_cars_has_required_fields(client):
    res = client.get('/api/cars')
    data = json.loads(res.data)
    if data:
        car = data[0]
        assert 'id' in car
        assert 'make' in car
        assert 'model' in car
        assert 'price' in car

def test_inquiry_post_valid(client):
    res = client.post('/inquiry', data={
        'car_id': 1,
        'name': 'Test Buyer',
        'phone': '0712345678',
        'email': 'test@example.com',
        'inquiry_type': 'general',
        'message': 'Test message'
    })
    assert res.status_code in [200, 302]

def test_admin_redirects_without_login(client):
    res = client.get('/admin')
    assert res.status_code == 302

def test_admin_login_page_loads(client):
    res = client.get('/admin/login')
    assert res.status_code == 200

def test_admin_login_wrong_password(client):
    res = client.post('/admin/login', data={
        'password': 'wrongpassword'
    })
    assert res.status_code == 200

def test_admin_add_car_redirects_without_login(client):
    res = client.get('/admin/cars/add')
    assert res.status_code == 302

def test_financing_calculation():
    price = 3800000
    deposit = 0.30
    months = 48
    annual_rate = 0.14
    principal = price * (1 - deposit)
    monthly_rate = annual_rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    assert payment > 0
    assert round(payment) == 72688