from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpRequest,HttpResponse
from django.views.decorators.http import require_POST
from .models import Plant, Comment, Rating, Favorite, Category, Country
from .forms import PlantForm, CommentForm, RatingForm, PlantImageFormSet


def all_plants(request:HttpRequest):
    plants = Plant.objects.select_related('category').prefetch_related('comments', 'countries').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    country_id = request.GET.get('country', '').strip()
    is_edible = request.GET.get('is_edible', '').strip()

    if query:
        plants = plants.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(description__icontains=query)
        )

    if category_id:
        plants = plants.filter(category_id=category_id)
    
    if country_id:
        plants = plants.filter(countries__id=country_id)

    if is_edible == 'true':
        plants = plants.filter(is_edible=True)
    elif is_edible == 'false':
        plants = plants.filter(is_edible=False)

    categories = Category.objects.all()
    countries = Country.objects.all()
    
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True))

    context = {
        'plants': plants,
        'categories': categories,
        'countries': countries,
        'selected_query': query,
        'selected_category': category_id,
        'selected_country': country_id,
        'selected_edible': is_edible,
        'plants_count': plants.count(),
        'user_favorites': user_favorites,
    }

    return render(request, 'plants/all_plants.html', context)




def add_plant(request:HttpRequest):
    if request.method == 'POST':
        form = PlantForm(request.POST)
        image_formset = PlantImageFormSet(request.POST)
        
        if form.is_valid() and image_formset.is_valid():
            plant = form.save()
            
            images = image_formset.save(commit=False)
            for image in images:
                image.plant = plant
                image.save()
            
            for image in image_formset.deleted_objects:
                image.delete()
            
            messages.success(request, f'Plant "{plant.name}" has been added successfully with {len(images)} image(s)!')
            return redirect('plants:detail', plant_id=plant.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlantForm()
        image_formset = PlantImageFormSet()

    context = {
        'form': form,
        'image_formset': image_formset,
        'page_title': 'Add New Plant',
        'button_text': 'Add Plant',
    }

    return render(request, 'plants/plant_form.html', context)


def update_plant(request, plant_id:HttpRequest):
    plant = get_object_or_404(Plant, id=plant_id)

    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)
        image_formset = PlantImageFormSet(request.POST, instance=plant)
        
        if form.is_valid() and image_formset.is_valid():
            form.save()
            
            images = image_formset.save(commit=False)
            for image in images:
                image.plant = plant
                image.save()
            
            for image in image_formset.deleted_objects:
                image.delete()
            
            messages.success(request, f'Plant "{plant.name}" has been updated successfully!')
            return redirect('plants:detail', plant_id=plant.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlantForm(instance=plant)
        image_formset = PlantImageFormSet(instance=plant)

    context = {
        'form': form,
        'image_formset': image_formset,
        'page_title': 'Update Plant',
        'button_text': 'Save Changes',
        'plant': plant,
    }

    return render(request, 'plants/plant_form.html', context)

def search_plants(request:HttpRequest):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Plant.objects.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category').prefetch_related('comments', 'countries').order_by('-created_at')

    context = {
        'query': query,
        'results': results,
        'results_count': len(results) if results else 0,
    }

    return render(request, 'plants/search.html', context)

def toggle_favorite(request: HttpRequest, plant_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'authentication_required',
                'message': 'You must be logged in to add favorites',
                'redirect_url': '/auth/login/'
            })
        
        plant = get_object_or_404(Plant, id=plant_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            plant=plant
        )
        
        if not created:
            favorite.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'is_favorite': False,
                'message': f'{plant.name} removed from favorites'
            })
        
        return JsonResponse({
            'success': True,
            'action': 'added',
            'is_favorite': True,
            'message': f'{plant.name} added to favorites'
        })
    
    return JsonResponse({'success': False})


@require_POST
def add_category(request: HttpRequest):
    category_name = request.POST.get('name', '').strip()
    
    if not category_name:
        return JsonResponse({
            'success': False,
            'error': 'Category name is required'
        })
    
    if Category.objects.filter(name__iexact=category_name).exists():
        return JsonResponse({
            'success': False,
            'error': f'Category "{category_name}" already exists'
        })
    
    try:
        category = Category.objects.create(name=category_name)
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            },
            'message': f'Category "{category.name}" added successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })



@login_required
def favorites(request:HttpRequest):
    favorites = Favorite.objects.filter(user=request.user).select_related('plant').prefetch_related('plant__comments', 'plant__ratings', 'plant__countries')
    plants = [fav.plant for fav in favorites]
    
    context = {
        'plants': plants,
        'page_title': 'My Favorites'
    }
    return render(request, 'plants/favorites.html', context)


def plants_by_country(request: HttpRequest, country_id):
    country = get_object_or_404(Country, id=country_id)
    plants = Plant.objects.filter(countries=country).select_related('category').prefetch_related('comments', 'countries').order_by('-created_at')
    
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True))
    
    context = {
        'country': country,
        'plants': plants,
        'plants_count': plants.count(),
        'user_favorites': user_favorites,
        'page_title': f'Plants Native to {country.name}'
    }
    
    return render(request, 'plants/plants_by_country.html', context)


def plant_detail(request, plant_id):
    plant = get_object_or_404(Plant.objects.prefetch_related('countries'), id=plant_id)
    
    plant.increment_views()
    
    related_plants = Plant.objects.filter(category=plant.category).exclude(id=plant.id).select_related('category').prefetch_related('countries')[:3]
    comments = plant.comments.all()
    ratings = plant.ratings.all()
    
    is_favorite = False
    user_rating = None
    user_favorites = []
    if request.user.is_authenticated:
        is_favorite = plant.is_favorited_by(request.user)
        user_rating = ratings.filter(user=request.user).first()
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('plant_id', flat=True))

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to comment or rate plants.')
            return redirect('auth:login')
        
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST, user=request.user)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.plant = plant
                comment.user = request.user
                comment.name = request.user.username
                comment.save()
                messages.success(request, 'Your comment has been posted successfully!')
                return redirect('plants:detail', plant_id=plant.id)
        
        elif 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST, user=request.user)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.plant = plant
                rating.user = request.user
                rating.name = request.user.username
                
                try:
                    rating.save()
                    messages.success(request, 'Your rating has been submitted successfully!')
                except:
                    messages.error(request, 'You have already rated this plant!')
                return redirect('plants:detail', plant_id=plant.id)
    
    comment_form = CommentForm(user=request.user) if request.user.is_authenticated else None
    rating_form = RatingForm(user=request.user) if request.user.is_authenticated else None

    return render(request, 'plants/plant_detail.html', {
        'plant': plant,
        'related_plants': related_plants,
        'comments': comments,
        'ratings': ratings,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'is_favorite': is_favorite,
        'user_rating': user_rating,
        'user_favorites': user_favorites,
    })