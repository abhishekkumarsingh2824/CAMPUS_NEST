"""
Core views for CampusNest: home, about, contact, error pages, admin dashboard.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from db_utils import get_db
from core.decorators import admin_required, login_required_custom
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


def home(request):
    """Home page with hero section and featured properties."""
    db = get_db()
    featured = list(db.properties.find(
        {'approval_status': 'approved', 'availability_status': True},
        limit=6
    ).sort('created_at', -1))
    stats = {
        'total_properties': db.properties.count_documents({'approval_status': 'approved'}),
        'total_cities': len(db.properties.distinct('city', {'approval_status': 'approved'})),
        'total_users': db.users.count_documents({'role': 'student'}),
    }
    return render(request, 'core/home.html', {
        'featured_properties': featured,
        'stats': stats,
    })


def about(request):
    """About CampusNest page."""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        if name and email and message_text:
            messages.success(request, 'Thank you! Your message has been sent. We will get back to you soon.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'core/contact.html')


@admin_required
def admin_dashboard(request):
    """Admin moderation dashboard."""
    db = get_db()
    pending_properties = list(db.properties.find({'approval_status': 'pending'}).sort('created_at', -1))
    all_properties = list(db.properties.find().sort('created_at', -1).limit(50))
    all_users = list(db.users.find().sort('created_at', -1).limit(50))
    all_inquiries = list(db.inquiries.find().sort('created_at', -1).limit(50))

    stats = {
        'total_users': db.users.count_documents({}),
        'total_students': db.users.count_documents({'role': 'student'}),
        'total_owners': db.users.count_documents({'role': 'owner'}),
        'total_properties': db.properties.count_documents({}),
        'pending_properties': db.properties.count_documents({'approval_status': 'pending'}),
        'approved_properties': db.properties.count_documents({'approval_status': 'approved'}),
        'rejected_properties': db.properties.count_documents({'approval_status': 'rejected'}),
        'total_inquiries': db.inquiries.count_documents({}),
    }

    return render(request, 'core/admin_dashboard.html', {
        'pending_properties': pending_properties,
        'all_properties': all_properties,
        'all_users': all_users,
        'all_inquiries': all_inquiries,
        'stats': stats,
    })


@admin_required
def admin_approve_property(request, property_id):
    """Approve a property listing."""
    if request.method == 'POST':
        try:
            db = get_db()
            result = db.properties.update_one(
                {'_id': ObjectId(property_id)},
                {'$set': {'approval_status': 'approved', 'updated_at': datetime.utcnow()}}
            )
            if result.modified_count:
                messages.success(request, 'Property approved successfully.')
            else:
                messages.warning(request, 'Property not found or already approved.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('core:admin_dashboard')


@admin_required
def admin_reject_property(request, property_id):
    """Reject a property listing."""
    if request.method == 'POST':
        try:
            db = get_db()
            result = db.properties.update_one(
                {'_id': ObjectId(property_id)},
                {'$set': {'approval_status': 'rejected', 'updated_at': datetime.utcnow()}}
            )
            if result.modified_count:
                messages.success(request, 'Property rejected.')
            else:
                messages.warning(request, 'Property not found.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('core:admin_dashboard')


@admin_required
def admin_delete_user(request, user_id):
    """Delete a user account (admin only)."""
    if request.method == 'POST':
        try:
            db = get_db()
            db.users.delete_one({'_id': ObjectId(user_id)})
            messages.success(request, 'User deleted.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('core:admin_dashboard')


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
