from django.contrib import admin
from .models import Membre, TontineGroup, Membership, Cotisation, Tour


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'get_full_name', 'get_email')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'contact')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Nom complet'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


@admin.register(TontineGroup)
class TontineGroupAdmin(admin.ModelAdmin):
    list_display = ('nomGroupe', 'montantCotisation', 'frequenceCotisation', 'dateCreation', 'chefGroupe', 'total_membres')
    list_filter = ('frequenceCotisation', 'dateCreation')
    search_fields = ('nomGroupe', 'chefGroupe__user__username')
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('membre', 'groupe', 'dateAdhesion')
    list_filter = ('groupe', 'dateAdhesion')
    search_fields = ('membre__user__username', 'groupe__nomGroupe')


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('ordre', 'membership', 'datePrevue', 'get_montant_effectif', 'statut')
    list_filter = ('statut', 'datePrevue', 'membership__groupe')
    search_fields = ('membership__membre__user__username', 'membership__groupe__nomGroupe')


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('membership', 'tour', 'montant', 'datePaiement', 'statut')
    list_filter = ('statut', 'datePaiement', 'membership__groupe')
    search_fields = ('membership__membre__user__username', 'membership__groupe__nomGroupe')
