from django import forms
from .models import PageContent, Section, UploadedImage, ContactMessage

class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        # Ajout de labels en français pour plus de clarté dans les templates
        labels = {
            'title': 'Titre',
            'slug': 'Slug (URL)',
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'content', 'link', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        # Ajout de labels en français pour plus de clarté dans les templates
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'link': 'Lien (optionnel)',
            'order': 'Ordre d’affichage',
        }

class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'section']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
        }
        # Ajout de labels en français pour plus de clarté dans les templates
        labels = {
            'image': 'Image',
            'section': 'Section associée',
        }

# Formulaire pour le message de contact
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Votre message'}),
        }
        labels = {
            'name': 'Nom',
            'email': 'Adresse email',
            'message': 'Message',
        }