from django import forms
from .models import JobOffer, News, PageContent, Section, UploadedImage, ContactMessage, ContactMessageAttachment
from .models import ArborescenceFile

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
        fields = ['title', 'content', 'link', 'order', 'unit', 'organigram_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'rows': 5}),
            'link': forms.URLInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'order': forms.NumberInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'unit': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'organigram_type': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'link': 'Lien (optionnel)',
            'order': 'Ordre d’affichage',
            'unit': 'Établissement/Service associé',
            'organigram_type': 'Type d’organigramme',
        }

class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'section', 'news']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg'}),
            'section': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'news': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'image': 'Image',
            'section': 'Section associée',
            'news': 'Actualité associée',
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'placeholder': 'Votre email'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all', 'rows': 5, 'placeholder': 'Votre message'}),
        }
        labels = {
            'name': 'Nom',
            'email': 'Adresse email',
            'subject': 'Objet',
            'message': 'Message',
        }

    SUBJECT_CHOICES = [
        ('', 'Choisissez un sujet'),
        ('question', 'Question générale'),
        ('partenariat', 'Demande de partenariat'),
        ('adhesion', 'Adhésion à l\'association'),
        ('don', 'Faire un don'),
        ('stage', 'Demande de stage'),
        ('candidature', 'Candidature spontanée'),
        ('evenement', 'Participer à un événement'),
        ('autre', 'Autre'),
    ]

    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        label='Objet',
        required=True
    )

    # Ajout de champs pour les pièces jointes (optionnels)
    attachment_1 = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg'})
    )
    attachment_2 = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg'})
    )
    attachment_3 = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg'})
    )

    def __init__(self, *args, **kwargs):
        initial_subject = kwargs.pop('initial_subject', '')
        super().__init__(*args, **kwargs)
        if initial_subject:
            self.fields['subject'].initial = initial_subject

    def clean(self):
        cleaned_data = super().clean()

        # Validation des fichiers (taille, type, etc.)
        for i in range(1, 4):
            field_name = f'attachment_{i}'
            file = cleaned_data.get(field_name)
            if file:
                # Vérifier la taille du fichier (max 10MB)
                if file.size > 10 * 1024 * 1024:
                    raise forms.ValidationError(f"Le fichier {file.name} est trop volumineux (max 10MB).")

                # Vérifier les extensions autorisées
                allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
                file_extension = file.name.lower().split('.')[-1]
                if f'.{file_extension}' not in allowed_extensions:
                    raise forms.ValidationError(f"Type de fichier non autorisé pour {file.name}. Extensions autorisées: {', '.join(allowed_extensions)}")

        return cleaned_data

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'date', 'image', 'document']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 5}),
            'date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
            'document': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

# Formulaire pour les offres d'emploi
class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = ['title', 'description', 'email_contact', 'document']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 5}),
            'email_contact': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded'}),
            'document': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

class ArborescenceFileForm(forms.ModelForm):
    class Meta:
        model = ArborescenceFile
        fields = ['title', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du fichier'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description optionnelle'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.txt'})
        }