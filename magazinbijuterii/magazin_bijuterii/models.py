from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Ambalaj(models.Model):
    class Meta:
        verbose_name = "Ambalaj"
        verbose_name_plural = "Ambalaje"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(nivel_rezistenta__lte=10) & models.Q(nivel_rezistenta__gte=1),
                name='limite_rezista_ambalaj',
                violation_error_message="Nivelul de rezistenta trebuie sa fie intre 1 si 10 inclusiv!"
            )
        ]
    nume=models.CharField(max_length=200, unique=True, error_messages={
        "unique": "Există deja un ambalaj cu acest nume.",
        "max_length": "Numele ambalajului poate avea cel mult 200 de caractere."})
    culoare=models.CharField(max_length=100, null=True, blank=True)
    nivel_rezistenta=models.PositiveIntegerField(
        help_text="Valori intre 1 si 10. Un numar mai mare indica rezistenta mai mare",
        null=True
    )
    descriere = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nume}: {self.culoare}"


class Categorie(models.Model):
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categorii"
        ordering = ["ordine_afisare", "nume"]
        constraints = [
            models.CheckConstraint(condition=models.Q(culoare__regex=r"^#[0-9a-fA-F]{6}$"),
                                   name="culoare_hex_valida",
                                   violation_error_message="Culoarea trebuie să fie în format hex, de exemplu #c9a227."),
        ]

    nume = models.CharField(max_length=100, unique=True, error_messages={
        "unique": "Există deja o categorie cu acest nume.",
        "max_length": "Numele categoriei poate avea cel mult 100 de caractere."})
    descriere = models.TextField()
    culoare = models.CharField(max_length=7, default="#c9a227",
                               help_text="Culoare hex, de exemplu #c9a227")
    sigla = models.CharField(max_length=100, default="fa-solid fa-gem",
                             help_text="Clasa unui icon FontAwesome sau calea catre o imagine")
    ordine_afisare = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nume

    def get_absolute_url(self):
        return reverse("magazin_bijuterii:categorie", args=[self.nume])


class Brand(models.Model):
    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Branduri"
        ordering = ["nume"]
        indexes = [models.Index(fields=["tara_origine"], name="idx_brand_tara")]
        constraints = [
            models.CheckConstraint(condition=models.Q(an_infiintare__gte=1500) & models.Q(an_infiintare__lte=2026),
                                   name="an_infiintare_valid",
                                   violation_error_message="Anul înființării trebuie să fie între 1500 și 2026."),
        ]

    nume = models.CharField(max_length=100, unique=True, error_messages={
        "unique": "Există deja un brand cu acest nume."})
    tara_origine = models.CharField(max_length=100)
    an_infiintare = models.PositiveIntegerField(help_text="Anul în care a fost înființat brandul (între 1500 și 2026).")
    premium = models.BooleanField(default=False, help_text="Bifați dacă brandul face parte din segmentul de lux.")
    site_web = models.URLField(null=True, blank=True, help_text="Adresa completă a site-ului oficial, inclusiv https://")
    descriere = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nume


class Colectie(models.Model):
    class Sezon(models.TextChoices):
        PRIMAVARA = "primavara", "Primăvară"
        VARA = "vara", "Vară"
        TOAMNA = "toamna", "Toamnă"
        IARNA = "iarna", "Iarnă"

    class Meta:
        verbose_name = "Colecție"
        verbose_name_plural = "Colecții"
        ordering = ["-data_lansare"]

    nume = models.CharField(max_length=100, unique=True, error_messages={
        "unique": "Există deja o colecție cu acest nume."})
    sezon = models.CharField(max_length=20, choices=Sezon.choices)
    data_lansare = models.DateField()
    editie_limitata = models.BooleanField(default=False)
    descriere = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nume} ({self.get_sezon_display()} {self.data_lansare.year})"


class PiatraPretioasa(models.Model):
    class Tip(models.TextChoices):
        PRETIOASA = "pretioasa", "Prețioasă"
        SEMIPRETIOASA = "semipretioasa", "Semiprețioasă"
        SINTETICA = "sintetica", "Sintetică"

    class Meta:
        verbose_name = "Piatră prețioasă"
        verbose_name_plural = "Pietre prețioase"
        ordering = ["nume"]
        constraints = [
            models.CheckConstraint(condition=models.Q(duritate_mohs__gte=1) & models.Q(duritate_mohs__lte=10),
                                   name="duritate_mohs_valida",
                                   violation_error_message="Duritatea pe scara Mohs trebuie să fie între 1 și 10."),
        ]

    nume = models.CharField(max_length=100, unique=True, error_messages={
        "unique": "Există deja o piatră cu acest nume."})
    duritate_mohs = models.FloatField(help_text="Duritatea pe scara Mohs, între 1 (talc) și 10 (diamant).")
    tip = models.CharField(max_length=20, choices=Tip.choices)

    def __str__(self):
        return self.nume


