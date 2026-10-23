from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Membre(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membre_profile')
    contact = models.CharField(max_length=20, verbose_name="Numéro de contact / Téléphone")

    def __str__(self):
        full_name = self.user.get_full_name()
        display_name = full_name if full_name else self.user.username
        return f"{display_name} ({self.contact})"

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"


class TontineGroup(models.Model):
    FREQUENCE_CHOICES = [
        ('hebdomadaire', 'Hebdomadaire (Toutes les semaines)'),
        ('bimensuelle', 'Bimensuelle (Toutes les 2 semaines)'),
        ('mensuelle', 'Mensuelle (Tous les mois)'),
    ]

    nomGroupe = models.CharField(max_length=107, verbose_name="Nom du groupe")
    montantCotisation = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant de la cotisation")
    frequenceCotisation = models.CharField(max_length=50, choices=FREQUENCE_CHOICES, default='mensuelle', verbose_name="Fréquence de cotisation")
    dateCreation = models.DateField(default=timezone.localdate, verbose_name="Date de création")
    chefGroupe = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name='groupes_geres', verbose_name="Chef de groupe")

    def total_membres(self):
        return self.memberships.count()

    def cagnotte_totale(self):
        return self.montantCotisation * self.total_membres()

    def prochain_tour(self):
        return Tour.objects.filter(membership__groupe=self, statut='en_attente').order_by('ordre', 'datePrevue').first()

    def tours_completes_count(self):
        return Tour.objects.filter(membership__groupe=self, statut='complete').count()

    def __str__(self):
        return self.nomGroupe

    class Meta:
        verbose_name = "Groupe de tontine"
        verbose_name_plural = "Groupes de tontine"


class Membership(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='memberships', verbose_name="Membre")
    groupe = models.ForeignKey(TontineGroup, on_delete=models.CASCADE, related_name='memberships', verbose_name="Groupe")
    dateAdhesion = models.DateField(auto_now_add=True, verbose_name="Date d'adhésion")

    class Meta:
        unique_together = ('membre', 'groupe')
        verbose_name = "Adhésion"
        verbose_name_plural = "Adhésions"

    def __str__(self):
        return f"{self.membre} - {self.groupe.nomGroupe}"


class Tour(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('complete', 'Complété'),
    ]
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='tours', verbose_name="Bénéficiaire (Membre & Groupe)")
    ordre = models.PositiveIntegerField(verbose_name="Ordre de passage")
    datePrevue = models.DateField(verbose_name="Date prévue du versement")
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant à verser")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut du tour")

    def get_montant_effectif(self):
        if self.montant is not None:
            return self.montant
        return self.membership.groupe.cagnotte_totale()

    def cotisations_payees(self):
        return self.cotisations.filter(statut='confirme')

    def cotisations_en_retard(self):
        return self.cotisations.filter(statut='en_retard')

    def __str__(self):
        return f"Tour {self.ordre} : {self.membership.membre.user.username} ({self.membership.groupe.nomGroupe})"

    class Meta:
        ordering = ['ordre', 'datePrevue']
        verbose_name = "Tour de versement"
        verbose_name_plural = "Tours de versement"


class Cotisation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('en_retard', 'En retard'),
    ]
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='cotisations', verbose_name="Membre cotisant")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='cotisations', null=True, blank=True, verbose_name="Tour associé")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant cotisé")
    datePaiement = models.DateField(default=timezone.localdate, verbose_name="Date de paiement")
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut du paiement")

    def __str__(self):
        tour_str = f"Tour {self.tour.ordre}" if self.tour else "Cotisation libre"
        return f"{self.membership.membre} - {tour_str} : {self.montant} ({self.get_statut_display()})"

    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ['-datePaiement', '-id']
