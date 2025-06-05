import os

from django.core.mail import EmailMessage
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContactMessage, ContactMessageAttachment, JobOffer, PageContent, Partner, Section, UploadedImage, \
    News, UserProfile
from .forms import ContactForm, JobOfferForm, PageContentForm, SectionForm, UploadedImageForm, NewsForm
from .models import ArborescenceFile
from .forms import ArborescenceFileForm
from .forms import ForcePasswordChangeForm
import json
from .models import CarouselImage
from .forms import CarouselImageForm, CarouselOrderForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models

# Page d'accueil
def accueil(request):
    try:
        page = PageContent.objects.get(slug='accueil')
    except PageContent.DoesNotExist:
        page = None

    # MODIFICATION : Utiliser les images du carrousel au lieu des UploadedImage
    carousel_images = CarouselImage.objects.filter(is_active=True).order_by('order')

    # Récupérer les 5 dernières actualités pour le carrousel d'actualités
    news_items = News.objects.prefetch_related('images').all().order_by('-date')[:5]

    return render(request, 'accueil.html', {
        'page': page,
        'carousel_images': carousel_images,
        'news_items': news_items
    })

# Page "Nos établissements & services"
def qui_sommes_nous(request):
    # Récupérer le paramètre 'unit' depuis l'URL
    selected_unit = request.GET.get('unit', '')

    # Liste des unités disponibles
    valid_units = ['marmousets', 'angelus', 'placement_modulable', 'aemo_h', 'accueil_parental']

    # Vérifier si l'unité sélectionnée est valide
    if selected_unit not in valid_units:
        selected_unit = ''

    # Récupérer les sections pour l'unité sélectionnée
    if selected_unit:
        sections = Section.objects.filter(unit=selected_unit)
    else:
        sections = None

    return render(request, 'qui_sommes_nous.html', {
        'selected_unit': selected_unit,
        'sections': sections,
        'valid_units': valid_units,
    })

# Page "Organisation"
def organisation(request):
    try:
        page = PageContent.objects.get(slug='organisation')
    except PageContent.DoesNotExist:
        page = None

    # Récupérer les sections pour les organigrammes
    direction_sections = Section.objects.filter(page=page, organigram_type='direction')
    structure_sections = Section.objects.filter(page=page, organigram_type='structure')

    # Vérifier si le fichier d'arborescence est disponible
    arborescence_file_available = False
    try:
        # Vérifier s'il existe un fichier d'arborescence en base de données
        arborescence = ArborescenceFile.objects.latest('uploaded_at')
        # Vérifier si le fichier existe physiquement sur le serveur
        if arborescence.file and os.path.exists(arborescence.file.path):
            arborescence_file_available = True
    except ArborescenceFile.DoesNotExist:
        pass
    except Exception:
        # En cas d'erreur (fichier corrompu, etc.), considérer comme non disponible
        pass

    return render(request, 'organisation.html', {
        'page': page,
        'direction_sections': direction_sections,
        'structure_sections': structure_sections,
        'arborescence_file_available': arborescence_file_available,
    })

# Page "Partenaires"
def partenaires(request):
    try:
        page = PageContent.objects.get(slug='partenaires')
    except PageContent.DoesNotExist:
        page = None
    partners = Partner.objects.all()
    return render(request, 'partenaires.html', {'page': page, 'partners': partners})

# Page "Dons"
def dons(request):
    try:
        page = PageContent.objects.get(slug='dons')
    except PageContent.DoesNotExist:
        page = None
    return render(request, 'dons.html', {'page': page})

# Page "Rejoignez-nous"
def rejoignez_nous(request):
    try:
        page = PageContent.objects.get(slug='rejoignez-nous')
    except PageContent.DoesNotExist:
        page = None
    return render(request, 'rejoignez_nous.html', {'page': page})

# Page de connexion
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # NOUVELLE LOGIQUE : Vérifier si l'utilisateur doit changer son mot de passe
            try:
                profile = user.userprofile
                if profile.must_change_password:
                    messages.warning(request, "Pour des raisons de sécurité, vous devez changer votre mot de passe avant de continuer.")
                    return redirect('forcer_changement_mot_de_passe')
            except UserProfile.DoesNotExist:
                # Si pas de profil, en créer un avec changement de mot de passe obligatoire
                UserProfile.objects.create(user=user, role='viewer', must_change_password=True)
                return redirect('forcer_changement_mot_de_passe')

            return redirect('tableau_de_bord')
        else:
            return render(request, 'connexion.html', {'error': 'Identifiants incorrects, veuillez réessayer.'})
    return render(request, 'connexion.html')

