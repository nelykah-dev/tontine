from django.urls import path
from . import views

app_name = 'tontineapp'

urlpatterns = [
    # Accueil
    path('', views.index, name='index'),

    # Groupes
    path('groupes/', views.liste_groupes, name='liste_groupes'),
    path('groupes/nouveau/', views.creer_groupe, name='creer_groupe'),
    path('groupes/<int:groupe_id>/', views.detail_groupe, name='detail_groupe'),
    path('groupes/<int:groupe_id>/modifier/', views.modifier_groupe, name='modifier_groupe'),
    path('groupes/<int:groupe_id>/supprimer/', views.supprimer_groupe, name='supprimer_groupe'),

    # Adhésions
    path('groupes/<int:groupe_id>/adherer/', views.ajouter_membre_groupe, name='ajouter_membre_groupe'),
    path('groupes/<int:groupe_id>/retirer/<int:membership_id>/', views.retirer_membre_groupe, name='retirer_membre_groupe'),

    # Membres
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/nouveau/', views.creer_membre, name='creer_membre'),
    path('membres/<int:membre_id>/modifier/', views.modifier_membre, name='modifier_membre'),
    path('membres/<int:membre_id>/supprimer/', views.supprimer_membre, name='supprimer_membre'),

    # Tours de versement
    path('groupes/<int:groupe_id>/tours/nouveau/', views.creer_tour, name='creer_tour'),
    path('tours/<int:tour_id>/modifier/', views.modifier_tour, name='modifier_tour'),
    path('tours/<int:tour_id>/statut/<str:nouveau_statut>/', views.changer_statut_tour, name='changer_statut_tour'),
    path('tours/<int:tour_id>/supprimer/', views.supprimer_tour, name='supprimer_tour'),

    # Cotisations
    path('cotisations/', views.liste_cotisations, name='liste_cotisations'),
    path('cotisations/nouvelle/', views.enregistrer_cotisation, name='enregistrer_cotisation_globale'),
    path('groupes/<int:groupe_id>/cotisations/nouvelle/', views.enregistrer_cotisation, name='enregistrer_cotisation'),
    path('cotisations/<int:cotisation_id>/modifier/', views.modifier_cotisation, name='modifier_cotisation'),
    path('cotisations/<int:cotisation_id>/supprimer/', views.supprimer_cotisation, name='supprimer_cotisation'),
]
