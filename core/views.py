from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ContactForm
from .models import Contact
from plants.models import Plant


def home(request):
    latest_plants = Plant.objects.select_related().prefetch_related(
        'comments'
    ).order_by('-created_at')[:6]
    
    context = {
        'latest_plants': latest_plants
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
