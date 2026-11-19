"""Reviews app views."""
from django.shortcuts import redirect
from django.contrib import messages
from db_utils import get_db
from core.decorators import student_required
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from pymongo.errors import DuplicateKeyError


@student_required
def add_review(request, property_id):
    """Student submits a review for a property."""
    if request.method == 'POST':
        db = get_db()
        user_id = request.session['user_id']

        try:
            rating = int(request.POST.get('rating', 0))
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            messages.error(request, 'Rating must be between 1 and 5.')
            return redirect('properties:property_detail', property_id=property_id)

        comment = request.POST.get('comment', '').strip()
        if len(comment) < 10:
            messages.error(request, 'Review must be at least 10 characters.')
            return redirect('properties:property_detail', property_id=property_id)

        try:
            doc = {
                'student_id': user_id,
                'property_id': property_id,
                'rating': rating,
                'comment': comment,
                'created_at': datetime.utcnow(),
            }
            db.reviews.insert_one(doc)
            messages.success(request, 'Review submitted successfully.')
        except DuplicateKeyError:
            messages.warning(request, 'You have already reviewed this property.')
        except (InvalidId, Exception) as e:
            messages.error(request, f'Error submitting review: {e}')

    return redirect('properties:property_detail', property_id=property_id)
