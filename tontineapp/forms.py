from django import forms
from django.db.models import Max
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import TontineGroup, Membre, Membership, Tour, Cotisation


class TontineGroupForm(forms.ModelForm):
    class Meta:
        model = TontineGroup
        fields = ['nomGroupe', 'montantCotisation', 'frequenceCotisation', 'dateCreation', 'chefGroupe']
        widgets = {
            'nomGroupe': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Tontine Solidarité Espoir'}),
            'montantCotisation': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Ex: 10000'}),
            'frequenceCotisation': forms.Select(attrs={'class': 'form-select'}),
            'dateCreation': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'chefGroupe': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nomGroupe': 'Nom du groupe',
            'montantCotisation': 'Montant unitaire par cotisation (€/CFA)',
            'frequenceCotisation': 'Périodicité des versements',
            'dateCreation': 'Date de démarrage',
            'chefGroupe': 'Responsable / Chef de groupe',
        }

    def clean_montantCotisation(self):
        montant = self.cleaned_data.get('montantCotisation')
        if montant is not None and montant <= 0:
            raise ValidationError("Le montant de cotisation doit être strictement supérieur à zéro.")
        return montant


class MembreForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Identifiant / Pseudo",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: moussa_diop'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Moussa'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nom de famille",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Diop'})
    )
    email = forms.EmailField(
        required=False,
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'moussa@example.com'})
    )
    contact = forms.CharField(
        max_length=20,
        label="Numéro de téléphone",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+221 77 123 45 67'})
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['contact'].initial = self.instance.contact

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            user_qs = user_qs.exclude(pk=self.instance.user.pk)
        if user_qs.exists():
            raise ValidationError("Cet identifiant est déjà utilisé par un autre membre.")
        return username

    def save(self):
        username = self.cleaned_data['username']
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        email = self.cleaned_data.get('email', '')
        contact = self.cleaned_data['contact']

        if self.instance and self.instance.pk:
            user = self.instance.user
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            self.instance.contact = contact
            self.instance.save()
            return self.instance
        else:
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.set_unusable_password()
            user.save()
            membre = Membre.objects.create(user=user, contact=contact)
            return membre


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['membre', 'groupe']
        widgets = {
            'membre': forms.Select(attrs={'class': 'form-select'}),
            'groupe': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'membre': 'Choisir un membre',
            'groupe': 'Groupe de tontine',
        }

    def __init__(self, *args, **kwargs):
        groupe_preselected = kwargs.pop('groupe', None)
        super().__init__(*args, **kwargs)
        if groupe_preselected:
            self.fields['groupe'].initial = groupe_preselected
            self.fields['groupe'].widget = forms.HiddenInput()
            # Exclude members already in this group
            already_members = Membership.objects.filter(groupe=groupe_preselected).values_list('membre_id', flat=True)
            self.fields['membre'].queryset = Membre.objects.exclude(id__in=already_members)

    def clean(self):
        cleaned_data = super().clean()
        membre = cleaned_data.get('membre')
        groupe = cleaned_data.get('groupe')
        if membre and groupe:
            qs = Membership.objects.filter(membre=membre, groupe=groupe)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ce membre fait déjà partie de ce groupe de tontine.")
        return cleaned_data


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['membership', 'ordre', 'datePrevue', 'montant', 'statut']
        widgets = {
            'membership': forms.Select(attrs={'class': 'form-select'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'datePrevue': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'montant': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Optionnel (calculé par défaut)'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'membership': 'Bénéficiaire du tour',
            'ordre': 'Numéro d’ordre du tour',
            'datePrevue': 'Date prévue de distribution',
            'montant': 'Montant personnalisé (laisser vide pour la cagnotte totale)',
            'statut': 'État du versement',
        }

    def __init__(self, *args, **kwargs):
        groupe = kwargs.pop('groupe', None)
        super().__init__(*args, **kwargs)
        if groupe:
            self.fields['membership'].queryset = Membership.objects.filter(groupe=groupe)
            # Default to next order number if new
            if not self.instance.pk:
                max_order = Tour.objects.filter(membership__groupe=groupe).aggregate(Max('ordre'))['ordre__max'] or 0
                self.fields['ordre'].initial = max_order + 1
                self.fields['montant'].initial = groupe.cagnotte_totale()

    def clean_ordre(self):
        ordre = self.cleaned_data.get('ordre')
        if ordre is not None and ordre <= 0:
            raise ValidationError("L'ordre de passage doit être supérieur à 0.")
        return ordre


class CotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = ['membership', 'tour', 'montant', 'datePaiement', 'statut']
        widgets = {
            'membership': forms.Select(attrs={'class': 'form-select'}),
            'tour': forms.Select(attrs={'class': 'form-select'}),
            'montant': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'datePaiement': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'membership': 'Membre cotisant',
            'tour': 'Tour concerné',
            'montant': 'Montant cotisé (€/CFA)',
            'datePaiement': 'Date du paiement',
            'statut': 'Statut du paiement',
        }

    def __init__(self, *args, **kwargs):
        groupe = kwargs.pop('groupe', None)
        super().__init__(*args, **kwargs)
        if groupe:
            self.fields['membership'].queryset = Membership.objects.filter(groupe=groupe)
            self.fields['tour'].queryset = Tour.objects.filter(membership__groupe=groupe).order_by('ordre')
            if not self.instance.pk:
                self.fields['montant'].initial = groupe.montantCotisation
                prochain = groupe.prochain_tour()
                if prochain:
                    self.fields['tour'].initial = prochain

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is not None and montant <= 0:
            raise ValidationError("Le montant cotisé doit être supérieur à zéro.")
        return montant
