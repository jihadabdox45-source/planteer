from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Country Name')
    flag = models.URLField(max_length=500, verbose_name='Flag Image URL', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name
    
    def plants_count(self):
        return self.plants.count()
    plants_count.short_description = 'Plants Count'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def plants_count(self):
        return self.plants.count()
    plants_count.short_description = 'Plants Count'


class PlantCategory(models.TextChoices):
    INDOOR = 'indoor', 'Indoor'
    OUTDOOR = 'outdoor', 'Outdoor'
    HERB = 'herb', 'Herb'
    FRUIT = 'fruit', 'Fruit'
    VEGETABLE = 'vegetable', 'Vegetable'
    MEDICINAL = 'medicinal', 'Medicinal'
    FLOWERING = 'flowering', 'Flowering'


class Plant(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    scientific_name = models.CharField(max_length=150)
    description = models.TextField()
    image_url = models.URLField(max_length=500, verbose_name='Primary Image URL')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        related_name='plants',
        null=True,
        blank=True
    )
    countries = models.ManyToManyField(
        Country,
        related_name='plants',
        blank=True,
        verbose_name='Native Countries'
    )
    is_edible = models.BooleanField(default=False, db_index=True)
    sunlight = models.CharField(max_length=100)
    water_needs = models.CharField(max_length=100)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
        indexes = [
            models.Index(fields=['-created_at', 'category']),
            models.Index(fields=['-views_count']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plants:detail', kwargs={'plant_id': self.pk})

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.score for r in ratings) / len(ratings), 1)
        return 0

    def rating_count(self):
        return self.ratings.count()

    def favorites_count(self):
        """عدد المستخدمين الذين أضافوا هذا النبات للمفضلة"""
        return self.favorited_by.count()
    
    def is_favorited_by(self, user):
        """التحقق من إضافة المستخدم لهذا النبات للمفضلة"""
        if user.is_authenticated:
            return self.favorited_by.filter(user=user).exists()
        return False
    
    def get_primary_image(self):
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image_url
        elif self.image_url:
            return self.image_url
        elif self.images.exists():
            return self.images.first().image_url
        return None
    
    def get_all_images(self):
        images = list(self.images.all())
        if self.image_url:
            primary_exists = any(img.image_url == self.image_url for img in images)
            if not primary_exists:
                images.insert(0, type('obj', (object,), {
                    'image_url': self.image_url,
                    'caption': 'Primary Image',
                    'is_primary': True
                }))
        return images
    
    def get_category_display(self):
        """عرض اسم الفئة"""
        if self.category:
            return self.category.name
        return 'Uncategorized'


class PlantImage(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, verbose_name='Image URL')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Caption')
    is_primary = models.BooleanField(default=False, verbose_name='Primary Image')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        verbose_name = 'Plant Image'
        verbose_name_plural = 'Plant Images'
    
    def __str__(self):
        return f"{self.plant.name} - {self.caption or 'Image'}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            PlantImage.objects.filter(plant=self.plant, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Comment(models.Model):
    plant = models.ForeignKey(
        Plant, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments', 
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['plant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.get_author_name()} on {self.plant.name}'
    
    def get_author_name(self):
        """الحصول على اسم الكاتب سواء كان مسجلاً أو ضيف"""
        return self.user.username if self.user else self.name


class Rating(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name='Name', blank=True, null=True)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        indexes = [
            models.Index(fields=['plant', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['plant', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_rating'
            ),
            models.UniqueConstraint(
                fields=['plant', 'name'],
                condition=models.Q(user__isnull=True),
                name='unique_guest_rating'
            ),
        ]

    def __str__(self):
        return f'{self.score} stars by {self.get_author_name()} for {self.plant.name}'
    
    def get_author_name(self):
        """الحصول على اسم الكاتب سواء كان مسجلاً أو ضيف"""
        return self.user.username if self.user else self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'plant']
        ordering = ['-created_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['plant', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.plant.name}"


