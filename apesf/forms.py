from django import forms
from .models import JobOffer, News, PageContent, Section, UploadedImage, ContactMessage, ContactMessageAttachment
from .models import ArborescenceFile
from django.contrib.auth.forms import PasswordChangeForm

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
            # MODIFICATION : Ajout de placeholder pour expliquer les sauts de ligne
            'content': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all',
                'rows': 8,
                'placeholder': 'Saisissez le contenu de la section. Les sauts de ligne seront préservés dans l\'affichage.'
            }),
            'link': forms.URLInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'order': forms.NumberInput(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'unit': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
            'organigram_type': forms.Select(attrs={'class': 'w-full p-3 border border-neutral-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all'}),
        }
        labels = {
            'title': 'Titre',
            'content': 'Contenu (les sauts de ligne seront préservés)',
            'link': 'Lien (optionnel)',
            'order': 'Ordre d\'affichage',
            'unit': 'Établissement/Service associé',
            'organigram_type': 'Type d\'organigramme',
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

        # AJOUT DE LA CORRESPONDANCE ENTRE LES PARAMÈTRES URL ET LES VALEURS DU FORMULAIRE
        if initial_subject:
            # Dictionnaire de correspondance entre les valeurs URL et les clés du formulaire
            subject_mapping = {
                'Candidature spontanée': 'candidature',
                'Demande de stage': 'stage',
                'Question générale': 'question',
                'Demande de partenariat': 'partenariat',
                'Adhésion à l\'association': 'adhesion',
                'Faire un don': 'don',
                'Participer à un événement': 'evenement',
                'Autre': 'autre',
            }

            # Utiliser la correspondance ou la valeur directe si elle existe déjà dans les choix
            mapped_subject = subject_mapping.get(initial_subject, initial_subject)

            # Vérifier que la valeur mappée existe dans les choix
            choice_keys = [choice[0] for choice in self.SUBJECT_CHOICES]
            if mapped_subject in choice_keys:
                self.fields['subject'].initial = mapped_subject
            else:
                # Debug : afficher les valeurs pour comprendre le problème
                print(f"Valeur reçue: '{initial_subject}'")
                print(f"Valeur mappée: '{mapped_subject}'")
                print(f"Choix disponibles: {choice_keys}")

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

class ForcePasswordChangeForm(PasswordChangeForm):
    """Formulaire pour forcer le changement de mot de passe"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border rounded-lg focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Votre mot de passe actuel'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border rounded-lg focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Nouveau mot de passe'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border rounded-lg focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirmez le nouveau mot de passe'
        })

        # Labels en français
        self.fields['old_password'].label = "Mot de passe actuel"
        self.fields['new_password1'].label = "Nouveau mot de passe"
        self.fields['new_password2'].label = "Confirmez le nouveau mot de passe"