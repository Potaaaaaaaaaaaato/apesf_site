from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContactMessage, ContactMessageAttachment, JobOffer, PageContent, Partner, Section, UploadedImage, News
from .forms import ContactForm, JobOfferForm, PageContentForm, SectionForm, UploadedImageForm, NewsForm

# Page d'accueil
def accueil(request):
    try:
        page = PageContent.objects.get(slug='accueil')
    except PageContent.DoesNotExist:
        page = None
    
    # Récupérer les 5 dernières images uploadées pour le carrousel
    carousel_images = UploadedImage.objects.all().order_by('-uploaded_at')[:5]
    
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
    valid_units = ['marmousets', 'angelus', 'placement_modulable', 'accueil_parental']
    
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

# Page "Partenaires"
def partenaires(request):
    try:
        page = PageContent.objects.get(slug='partenaires')
    except PageContent.DoesNotExist:
        page = None
    return render(request, 'partenaires.html', {'page': page})

# Page "Contact"
def contact(request):
    try:
        page = PageContent.objects.get(slug='contact')
    except PageContent.DoesNotExist:
        page = None

    # Récupérer le paramètre 'subject' depuis l'URL
    initial_subject = request.GET.get('subject', '')

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, initial_subject=initial_subject)
        if form.is_valid():
            # Enregistrer le message de contact
            contact_message = form.save()
            # Gérer les pièces jointes
            files = request.FILES.getlist('attachments')
            for file in files:
                ContactMessageAttachment.objects.create(contact_message=contact_message, file=file)
            messages.success(request, "Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.")
            return redirect('contact')
    else:
        form = ContactForm(initial_subject=initial_subject)

    return render(request, 'contact.html', {'page': page, 'form': form})

# Page "Dons"
def dons(request):
    try:
        page = PageContent.objects.get(slug='dons')
    except PageContent.DoesNotExist:
        page = None
    return render(request, 'dons.html', {'page': page})

# Page de connexion
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.page = page
            section.save()
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
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section modifiée avec succès !")
            # Rediriger en fonction de si la section est associée à une page ou une unité
            if section.page and isinstance(section.page, PageContent):
                return redirect('gerer_sections', page_id=section.page.id)
            elif section.unit:
                return redirect('gerer_sections_unite', unit=section.unit)
            else:
                messages.warning(request, "La section n'est associée ni à une page ni à une unité. Redirection vers le tableau de bord.")
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
            form = SectionForm(request.POST)
            if form.is_valid():
                section = form.save(commit=False)
                section.page = page
                section.save()
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
    valid_units = ['marmousets', 'angelus', 'placement_modulable', 'accueil_parental']
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
            form = SectionForm(request.POST)
            if form.is_valid():
                section = form.save(commit=False)
                section.unit = unit  # Associer la section à l'unité
                section.save()
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

# Page "Partenaires"
def partners(request):
    # Récupérer la page "Partenaires"
    page = get_object_or_404(PageContent, slug='partenaires')
    # Récupérer tous les partenaires
    partners = Partner.objects.all()
    return render(request, 'partenaires.html', {'page': page, 'partners': partners})

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

# Nouveau modèle pour les contacts
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Enregistrer le message
            contact_message = form.save()
            # Gérer les pièces jointes
            for key, file in request.FILES.items():
                if key.startswith('attachment_'):
                    ContactMessageAttachment.objects.create(
                        contact_message=contact_message,
                        file=file
                    )
            messages.success(request, 'Votre message a été envoyé avec succès !')
            return redirect('contact')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})