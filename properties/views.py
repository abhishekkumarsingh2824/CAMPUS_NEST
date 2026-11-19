"""
Properties views for CampusNest.
Handles search, filter, CRUD operations, and image uploads via PyMongo.
"""
import os
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from db_utils import get_db
from core.decorators import owner_required, login_required_custom
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime


ROOM_TYPES = ['Single Room', 'Shared Room', 'PG', 'Hostel', 'Studio Apartment', '1BHK', '2BHK']
AMENITY_LIST = ['WiFi', 'AC', 'Attached Bathroom', 'Meals Included', 'Laundry', 'Parking',
                'Security', 'Power Backup', 'CCTV', 'Gym', 'Study Room', 'TV', 'Geyser']


def _save_image(image_file):
    """Save an uploaded image and return its URL path."""
    ext = image_file.name.rsplit('.', 1)[-1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'properties')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, 'wb') as f:
        for chunk in image_file.chunks():
            f.write(chunk)
    return f"properties/{filename}"


def find_rooms(request):
    """Search and filter properties page."""
    db = get_db()
    query = {'approval_status': 'approved'}

    search_q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    room_type = request.GET.get('room_type', '').strip()
    min_rent = request.GET.get('min_rent', '').strip()
    max_rent = request.GET.get('max_rent', '').strip()
    amenities_filter = request.GET.getlist('amenities')
    availability = request.GET.get('availability', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    if search_q:
        query['$or'] = [
            {'title': {'$regex': search_q, '$options': 'i'}},
            {'city': {'$regex': search_q, '$options': 'i'}},
            {'locality': {'$regex': search_q, '$options': 'i'}},
            {'nearby_college': {'$regex': search_q, '$options': 'i'}},
            {'description': {'$regex': search_q, '$options': 'i'}},
        ]
    if city:
        query['city'] = {'$regex': city, '$options': 'i'}
    if room_type:
        query['room_type'] = room_type
    if min_rent:
        try:
            query.setdefault('monthly_rent', {})['$gte'] = int(min_rent)
        except ValueError:
            pass
    if max_rent:
        try:
            query.setdefault('monthly_rent', {})['$lte'] = int(max_rent)
        except ValueError:
            pass
    if amenities_filter:
        query['amenities'] = {'$all': amenities_filter}
    if availability == 'available':
        query['availability_status'] = True
    elif availability == 'unavailable':
        query['availability_status'] = False

    sort_map = {
        'newest': [('created_at', -1)],
        'oldest': [('created_at', 1)],
        'rent_low': [('monthly_rent', 1)],
        'rent_high': [('monthly_rent', -1)],
    }
    sort_order = sort_map.get(sort_by, [('created_at', -1)])
    properties = list(db.properties.find(query).sort(sort_order))
    cities = db.properties.distinct('city', {'approval_status': 'approved'})

    return render(request, 'properties/find_rooms.html', {
        'properties': properties,
        'cities': sorted(cities),
        'room_types': ROOM_TYPES,
        'amenity_list': AMENITY_LIST,
        'filters': {
            'q': search_q, 'city': city, 'room_type': room_type,
            'min_rent': min_rent, 'max_rent': max_rent,
            'amenities': amenities_filter, 'availability': availability,
            'sort': sort_by,
        },
        'total': len(properties),
    })


def property_detail(request, property_id):
    """View property details and photo gallery."""
    db = get_db()
    try:
        prop = db.properties.find_one({'_id': ObjectId(property_id)})
    except (InvalidId, Exception):
        return render(request, 'errors/404.html', status=404)

    if not prop:
        return render(request, 'errors/404.html', status=404)

    owner = None
    try:
        owner = db.users.find_one({'_id': ObjectId(prop['owner_id'])})
    except Exception:
        pass

    reviews = list(db.reviews.find({'property_id': property_id}).sort('created_at', -1))
    for rev in reviews:
        try:
            reviewer = db.users.find_one({'_id': ObjectId(rev['student_id'])})
            rev['reviewer'] = reviewer
        except Exception:
            rev['reviewer'] = None

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.get('rating', 0) for r in reviews) / len(reviews), 1)

    is_favorited = False
    user_id = request.session.get('user_id')
    if user_id:
        is_favorited = bool(db.favorites.find_one({
            'student_id': user_id,
            'property_id': property_id
        }))

    similar = list(db.properties.find({
        'approval_status': 'approved',
        'city': prop.get('city'),
        '_id': {'$ne': prop['_id']},
    }, limit=3))

    return render(request, 'properties/property_detail.html', {
        'property': prop,
        'owner': owner,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'is_favorited': is_favorited,
        'similar_properties': similar,
    })


