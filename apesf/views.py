from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContactMessage, PageContent, Partner, Section, UploadedImage
from .forms import ContactForm, PageContentForm, SectionForm, UploadedImageForm

# Page d'accueil
def accueil(request):
    try:
        page = PageContent.objects.get(slug='accueil')
    except PageContent.DoesNotExist:
        page = None
    
    # Récupérer les 5 dernières images uploadées pour le carrousel
    carousel_images = UploadedImage.objects.all().order_by('-uploaded_at')[:5]
    
    return render(request, 'accueil.html', {'page': page, 'carousel_images': carousel_images})

# Page "Qui sommes-nous ?"
def qui_sommes_nous(request):
    try:
        page = PageContent.objects.get(slug='qui-sommes-nous')
    except PageContent.DoesNotExist:
        page = None
    
    marmousets_sections = Section.objects.filter(unit='marmousets')
    angelus_sections = Section.objects.filter(unit='angelus')
    service_sections = Section.objects.filter(unit='service_externalise')
    
    return render(request, 'qui_sommes_nous.html', {
        'page': page,
        'marmousets_sections': marmousets_sections,
        'angelus_sections': angelus_sections,
        'service_sections': service_sections,
    })

# Page "Nos actions"
def nos_actions(request):
    try:
        page = PageContent.objects.get(slug='nos-actions')
    except PageContent.DoesNotExist:
        page = None
    return render(request, 'nos_actions.html', {'page': page})

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

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.")
            return redirect('contact')
    else:
        form = ContactForm()

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
    images = UploadedImage.objects.all()  # Récupère toutes les images uploadées
    return render(request, 'tableau_de_bord.html', {'pages': pages, 'messages_contact': messages_contact, 'images': images})

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
            return redirect('gerer_sections', page_id=section.page.id)
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