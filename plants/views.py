from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Plant, Comment, Rating
from .forms import PlantForm, CommentForm, RatingForm


def all_plants(request):
    plants = Plant.objects.select_related().prefetch_related('comments').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    is_edible = request.GET.get('is_edible', '').strip()

    if query:
        plants = plants.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        plants = plants.filter(category=category)

    if is_edible == 'true':
        plants = plants.filter(is_edible=True)
    elif is_edible == 'false':
        plants = plants.filter(is_edible=False)

    categories = Plant._meta.get_field('category').choices

    context = {
        'plants': plants,
        'categories': categories,
        'selected_query': query,
        'selected_category': category,
        'selected_edible': is_edible,
        'plants_count': plants.count(),
    }

    return render(request, 'plants/all_plants.html', context)


def plant_detail(request, plant_id):
    plant = get_object_or_404(
        Plant.objects.prefetch_related('comments', 'ratings'),
        id=plant_id
    )
    
    plant.increment_views()
    
    related_plants = Plant.objects.filter(
        category=plant.category
    ).exclude(
        id=plant.id
    ).prefetch_related('comments', 'ratings')[:4]
    
    comments = plant.comments.all()
    ratings = plant.ratings.all()
    
    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.plant = plant
                comment.save()
                messages.success(request, 'Your comment has been posted successfully!')
                return redirect('plants:detail', plant_id=plant.id)
            else:
                messages.error(request, 'Please correct the errors in your comment.')
        
        elif 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                name = rating_form.cleaned_data['name']
                existing_rating = Rating.objects.filter(plant=plant, name=name).first()
                
                if existing_rating:
                    existing_rating.score = rating_form.cleaned_data['score']
                    existing_rating.save()
                    messages.success(request, 'Your rating has been updated successfully!')
                else:
                    rating = rating_form.save(commit=False)
                    rating.plant = plant
                    rating.save()
                    messages.success(request, 'Your rating has been submitted successfully!')
                return redirect('plants:detail', plant_id=plant.id)
            else:
                messages.error(request, 'Please correct the errors in your rating.')
    
    comment_form = CommentForm()
    rating_form = RatingForm()

    context = {
        'plant': plant,
        'related_plants': related_plants,
        'comments': comments,
        'ratings': ratings,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'comments_count': comments.count(),
        'average_rating': plant.average_rating(),
        'rating_count': plant.rating_count(),
    }

    return render(request, 'plants/plant_detail.html', context)


def add_plant(request):
    if request.method == 'POST':
        form = PlantForm(request.POST)
        if form.is_valid():
            plant = form.save()
            messages.success(request, f'Plant "{plant.name}" has been added successfully!')
            return redirect('plants:detail', plant_id=plant.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlantForm()

    context = {
        'form': form,
        'page_title': 'Add New Plant',
        'button_text': 'Add Plant',
    }

    return render(request, 'plants/plant_form.html', context)


def update_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plant "{plant.name}" has been updated successfully!')
            return redirect('plants:detail', plant_id=plant.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlantForm(instance=plant)

    context = {
        'form': form,
        'page_title': 'Update Plant',
        'button_text': 'Save Changes',
        'plant': plant,
    }

    return render(request, 'plants/plant_form.html', context)


def delete_plant(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)

    if request.method == 'POST':
        plant_name = plant.name
        plant.delete()
        messages.success(request, f'Plant "{plant_name}" has been deleted successfully!')
        return redirect('plants:all_plants')

    context = {
        'plant': plant
    }

    return render(request, 'plants/plant_delete.html', context)


def search_plants(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Plant.objects.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(category__icontains=query)
        ).prefetch_related('comments').order_by('-created_at')

    context = {
        'query': query,
        'results': results,
        'results_count': len(results) if results else 0,
    }

    return render(request, 'plants/search.html', context)


def toggle_favorite(request, plant_id):
    if request.method == 'POST':
        plant = get_object_or_404(Plant, id=plant_id)
        return JsonResponse({
            'success': True,
            'plant_id': plant_id,
            'plant_name': plant.name
        })
    return JsonResponse({'success': False})


def favorites(request):
    context = {
        'page_title': 'My Favorites'
    }
    return render(request, 'plants/favorites.html', context)