class SediuMagazin(models.Model):
    class Meta:
        verbose_name = "Sediu magazin"
        verbose_name_plural = "Sedii magazin"
        ordering = ["nume"]

    nume = models.CharField(max_length=100, unique=True, error_messages={
        "unique": "Există deja un sediu cu acest nume."})
    adresa = models.CharField(max_length=255)
    telefon = models.CharField(max_length=20, help_text="Număr de telefon fără spații, de exemplu 0211234567.",
                               error_messages={"max_length": "Numărul de telefon poate avea cel mult 20 de caractere."})
    email = models.EmailField(null=True, blank=True)
    data_deschidere = models.DateField()

    def __str__(self):
        return self.nume


class Vitrina(models.Model):
    class Meta:
        verbose_name = "Vitrină"
        verbose_name_plural = "Vitrine"
        ordering = ["sediu", "nr_vitrina"]
        constraints = [
            models.UniqueConstraint(fields=["sediu", "nr_vitrina"], name="vitrina_unica_in_sediu"),
            models.CheckConstraint(condition=models.Q(etaj__gte=-1) & models.Q(etaj__lte=10),
                                   name="etaj_valid",
                                   violation_error_message="Etajul trebuie să fie între -1 (subsol) și 10."),
        ]

    sediu = models.ForeignKey(SediuMagazin, on_delete=models.CASCADE, related_name="vitrine")
    nr_vitrina = models.PositiveIntegerField()
    etaj = models.IntegerField(default=0, help_text="-1 pentru subsol, 0 pentru parter.")
    iluminata = models.BooleanField(default=True, help_text="Bifați dacă vitrina are iluminare LED proprie.")

    def __str__(self):
        return f"{self.sediu.nume} - vitrina {self.nr_vitrina}"


class Bijuterie(models.Model):
    class Material(models.TextChoices):
        AUR = "aur", "Aur"
        AUR_ALB = "aur_alb", "Aur alb"
        ARGINT = "argint", "Argint"
        PLATINA = "platina", "Platină"
        OTEL = "otel", "Oțel chirurgical"
        TITAN = "titan", "Titan"

    class Meta:
        verbose_name = "Bijuterie"
        verbose_name_plural = "Bijuterii"
        ordering = ["-data_adaugare", "nume"]
        indexes = [
            models.Index(fields=["nume"], name="idx_bijuterie_nume"),
            models.Index(fields=["pret"], name="idx_bijuterie_pret"),
            models.Index(fields=["material"], name="idx_bijuterie_material"),
            models.Index(fields=["-data_adaugare"], name="idx_bijuterie_data"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(pret__gt=0), name="pret_pozitiv",
                                   violation_error_message="Prețul trebuie să fie strict pozitiv."),
            models.CheckConstraint(condition=models.Q(puritate_carate__lte=24), name="puritate_maxim_24",
                                   violation_error_message="Puritatea nu poate depăși 24 de carate."),
            models.CheckConstraint(condition=models.Q(greutate_grame__gt=0), name="greutate_pozitiva",
                                   violation_error_message="Greutatea trebuie să fie strict pozitivă."),
        ]

    nume = models.CharField(max_length=200, error_messages={
        "max_length": "Numele bijuteriei poate avea cel mult 200 de caractere.",
        "blank": "Numele bijuteriei este obligatoriu."})
    descriere = models.TextField(blank=True)
    pret = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preț (lei)", error_messages={
        "invalid": "Prețul trebuie să fie un număr cu cel mult două zecimale.",
        "max_digits": "Prețul poate avea cel mult 10 cifre."})
    material = models.CharField(max_length=20, choices=Material.choices)
    puritate_carate = models.PositiveIntegerField(default=0, help_text="14, 18, 24 pentru aur; 0 pentru celelalte materiale")
    greutate_grame = models.FloatField()
    stoc = models.PositiveIntegerField(default=0)
    taguri = ArrayField(models.CharField(max_length=50), blank=True, default=list,
                        help_text="Cuvinte cheie separate prin virgulă")
    data_adaugare = models.DateTimeField(default=timezone.now, help_text="Se completează automat cu momentul adăugării.")
    imagine = models.ImageField(upload_to="produse/", blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="bijuterii")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="bijuterii")
    colectie = models.ForeignKey(Colectie, on_delete=models.SET_NULL, null=True, blank=True, related_name="bijuterii")
    pietre = models.ManyToManyField(PiatraPretioasa, blank=True, related_name="bijuterii")
    vitrine = models.ManyToManyField(Vitrina, blank=True, related_name="bijuterii")

    def __str__(self):
        return self.nume

    def get_absolute_url(self):
        return reverse("magazin_bijuterii:produs", args=[self.pk])

    @property
    def stoc_limitat(self):
        return self.stoc < settings.STOC_MIN