@owner_required
def add_property(request):
    """Add a new property listing."""
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        city = request.POST.get('city', '').strip()
        locality = request.POST.get('locality', '').strip()
        address = request.POST.get('address', '').strip()
        nearby_college = request.POST.get('nearby_college', '').strip()
        room_type = request.POST.get('room_type', '').strip()
        occupancy = request.POST.get('occupancy', '').strip()
        amenities = request.POST.getlist('amenities')

        errors = []
        if not title:
            errors.append('Property title is required.')
        if not city:
            errors.append('City is required.')
        if not address:
            errors.append('Address is required.')
        if room_type not in ROOM_TYPES:
            errors.append('Select a valid room type.')

        try:
            monthly_rent = int(request.POST.get('monthly_rent', 0))
            if monthly_rent < 100:
                errors.append('Monthly rent must be at least ₹100.')
        except ValueError:
            errors.append('Monthly rent must be a number.')
            monthly_rent = 0

        try:
            security_deposit = int(request.POST.get('security_deposit', 0))
        except ValueError:
            security_deposit = 0

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'properties/add_property.html', {
                'room_types': ROOM_TYPES,
                'amenity_list': AMENITY_LIST,
                'form_data': request.POST,
            })

        # Handle image uploads
        images = []
        for img_file in request.FILES.getlist('images')[:settings.MAX_IMAGES_PER_PROPERTY]:
            if img_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                messages.warning(request, f'Image {img_file.name} is too large (max 5MB) and was skipped.')
                continue
            img_path = _save_image(img_file)
            if img_path:
                images.append(img_path)
            else:
                messages.warning(request, f'Invalid image format for {img_file.name}.')

        doc = {
            'owner_id': user_id,
            'title': title,
            'description': description,
            'city': city,
            'locality': locality,
            'address': address,
            'nearby_college': nearby_college,
            'monthly_rent': monthly_rent,
            'security_deposit': security_deposit,
            'room_type': room_type,
            'occupancy': occupancy,
            'amenities': amenities,
            'images': images,
            'availability_status': True,
            'approval_status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        result = db.properties.insert_one(doc)
        messages.success(request, 'Property submitted for approval. You will be notified once reviewed.')
        return redirect('accounts:owner_dashboard')

    return render(request, 'properties/add_property.html', {
        'room_types': ROOM_TYPES,
        'amenity_list': AMENITY_LIST,
    })


@owner_required
def edit_property(request, property_id):
    """Edit an existing property. Owner can only edit their own listings."""
    db = get_db()
    user_id = request.session['user_id']
    try:
        prop = db.properties.find_one({'_id': ObjectId(property_id)})
    except (InvalidId, Exception):
        return render(request, 'errors/404.html', status=404)

    if not prop:
        return render(request, 'errors/404.html', status=404)

    if prop['owner_id'] != user_id:
        messages.error(request, 'You are not authorised to edit this listing.')
        return redirect('accounts:owner_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        city = request.POST.get('city', '').strip()
        locality = request.POST.get('locality', '').strip()
        address = request.POST.get('address', '').strip()
        nearby_college = request.POST.get('nearby_college', '').strip()
        room_type = request.POST.get('room_type', '').strip()
        occupancy = request.POST.get('occupancy', '').strip()
        amenities = request.POST.getlist('amenities')
        availability_status = request.POST.get('availability_status') == 'on'

        errors = []
        try:
            monthly_rent = int(request.POST.get('monthly_rent', 0))
        except ValueError:
            monthly_rent = prop['monthly_rent']
        try:
            security_deposit = int(request.POST.get('security_deposit', 0))
        except ValueError:
            security_deposit = prop['security_deposit']

        if not title:
            errors.append('Title is required.')
        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'properties/edit_property.html', {
                'property': prop, 'room_types': ROOM_TYPES, 'amenity_list': AMENITY_LIST
            })

        # Handle new image uploads
        new_images = []
        for img_file in request.FILES.getlist('new_images')[:settings.MAX_IMAGES_PER_PROPERTY]:
            img_path = _save_image(img_file)
            if img_path:
                new_images.append(img_path)

        existing_images = prop.get('images', [])
        # Remove images marked for deletion
        delete_images = request.POST.getlist('delete_images')
        existing_images = [img for img in existing_images if img not in delete_images]
        all_images = (existing_images + new_images)[:settings.MAX_IMAGES_PER_PROPERTY]

        update = {
            'title': title,
            'description': description,
            'city': city,
            'locality': locality,
            'address': address,
            'nearby_college': nearby_college,
            'monthly_rent': monthly_rent,
            'security_deposit': security_deposit,
            'room_type': room_type,
            'occupancy': occupancy,
            'amenities': amenities,
            'images': all_images,
            'availability_status': availability_status,
            'updated_at': datetime.utcnow(),
        }
        db.properties.update_one({'_id': ObjectId(property_id)}, {'$set': update})
        messages.success(request, 'Property updated successfully.')
        return redirect('accounts:owner_dashboard')

    return render(request, 'properties/edit_property.html', {
        'property': prop,
        'room_types': ROOM_TYPES,
        'amenity_list': AMENITY_LIST,
    })


@owner_required
def delete_property(request, property_id):
    """Delete a property (owner only)."""
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']
        try:
            prop = db.properties.find_one({'_id': ObjectId(property_id)})
            if prop and prop['owner_id'] == user_id:
                db.properties.delete_one({'_id': ObjectId(property_id)})
                db.favorites.delete_many({'property_id': property_id})
                db.inquiries.delete_many({'property_id': property_id})
                messages.success(request, 'Property deleted successfully.')
            else:
                messages.error(request, 'Property not found or access denied.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('accounts:owner_dashboard')


@owner_required
def toggle_availability(request, property_id):
    """Toggle availability status of a property."""
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']
        try:
            prop = db.properties.find_one({'_id': ObjectId(property_id)})
            if prop and prop['owner_id'] == user_id:
                new_status = not prop.get('availability_status', True)
                db.properties.update_one(
                    {'_id': ObjectId(property_id)},
                    {'$set': {'availability_status': new_status, 'updated_at': datetime.utcnow()}}
                )
                status_text = 'available' if new_status else 'unavailable'
                messages.success(request, f'Property marked as {status_text}.')
            else:
                messages.error(request, 'Access denied.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error: {e}')
    return redirect('accounts:owner_dashboard')
