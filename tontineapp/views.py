from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .models import TontineGroup, Membre, Membership, Tour, Cotisation
from .forms import TontineGroupForm, MembreForm, MembershipForm, TourForm, CotisationForm


def index(request):
    total_groupes = TontineGroup.objects.count()
    total_membres = Membre.objects.count()
    total_cotise = Cotisation.objects.filter(statut='confirme').aggregate(Sum('montant'))['montant__sum'] or 0
    tours_actifs = Tour.objects.filter(statut='en_attente').count()
    groupes_recents = TontineGroup.objects.select_related('chefGroupe__user').order_by('-id')[:3]

    context = {
        'total_groupes': total_groupes,
        'total_membres': total_membres,
        'total_cotise': total_cotise,
        'tours_actifs': tours_actifs,
        'groupes_recents': groupes_recents,
    }
    return render(request, "tontineapp/index.html", context)


# ==========================================
# CRUD GROUPES
# ==========================================

def liste_groupes(request):
    groupes = TontineGroup.objects.select_related('chefGroupe__user').annotate(
        nb_membres=Count('memberships')
    ).order_by('-id')
    return render(request, "tontineapp/liste_groupes.html", {"groupes": groupes})


def creer_groupe(request):
    if request.method == 'POST':
        form = TontineGroupForm(request.POST)
        if form.is_valid():
            groupe = form.save()
            # If chef de groupe is set, add them as member if not already
            if groupe.chefGroupe:
                Membership.objects.get_or_create(membre=groupe.chefGroupe, groupe=groupe)
            messages.success(request, f"Le groupe « {groupe.nomGroupe} » a été créé avec succès !")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = TontineGroupForm()

    return render(request, 'tontineapp/form_groupe.html', {
        'form': form,
        'titre': 'Créer un nouveau groupe de tontine',
        'bouton_label': 'Créer le groupe',
    })


def modifier_groupe(request, groupe_id):
    groupe = get_object_or_404(TontineGroup, id=groupe_id)
    if request.method == 'POST':
        form = TontineGroupForm(request.POST, instance=groupe)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le groupe « {groupe.nomGroupe} » a été mis à jour.")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = TontineGroupForm(instance=groupe)

    return render(request, 'tontineapp/form_groupe.html', {
        'form': form,
        'groupe': groupe,
        'titre': f"Modifier le groupe : {groupe.nomGroupe}",
        'bouton_label': 'Enregistrer les modifications',
    })


def supprimer_groupe(request, groupe_id):
    groupe = get_object_or_404(TontineGroup, id=groupe_id)
    if request.method == 'POST':
        nom = groupe.nomGroupe
        groupe.delete()
        messages.success(request, f"Le groupe « {nom} » a été supprimé.")
        return redirect('tontineapp:liste_groupes')

    return render(request, 'tontineapp/confirmer_suppression.html', {
        'objet': groupe,
        'type_objet': 'le groupe de tontine',
        'url_retour': redirect('tontineapp:detail_groupe', groupe_id=groupe.id).url,
    })


def detail_groupe(request, groupe_id):
    groupe = get_object_or_404(
        TontineGroup.objects.select_related('chefGroupe__user'),
        id=groupe_id
    )
    memberships = groupe.memberships.select_related('membre__user').annotate(
        total_cotise=Sum('cotisations__montant', filter=Q(cotisations__statut='confirme')),
        nb_retards=Count('cotisations', filter=Q(cotisations__statut='en_retard'))
    ).order_by('dateAdhesion')

    tours = Tour.objects.filter(membership__groupe=groupe).select_related(
        'membership__membre__user'
    ).order_by('ordre', 'datePrevue')

    cotisations = Cotisation.objects.filter(membership__groupe=groupe).select_related(
        'membership__membre__user', 'tour'
    ).order_by('-datePaiement', '-id')

    prochain_tour = groupe.prochain_tour()
    total_confirme = cotisations.filter(statut='confirme').aggregate(Sum('montant'))['montant__sum'] or 0
    total_retards = cotisations.filter(statut='en_retard').count()
    total_attente = cotisations.filter(statut='en_attente').count()

    context = {
        'groupe': groupe,
        'memberships': memberships,
        'tours': tours,
        'cotisations': cotisations,
        'prochain_tour': prochain_tour,
        'total_confirme': total_confirme,
        'total_retards': total_retards,
        'total_attente': total_attente,
    }
    return render(request, 'tontineapp/detail_groupe.html', context)


