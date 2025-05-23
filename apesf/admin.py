from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, ContactMessageAttachment, News, PageContent, Section, UploadedImage, UserProfile, Partner

# Inline pour gérer les sections dans l'édition d'une page
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1  # Nombre de formulaires vides affichés par défaut
    fields = ('title', 'content', 'link', 'order', 'unit', 'organigram_type')  # Ajout de organigram_type
    verbose_name = "Section"  # Nom en français pour une section individuelle
    verbose_name_plural = "Sections"  # Nom en français pour plusieurs sections

# Inline pour gérer les pièces jointes dans l'édition d'un message de contact
class ContactMessageAttachmentInline(admin.TabularInline):
    model = ContactMessageAttachment
    extra = 1  # Nombre de formulaires vides affichés par défaut
    fields = ('file', 'file_link')  # Ajoute un champ pour le lien cliquable
    readonly_fields = ('file_link',)  # Le lien est en lecture seule
    verbose_name = "Pièce jointe"
    verbose_name_plural = "Pièces jointes"

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.file.url)
        return "-"
    file_link.short_description = "Lien"

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')  # Champs dans la liste
    list_filter = ('created_at', 'updated_at')  # Filtres dans la barre latérale
    search_fields = ('title', 'slug')  # Recherche par titre ou slug
    prepopulated_fields = {'slug': ('title',)}  # Préremplit le slug à partir du titre
    inlines = [SectionInline]  # Ajoute les sections en inline
    ordering = ('-created_at',)  # Trie par date de création décroissante

    # Noms en français pour l'interface admin
    verbose_name = "Contenu de page"
    verbose_name_plural = "Contenus de page"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'unit', 'organigram_type', 'order', 'created_at', 'updated_at')  # Ajout de 'organigram_type'
    list_filter = ('page', 'unit', 'organigram_type', 'created_at', 'updated_at')  # Filtres par page, unité, type d'organigramme et dates
    search_fields = ('title', 'content')  # Recherche par titre ou contenu
    list_select_related = ('page',)  # Optimise les requêtes SQL pour la page associée
    ordering = ('order',)  # Trie par ordre d’affichage

    # Noms en français pour l'interface admin
    verbose_name = "Section"
    verbose_name_plural = "Sections"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'section', 'news', 'uploaded_at')  # Ajout de 'news'
    list_filter = ('uploaded_at', 'section', 'news')  # Filtres par date, section et actualité
    search_fields = ('image',)  # Recherche par nom de fichier
    list_select_related = ('section', 'news')  # Optimise les requêtes SQL
    ordering = ('-uploaded_at',)  # Trie par date d’upload décroissante

    # Noms en français pour l'interface admin
    verbose_name = "Image uploadée"
    verbose_name_plural = "Images uploadées"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Champs dans la liste
    list_filter = ('role',)  # Filtre par rôle
    search_fields = ('user__username',)  # Recherche par nom d’utilisateur
    ordering = ('user__username',)  # Trie par nom d’utilisateur

    # Noms en français pour l'interface admin
    verbose_name = "Profil utilisateur"
    verbose_name_plural = "Profils utilisateurs"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role == 'superuser'  # Seuls les superusers peuvent voir/modifier les profils
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at', 'subject')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-submitted_at',)
    inlines = [ContactMessageAttachmentInline]
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Les messages sélectionnés ont été marqués comme lus.")
    mark_as_read.short_description = "Marquer comme lu"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    verbose_name = "Partenaire"
    verbose_name_plural = "Partenaires"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-date',)

    verbose_name = "Actualité"
    verbose_name_plural = "Actualités"

    def has_view_or_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            profile = request.user.userprofile
            return profile.role in ['superuser', 'admin']
        except UserProfile.DoesNotExist:
            return False

    def has_add_permission(self, request):
        return self.has_view_or_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_view_or_change_permission(request)

@admin.register(ContactMessageAttachment)
class ContactMessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('contact_message', 'file_name', 'file_link')
    search_fields = ('contact_message__name', 'contact_message__email', 'file')
    list_filter = ('contact_message__submitted_at',)

    def file_name(self, obj):
        return obj.file.name.split('/')[-1]
    file_name.short_description = "Nom du fichier"

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Ouvrir</a>', obj.file.url)
        return "-"
    file_link.short_description = "Lien"