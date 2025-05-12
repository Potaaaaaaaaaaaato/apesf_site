from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apesf.views import erreur_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apesf.urls')),
]

# Ajouter la gestion des fichiers médias (toujours actif, même en production pour le développement local)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apesf.views.erreur_404' 

