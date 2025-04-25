from django.contrib import admin
from .models import ContactMessage, News, PageContent, Section, UploadedImage, UserProfile, Partner

# Inline pour gérer les sections dans l'édition d'une page
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1  # Nombre de formulaires vides affichés par défaut
    fields = ('title', 'content', 'link', 'order')  # Champs affichés dans l'inline
    verbose_name = "Section"  # Nom en français pour une section individuelle
    verbose_name_plural = "Sections"  # Nom en français pour plusieurs sections

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
    list_display = ('title', 'page', 'order', 'created_at', 'updated_at')  # Champs dans la liste
    list_filter = ('page', 'created_at', 'updated_at')  # Filtres par page et dates
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
    list_display = ('image', 'section', 'uploaded_at')  # Champs dans la liste
    list_filter = ('uploaded_at', 'section')  # Filtres par date et section
    search_fields = ('image',)  # Recherche par nom de fichier
    list_select_related = ('section',)  # Optimise les requêtes SQL pour la section associée
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
    list_display = ('name', 'email', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    ordering = ('-submitted_at',)

    # Seuls les superusers et admins peuvent voir/modifier les messages
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

# Administration du modèle Partner (ajouté)
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Champs dans la liste
    search_fields = ('name',)  # Recherche par nom du partenaire
    ordering = ('name',)  # Trie par nom

    # Noms en français pour l'interface admin
    verbose_name = "Partenaire"
    verbose_name_plural = "Partenaires"

    # Seuls les superusers et admins peuvent gérer les partenaires
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
    
# Administration du modèle News
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')  # Champs dans la liste
    list_filter = ('date', 'created_at')  # Filtres par date
    search_fields = ('title', 'content')  # Recherche par titre ou contenu
    ordering = ('-date',)  # Trie par date décroissante

    # Noms en français pour l'interface admin
    verbose_name = "Actualité"
    verbose_name_plural = "Actualités"

    # Seuls les superusers et admins peuvent gérer les actualités
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