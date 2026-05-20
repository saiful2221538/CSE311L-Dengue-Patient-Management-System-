from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'dengue-tracking-secret-key-2024'
CORS(app)

# Database Configuration for XAMPP MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/denguetrackingsystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Database Models
class Patient(db.Model):
    __tablename__ = 'Patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10), nullable=False)
    blood_type = db.Column(db.String(5))
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(15))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)


class Address(db.Model):
    __tablename__ = 'Addresses'
    address_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patients.patient_id'), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=True)


class DengueDetail(db.Model):
    __tablename__ = 'DengueDetails'
    dengue_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patients.patient_id'), unique=True, nullable=False)
    diagnosis_date = db.Column(db.Date, nullable=False)
    dengue_type = db.Column(db.String(50), nullable=False)
    severity_level = db.Column(db.String(20), nullable=False)
    infection_source = db.Column(db.String(20))
    travel_history = db.Column(db.Text)
    hospitalization_required = db.Column(db.Boolean, default=False)
    platelet_count = db.Column(db.Integer)
    outcome = db.Column(db.String(20), default='Under Treatment')


# Add missing models
class ContactTracing(db.Model):
    __tablename__ = 'ContactTracing'
    trace_id = db.Column(db.Integer, primary_key=True)
    infected_patient_id = db.Column(db.Integer, db.ForeignKey('Patients.patient_id'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(15))
    contact_relation = db.Column(db.String(50))
    exposure_date = db.Column(db.Date)
    exposure_location = db.Column(db.String(255))
    contact_status = db.Column(db.String(20), default='Monitored')


class LabTest(db.Model):
    __tablename__ = 'LabTests'
    test_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patients.patient_id'), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    test_result = db.Column(db.String(20), nullable=False)
    result_value = db.Column(db.String(50))
    normal_range = db.Column(db.String(50))
    lab_name = db.Column(db.String(200))


class DailyMonitoring(db.Model):
    __tablename__ = 'DailyMonitoring'
    monitor_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('Patients.patient_id'), nullable=False)
    monitor_date = db.Column(db.Date, nullable=False)
    temperature = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    platelet_count = db.Column(db.Integer)
    oxygen_saturation = db.Column(db.Float)
    pain_level = db.Column(db.Integer)
    nurse_notes = db.Column(db.Text)


class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))


# Serve the main application
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # For demo purposes
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'full_name': 'System Administrator',
                'role': 'Admin',
                'email': 'admin@dengue.gov'
            }
        })

    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    try:
        total_patients = Patient.query.count() or 0
        dengue_patients = DengueDetail.query.count() or 0
        critical_cases = DengueDetail.query.filter_by(severity_level='Critical').count() or 0

        # Get recent patients
        recent_patients = get_recent_patients()

        return jsonify({
            'total_patients': total_patients,
            'dengue_patients': dengue_patients,
            'active_cases': dengue_patients,
            'critical_cases': critical_cases,
            'recovered': 0,
            'hospitalized': 0,
            'today_cases': 0,
            'recent_patients': recent_patients
        })
    except:
        # Return demo data if database error
        return jsonify({
            'total_patients': 156,
            'dengue_patients': 123,
            'active_cases': 89,
            'critical_cases': 15,
            'recovered': 34,
            'hospitalized': 67,
            'today_cases': 8,
            'recent_patients': []
        })