# Page de déconnexion
def deconnexion(request):
    logout(request)
    return redirect('accueil')

# Tableau de bord admin
@login_required
def tableau_de_bord(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page. Contactez un administrateur.")
        return redirect('accueil')

    pages = PageContent.objects.all()
    messages_contact = ContactMessage.objects.all()
    images = UploadedImage.objects.all()
    news_items = News.objects.all()

    # Gestion de l'ajout d'une actualité
    if request.method == 'POST' and 'add_news' in request.POST:
        news_form = NewsForm(request.POST, request.FILES)
        if news_form.is_valid():
            news_form.save()
            messages.success(request, "Actualité ajoutée avec succès !")
            return redirect('tableau_de_bord')
    else:
        news_form = NewsForm()

    return render(request, 'tableau_de_bord.html', {
        'pages': pages,
        'messages_contact': messages_contact,
        'images': images,
        'news_items': news_items,
        'news_form': news_form,
    })

# Ajouter une nouvelle page
@login_required
def ajouter_page(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour ajouter une page. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        form = PageContentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Page ajoutée avec succès ! Les modifications sont visibles sur le site instantanément.")
            return redirect('tableau_de_bord')
    else:
        form = PageContentForm()
    return render(request, 'ajouter_page.html', {'form': form})

# Modifier une page
@login_required
def modifier_page(request, page_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour modifier une page. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    page = get_object_or_404(PageContent, id=page_id)
    if request.method == 'POST':
        form = PageContentForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, "Page modifiée avec succès ! Les modifications sont visibles sur le site instantanément.")
            return redirect('tableau_de_bord')
    else:
        form = PageContentForm(instance=page)
    return render(request, 'modifier_page.html', {'form': form, 'page': page})

# Ajouter une section à une page
@login_required
def ajouter_section(request, page_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour ajouter une section. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    page = get_object_or_404(PageContent, id=page_id)
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.page = page
            section.save()
            # Gérer les images téléchargées
            images = request.FILES.getlist('images')
            for image in images:
                UploadedImage.objects.create(section=section, image=image)
            messages.success(request, "Section ajoutée avec succès ! Les modifications sont visibles sur le site instantanément.")
            return redirect('modifier_page', page_id=page.id)
    else:
        form = SectionForm()
    return render(request, 'ajouter_section.html', {'form': form, 'page': page})

# Modifier une section
@login_required
def modifier_section(request, section_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour modifier une section.")
        return redirect('tableau_de_bord')

    section = get_object_or_404(Section, id=section_id)
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            # Gérer les images téléchargées
            images = request.FILES.getlist('images')
            for image in images:
                UploadedImage.objects.create(section=section, image=image)
            messages.success(request, "Section modifiée avec succès !")
            # Rediriger en fonction de si la section est associée à une page ou une unité
            if section.page and isinstance(section.page, PageContent):
                return redirect('gerer_sections', page_id=section.page.id)
            elif section.unit:
                return redirect('gerer_sections_unite', unit=section.unit)
            elif section.organigram_type:
                return redirect('gerer_organigrammes')
            else:
                messages.warning(request, "La section n'est associée ni à une page ni à une unité ni à un organigramme. Redirection vers le tableau de bord.")
                return redirect('tableau_de_bord')
    else:
        form = SectionForm(instance=section)
    return render(request, 'modifier_section.html', {'form': form, 'section': section})

# Uploader une image
@login_required
def telecharger_image(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour uploader une image. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        form = UploadedImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image uploadée avec succès !")
            return redirect('tableau_de_bord')
    else:
        form = UploadedImageForm()
    return render(request, 'telecharger_image.html', {'form': form})

# Gestion des organigrammes
@login_required
def gerer_organigrammes(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    try:
        page = PageContent.objects.get(slug='organisation')
    except PageContent.DoesNotExist:
        messages.error(request, "La page 'Organisation' n'existe pas. Veuillez la créer d'abord.")
        return redirect('tableau_de_bord')

    sections = Section.objects.filter(page=page)

    if request.method == 'POST':
        # Gestion de la suppression
        if 'section_id' in request.POST:
            section_id = request.POST.get('section_id')
            section = get_object_or_404(Section, id=section_id, page=page)
            section.delete()
            messages.success(request, "Section supprimée avec succès !")
            return redirect('gerer_organigrammes')
        # Gestion de la création
        else:
            form = SectionForm(request.POST, request.FILES)
            if form.is_valid():
                section = form.save(commit=False)
                section.page = page
                section.save()
                # Gérer les images téléchargées
                images = request.FILES.getlist('images')
                for image in images:
                    UploadedImage.objects.create(section=section, image=image)
                messages.success(request, "Section ajoutée avec succès !")
                return redirect('gerer_organigrammes')

    else:
        form = SectionForm()

    return render(request, 'gerer_organigrammes.html', {
        'page': page,
        'sections': sections,
        'form': form,
    })

# Gestionnaire d'erreur 404
def erreur_404(request, exception):
    return render(request, '404.html', status=404)

# Marquer un message comme lu
@login_required
def mark_message_as_read(request, message_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour effectuer cette action. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    message = get_object_or_404(ContactMessage, id=message_id)
    if not message.is_read:
        message.is_read = True
        message.save()
        messages.success(request, "Message marqué comme lu.")
    return redirect('tableau_de_bord')

# Vue pour gérer les sections d'une page (suppression et création)
@login_required
def gerer_sections(request, page_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    page = get_object_or_404(PageContent, id=page_id)
    sections = page.sections.all()

    if request.method == 'POST':
        # Gestion de la suppression
        if 'section_id' in request.POST:
            section_id = request.POST.get('section_id')
            section = get_object_or_404(Section, id=section_id, page=page)
            section.delete()
            messages.success(request, "Section supprimée avec succès !")
            return redirect('gerer_sections', page_id=page.id)
        # Gestion de la création
        else:
            form = SectionForm(request.POST, request.FILES)
            if form.is_valid():
                section = form.save(commit=False)
                section.page = page
                section.save()
                # Gérer les images téléchargées
                images = request.FILES.getlist('images')
                for image in images:
                    UploadedImage.objects.create(section=section, image=image)
                messages.success(request, "Section ajoutée avec succès !")
                return redirect('gerer_sections', page_id=page.id)

    else:
        form = SectionForm()

    return render(request, 'gerer_sections.html', {'page': page, 'sections': sections, 'form': form})

# Nouvelle vue pour gérer les sections par unité
@login_required
def gerer_sections_unite(request, unit):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    # Vérifier que l'unité est valide
    valid_units = ['marmousets', 'angelus', 'placement_modulable', 'aemo_h', 'accueil_parental']
    if unit not in valid_units:
        messages.error(request, "Unité invalide.")
        return redirect('tableau_de_bord')

    sections = Section.objects.filter(unit=unit)

    if request.method == 'POST':
        # Gestion de la suppression
        if 'section_id' in request.POST:
            section_id = request.POST.get('section_id')
            section = get_object_or_404(Section, id=section_id, unit=unit)
            section.delete()
            messages.success(request, "Section supprimée avec succès !")
            return redirect('gerer_sections_unite', unit=unit)
        # Gestion de la création
        else:
            form = SectionForm(request.POST, request.FILES)
            if form.is_valid():
                section = form.save(commit=False)
                section.unit = unit  # Associer la section à l'unité
                section.save()
                # Gérer les images téléchargées
                images = request.FILES.getlist('images')
                for image in images:
                    UploadedImage.objects.create(section=section, image=image)
                messages.success(request, "Section ajoutée avec succès !")
                return redirect('gerer_sections_unite', unit=unit)

    else:
        form = SectionForm()

    return render(request, 'gerer_sections_unite.html', {
        'unit': unit,
        'sections': sections,
        'form': form,
        'unit_display': dict(Section.UNIT_CHOICES).get(unit, 'Unité inconnue')
    })

# Supprimer un message de contact
@login_required
def supprimer_message(request, message_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour effectuer cette action.")
        return redirect('tableau_de_bord')

    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    messages.success(request, "Message supprimé avec succès !")
    return redirect('tableau_de_bord')

# Modifier une image
@login_required
def modifier_image(request, image_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour modifier une image. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    image = get_object_or_404(UploadedImage, id=image_id)
    if request.method == 'POST':
        form = UploadedImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, "Image modifiée avec succès !")
            return redirect('tableau_de_bord')
    else:
        form = UploadedImageForm(instance=image)
    return render(request, 'modifier_image.html', {'form': form, 'image': image})

# Supprimer une image
@login_required
def supprimer_image(request, image_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour supprimer une image. Contactez un administrateur.")
        return redirect('tableau_de_bord')

    image = get_object_or_404(UploadedImage, id=image_id)
    image.delete()
    messages.success(request, "Image supprimée avec succès !")
    return redirect('tableau_de_bord')

# Nouvelle vue pour gérer les actualités (suppression et création)
@login_required
def gerer_actualites(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    news_items = News.objects.all()

    if request.method == 'POST':
        # Gestion de la suppression
        if 'news_id' in request.POST:
            news_id = request.POST.get('news_id')
            news = get_object_or_404(News, id=news_id)
            news.delete()
            messages.success(request, "Actualité supprimée avec succès !")
            return redirect('gerer_actualites')
        # Gestion de la création
        else:
            form = NewsForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Actualité ajoutée avec succès !")
                return redirect('gerer_actualites')

    else:
        form = NewsForm()

    return render(request, 'gerer_actualites.html', {'news_items': news_items, 'form': form})

# Modifier une actualité
@login_required
def modifier_actualite(request, news_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour modifier une actualité.")
        return redirect('tableau_de_bord')

    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Actualité modifiée avec succès !")
            return redirect('gerer_actualites')
    else:
        form = NewsForm(instance=news)
    return render(request, 'modifier_actualite.html', {'form': form, 'news': news})

# Page "Mentions légales"
def mentions_legales(request):
    return render(request, 'mentions_legales.html')

# Page "Crédits"
def credits(request):
    return render(request, 'credits.html')

# Page "Panel admin"
def panel_admin(request):
    return render(request, 'panel_admin.html')

# Page "Offres d'emplois"
def offres_emplois(request):
    try:
        page = PageContent.objects.get(slug='offres-emplois')
    except PageContent.DoesNotExist:
        page = None

    job_offers = JobOffer.objects.all()
    return render(request, 'offres_emplois.html', {'page': page, 'job_offers': job_offers})

# Nouvelle vue pour gérer les offres d'emploi (suppression et création)
@login_required
def gerer_offres_emplois(request):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    job_offers = JobOffer.objects.all()

    if request.method == 'POST':
        # Gestion de la suppression
        if 'job_id' in request.POST:
            job_id = request.POST.get('job_id')
            job = get_object_or_404(JobOffer, id=job_id)
            job.delete()
            messages.success(request, "Offre d'emploi supprimée avec succès !")
            return redirect('gerer_offres_emplois')
        # Gestion de la création
        else:
            form = JobOfferForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Offre d'emploi ajoutée avec succès !")
                return redirect('gerer_offres_emplois')

    else:
        form = JobOfferForm()

    return render(request, 'gerer_offres_emplois.html', {'job_offers': job_offers, 'form': form})

# Modifier une offre d'emploi
@login_required
def modifier_offre_emploi(request, job_id):
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour modifier une offre d'emploi.")
        return redirect('tableau_de_bord')

    job = get_object_or_404(JobOffer, id=job_id)
    if request.method == 'POST':
        form = JobOfferForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Offre d'emploi modifiée avec succès !")
            return redirect('gerer_offres_emplois')
    else:
        form = JobOfferForm(instance=job)
    return render(request, 'modifier_offre_emploi.html', {'form': form, 'job': job})

def contact_view(request):
    try:
        page = PageContent.objects.get(slug='contact')
    except PageContent.DoesNotExist:
        page = None

    initial_subject = request.GET.get('subject', '')

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, initial_subject=initial_subject)
        print("Formulaire soumis, validation en cours...")

        if form.is_valid():
            print("Formulaire valide, enregistrement du message...")
            contact_message = form.save()

            # Traitement des pièces jointes du formulaire
            attachments_added = []
            for i in range(1, 4):  # Pour les 3 champs de pièces jointes
                field_name = f'attachment_{i}'
                file = form.cleaned_data.get(field_name)
                if file:
                    print(f"Enregistrement de la pièce jointe : {field_name} - {file.name}")
                    attachment = ContactMessageAttachment.objects.create(
                        contact_message=contact_message,
                        file=file
                    )
                    attachments_added.append(attachment)

            # Traitement des pièces jointes dynamiques (JavaScript)
            for key, file in request.FILES.items():
                if key.startswith('attachment_') and key not in [f'attachment_{i}' for i in range(1, 4)]:
                    print(f"Enregistrement de la pièce jointe dynamique : {key} - {file.name}")
                    attachment = ContactMessageAttachment.objects.create(
                        contact_message=contact_message,
                        file=file
                    )
                    attachments_added.append(attachment)

            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message_content = form.cleaned_data.get('message')
            subject_display = dict(form.fields['subject'].choices).get(subject, subject)
            print(f"Préparation de l'email - Objet : {subject_display}")

            # Corps de l'email
            email_body = f"""
Un message a été transmis via le formulaire de contact du site https://tristan-devaux.fr.
Pour répondre, utilisez l'adresse e-mail indiquée dans le message.
Attention : ne répondez pas directement à cet e-mail, votre réponse ne sera pas consultée.

Contenu du message :

Nom et prénom : {name}
Adresse mail : {email}
Objet : {subject_display}
Message :

{message_content}

{f"Nombre de pièces jointes : {len(attachments_added)}" if attachments_added else "Aucune pièce jointe"}
"""

            # Définir les destinataires
            recipients = ['tristandevaux6@gmail.com'] if subject in ['partenariat', 'don'] else ['tristandevaux6@gmail.com']
            print(f"Destinataires choisis : {recipients}")

            # Créer l'email
            email_message = EmailMessage(
                subject=f"[APESF] {subject_display}",
                body=email_body,
                from_email='tristandevaux6@gmail.com',  # Remplacez par votre vrai email
                to=recipients,
                reply_to=[email],
            )

            # Ajouter les pièces jointes
            for attachment in attachments_added:
                try:
                    with attachment.file.open('rb') as f:
                        print(f"Ajout de la pièce jointe : {attachment.file.name}")

                        # Déterminer le type MIME
                        import mimetypes
                        mime_type, _ = mimetypes.guess_type(attachment.file.name)
                        if mime_type is None:
                            mime_type = 'application/octet-stream'

                        email_message.attach(
                            attachment.file.name.split('/')[-1],  # Nom du fichier seulement
                            f.read(),
                            mime_type
                        )
                except Exception as e:
                    print(f"Erreur lors de l'ajout de la pièce jointe {attachment.file.name} : {str(e)}")

            try:
                print("Tentative d'envoi de l'email...")
                email_message.send()
                print(f"Email envoyé avec succès aux destinataires : {recipients}")
                success_message = "Votre message a été envoyé avec succès !"
                if attachments_added:
                    success_message += f" {len(attachments_added)} pièce(s) jointe(s) incluse(s)."
                success_message += " Nous vous répondrons dans les plus brefs délais."
                messages.success(request, success_message)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email : {str(e)}")
                messages.error(request, f"Une erreur est survenue lors de l'envoi de votre message : {str(e)}")

            return redirect('contact')
        else:
            print("Formulaire non valide, erreurs : {}".format(form.errors))
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        # CORRECTION : utiliser initial_subject au lieu de initial={'subject': initial_subject}
        form = ContactForm(initial_subject=initial_subject)

    return render(request, 'contact.html', {'page': page, 'form': form})

@login_required
def download_arborescence(request):
    """Vue pour télécharger le fichier d'arborescence"""
    try:
        # Récupérer le fichier le plus récent
        arborescence = ArborescenceFile.objects.latest('uploaded_at')
        return FileResponse(
            arborescence.file.open(),
            as_attachment=True,
            filename=f"arborescence_conseil_administration.{arborescence.file.name.split('.')[-1]}"
        )
    except ArborescenceFile.DoesNotExist:
        raise Http404("Aucun fichier d'arborescence disponible")

@login_required
def gerer_fichier_arborescence(request):
    """Vue pour gérer le fichier d'arborescence"""
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('tableau_de_bord')

    try:
        arborescence = ArborescenceFile.objects.latest('uploaded_at')
    except ArborescenceFile.DoesNotExist:
        arborescence = None

    if request.method == 'POST':
        form = ArborescenceFileForm(request.POST, request.FILES, instance=arborescence)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fichier d\'arborescence mis à jour avec succès!')
            return redirect('gerer_fichier_arborescence')
    else:
        form = ArborescenceFileForm(instance=arborescence)

    return render(request, 'gerer_fichier_arborescence.html', {
        'form': form,
        'arborescence': arborescence
    })

# NOUVELLE VUE : Forcer le changement de mot de passe
@login_required
def forcer_changement_mot_de_passe(request):
    """Vue pour forcer l'utilisateur à changer son mot de passe"""

    # Vérifier si l'utilisateur doit vraiment changer son mot de passe
    try:
        profile = request.user.userprofile
        if not profile.must_change_password:
            return redirect('tableau_de_bord')
    except UserProfile.DoesNotExist:
        # Créer un profil s'il n'existe pas
        profile = UserProfile.objects.create(
            user=request.user,
            role='viewer',
            must_change_password=True
        )

    if request.method == 'POST':
        form = ForcePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mettre à jour la session pour éviter la déconnexion
            update_session_auth_hash(request, user)

            # Marquer que l'utilisateur a changé son mot de passe
            profile.must_change_password = False
            profile.first_login_completed = True
            profile.save()

            messages.success(request, "Votre mot de passe a été changé avec succès ! Vous pouvez maintenant accéder au tableau de bord.")
            return redirect('tableau_de_bord')
    else:
        form = ForcePasswordChangeForm(request.user)

    return render(request, 'forcer_changement_mot_de_passe.html', {'form': form})

@login_required
def manage_carousel(request):
    """Vue pour gérer les images du carrousel"""
    if not request.user.userprofile.role in ['admin', 'superuser']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('tableau_de_bord')

    carousel_images = CarouselImage.objects.all().order_by('order')

    return render(request, 'manage_carousel.html', {
        'carousel_images': carousel_images
    })

@login_required
def add_carousel_image(request):
    """Vue pour ajouter une image au carrousel"""
    if not request.user.userprofile.role in ['admin', 'superuser']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('tableau_de_bord')

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Définir l'ordre automatiquement
            last_order = CarouselImage.objects.aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0

            carousel_image = form.save(commit=False)
            carousel_image.order = last_order + 1
            carousel_image.save()

            messages.success(request, 'Image ajoutée au carrousel avec succès!')
            return redirect('manage_carousel')
    else:
        form = CarouselImageForm()

    return render(request, 'add_carousel_image.html', {
        'form': form
    })

@login_required
def edit_carousel_image(request, image_id):
    """Vue pour modifier une image du carrousel"""
    if not request.user.userprofile.role in ['admin', 'superuser']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('tableau_de_bord')

    carousel_image = get_object_or_404(CarouselImage, id=image_id)

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=carousel_image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image modifiée avec succès!')
            return redirect('manage_carousel')
    else:
        form = CarouselImageForm(instance=carousel_image)

    return render(request, 'edit_carousel_image.html', {
        'form': form,
        'carousel_image': carousel_image
    })

@login_required
def delete_carousel_image(request, image_id):
    """Vue pour supprimer une image du carrousel"""
    if not request.user.userprofile.role in ['admin', 'superuser']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires.")
        return redirect('tableau_de_bord')

    carousel_image = get_object_or_404(CarouselImage, id=image_id)

    if request.method == 'POST':
        carousel_image.delete()
        messages.success(request, 'Image supprimée du carrousel avec succès!')
        return redirect('manage_carousel')

    return render(request, 'delete_carousel_image.html', {
        'carousel_image': carousel_image
    })

@login_required
@require_POST
def reorder_carousel_images(request):
    """Vue AJAX pour réorganiser les images du carrousel"""
    if not request.user.userprofile.role in ['admin', 'superuser']:
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})

    try:
        data = json.loads(request.body)
        image_ids = data.get('image_ids', [])

        for index, image_id in enumerate(image_ids):
            CarouselImage.objects.filter(id=image_id).update(order=index + 1)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def supprimer_fichier_arborescence(request):
    """Vue pour supprimer le fichier d'arborescence"""
    if request.user.userprofile.role not in ['superuser', 'admin']:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour effectuer cette action.")
        return redirect('tableau_de_bord')

    try:
        arborescence = ArborescenceFile.objects.latest('uploaded_at')
    except ArborescenceFile.DoesNotExist:
        messages.error(request, "Aucun fichier d'arborescence à supprimer.")
        return redirect('gerer_fichier_arborescence')

    if request.method == 'POST':
        # Supprimer le fichier physique si il existe
        try:
            if arborescence.file and os.path.exists(arborescence.file.path):
                os.remove(arborescence.file.path)
        except Exception as e:
            messages.warning(request, f"Le fichier physique n'a pas pu être supprimé : {str(e)}")

        # Supprimer l'enregistrement en base de données
        arborescence.delete()
        messages.success(request, "Le fichier d'arborescence a été supprimé avec succès !")
        return redirect('gerer_fichier_arborescence')

    return render(request, 'supprimer_fichier_arborescence.html', {
        'arborescence': arborescence
    })