# ==========================================
# CRUD MEMBRES
# ==========================================

def liste_membres(request):
    membres = Membre.objects.select_related('user').annotate(
        nb_groupes=Count('memberships', distinct=True),
        total_verse=Sum('memberships__cotisations__montant', filter=Q(memberships__cotisations__statut='confirme'))
    ).order_by('user__username')
    return render(request, 'tontineapp/liste_membres.html', {'membres': membres})


def creer_membre(request):
    if request.method == 'POST':
        form = MembreForm(request.POST)
        if form.is_valid():
            membre = form.save()
            messages.success(request, f"Le membre « {membre} » a été enregistré avec succès.")
            return redirect('tontineapp:liste_membres')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = MembreForm()

    return render(request, 'tontineapp/form_membre.html', {
        'form': form,
        'titre': 'Ajouter un nouveau membre',
        'bouton_label': 'Enregistrer le membre',
    })


def modifier_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            messages.success(request, f"Les informations du membre « {membre} » ont été mises à jour.")
            return redirect('tontineapp:liste_membres')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = MembreForm(instance=membre)

    return render(request, 'tontineapp/form_membre.html', {
        'form': form,
        'membre': membre,
        'titre': f"Modifier le membre : {membre}",
        'bouton_label': 'Mettre à jour',
    })


def supprimer_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == 'POST':
        nom = str(membre)
        user = membre.user
        membre.delete()
        user.delete()
        messages.success(request, f"Le membre « {nom} » et son compte ont été supprimés.")
        return redirect('tontineapp:liste_membres')

    return render(request, 'tontineapp/confirmer_suppression.html', {
        'objet': membre,
        'type_objet': 'le membre',
        'url_retour': redirect('tontineapp:liste_membres').url,
    })


# ==========================================
# GESTION DES ADHÉSIONS (MEMBERSHIPS)
# ==========================================

def ajouter_membre_groupe(request, groupe_id):
    groupe = get_object_or_404(TontineGroup, id=groupe_id)
    if request.method == 'POST':
        form = MembershipForm(request.POST, groupe=groupe)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.groupe = groupe
            membership.save()
            messages.success(request, f"{membership.membre} a rejoint le groupe {groupe.nomGroupe}.")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Impossible d'ajouter ce membre au groupe.")
    else:
        form = MembershipForm(groupe=groupe)

    return render(request, 'tontineapp/form_adhesion.html', {
        'form': form,
        'groupe': groupe,
    })


def retirer_membre_groupe(request, groupe_id, membership_id):
    groupe = get_object_or_404(TontineGroup, id=groupe_id)
    membership = get_object_or_404(Membership, id=membership_id, groupe=groupe)
    if request.method == 'POST':
        nom_membre = str(membership.membre)
        membership.delete()
        messages.success(request, f"Le membre {nom_membre} a été retiré du groupe {groupe.nomGroupe}.")
        return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)

    return render(request, 'tontineapp/confirmer_suppression.html', {
        'objet': f"{membership.membre} du groupe {groupe.nomGroupe}",
        'type_objet': "l'adhésion de",
        'url_retour': redirect('tontineapp:detail_groupe', groupe_id=groupe.id).url,
    })


# ==========================================
# GESTION DES TOURS DE VERSEMENT
# ==========================================

def creer_tour(request, groupe_id):
    groupe = get_object_or_404(TontineGroup, id=groupe_id)
    if request.method == 'POST':
        form = TourForm(request.POST, groupe=groupe)
        if form.is_valid():
            tour = form.save()
            messages.success(request, f"Le tour #{tour.ordre} pour {tour.membership.membre} a été programmé.")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Veuillez vérifier les informations du tour.")
    else:
        form = TourForm(groupe=groupe)

    return render(request, 'tontineapp/form_tour.html', {
        'form': form,
        'groupe': groupe,
        'titre': f"Programmer un tour pour le groupe {groupe.nomGroupe}",
    })


def modifier_tour(request, tour_id):
    tour = get_object_or_404(Tour.objects.select_related('membership__groupe'), id=tour_id)
    groupe = tour.membership.groupe
    if request.method == 'POST':
        form = TourForm(request.POST, instance=tour, groupe=groupe)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le tour #{tour.ordre} a été modifié.")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = TourForm(instance=tour, groupe=groupe)

    return render(request, 'tontineapp/form_tour.html', {
        'form': form,
        'groupe': groupe,
        'tour': tour,
        'titre': f"Modifier le tour #{tour.ordre} ({groupe.nomGroupe})",
    })


