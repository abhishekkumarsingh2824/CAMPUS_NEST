"""
Accounts views for CampusNest.
Implements custom session-based authentication using PyMongo.
Passwords are hashed using Django's make_password / check_password utilities.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from db_utils import get_db
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import re


def _validate_email(email):
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None


def _validate_phone(phone):
    return re.match(r'^[6-9]\d{9}$', phone) is not None


def register(request):
    """Unified registration page with role selection."""
    if request.session.get('user_id'):
        return redirect('core:home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'student')

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if not _validate_email(email):
            errors.append('Enter a valid email address.')
        if phone and not _validate_phone(phone):
            errors.append('Enter a valid 10-digit Indian mobile number.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if role not in ('student', 'owner'):
            errors.append('Invalid role selected.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        db = get_db()
        if db.users.find_one({'email': email}):
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        user_doc = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password_hash': make_password(password),
            'role': role,
            'created_at': datetime.utcnow(),
            'profile_pic': None,
            'college': request.POST.get('college', '').strip(),
            'city': request.POST.get('city', '').strip(),
        }
        result = db.users.insert_one(user_doc)
        messages.success(request, f'Welcome to CampusNest! Please log in.')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')


def login_view(request):
    """Login page."""
    if request.session.get('user_id'):
        return redirect('core:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'accounts/login.html', {'email': email})

        db = get_db()
        user = db.users.find_one({'email': email})

        if user and check_password(password, user['password_hash']):
            request.session['user_id'] = str(user['_id'])
            request.session['user_role'] = user['role']
            request.session['user_name'] = user['full_name']
            messages.success(request, f'Welcome back, {user["full_name"]}!')
            # Role-based redirect
            role = user['role']
            if role == 'student':
                return redirect('accounts:student_dashboard')
            elif role == 'owner':
                return redirect('accounts:owner_dashboard')
            elif role == 'admin':
                return redirect('core:admin_dashboard')
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'accounts/login.html', {'email': email})

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Logout and clear session."""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def student_dashboard(request):
    """Student dashboard: saved properties + recent inquiries."""
    if not request.session.get('user_id'):
        return redirect('accounts:login')
    if request.session.get('user_role') != 'student':
        return redirect('core:home')

    db = get_db()
    user_id = request.session['user_id']
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        request.session.flush()
        return redirect('accounts:login')

    # Favorites
    favs = list(db.favorites.find({'student_id': user_id}).sort('created_at', -1))
    fav_property_ids = [ObjectId(f['property_id']) for f in favs if f.get('property_id')]
    fav_properties = list(db.properties.find({'_id': {'$in': fav_property_ids}})) if fav_property_ids else []

    # Recent inquiries
    inquiries = list(db.inquiries.find({'student_id': user_id}).sort('created_at', -1).limit(10))
    for inq in inquiries:
        try:
            prop = db.properties.find_one({'_id': ObjectId(inq['property_id'])})
            inq['property'] = prop
        except Exception:
            inq['property'] = None

    return render(request, 'accounts/student_dashboard.html', {
        'user': user,
        'fav_properties': fav_properties,
        'inquiries': inquiries,
    })


def owner_dashboard(request):
    """Owner dashboard: my listings + inquiry management."""
    if not request.session.get('user_id'):
        return redirect('accounts:login')
    if request.session.get('user_role') != 'owner':
        return redirect('core:home')

    db = get_db()
    user_id = request.session['user_id']
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        request.session.flush()
        return redirect('accounts:login')

    my_properties = list(db.properties.find({'owner_id': user_id}).sort('created_at', -1))
    # Inquiry counts per property
    for prop in my_properties:
        prop['inquiry_count'] = db.inquiries.count_documents({'property_id': str(prop['_id'])})

    recent_inquiries = list(db.inquiries.find({'owner_id': user_id}).sort('created_at', -1).limit(10))
    for inq in recent_inquiries:
        try:
            prop = db.properties.find_one({'_id': ObjectId(inq['property_id'])})
            inq['property'] = prop
            student = db.users.find_one({'_id': ObjectId(inq['student_id'])})
            inq['student'] = student
        except Exception:
            inq['property'] = None
            inq['student'] = None

    stats = {
        'total_listings': len(my_properties),
        'approved': sum(1 for p in my_properties if p.get('approval_status') == 'approved'),
        'pending': sum(1 for p in my_properties if p.get('approval_status') == 'pending'),
        'available': sum(1 for p in my_properties if p.get('availability_status')),
        'total_inquiries': db.inquiries.count_documents({'owner_id': user_id}),
    }

    return render(request, 'accounts/owner_dashboard.html', {
        'user': user,
        'my_properties': my_properties,
        'recent_inquiries': recent_inquiries,
        'stats': stats,
    })


def edit_profile(request):
    """Edit own profile."""
    if not request.session.get('user_id'):
        return redirect('accounts:login')

    db = get_db()
    user_id = request.session['user_id']
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return redirect('accounts:login')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        college = request.POST.get('college', '').strip()
        city = request.POST.get('city', '').strip()

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if phone and not _validate_phone(phone):
            errors.append('Enter a valid 10-digit Indian mobile number.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'accounts/edit_profile.html', {'user': user})

        update = {
            'full_name': full_name,
            'phone': phone,
            'college': college,
            'city': city,
        }
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update})
        request.session['user_name'] = full_name
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:edit_profile')

    return render(request, 'accounts/edit_profile.html', {'user': user})


def change_password(request):
    """Change password for current session user."""
    if not request.session.get('user_id'):
        return redirect('accounts:login')

    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']
        user = db.users.find_one({'_id': ObjectId(user_id)})
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')

        if not check_password(current_password, user['password_hash']):
            messages.error(request, 'Current password is incorrect.')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters.')
        elif new_password != confirm:
            messages.error(request, 'New passwords do not match.')
        else:
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password_hash': make_password(new_password)}}
            )
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:edit_profile')

    return render(request, 'accounts/change_password.html')
