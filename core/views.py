from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm

from .forms import ContactForm
from .models import Contact
from plants.models import Plant, Favorite


def home(request):
    latest_plants = Plant.objects.select_related('category').prefetch_related(
        'comments', 'countries'
    ).order_by('-created_at')[:8]
    
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True))
    
    context = {
        'latest_plants': latest_plants,
        'user_favorites': user_favorites,
    }
    
    return render(request, 'core/home.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(
                request, 
                'Thank you for your message! We will get back to you soon.'
            )
            return redirect('core:contact_messages')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    context = {
        'form': form
    }

    return render(request, 'core/contact.html', context)


def contact_messages(request):
    contact_messages = Contact.objects.all().order_by('-created_at')
    
    context = {
        'messages': contact_messages,
        'messages_count': contact_messages.count(),
    }
    
    return render(request, 'core/contact_messages.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')