def changer_statut_tour(request, tour_id, nouveau_statut):
    tour = get_object_or_404(Tour.objects.select_related('membership__groupe'), id=tour_id)
    if nouveau_statut in ['en_attente', 'complete']:
        tour.statut = nouveau_statut
        tour.save()
        messages.success(request, f"Le statut du tour #{tour.ordre} est désormais « {tour.get_statut_display()} ».")
    return redirect('tontineapp:detail_groupe', groupe_id=tour.membership.groupe.id)


def supprimer_tour(request, tour_id):
    tour = get_object_or_404(Tour.objects.select_related('membership__groupe'), id=tour_id)
    groupe_id = tour.membership.groupe.id
    if request.method == 'POST':
        num = tour.ordre
        tour.delete()
        messages.success(request, f"Le tour #{num} a été supprimé.")
        return redirect('tontineapp:detail_groupe', groupe_id=groupe_id)

    return render(request, 'tontineapp/confirmer_suppression.html', {
        'objet': f"Tour #{tour.ordre} de {tour.membership.membre}",
        'type_objet': 'le tour',
        'url_retour': redirect('tontineapp:detail_groupe', groupe_id=groupe_id).url,
    })


# ==========================================
# GESTION DES COTISATIONS
# ==========================================

def liste_cotisations(request):
    cotisations = Cotisation.objects.select_related(
        'membership__membre__user', 'membership__groupe', 'tour'
    ).order_by('-datePaiement', '-id')

    statut_filter = request.GET.get('statut')
    if statut_filter:
        cotisations = cotisations.filter(statut=statut_filter)

    total_encaisse = Cotisation.objects.filter(statut='confirme').aggregate(Sum('montant'))['montant__sum'] or 0

    return render(request, 'tontineapp/liste_cotisations.html', {
        'cotisations': cotisations,
        'total_encaisse': total_encaisse,
        'statut_actif': statut_filter,
    })


def enregistrer_cotisation(request, groupe_id=None):
    groupe = None
    if groupe_id:
        groupe = get_object_or_404(TontineGroup, id=groupe_id)

    if request.method == 'POST':
        form = CotisationForm(request.POST, groupe=groupe)
        if form.is_valid():
            cotisation = form.save()
            messages.success(
                request,
                f"Cotisation de {cotisation.montant} enregistrée avec succès pour {cotisation.membership.membre}."
            )
            if groupe:
                return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
            return redirect('tontineapp:liste_cotisations')
        else:
            messages.error(request, "Erreur lors de l'enregistrement de la cotisation. Vérifiez les champs.")
    else:
        form = CotisationForm(groupe=groupe)

    return render(request, 'tontineapp/form_cotisation.html', {
        'form': form,
        'groupe': groupe,
        'titre': f"Enregistrer une cotisation {f'pour {groupe.nomGroupe}' if groupe else ''}",
    })


def modifier_cotisation(request, cotisation_id):
    cotisation = get_object_or_404(
        Cotisation.objects.select_related('membership__groupe'),
        id=cotisation_id
    )
    groupe = cotisation.membership.groupe
    if request.method == 'POST':
        form = CotisationForm(request.POST, instance=cotisation, groupe=groupe)
        if form.is_valid():
            form.save()
            messages.success(request, "La cotisation a été mise à jour.")
            return redirect('tontineapp:detail_groupe', groupe_id=groupe.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = CotisationForm(instance=cotisation, groupe=groupe)

    return render(request, 'tontineapp/form_cotisation.html', {
        'form': form,
        'groupe': groupe,
        'cotisation': cotisation,
        'titre': f"Modifier la cotisation de {cotisation.membership.membre}",
    })


def supprimer_cotisation(request, cotisation_id):
    cotisation = get_object_or_404(
        Cotisation.objects.select_related('membership__groupe'),
        id=cotisation_id
    )
    groupe_id = cotisation.membership.groupe.id
    if request.method == 'POST':
        cotisation.delete()
        messages.success(request, "La cotisation a été supprimée.")
        return redirect('tontineapp:detail_groupe', groupe_id=groupe_id)

    return render(request, 'tontineapp/confirmer_suppression.html', {
        'objet': f"Cotisation de {cotisation.montant} de {cotisation.membership.membre}",
        'type_objet': 'la cotisation',
        'url_retour': redirect('tontineapp:detail_groupe', groupe_id=groupe_id).url,
    })
