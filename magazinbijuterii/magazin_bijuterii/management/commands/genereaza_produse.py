import random
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from magazin_bijuterii.models import Bijuterie, Brand, Categorie, Colectie, PiatraPretioasa, Vitrina

TABEL = Bijuterie._meta.db_table
COLOANE = ["nume", "descriere", "pret", "material", "puritate_carate", "greutate_grame",
           "stoc", "taguri", "data_adaugare", "imagine", "categorie_id", "brand_id", "colectie_id"]

TIPURI = {
    "Inele": ["Inel", "Verighetă", "Inel de logodnă"],
    "Coliere": ["Colier", "Lănțișor", "Colier statement"],
    "Cercei": ["Cercei", "Cercei lungi", "Cercei cu șurub"],
    "Brățări": ["Brățară", "Brățară rigidă", "Brățară cu talismane"],
    "Pandantive": ["Pandantiv", "Medalion", "Pandantiv gravat"],
    "Ceasuri": ["Ceas", "Ceas de damă", "Ceas bărbătesc"],
}
NUME = ["Aurora", "Luna", "Stella", "Venus", "Eclipsă", "Royal", "Infinity", "Harmony", "Zenith",
        "Grace", "Solitaire", "Elegance", "Noir", "Céleste", "Imperial", "Amour", "Serenity", "Opal"]
ADJECTIVE = ["clasic", "modern", "elegant", "delicat", "rafinat", "spectaculos", "minimalist", "vintage"]
TAGURI = ["clasic", "minimalist", "vintage", "logodna", "cadou", "lux", "zilnic", "nunta",
          "aniversare", "diamant", "perla", "unisex", "handmade", "editie-limitata"]
PURITATI = {
    "aur": [14, 18, 24],
    "aur_alb": [14, 18],
    "argint": [0],
    "platina": [0],
    "otel": [0],
    "titan": [0],
}
INTERVAL_PRET = {
    "aur": (900, 25000), "aur_alb": (1200, 30000), "argint": (80, 1500),
    "platina": (3000, 45000), "otel": (50, 600), "titan": (100, 900),
}


def sql_text(valoare):
    return "'" + str(valoare).replace("'", "''") + "'"


def sql_array(valori):
    if not valori:
        return "ARRAY[]::varchar[]"
    return "ARRAY[" + ", ".join(sql_text(v) for v in valori) + "]::varchar[]"


def genereaza_produs(categorie, branduri, colectii, nume_folosite):
    while True:
        nume = f"{random.choice(TIPURI.get(categorie.nume, ['Bijuterie']))} {random.choice(NUME)} {random.randint(1, 99)}"
        if nume not in nume_folosite:
            nume_folosite.add(nume)
            break
    material = random.choice(list(PURITATI))
    minim, maxim = INTERVAL_PRET[material]
    pret = round(random.uniform(minim, maxim), 2)
    puritate = random.choice(PURITATI[material])
    greutate = round(random.uniform(0.8, 60.0), 2)
    stoc = random.choice([0, 1, 2, 3, 4] + list(range(5, 41)))
    taguri = random.sample(TAGURI, k=random.randint(1, 4))
    data_adaugare = (timezone.now() - timedelta(days=random.randint(0, 730), minutes=random.randint(0, 1440))).isoformat()
    brand = random.choice(branduri)
    colectie = random.choice(colectii + [None, None])
    descriere = (f"{nume} este un produs {random.choice(ADJECTIVE)} din {dict(Bijuterie.Material.choices)[material].lower()}"
                 f"{f' de {puritate} carate' if puritate else ''}, semnat {brand.nume}. "
                 f"Potrivit pentru {random.choice(['purtarea zilnică', 'ocazii speciale', 'un cadou memorabil', 'ținute de seară'])}.")
    return {
        "nume": nume, "descriere": descriere, "pret": pret, "material": material,
        "puritate_carate": puritate, "greutate_grame": greutate, "stoc": stoc, "taguri": taguri,
        "data_adaugare": data_adaugare, "imagine": "", "categorie_id": categorie.id,
        "brand_id": brand.id, "colectie_id": colectie.id if colectie else None,
    }


def linie_insert(produs):
    valori = []
    for coloana in COLOANE:
        v = produs[coloana]
        if v is None:
            valori.append("NULL")
        elif coloana == "taguri":
            valori.append(sql_array(v))
        elif isinstance(v, (int, float)):
            valori.append(str(v))
        else:
            valori.append(sql_text(v))
    return f"INSERT INTO {TABEL} ({', '.join(COLOANE)}) VALUES ({', '.join(valori)});"


class Command(BaseCommand):
    help = "Generează comenzi INSERT cu date aleatoare, dar valide, pentru tabelul de produse."

    def add_arguments(self, parser):
        parser.add_argument("--numar", type=int, default=50, help="Câte produse se generează (implicit 50).")
        parser.add_argument("--fisier", default=str(settings.BASE_DIR / "insert_produse.sql"),
                            help="Fișierul în care se scriu comenzile INSERT.")
        parser.add_argument("--executa", action="store_true", help="Rulează comenzile generate în baza de date.")
        parser.add_argument("--seed", type=int, default=None, help="Seed pentru generatorul aleator.")

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])
        categorii = list(Categorie.objects.exclude(nume="Broșe"))
        branduri = list(Brand.objects.all())
        colectii = list(Colectie.objects.all())
        if not categorii or not branduri:
            raise CommandError("Rulați mai întâi comanda populeaza (lipsesc categoriile sau brandurile).")

        nume_folosite = set(Bijuterie.objects.values_list("nume", flat=True))
        produse = [genereaza_produs(random.choice(categorii), branduri, colectii, nume_folosite)
                   for _ in range(options["numar"])]
        linii = [linie_insert(p) for p in produse]

        cale = Path(options["fisier"])
        cale.write_text("-- Generat automat de comanda genereaza_produse\n" + "\n".join(linii) + "\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"{len(linii)} comenzi INSERT scrise în {cale}"))

        if options["executa"]:
            with connection.cursor() as cursor:
                for linie in linii:
                    cursor.execute(linie)
            self.asociaza_relatii(produse)
            self.stdout.write(self.style.SUCCESS(
                f"Comenzile au fost executate. Produse în baza de date: {Bijuterie.objects.count()}"))

    def asociaza_relatii(self, produse):
        pietre = list(PiatraPretioasa.objects.all())
        vitrine = list(Vitrina.objects.all())
        for p in produse:
            bijuterie = Bijuterie.objects.get(nume=p["nume"])
            if pietre and random.random() < 0.7:
                bijuterie.pietre.set(random.sample(pietre, k=random.randint(1, 3)))
            if vitrine and random.random() < 0.6:
                bijuterie.vitrine.set(random.sample(vitrine, k=random.randint(1, 2)))
