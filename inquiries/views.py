"""Inquiries app views."""
from django.shortcuts import render, redirect
from django.contrib import messages
from db_utils import get_db
from core.decorators import student_required, owner_required, login_required_custom
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


@student_required
def send_inquiry(request, property_id):
    """Student sends inquiry for a property."""
    db = get_db()
    try:
        prop = db.properties.find_one({'_id': ObjectId(property_id)})
    except (InvalidId, Exception):
        messages.error(request, 'Property not found.')
        return redirect('properties:find_rooms')

    if not prop:
        messages.error(request, 'Property not found.')
        return redirect('properties:find_rooms')

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if not message_text or len(message_text) < 10:
            messages.error(request, 'Please write a meaningful message (at least 10 characters).')
            return redirect('properties:property_detail', property_id=property_id)

        user_id = request.session['user_id']
        doc = {
            'student_id': user_id,
            'owner_id': prop['owner_id'],
            'property_id': property_id,
            'message': message_text,
            'status': 'pending',
            'created_at': datetime.utcnow(),
        }
        db.inquiries.insert_one(doc)
        messages.success(request, 'Inquiry sent successfully! The owner will contact you soon.')
        return redirect('properties:property_detail', property_id=property_id)

    return redirect('properties:property_detail', property_id=property_id)


@student_required
def my_inquiries(request):
    """Student views their inquiry history."""
    db = get_db()
    user_id = request.session['user_id']
    inquiries = list(db.inquiries.find({'student_id': user_id}).sort('created_at', -1))
    for inq in inquiries:
        try:
            prop = db.properties.find_one({'_id': ObjectId(inq['property_id'])})
            inq['property'] = prop
        except Exception:
            inq['property'] = None
    return render(request, 'inquiries/my_inquiries.html', {'inquiries': inquiries})


@owner_required
def owner_inquiries(request):
    """Owner views all inquiries for their properties."""
    db = get_db()
    user_id = request.session['user_id']
    status_filter = request.GET.get('status', '').strip()
    query = {'owner_id': user_id}
    if status_filter:
        query['status'] = status_filter

    inquiries = list(db.inquiries.find(query).sort('created_at', -1))
    for inq in inquiries:
        try:
            prop = db.properties.find_one({'_id': ObjectId(inq['property_id'])})
            inq['property'] = prop
            student = db.users.find_one({'_id': ObjectId(inq['student_id'])})
            inq['student'] = student
        except Exception:
            inq['property'] = None
            inq['student'] = None
    return render(request, 'inquiries/owner_inquiries.html', {
        'inquiries': inquiries,
        'status_filter': status_filter,
    })


@owner_required
def update_inquiry_status(request, inquiry_id):
    """Owner updates inquiry status."""
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']
        new_status = request.POST.get('status', '')
        valid_statuses = ['pending', 'responded', 'closed']
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status.')
            return redirect('inquiries:owner_inquiries')
        try:
            inq = db.inquiries.find_one({'_id': ObjectId(inquiry_id)})
            if inq and inq['owner_id'] == user_id:
                db.inquiries.update_one(
                    {'_id': ObjectId(inquiry_id)},
                    {'$set': {'status': new_status}}
                )
                messages.success(request, f'Inquiry marked as {new_status}.')
            else:
                messages.error(request, 'Access denied.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('inquiries:owner_inquiries')
