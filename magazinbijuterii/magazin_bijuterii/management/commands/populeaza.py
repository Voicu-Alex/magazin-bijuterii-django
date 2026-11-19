from datetime import date

from django.core.management.base import BaseCommand

from magazin_bijuterii.models import (Ambalaj, Brand, Categorie, Colectie,
                                      PiatraPretioasa, SediuMagazin, Vitrina)

CATEGORII = [
    ("Inele", "Inele de logodnă, verighete și inele de zi cu zi, din aur, argint sau platină.", "#c0392b", "fa-solid fa-ring", 1),
    ("Coliere", "Coliere și lănțișoare fine sau statement, cu sau fără pandantiv.", "#2980b9", "fa-solid fa-link", 2),
    ("Cercei", "Cercei cu șurub, cu tortiță sau lungi, pentru orice ocazie.", "#8e44ad", "fa-solid fa-star", 3),
    ("Brățări", "Brățări rigide, lanț sau cu talismane, din metale prețioase.", "#16a085", "fa-solid fa-circle-notch", 4),
    ("Pandantive", "Pandantive cu pietre prețioase sau gravate, pentru lanțurile preferate.", "#d35400", "fa-solid fa-heart", 5),
    ("Ceasuri", "Ceasuri de damă și bărbătești semnate de branduri de lux.", "#2c3e50", "fa-solid fa-clock", 6),
    ("Broșe", "Broșe vintage și moderne. Categorie fără produse, folosită pentru testarea meniului.", "#7f8c8d", "fa-solid fa-leaf", 7),
]

BRANDURI = [
    ("Aurora Atelier", "România", 2012, False, "https://www.auroraatelier.ro"),
    ("Cartier", "Franța", 1847, True, "https://www.cartier.com"),
    ("Pandora", "Danemarca", 1982, False, "https://www.pandora.net"),
    ("Tiffany & Co.", "SUA", 1837, True, "https://www.tiffany.com"),
    ("Bulgari", "Italia", 1884, True, "https://www.bulgari.com"),
    ("Swarovski", "Austria", 1895, False, "https://www.swarovski.com"),
    ("Sabion", "România", 1991, False, None),
    ("Chopard", "Elveția", 1860, True, "https://www.chopard.com"),
]

COLECTII = [
    ("Flori de Primăvară", "primavara", date(2025, 3, 1), False),
    ("Briză Marină", "vara", date(2025, 6, 15), False),
    ("Frunze de Aur", "toamna", date(2025, 9, 20), True),
    ("Cristale de Gheață", "iarna", date(2025, 12, 1), True),
    ("Eternity", "iarna", date(2024, 12, 1), False),
]

PIETRE = [
    ("Diamant", 10.0, "pretioasa"),
    ("Rubin", 9.0, "pretioasa"),
    ("Safir", 9.0, "pretioasa"),
    ("Smarald", 7.5, "pretioasa"),
    ("Ametist", 7.0, "semipretioasa"),
    ("Topaz", 8.0, "semipretioasa"),
    ("Granat", 7.0, "semipretioasa"),
    ("Perlă", 3.0, "semipretioasa"),
    ("Zirconiu cubic", 8.5, "sintetica"),
    ("Moissanit", 9.25, "sintetica"),
]

SEDII = [
    ("Showroom București", "Calea Victoriei 120, București", "0211234567", date(2012, 5, 10), 4),
    ("Showroom Cluj", "Str. Memorandumului 8, Cluj-Napoca", "0264123456", date(2018, 9, 1), 3),
    ("Showroom Timișoara", "Piața Victoriei 3, Timișoara", "0256123456", date(2022, 3, 15), 2),
    ("Showroom Iași", "Str. Lăpușneanu 14, Iași", "0232123456", date(2023, 10, 5), 2),
    ("Showroom Brașov", "Str. Republicii 22, Brașov", "0268123456", date(2024, 4, 20), 2),
]

AMBALAJE = [
    ("Cutie catifea neagră", "negru", 8, "Cutie rigidă îmbrăcată în catifea, pentru inele și cercei."),
    ("Săculeț din satin", "crem", 3, "Săculeț moale pentru lănțișoare și brățări."),
    ("Cutie cadou premium", "auriu", 10, "Cutie din lemn cu interior de mătase, pentru colecțiile de lux."),
    ("Plic din hârtie reciclată", "maro", 2, "Plic simplu pentru certificate și bonuri de garanție."),
    ("Cutie pentru ceas", "negru", 9, "Cutie cu pernă interioară pentru ceasuri."),
]


class Command(BaseCommand):
    help = "Populează tabelele de bază (categorii, branduri, colecții, pietre, sedii, vitrine, ambalaje)."

    def handle(self, *args, **options):
        for nume, descriere, culoare, sigla, ordine in CATEGORII:
            Categorie.objects.update_or_create(nume=nume, defaults={
                "descriere": descriere, "culoare": culoare, "sigla": sigla, "ordine_afisare": ordine})
        for nume, tara, an, premium, site in BRANDURI:
            Brand.objects.update_or_create(nume=nume, defaults={
                "tara_origine": tara, "an_infiintare": an, "premium": premium, "site_web": site})
        for nume, sezon, data_lansare, limitata in COLECTII:
            Colectie.objects.update_or_create(nume=nume, defaults={
                "sezon": sezon, "data_lansare": data_lansare, "editie_limitata": limitata})
        for nume, duritate, tip in PIETRE:
            PiatraPretioasa.objects.update_or_create(nume=nume, defaults={
                "duritate_mohs": duritate, "tip": tip})
        for nume, adresa, telefon, data_deschidere, nr_vitrine in SEDII:
            sediu, _ = SediuMagazin.objects.update_or_create(nume=nume, defaults={
                "adresa": adresa, "telefon": telefon, "data_deschidere": data_deschidere,
                "email": nume.lower().replace("showroom ", "").replace("ș", "s").replace("ț", "t") + "@bijuterii.ro"})
            for nr in range(1, nr_vitrine + 1):
                Vitrina.objects.update_or_create(sediu=sediu, nr_vitrina=nr, defaults={
                    "etaj": 0 if nr <= 2 else 1, "iluminata": nr % 2 == 1})
        for nume, culoare, nivel, descriere in AMBALAJE:
            Ambalaj.objects.update_or_create(nume=nume, defaults={
                "culoare": culoare, "nivel_rezistenta": nivel, "descriere": descriere})

        self.stdout.write(self.style.SUCCESS(
            f"Categorii: {Categorie.objects.count()}, branduri: {Brand.objects.count()}, "
            f"colecții: {Colectie.objects.count()}, pietre: {PiatraPretioasa.objects.count()}, "
            f"sedii: {SediuMagazin.objects.count()}, vitrine: {Vitrina.objects.count()}, "
            f"ambalaje: {Ambalaj.objects.count()}"))
