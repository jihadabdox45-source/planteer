from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


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
    image_url = models.URLField(max_length=500)
    category = models.CharField(
        max_length=20, 
        choices=PlantCategory.choices,
        db_index=True
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


class Comment(models.Model):
    plant = models.ForeignKey(
        Plant, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    name = models.CharField(max_length=100, verbose_name='Name')
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['plant', '-created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.plant.name}'


class Rating(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    name = models.CharField(max_length=100, verbose_name='Name')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['plant', 'name']
        indexes = [
            models.Index(fields=['plant', '-created_at']),
        ]

    def __str__(self):
        return f'{self.score} stars by {self.name} for {self.plant.name}'


