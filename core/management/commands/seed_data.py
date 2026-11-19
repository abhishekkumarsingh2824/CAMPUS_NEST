"""
Management command to seed MongoDB with realistic Lovely Professional University (LPU) sample data.
Places: Law Gate, Chiheru, Phagwara, Jalandhar, Hardaspur, Maheru.
Usage: python manage.py seed_data
       python manage.py seed_data --clear  (clears existing demo data first)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from db_utils import get_db
from datetime import datetime, timedelta
import random


LPU_PROPERTIES = [
    {
        'title': 'Premium AC Room at Law Gate (Near LPU Main Gate)',
        'description': 'Modern furnished student room just 2 minutes walking distance from LPU Law Gate. Features high-speed WiFi, split AC, study table, ergonomic chair, and attached western washroom. 24/7 power backup and RO water purifier.',
        'city': 'Phagwara',
        'locality': 'Law Gate',
        'address': 'Street No. 3, Near Domino\'s, Law Gate, LPU, Phagwara, Punjab - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 6500,
        'security_deposit': 6500,
        'room_type': 'Single Room',
        'occupancy': '1 Person',
        'amenities': ['WiFi', 'AC', 'Attached Bathroom', 'Geyser', 'Power Backup', 'CCTV', 'Security'],
        'availability_status': True,
    },
    {
        'title': 'Green Valley Boys PG & Mess — Chiheru',
        'description': 'Affordable and clean boys PG in Chiheru, just 1.5 km from LPU campus. Includes 3 hygienic North/South Indian meals per day, daily room cleaning, laundry facility, and high-speed fiber internet. Very peaceful study atmosphere.',
        'city': 'Phagwara',
        'locality': 'Chiheru',
        'address': 'Near Chiheru Railway Crossing, GT Road, Phagwara - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 5000,
        'security_deposit': 5000,
        'room_type': 'PG',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'Meals Included', 'Laundry', 'Study Room', 'CCTV', 'Power Backup'],
        'availability_status': True,
    },
    {
        'title': 'Fully Furnished 1BHK Flat Near Maheru / Law Gate',
        'description': 'Independent 1BHK apartment with private kitchen, balcony, and modular fittings. Ideal for 2 friends or PG scholars wanting private space. 5 minutes auto ride to LPU Uni-Mall / Academic blocks.',
        'city': 'Phagwara',
        'locality': 'Maheru',
        'address': 'Opposite Maheru Road, Near LPU Gate 4, Phagwara - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 9000,
        'security_deposit': 9000,
        'room_type': '1BHK',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'AC', 'Attached Bathroom', 'Parking', 'Power Backup', 'Security'],
        'availability_status': True,
    },
    {
        'title': 'Royal Girls PG with 3-Time Food — Law Gate',
        'description': 'Safe, secure, and dedicated PG for female LPU students. Biometric gate entry, 24/7 CCTV surveillance, in-house warden, hot water geyser, nutritious home-cooked meals, and AC/cooler options. Walkable to university.',
        'city': 'Phagwara',
        'locality': 'Law Gate',
        'address': 'Lane 5, Near Grand Trunk Market, Law Gate, Phagwara - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 7000,
        'security_deposit': 7000,
        'room_type': 'PG',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'AC', 'Meals Included', 'Attached Bathroom', 'CCTV', 'Security', 'Geyser', 'Laundry'],
        'availability_status': True,
    },
    {
        'title': 'Budget Shared Room for Students — Hardaspur',
        'description': 'Affordable 2-seater sharing room with bed, mattress, personal almirah, and study desk. 3 km from LPU with regular e-rickshaws available. High-speed WiFi and chilled RO drinking water included.',
        'city': 'Phagwara',
        'locality': 'Hardaspur',
        'address': 'Hardaspur Village Main Road, Phagwara - 144401',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 3500,
        'security_deposit': 3500,
        'room_type': 'Shared Room',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'Power Backup', 'Attached Bathroom', 'Geyser'],
        'availability_status': True,
    },
    {
        'title': 'Comfort Studio Apartment — Model Town, Phagwara',
        'description': 'Independent modern studio apartment in prime Model Town, Phagwara (approx. 7 km from LPU). Close to cafes, gym, railway station, and markets. Fully furnished with refrigerator, microwave, and high-speed Wi-Fi.',
        'city': 'Phagwara',
        'locality': 'Model Town',
        'address': 'B-Block, Model Town, Phagwara, Punjab - 144401',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 11000,
        'security_deposit': 11000,
        'room_type': 'Studio Apartment',
        'occupancy': '1 Person',
        'amenities': ['WiFi', 'AC', 'Parking', 'Gym', 'Security', 'Attached Bathroom', 'Geyser', 'Power Backup'],
        'availability_status': True,
    },
    {
        'title': 'Spacious 2BHK Student Flat — Rama Mandi, Jalandhar',
        'description': 'Complete 2BHK flat located in Rama Mandi, Jalandhar (around 12 km from LPU on GT Road). Direct bus and auto connectivity right outside. Best for a group of 3-4 students seeking comfortable living with low per-head expenses.',
        'city': 'Jalandhar',
        'locality': 'Rama Mandi',
        'address': 'GT Road, Near Rama Mandi Flyover, Jalandhar, Punjab - 144005',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 14000,
        'security_deposit': 14000,
        'room_type': '2BHK',
        'occupancy': '3+ Persons',
        'amenities': ['WiFi', 'Parking', 'Attached Bathroom', 'Power Backup', 'CCTV', 'Security'],
        'availability_status': True,
    },
    {
        'title': 'Deluxe Single Room with Balcony — Law Gate Backside',
        'description': 'Private single occupancy room with private balcony overlooking green fields. Well lit, quiet for exams and coding prep. Lift facility, generator backup, and high-speed fiber connection.',
        'city': 'Phagwara',
        'locality': 'Law Gate',
        'address': 'Near Verka Booth, Backside Law Gate, Phagwara - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 7500,
        'security_deposit': 7500,
        'room_type': 'Single Room',
        'occupancy': '1 Person',
        'amenities': ['WiFi', 'AC', 'Attached Bathroom', 'Geyser', 'Power Backup', 'Security'],
        'availability_status': True,
    },
    {
        'title': 'Sunshine Boys Hostel & Mess — GT Road, Chiheru',
        'description': 'Dedicated student hostel with breakfast, lunch, and dinner included. Free gym area, indoor games room, table tennis, and 24/7 security guard. Walking distance to Chiheru bus stop.',
        'city': 'Phagwara',
        'locality': 'Chiheru',
        'address': 'NH-44 GT Road, Chiheru, Phagwara - 144411',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 5800,
        'security_deposit': 5800,
        'room_type': 'Hostel',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'Meals Included', 'Gym', 'Laundry', 'Security', 'CCTV', 'Power Backup'],
        'availability_status': True,
    },
    {
        'title': 'Modern 1BHK Furnished Apartment — Cantt Road, Jalandhar',
        'description': '1BHK apartment near Jalandhar Cantt (10 km from LPU). Ideal for students who want peaceful city lifestyle with easy highway access to LPU via local autos or personal bike/car.',
        'city': 'Jalandhar',
        'locality': 'Jalandhar Cantt',
        'address': 'Defense Colony, Near Cantt Railway Station, Jalandhar - 144005',
        'nearby_college': 'Lovely Professional University (LPU)',
        'monthly_rent': 10500,
        'security_deposit': 10500,
        'room_type': '1BHK',
        'occupancy': '2 Persons',
        'amenities': ['WiFi', 'AC', 'Attached Bathroom', 'Parking', 'Security', 'Power Backup', 'Geyser'],
        'availability_status': True,
    },
]

SAMPLE_USERS = [
    {
        'full_name': 'Aarav Singhania',
        'email': 'student@demo.com',
        'phone': '9876543210',
        'role': 'student',
        'college': 'Lovely Professional University (LPU)',
        'city': 'Phagwara',
    },
    {
        'full_name': 'Simran Kaur',
        'email': 'student2@demo.com',
        'phone': '9123456789',
        'role': 'student',
        'college': 'Lovely Professional University (LPU)',
        'city': 'Phagwara',
    },
    {
        'full_name': 'Gurpreet Singh (PG Owner)',
        'email': 'owner@demo.com',
        'phone': '9988776655',
        'role': 'owner',
        'college': '',
        'city': 'Phagwara',
    },
    {
        'full_name': 'Rajesh Sharma (Law Gate Stays)',
        'email': 'owner2@demo.com',
        'phone': '9977665544',
        'role': 'owner',
        'college': '',
        'city': 'Phagwara',
    },
    {
        'full_name': 'CampusNest LPU Admin',
        'email': 'admin@demo.com',
        'phone': '9000000000',
        'role': 'admin',
        'college': '',
        'city': 'Phagwara',
    },
]


class Command(BaseCommand):
    help = 'Seeds MongoDB with realistic sample data around Lovely Professional University (LPU).'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing demo data before seeding.')

    def handle(self, *args, **options):
        db = get_db()
        
        if options['clear']:
            self.stdout.write('Clearing existing demo data...')
            db.users.delete_many({'email': {'$in': [u['email'] for u in SAMPLE_USERS]}})
            db.properties.delete_many({'_is_demo': True})
            self.stdout.write(self.style.WARNING('Cleared demo data.'))

        # Insert sample users
        self.stdout.write('Creating demo LPU users...')
        user_ids = {}
        for user_data in SAMPLE_USERS:
            existing = db.users.find_one({'email': user_data['email']})
            if existing:
                user_ids[user_data['email']] = str(existing['_id'])
                self.stdout.write(f'  User {user_data["email"]} already exists — skipping.')
                continue
            doc = {**user_data, 'password_hash': make_password('demo1234'), 'created_at': datetime.utcnow()}
            result = db.users.insert_one(doc)
            user_ids[user_data['email']] = str(result.inserted_id)
            self.stdout.write(self.style.SUCCESS(f'  Created user: {user_data["email"]}'))

        # Alternate owner IDs for properties
        owner1_id = user_ids.get('owner@demo.com')
        owner2_id = user_ids.get('owner2@demo.com')
        
        # Insert sample properties around LPU
        self.stdout.write('Creating demo properties near LPU...')
        created = 0
        for i, prop in enumerate(LPU_PROPERTIES):
            owner_id = owner1_id if i % 2 == 0 else owner2_id
            if not owner_id:
                continue
            days_ago = random.randint(1, 20)
            img_num = (i % 10) + 1
            images = [f'properties/room_{img_num}.jpg']
            doc = {
                **prop,
                'owner_id': owner_id,
                'images': images,
                'approval_status': 'approved',
                '_is_demo': True,
                'created_at': datetime.utcnow() - timedelta(days=days_ago),
                'updated_at': datetime.utcnow() - timedelta(days=days_ago),
            }
            db.properties.insert_one(doc)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n[SUCCESS] LPU Data Seeding complete!\n'
            f'   Users created: {len(SAMPLE_USERS)}\n'
            f'   Properties created: {created} (Law Gate, Chiheru, Phagwara, Jalandhar)\n\n'
            f'Demo Login Credentials:\n'
            f'   Student : student@demo.com / demo1234\n'
            f'   Owner   : owner@demo.com   / demo1234\n'
            f'   Admin   : admin@demo.com   / demo1234\n'
        ))