@app.route('/api/patients', methods=['POST'])
def create_patient():
    try:
        data = request.get_json()
        print(f"Received patient data: {data}")

        # Calculate age
        dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # Create patient
        patient = Patient(
            national_id=data.get('national_id', f"NID{int(datetime.now().timestamp())}"),
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=dob,
            age=age,
            gender=data['gender'],
            blood_type=data.get('blood_type'),
            phone_number=data['phone_number'],
            email=data.get('email'),
            emergency_contact=data.get('emergency_contact')
        )
        db.session.add(patient)
        db.session.flush()

        # Add address
        address = Address(
            patient_id=patient.patient_id,
            street_address=data['address']['street_address'],
            city=data['address']['city'],
            district=data['address']['district'],
            division=data['address'].get('division'),
            is_primary=True
        )
        db.session.add(address)

        # Add dengue details
        dengue = DengueDetail(
            patient_id=patient.patient_id,
            diagnosis_date=datetime.strptime(data['dengue_details']['diagnosis_date'], '%Y-%m-%d'),
            dengue_type=data['dengue_details']['dengue_type'],
            severity_level=data['dengue_details']['severity_level'],
            infection_source=data['dengue_details'].get('infection_source'),
            travel_history=data['dengue_details'].get('travel_history'),
            platelet_count=data['dengue_details'].get('platelet_count'),
            hospitalization_required=data['dengue_details'].get('hospitalization_required', False),
            outcome='Under Treatment'
        )
        db.session.add(dengue)

        db.session.commit()

        print(f"Patient created with ID: {patient.patient_id}")
        return jsonify({
            'success': True,
            'patient_id': patient.patient_id,
            'message': 'Patient registered successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating patient: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        severity = request.args.get('severity', '')
        district = request.args.get('district', '')

        # Build query
        query = db.session.query(Patient, DengueDetail, Address) \
            .join(DengueDetail, Patient.patient_id == DengueDetail.patient_id) \
            .join(Address, Patient.patient_id == Address.patient_id) \
            .filter(Address.is_primary == True)

        if search:
            query = query.filter(
                (Patient.first_name.like(f'%{search}%')) |
                (Patient.last_name.like(f'%{search}%')) |
                (Patient.phone_number.like(f'%{search}%')) |
                (Patient.national_id.like(f'%{search}%'))
            )

        if severity:
            query = query.filter(DengueDetail.severity_level == severity)

        if district:
            query = query.filter(Address.district == district)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        patients_data = query.order_by(Patient.patient_id.desc()) \
            .offset(offset).limit(per_page).all()

        result = []
        for patient, dengue, address in patients_data:
            result.append({
                'patient_id': patient.patient_id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': patient.age,
                'gender': patient.gender,
                'phone': patient.phone_number,
                'district': address.district,
                'severity': dengue.severity_level,
                'diagnosis_date': dengue.diagnosis_date.strftime('%Y-%m-%d') if dengue.diagnosis_date else '',
                'outcome': dengue.outcome
            })

        return jsonify({
            'patients': result,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page
        })
    except Exception as e:
        print(f"Error getting patients: {str(e)}")
        return jsonify({'patients': [], 'total': 0, 'pages': 0, 'current_page': 1})


@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        dengue = DengueDetail.query.filter_by(patient_id=patient_id).first()
        address = Address.query.filter_by(patient_id=patient_id, is_primary=True).first()

        patient_data = {
            'patient_id': patient.patient_id,
            'personal_info': {
                'name': f"{patient.first_name} {patient.last_name}",
                'national_id': patient.national_id,
                'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
                'age': patient.age,
                'gender': patient.gender,
                'blood_type': patient.blood_type,
                'phone': patient.phone_number,
                'email': patient.email,
                'emergency_contact': patient.emergency_contact
            },
            'address': {
                'street': address.street_address if address else '',
                'city': address.city if address else '',
                'district': address.district if address else '',
                'division': address.division if address else ''
            },
            'dengue_info': {
                'diagnosis_date': dengue.diagnosis_date.strftime('%Y-%m-%d') if dengue else '',
                'dengue_type': dengue.dengue_type if dengue else '',
                'severity': dengue.severity_level if dengue else '',
                'platelet_count': dengue.platelet_count if dengue else '',
                'outcome': dengue.outcome if dengue else ''
            }
        }

        return jsonify(patient_data)
    except Exception as e:
        print(f"Error getting patient {patient_id}: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/dengue/critical', methods=['GET'])
def get_critical_patients():
    try:
        patients = db.session.query(Patient, DengueDetail, Address) \
            .join(DengueDetail, Patient.patient_id == DengueDetail.patient_id) \
            .join(Address, Patient.patient_id == Address.patient_id) \
            .filter(
            DengueDetail.severity_level.in_(['Critical', 'Severe']),
            DengueDetail.outcome == 'Under Treatment',
            Address.is_primary == True
        ) \
            .order_by(DengueDetail.severity_level.desc()) \
            .all()

        result = []
        for patient, dengue, address in patients:
            result.append({
                'patient_id': patient.patient_id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': patient.age,
                'emergency_contact': patient.emergency_contact,
                'severity': dengue.severity_level,
                'platelet_count': dengue.platelet_count,
                'district': address.district,
                'diagnosis_date': dengue.diagnosis_date.strftime('%Y-%m-%d') if dengue.diagnosis_date else ''
            })

        return jsonify({'critical_patients': result})
    except Exception as e:
        print(f"Error getting critical patients: {str(e)}")
        return jsonify({'critical_patients': []})


@app.route('/api/dengue/district-stats', methods=['GET'])
def get_district_statistics():
    try:
        from sqlalchemy import func

        stats = db.session.query(
            Address.district,
            func.count(DengueDetail.dengue_id).label('total_cases'),
            func.sum(db.case((DengueDetail.severity_level == 'Critical', 1), else_=0)).label('critical_cases'),
            func.sum(db.case((DengueDetail.severity_level == 'Severe', 1), else_=0)).label('severe_cases'),
            func.min(DengueDetail.diagnosis_date).label('first_case'),
            func.max(DengueDetail.diagnosis_date).label('latest_case')
        ).join(
            Patient, Patient.patient_id == Address.patient_id
        ).join(
            DengueDetail, Patient.patient_id == DengueDetail.patient_id
        ).filter(
            Address.is_primary == True
        ).group_by(
            Address.district
        ).all()

        result = []
        for stat in stats:
            result.append({
                'district': stat.district,
                'total_cases': stat.total_cases or 0,
                'critical_cases': stat.critical_cases or 0,
                'severe_cases': stat.severe_cases or 0,
                'deaths': 0,
                'first_case': stat.first_case.strftime('%Y-%m-%d') if stat.first_case else '',
                'latest_case': stat.latest_case.strftime('%Y-%m-%d') if stat.latest_case else ''
            })

        return jsonify({'district_stats': result})
    except Exception as e:
        print(f"Error getting district stats: {str(e)}")
        # Return demo data
        demo_stats = [
            {'district': 'Dhaka', 'total_cases': 45, 'critical_cases': 6, 'severe_cases': 9, 'deaths': 1,
             'first_case': '2024-01-05', 'latest_case': '2024-01-15'},
            {'district': 'Chittagong', 'total_cases': 28, 'critical_cases': 3, 'severe_cases': 5, 'deaths': 0,
             'first_case': '2024-01-06', 'latest_case': '2024-01-14'},
            {'district': 'Rajshahi', 'total_cases': 18, 'critical_cases': 2, 'severe_cases': 3, 'deaths': 0,
             'first_case': '2024-01-08', 'latest_case': '2024-01-14'},
            {'district': 'Khulna', 'total_cases': 12, 'critical_cases': 1, 'severe_cases': 2, 'deaths': 0,
             'first_case': '2024-01-09', 'latest_case': '2024-01-13'}
        ]
        return jsonify({'district_stats': demo_stats})


# CONTACT TRACING ENDPOINTS
@app.route('/api/patients/<int:patient_id>/contacts', methods=['POST'])
def add_contact(patient_id):
    try:
        data = request.get_json()
        print(f"Adding contact for patient {patient_id}: {data}")

        contact = ContactTracing(
            infected_patient_id=patient_id,
            contact_name=data['contact_name'],
            contact_phone=data.get('contact_phone'),
            contact_relation=data.get('contact_relation'),
            exposure_date=datetime.strptime(data['exposure_date'], '%Y-%m-%d') if data.get('exposure_date') else None,
            exposure_location=data.get('exposure_location'),
            contact_status=data.get('contact_status', 'Monitored')
        )

        db.session.add(contact)
        db.session.commit()

        return jsonify({'success': True, 'contact_id': contact.trace_id})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding contact: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/contact-tracing', methods=['GET'])
def get_contact_tracing():
    try:
        contacts = db.session.query(ContactTracing, Patient) \
            .join(Patient, ContactTracing.infected_patient_id == Patient.patient_id) \
            .order_by(ContactTracing.exposure_date.desc()) \
            .all()

        result = []
        for contact, patient in contacts:
            result.append({
                'infected_patient': f"{patient.first_name} {patient.last_name} ({patient.patient_id})",
                'contact_name': contact.contact_name,
                'relation': contact.contact_relation,
                'exposure_date': contact.exposure_date.strftime('%Y-%m-%d') if contact.exposure_date else '',
                'status': contact.contact_status,
                'phone': contact.contact_phone
            })

        stats = {
            'total': ContactTracing.query.count(),
            'positive': ContactTracing.query.filter_by(contact_status='Positive').count(),
            'monitored': ContactTracing.query.filter_by(contact_status='Monitored').count()
        }

        return jsonify({'contacts': result, 'stats': stats})
    except Exception as e:
        print(f"Error getting contact tracing: {str(e)}")
        return jsonify({'contacts': [], 'stats': {'total': 0, 'positive': 0, 'monitored': 0}})


# LAB TESTS ENDPOINTS
@app.route('/api/patients/<int:patient_id>/lab-tests', methods=['POST'])
def add_lab_test(patient_id):
    try:
        data = request.get_json()
        print(f"Adding lab test for patient {patient_id}: {data}")

        test = LabTest(
            patient_id=patient_id,
            test_date=datetime.strptime(data['test_date'], '%Y-%m-%d'),
            test_type=data['test_type'],
            test_result=data['test_result'],
            result_value=data.get('result_value'),
            normal_range=data.get('normal_range'),
            lab_name=data.get('lab_name')
        )

        db.session.add(test)

        # Update platelet count in dengue details
        if data['test_type'] == 'Platelet Count' and data.get('result_value'):
            try:
                platelet_count = int(data['result_value'])
                dengue = DengueDetail.query.filter_by(patient_id=patient_id).first()
                if dengue:
                    dengue.platelet_count = platelet_count
                    # Update severity based on platelet count
                    if platelet_count < 20000:
                        dengue.severity_level = 'Critical'
                    elif platelet_count < 50000:
                        dengue.severity_level = 'Severe'
                    elif platelet_count < 100000:
                        dengue.severity_level = 'Moderate'
                    else:
                        dengue.severity_level = 'Mild'
            except ValueError:
                pass

        db.session.commit()

        return jsonify({'success': True, 'test_id': test.test_id})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding lab test: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/lab-tests/recent', methods=['GET'])
def get_recent_lab_tests():
    try:
        tests = LabTest.query.order_by(LabTest.test_date.desc()).limit(10).all()

        result = []
        for test in tests:
            result.append({
                'test_id': test.test_id,
                'patient_id': test.patient_id,
                'test_type': test.test_type,
                'result': test.test_result,
                'date': test.test_date.strftime('%Y-%m-%d'),
                'value': test.result_value
            })

        return jsonify({'tests': result})
    except Exception as e:
        print(f"Error getting lab tests: {str(e)}")
        return jsonify({'tests': []})


# DAILY MONITORING ENDPOINTS
@app.route('/api/patients/<int:patient_id>/daily-monitoring', methods=['POST'])
def add_daily_monitoring(patient_id):
    try:
        data = request.get_json()
        print(f"Adding daily monitoring for patient {patient_id}: {data}")

        # Check if record exists for this date
        existing = DailyMonitoring.query.filter_by(
            patient_id=patient_id,
            monitor_date=datetime.strptime(data['monitor_date'], '%Y-%m-%d')
        ).first()

        if existing:
            return jsonify({'success': False, 'error': 'Record already exists for this date'}), 400

        monitoring = DailyMonitoring(
            patient_id=patient_id,
            monitor_date=datetime.strptime(data['monitor_date'], '%Y-%m-%d'),
            temperature=data.get('temperature'),
            blood_pressure=data.get('blood_pressure'),
            platelet_count=data.get('platelet_count'),
            oxygen_saturation=data.get('oxygen_saturation'),
            pain_level=data.get('pain_level'),
            nurse_notes=data.get('nurse_notes')
        )

        db.session.add(monitoring)

        # Update dengue details if platelet count provided
        if data.get('platelet_count'):
            dengue = DengueDetail.query.filter_by(patient_id=patient_id).first()
            if dengue:
                dengue.platelet_count = data['platelet_count']

        db.session.commit()

        return jsonify({'success': True, 'monitor_id': monitoring.monitor_id})
    except Exception as e:
        db.session.rollback()
        print(f"Error adding daily monitoring: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/monitoring/recent', methods=['GET'])
def get_recent_monitoring():
    try:
        monitoring = DailyMonitoring.query.order_by(DailyMonitoring.monitor_date.desc()).limit(10).all()

        result = []
        for record in monitoring:
            result.append({
                'date': record.monitor_date.strftime('%Y-%m-%d'),
                'patient_id': record.patient_id,
                'temperature': record.temperature,
                'blood_pressure': record.blood_pressure,
                'platelet_count': record.platelet_count,
                'oxygen_saturation': record.oxygen_saturation
            })

        return jsonify({'monitoring': result})
    except Exception as e:
        print(f"Error getting monitoring data: {str(e)}")
        return jsonify({'monitoring': []})


@app.route('/api/search/patients', methods=['GET'])
def search_patients():
    try:
        name = request.args.get('name', '')
        phone = request.args.get('phone', '')
        district = request.args.get('district', '')
        severity = request.args.get('severity', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

        query = db.session.query(Patient, DengueDetail, Address) \
            .join(DengueDetail, Patient.patient_id == DengueDetail.patient_id) \
            .join(Address, Patient.patient_id == Address.patient_id) \
            .filter(Address.is_primary == True)

        if name:
            query = query.filter(
                (Patient.first_name.like(f'%{name}%')) |
                (Patient.last_name.like(f'%{name}%'))
            )

        if phone:
            query = query.filter(Patient.phone_number.like(f'%{phone}%'))

        if district:
            query = query.filter(Address.district == district)

        if severity:
            query = query.filter(DengueDetail.severity_level == severity)

        if date_from:
            query = query.filter(DengueDetail.diagnosis_date >= datetime.strptime(date_from, '%Y-%m-%d'))

        if date_to:
            query = query.filter(DengueDetail.diagnosis_date <= datetime.strptime(date_to, '%Y-%m-%d'))

        patients = query.order_by(DengueDetail.diagnosis_date.desc()).limit(50).all()

        result = []
        for patient, dengue, address in patients:
            result.append({
                'patient_id': patient.patient_id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': patient.age,
                'phone': patient.phone_number,
                'district': address.district,
                'severity': dengue.severity_level,
                'platelet_count': dengue.platelet_count,
                'diagnosis_date': dengue.diagnosis_date.strftime('%Y-%m-%d') if dengue.diagnosis_date else ''
            })

        return jsonify({'patients': result})
    except Exception as e:
        print(f"Error searching patients: {str(e)}")
        return jsonify({'patients': []})


# Test route to check if API is working
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'API is working!'})


# Helper function to get recent patients
def get_recent_patients(limit=5):
    try:
        patients = db.session.query(Patient, DengueDetail, Address) \
            .join(DengueDetail, Patient.patient_id == DengueDetail.patient_id) \
            .join(Address, Patient.patient_id == Address.patient_id) \
            .order_by(DengueDetail.diagnosis_date.desc()) \
            .limit(limit).all()

        result = []
        for patient, dengue, address in patients:
            result.append({
                'patient_id': patient.patient_id,
                'name': f"{patient.first_name} {patient.last_name}",
                'age': patient.age,
                'district': address.district,
                'severity': dengue.severity_level,
                'date': dengue.diagnosis_date.strftime('%Y-%m-%d') if dengue.diagnosis_date else ''
            })

        return result
    except Exception as e:
        print(f"Error getting recent patients: {e}")
        return []


def init_database():
    with app.app_context():
        try:
            db.create_all()

            # Create admin user if not exists
            if User.query.filter_by(username='admin').first() is None:
                admin = User(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    full_name='System Administrator',
                    role='Admin',
                    email='admin@dengue.gov'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")


if __name__ == '__main__':
    init_database()
    print("🚀 Starting Dengue Tracking System...")
    print("🌐 Access the application at: http://localhost:5000")
    print("🔑 Login with: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)