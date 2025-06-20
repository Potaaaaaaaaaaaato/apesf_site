from pyexpat.errors import messages
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

# Modèle pour une page
class PageContent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, verbose_name="Slug (URL)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        verbose_name = "Contenu de page"
        verbose_name_plural = "Contenus de page"

    def __str__(self):
        return self.title

# Modèle pour une section dans une page
class Section(models.Model):
    UNIT_CHOICES = [
        ('marmousets', 'Marmousets'),
        ('angelus', 'Angélus'),
        ('placement_modulable', 'Placement modulable'),
        ('aemo_h', 'AEMO H'),
        ('accueil_parental', 'Accueil parental'),
        ('', 'Aucune unité'),  # Option pour les sections générales
    ]

    ORGANIGRAM_TYPE_CHOICES = [
        ('', 'Aucun'),
        ('direction', 'Direction'),
        ('structure', 'Structure'),
    ]

    page = models.ForeignKey(PageContent, on_delete=models.CASCADE, related_name='sections', verbose_name="Page associée", null=True, blank=True)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES, default='', verbose_name="Unité associée", blank=True)
    organigram_type = models.CharField(max_length=50, choices=ORGANIGRAM_TYPE_CHOICES, default='', verbose_name="Type d'organigramme", blank=True)
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    description = models.TextField(blank=True, null=True, verbose_name="Description pour l'organigramme", help_text="Description affichée dans le modal de l'organigramme entre l'image et le bouton")
    link = models.URLField(blank=True, null=True, verbose_name="Lien (optionnel)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")

    class Meta:
        ordering = ['order']
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        if self.page:
            return f"{self.title} (Section de {self.page.title})"
        elif self.organigram_type:
            return f"{self.title} (Organigramme: {self.get_organigram_type_display()})"
        return f"{self.title} (Unité: {self.get_unit_display() or 'Aucune unité'})"

    # NOUVELLE MÉTHODE : Pour préserver les sauts de ligne
    def get_formatted_content(self):
        """Retourne le contenu avec les sauts de ligne convertis en balises HTML"""
        return self.content.replace('\n', '<br>')

# Modèle pour les images uploadées (associées à une section ou une actualité)
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/', verbose_name="Image")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='images', null=True, blank=True, verbose_name="Section associée")
    news = models.ForeignKey('News', on_delete=models.CASCADE, related_name='images', null=True, blank=True, verbose_name="Actualité associée")

    class Meta:
        verbose_name = "Image uploadée"
        verbose_name_plural = "Images uploadées"

    def __str__(self):
        if self.section:
            return f"Image pour {self.section.title}"
        elif self.news:
            return f"Image pour l'actualité {self.news.title}"
        return "Image non associée"

# Modèle pour les rôles utilisateurs
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    role = models.CharField(max_length=50, choices=[
        ('superuser', 'Super utilisateur (Accès total : peut supprimer des utilisateurs et du contenu. Rôle le plus puissant.)'),
        ('admin', 'Administrateur (Peut créer, modifier et supprimer du contenu. Aucun accès aux actions irréversibles comme la suppression des utilisateurs.)'),
        ('viewer', 'Lecteur (Accès en lecture et modification mineure du texte. Aucun pouvoir sur la structure ou les utilisateurs.)'),
    ], verbose_name="Rôle")

    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Doit changer le mot de passe",
        help_text="Si coché, l'utilisateur sera obligé de changer son mot de passe à la prochaine connexion"
    )

    # NOUVEAU CHAMP pour tracer la première connexion
    first_login_completed = models.BooleanField(
        default=False,
        verbose_name="Première connexion effectuée"
    )

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Modèle pour les pièces jointes des messages de contact
class ContactMessageAttachment(models.Model):
    contact_message = models.ForeignKey('ContactMessage', on_delete=models.CASCADE, related_name='attachments', verbose_name="Message de contact")
    file = models.FileField(upload_to='contact_attachments/', verbose_name="Pièce jointe")

    class Meta:
        verbose_name = "Pièce jointe de message de contact"
        verbose_name_plural = "Pièces jointes de messages de contact"

    def __str__(self):
        return f"Pièce jointe pour {self.contact_message.name} ({self.contact_message.email})"

# Modèle pour les messages de contact
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('question', 'Question générale'),
        ('partenariat', 'Demande de partenariat'),
        ('adhesion', 'Adhésion à l’association'),
        ('don', 'Faire un don'),
        ('stage', 'Demande de stage'),
        ('candidature', 'Candidature spontanée'),
        ('evenement', 'Participer à un événement'),
        ('autre', 'Autre'),
    ]
    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Adresse email")
    subject = models.CharField(max_length=200, choices=SUBJECT_CHOICES, verbose_name="Objet", blank=True, default="")
    message = models.TextField(verbose_name="Message")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Message de {self.name} ({self.email}) - {self.submitted_at}"

# Modèle pour les partenaires
class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du partenaire")
    logo = models.ImageField(upload_to='partner_logos/', verbose_name="Logo")

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Enregistrer d'abord l'image pour accéder à son chemin
        if self.logo:
            img_path = self.logo.path
            try:
                img = Image.open(img_path)
                output_size = (90, 90)  # Taille actuelle selon ton fichier
                img.thumbnail(output_size, Image.Resampling.LANCZOS)  # Redimensionner tout en préservant les proportions
                img.save(img_path, quality=85)  # Sauvegarder l'image redimensionnée
            except Exception as e:
                print(f"Erreur lors du redimensionnement de l'image {self.logo.name} : {e}")

# Modèle pour les actualités
class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    date = models.DateField(verbose_name="Date")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name="Image principale (optionnelle)")
    document = models.FileField(upload_to='news_documents/', blank=True, null=True, verbose_name="Pièce jointe (PDF, DOCX, TXT, etc.)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['-date']  # Trie par date, les plus récentes en premier
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"

    def __str__(self):
        return self.title
    
# Modèle pour les offres d'emploi
class JobOffer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    posted_date = models.DateField(auto_now_add=True)
    email_contact = models.EmailField()  # Email pour postuler
    document = models.FileField(upload_to='job_documents/', blank=True, null=True)  # Document joint (PDF, DOCX, etc.)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-posted_date']

# Modèle pour gérer les fichiers liés aux arborescences
class ArborescenceFile(models.Model):
    title = models.CharField(max_length=200, default="Arborescence du conseil d'administration")
    file = models.FileField(upload_to='arborescence/', help_text="Fichier contenant l'arborescence du conseil d'administration")
    uploaded_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, help_text="Description du fichier")

    class Meta:
        verbose_name = "Fichier d'arborescence"
        verbose_name_plural = "Fichiers d'arborescence"

    def __str__(self):
        return self.title

# Modèle pour gérer les images du carrousel de la page d'accueil
class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel/', verbose_name="Image du carrousel")
    title = models.CharField(max_length=200, verbose_name="Titre de l'image", help_text="Texte alternatif pour l'accessibilité")
    description = models.TextField(blank=True, verbose_name="Description", help_text="Description optionnelle de l'image")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Image du carrousel"
        verbose_name_plural = "Images du carrousel"

    def __str__(self):
        return f"{self.title} (Ordre: {self.order})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            try:
                img = Image.open(img_path)
                # Redimensionner pour le carrousel (optionnel)
                if img.width > 1200 or img.height > 800:
                    output_size = (1200, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(img_path, quality=90)
            except Exception as e:
                print(f"Erreur lors du redimensionnement de l'image {self.image.name} : {e}")