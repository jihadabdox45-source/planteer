from django import forms
from .models import Plant, Comment, Rating


class PlantForm(forms.ModelForm):
    
    class Meta:
        model = Plant
        fields = [
            'name',
            'scientific_name',
            'description',
            'image_url',
            'category',
            'is_edible',
            'sunlight',
            'water_needs',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monstera Deliciosa',
                'required': True,
                'minlength': 2,
                'maxlength': 100,
            }),
            'scientific_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monstera deliciosa',
                'required': True,
                'minlength': 2,
                'maxlength': 150,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the plant, its characteristics, and care tips...',
                'required': True,
                'minlength': 10,
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg',
                'required': True,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'is_edible': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'sunlight': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Full sun, Partial shade',
                'required': True,
                'maxlength': 100,
            }),
            'water_needs': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Moderate, Once a week',
                'required': True,
                'maxlength': 100,
            }),
        }
        labels = {
            'name': 'Plant Name',
            'scientific_name': 'Scientific Name',
            'description': 'Description',
            'image_url': 'Image URL',
            'category': 'Category',
            'is_edible': 'Is this plant edible?',
            'sunlight': 'Sunlight Requirements',
            'water_needs': 'Water Requirements',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Plant name must be at least 2 characters long.')
        return name

    def clean_scientific_name(self):
        scientific_name = self.cleaned_data.get('scientific_name', '').strip()
        if len(scientific_name) < 2:
            raise forms.ValidationError('Scientific name must be at least 2 characters long.')
        return scientific_name

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long.')
        return description


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name',
                'required': True,
                'minlength': 2,
                'maxlength': 100,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about this plant...',
                'required': True,
                'minlength': 5,
            }),
        }
        labels = {
            'name': 'Your Name',
            'content': 'Your Comment',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters long.')
        return name

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters long.')
        return content


class RatingForm(forms.ModelForm):
    
    class Meta:
        model = Rating
        fields = ['name', 'score']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name',
                'required': True,
                'minlength': 2,
                'maxlength': 100,
            }),
            'score': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'form-select',
                    'required': True,
                }
            ),
        }
        labels = {
            'name': 'Your Name',
            'score': 'Rating',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters long.')
        return name
