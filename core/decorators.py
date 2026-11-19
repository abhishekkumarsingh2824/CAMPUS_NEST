"""
Core app decorators for CampusNest role-based access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required_custom(func):
    """Require any authenticated session user."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to continue.')
            return redirect('accounts:login')
        return func(request, *args, **kwargs)
    return wrapper


def student_required(func):
    """Require role == student."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to continue.')
            return redirect('accounts:login')
        if request.session.get('user_role') != 'student':
            messages.error(request, 'This page is only for students.')
            return redirect('core:home')
        return func(request, *args, **kwargs)
    return wrapper


def owner_required(func):
    """Require role == owner."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to continue.')
            return redirect('accounts:login')
        if request.session.get('user_role') != 'owner':
            messages.error(request, 'This page is only for property owners.')
            return redirect('core:home')
        return func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    """Require role == admin."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to continue.')
            return redirect('accounts:login')
        if request.session.get('user_role') != 'admin':
            messages.error(request, 'Access denied.')
            return redirect('core:home')
        return func(request, *args, **kwargs)
    return wrapper
