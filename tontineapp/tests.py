from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Membre, TontineGroup, Membership, Tour, Cotisation
from .forms import MembreForm, TontineGroupForm, MembershipForm, TourForm, CotisationForm


class TontineAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user & member
        self.user1 = User.objects.create(username="fatou", first_name="Fatou", last_name="Sow")
        self.membre1 = Membre.objects.create(user=self.user1, contact="770001122")

        self.user2 = User.objects.create(username="modou", first_name="Modou", last_name="Fall")
        self.membre2 = Membre.objects.create(user=self.user2, contact="771112233")

        # Create group
        self.groupe = TontineGroup.objects.create(
            nomGroupe="Tontine Espoir",
            montantCotisation=5000.00,
            frequenceCotisation="mensuelle",
            dateCreation=timezone.now().date(),
            chefGroupe=self.membre1
        )

        # Memberships
        self.m1 = Membership.objects.create(membre=self.membre1, groupe=self.groupe)
        self.m2 = Membership.objects.create(membre=self.membre2, groupe=self.groupe)

        # Tour
        self.tour1 = Tour.objects.create(
            membership=self.m1,
            ordre=1,
            datePrevue=timezone.now().date(),
            montant=10000.00,
            statut="en_attente"
        )

        # Cotisation
        self.cotisation1 = Cotisation.objects.create(
            membership=self.m1,
            tour=self.tour1,
            montant=5000.00,
            statut="confirme"
        )

    def test_index_page(self):
        response = self.client.get(reverse('tontineapp:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestionnaire de Tontine")
        self.assertContains(response, "Tontine Espoir")

    def test_liste_groupes_page(self):
        response = self.client.get(reverse('tontineapp:liste_groupes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tontine Espoir")

    def test_detail_groupe_page(self):
        response = self.client.get(reverse('tontineapp:detail_groupe', args=[self.groupe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tontine Espoir")
        self.assertContains(response, "Prochain Bénéficiaire")
        self.assertContains(response, "Fatou Sow")

    def test_creer_groupe(self):
        response = self.client.post(reverse('tontineapp:creer_groupe'), {
            'nomGroupe': 'Tontine Solidarité',
            'montantCotisation': '10000.00',
            'frequenceCotisation': 'hebdomadaire',
            'dateCreation': str(timezone.now().date()),
            'chefGroupe': self.membre2.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TontineGroup.objects.filter(nomGroupe='Tontine Solidarité').exists())

    def test_modifier_groupe(self):
        response = self.client.post(reverse('tontineapp:modifier_groupe', args=[self.groupe.id]), {
            'nomGroupe': 'Tontine Espoir Renouvelée',
            'montantCotisation': '7500.00',
            'frequenceCotisation': 'mensuelle',
            'dateCreation': str(self.groupe.dateCreation),
            'chefGroupe': self.membre1.id,
        })
        self.assertEqual(response.status_code, 302)
        self.groupe.refresh_from_db()
        self.assertEqual(self.groupe.nomGroupe, 'Tontine Espoir Renouvelée')
        self.assertEqual(float(self.groupe.montantCotisation), 7500.00)

    def test_creer_membre(self):
        response = self.client.post(reverse('tontineapp:creer_membre'), {
            'username': 'aminata',
            'first_name': 'Aminata',
            'last_name': 'Ndiaye',
            'email': 'aminata@test.sn',
            'contact': '778889900',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Membre.objects.filter(user__username='aminata').exists())

    def test_modifier_membre(self):
        response = self.client.post(reverse('tontineapp:modifier_membre', args=[self.membre2.id]), {
            'username': 'modou_fall',
            'first_name': 'Mamadou',
            'last_name': 'Fall',
            'email': 'modou@test.sn',
            'contact': '779998877',
        })
        self.assertEqual(response.status_code, 302)
        self.membre2.refresh_from_db()
        self.assertEqual(self.membre2.user.username, 'modou_fall')
        self.assertEqual(self.membre2.contact, '779998877')

    def test_supprimer_membre(self):
        membre_id = self.membre2.id
        response = self.client.post(reverse('tontineapp:supprimer_membre', args=[membre_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Membre.objects.filter(id=membre_id).exists())

    def test_creer_tour(self):
        response = self.client.post(reverse('tontineapp:creer_tour', args=[self.groupe.id]), {
            'membership': self.m2.id,
            'ordre': 2,
            'datePrevue': str(timezone.now().date()),
            'montant': '10000.00',
            'statut': 'en_attente',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tour.objects.filter(membership=self.m2, ordre=2).exists())

    def test_modifier_tour(self):
        response = self.client.post(reverse('tontineapp:modifier_tour', args=[self.tour1.id]), {
            'membership': self.m1.id,
            'ordre': 1,
            'datePrevue': str(self.tour1.datePrevue),
            'montant': '12000.00',
            'statut': 'complete',
        })
        self.assertEqual(response.status_code, 302)
        self.tour1.refresh_from_db()
        self.assertEqual(float(self.tour1.montant), 12000.00)
        self.assertEqual(self.tour1.statut, 'complete')

    def test_changer_statut_tour(self):
        response = self.client.get(reverse('tontineapp:changer_statut_tour', args=[self.tour1.id, 'complete']))
        self.assertEqual(response.status_code, 302)
        self.tour1.refresh_from_db()
        self.assertEqual(self.tour1.statut, 'complete')

    def test_enregistrer_cotisation(self):
        response = self.client.post(reverse('tontineapp:enregistrer_cotisation', args=[self.groupe.id]), {
            'membership': self.m2.id,
            'tour': self.tour1.id,
            'montant': '5000.00',
            'datePaiement': str(timezone.now().date()),
            'statut': 'confirme',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cotisation.objects.filter(membership=self.m2).count(), 1)

    def test_modifier_cotisation(self):
        response = self.client.post(reverse('tontineapp:modifier_cotisation', args=[self.cotisation1.id]), {
            'membership': self.m1.id,
            'tour': self.tour1.id,
            'montant': '6000.00',
            'datePaiement': str(self.cotisation1.datePaiement),
            'statut': 'en_retard',
        })
        self.assertEqual(response.status_code, 302)
        self.cotisation1.refresh_from_db()
        self.assertEqual(float(self.cotisation1.montant), 6000.00)
        self.assertEqual(self.cotisation1.statut, 'en_retard')

    def test_supprimer_cotisation(self):
        c_id = self.cotisation1.id
        response = self.client.post(reverse('tontineapp:supprimer_cotisation', args=[c_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cotisation.objects.filter(id=c_id).exists())

    def test_liste_cotisations_page(self):
        response = self.client.get(reverse('tontineapp:liste_cotisations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5000.00")

    def test_retirer_membre_groupe(self):
        response = self.client.post(reverse('tontineapp:retirer_membre_groupe', args=[self.groupe.id, self.m2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Membership.objects.filter(id=self.m2.id).exists())

    def test_supprimer_groupe(self):
        response = self.client.post(reverse('tontineapp:supprimer_groupe', args=[self.groupe.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TontineGroup.objects.filter(id=self.groupe.id).exists())

    def test_validations_formulaires(self):
        # Montant négatif cotisation
        form = CotisationForm(data={'montant': -500})
        self.assertFalse(form.is_valid())
        self.assertIn('montant', form.errors)

        # Montant négatif groupe
        form_groupe = TontineGroupForm(data={'montantCotisation': -100})
        self.assertFalse(form_groupe.is_valid())
        self.assertIn('montantCotisation', form_groupe.errors)
