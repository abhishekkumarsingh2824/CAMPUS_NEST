"""Favorites app views."""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from db_utils import get_db
from core.decorators import student_required
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from pymongo.errors import DuplicateKeyError


@student_required
def toggle_favorite(request, property_id):
    """Add or remove a property from favorites."""
    db = get_db()
    user_id = request.session['user_id']
    try:
        existing = db.favorites.find_one({
            'student_id': user_id,
            'property_id': property_id
        })
        if existing:
            db.favorites.delete_one({'_id': existing['_id']})
            added = False
        else:
            db.favorites.insert_one({
                'student_id': user_id,
                'property_id': property_id,
                'created_at': datetime.utcnow(),
            })
            added = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'added': added})
        
        if added:
            messages.success(request, 'Property saved to favorites.')
        else:
            messages.info(request, 'Property removed from favorites.')
    except DuplicateKeyError:
        pass
    except (InvalidId, Exception) as e:
        messages.error(request, f'Error: {e}')

    return redirect(request.META.get('HTTP_REFERER', 'properties:find_rooms'))


@student_required
def my_favorites(request):
    """View all favorited properties."""
    db = get_db()
    user_id = request.session['user_id']
    favs = list(db.favorites.find({'student_id': user_id}).sort('created_at', -1))
    property_ids = [ObjectId(f['property_id']) for f in favs if f.get('property_id')]
    properties = list(db.properties.find({'_id': {'$in': property_ids}})) if property_ids else []
    return render(request, 'favorites/my_favorites.html', {'properties': properties})
