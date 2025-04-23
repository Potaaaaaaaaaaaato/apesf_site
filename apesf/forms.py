from django import forms
from .models import PageContent, Section, UploadedImage, ContactMessage

class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'slug': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'title': 'Titre',
            'slug': 'Slug (URL)',
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'content', 'link', 'order', 'unit']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'rows': 5}),
            'link': forms.URLInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'order': forms.NumberInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'unit': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'link': 'Lien (optionnel)',
            'order': 'Ordre d’affichage',
            'unit': 'Unité associée',
        }

class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'section']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg'}),
            'section': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'image': 'Image',
            'section': 'Section associée',
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'placeholder': 'Votre email'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'rows': 5, 'placeholder': 'Votre message'}),
        }
        labels = {
            'name': 'Nom',
            'email': 'Adresse email',
            'message': 'Message',
        }