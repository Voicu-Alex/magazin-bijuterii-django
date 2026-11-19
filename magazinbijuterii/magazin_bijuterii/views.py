from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Bijuterie, Categorie


PREFIX_APLICATIE = "/magazin_bijuterii"

ZILE_SAPTAMANA = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
LUNI_AN = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
           "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]

FORMAT_ZI = "%A, %-d %B %Y"
FORMAT_TIMP = "%H:%M:%S"
FORMAT_DATA_ORA = FORMAT_ZI + ", ora " + FORMAT_TIMP

PAGINI_SITE = ["/", "/info", "/log", "/istoric", "/despre", "/produse"]
PROPRIETATI_ACCESARE = ["id", "ip_client", "url", "parametri", "data"]

COLOANE_SORTARE = {
    "nume": "nume",
    "pret": "preț",
    "data_adaugare": "data adăugării",
    "stoc": "stoc",
    "greutate_grame": "greutate",
}


def formateaza_data_ro(data, format=FORMAT_ZI):
    format = format.replace("%A", ZILE_SAPTAMANA[data.weekday()])
    format = format.replace("%B", LUNI_AN[data.month - 1])
    format = format.replace("%-d", str(data.day))
    return data.strftime(format)


class Accesare:
    nr_accesari = 0

    def __init__(self, ip_client, url, parametri={}):
        Accesare.nr_accesari += 1
        self.id = Accesare.nr_accesari
        self.ip_client = ip_client
        self.url = url
        self.parametri = dict(parametri)
        self.data = datetime.now()

    def lista_parametri(self):
        lista = []
        for nume, valori in self.parametri.items():
            if len(valori) == 0 or valori == [""]:
                valoare = None
            elif len(valori) == 1:
                valoare = valori[0]
            else:
                valoare = valori
            lista.append((nume, valoare))
        return lista

    def string_url(self):
        return self.url

    def pagina(self):
        cale = urlparse(self.url).path
        if cale.startswith(PREFIX_APLICATIE):
            cale = cale[len(PREFIX_APLICATIE):]
        return cale if cale else "/"

    def calculeaza_data(self, tip="", format=FORMAT_ZI):
        if tip == "":
            return formateaza_data_ro(self.data, format)
        if tip == "zi":
            text = formateaza_data_ro(self.data, FORMAT_ZI)
        elif tip == "timp":
            text = formateaza_data_ro(self.data, FORMAT_TIMP)
        else:
            text = formateaza_data_ro(self.data, FORMAT_DATA_ORA)
        return f"<section><h2>Data si ora</h2><p>{text}</p></section>"

    def valoare_proprietate(self, nume):
        if nume == "data":
            return self.calculeaza_data(format=FORMAT_DATA_ORA)
        if nume == "parametri":
            return self.lista_parametri()
        return getattr(self, nume)

    def __str__(self):
        return (f"id: {self.id}\n"
                f"ip_client: {self.ip_client}\n"
                f"string_url: {self.string_url()}\n"
                f"pagina: {self.pagina()}\n"
                f"calculeaza_data: {self.calculeaza_data(format=FORMAT_DATA_ORA)}\n"
                f"lista_parametri: {self.lista_parametri()}")


lista_accesari = []


def inregistreaza_accesare(request):
    accesare = Accesare(
        ip_client=request.ip_client,
        url=request.build_absolute_uri(),
        parametri={nume: request.GET.getlist(nume) for nume in request.GET},
    )
    lista_accesari.append(accesare)
    print(accesare)
    print("-" * 40)
    return accesare


def index(request):
    inregistreaza_accesare(request)
    if request.user.has_perm("magazin_bijuterii.change_bijuterie"):
        messages.success(request, "Ai permisiunea de a modifica produsele.")
    return render(request, "magazin_bijuterii/index.html", {"titlu": "Magazin de Bijuterii"})


def info(request):
    accesare = inregistreaza_accesare(request)
    tip_data = request.GET.get("data") or "complet"
    continut = accesare.calculeaza_data(tip=tip_data)
    return render(request, "magazin_bijuterii/info.html",
                  {"titlu": "Informatii despre server", "continut": continut})


def selecteaza_dupa_iduri(liste_iduri, dubluri):
    accesari_dupa_id = {acc.id: acc for acc in lista_accesari}
    selectie = []
    iduri_vazute = set()
    erori = []
    for sir in liste_iduri:
        for bucata in sir.split(","):
            bucata = bucata.strip()
            if not bucata:
                continue
            if not bucata.isdigit():
                erori.append(f"Id-ul \"{bucata}\" nu este un numar.")
                continue
            id = int(bucata)
            if id not in accesari_dupa_id:
                erori.append(f"Nu exista accesarea cu id-ul {id}.")
                continue
            if id in iduri_vazute and not dubluri:
                continue
            iduri_vazute.add(id)
            selectie.append(accesari_dupa_id[id])
    return selectie, erori


def pagini_extreme():
    numar_accesari = {pagina: 0 for pagina in PAGINI_SITE}
    for acc in lista_accesari:
        numar_accesari[acc.pagina()] = numar_accesari.get(acc.pagina(), 0) + 1
    cea_mai_putin = min(numar_accesari, key=lambda p: numar_accesari[p])
    cea_mai_mult = max(numar_accesari, key=lambda p: numar_accesari[p])
    return (cea_mai_putin, numar_accesari[cea_mai_putin]), (cea_mai_mult, numar_accesari[cea_mai_mult])


def log(request):
    inregistreaza_accesare(request)
    erori = []
    context = {"titlu": "Log accesari"}

    liste_iduri = request.GET.getlist("iduri")
    dubluri = request.GET.get("dubluri", "false").lower() == "true"
    if liste_iduri:
        accesari, erori_iduri = selecteaza_dupa_iduri(liste_iduri, dubluri)
        erori += erori_iduri
    else:
        accesari = list(lista_accesari)

    ultimele = request.GET.get("ultimele")
    if ultimele is not None:
        try:
            n = int(ultimele)
            if n < 0:
                raise ValueError
        except ValueError:
            erori.append(f"Parametrul ultimele trebuie sa fie un numar intreg pozitiv (s-a primit \"{ultimele}\").")
        else:
            k = len(accesari)
            if n > k:
                erori.append(f"Exista doar {k} accesari fata de {n} accesari cerute")
            else:
                accesari = accesari[k - n:]

    tabel = request.GET.get("tabel")
    coloane = []
    if tabel:
        if tabel == "tot":
            coloane = PROPRIETATI_ACCESARE
        else:
            coloane = [c.strip() for c in tabel.split(",") if c.strip()]
            invalide = [c for c in coloane if c not in PROPRIETATI_ACCESARE]
            if invalide:
                erori.append(f"Proprietati inexistente: {', '.join(invalide)}. "
                             f"Proprietati posibile: {', '.join(PROPRIETATI_ACCESARE)}.")
                coloane = [c for c in coloane if c in PROPRIETATI_ACCESARE]
        context["randuri"] = [[acc.valoare_proprietate(col) for col in coloane] for acc in accesari]

    (pag_min, nr_min), (pag_max, nr_max) = pagini_extreme()
    context.update({
        "accesari": accesari,
        "tabel": bool(tabel),
        "coloane": coloane,
        "pagina_min": pag_min, "nr_min": nr_min,
        "pagina_max": pag_max, "nr_max": nr_max,
        "tip_accesari": request.GET.get("accesari"),
        "total_accesari": len(lista_accesari),
        "nume_parametri": list(request.GET.keys()),
        "erori": erori,
    })
    return render(request, "magazin_bijuterii/log.html", context)


def istoric(request):
    inregistreaza_accesare(request)
    return render(request, "magazin_bijuterii/istoric.html", {"titlu": "Istoric"})


def despre(request):
    inregistreaza_accesare(request)
    return render(request, "magazin_bijuterii/despre.html", {"titlu": "Despre noi"})


def afis_accesare(request, id):
    inregistreaza_accesare(request)
    id = int(id)
    accesare = next((acc for acc in lista_accesari if acc.id == id), None)
    linii = str(accesare).split("\n") if accesare else []
    return render(request, "magazin_bijuterii/accesare.html",
                  {"titlu": f"Accesarea {id}", "accesare": accesare, "linii": linii})


def listare_produse(request, categorie=None):
    produse = Bijuterie.objects.select_related("categorie", "brand")
    if categorie is not None:
        produse = produse.filter(categorie=categorie)

    taguri_active = [tag for tag in request.GET.getlist("tag") if tag]
    for tag in taguri_active:
        produse = produse.filter(taguri__contains=[tag])

    coloana = request.GET.get("col", "nume")
    if coloana not in COLOANE_SORTARE:
        coloana = "nume"
    sortare = "d" if request.GET.get("sort") == "d" else "a"
    produse = produse.order_by(("-" if sortare == "d" else "") + coloana, "id")

    paginator = Paginator(produse, settings.PROD_PER_PAG)
    pagina = paginator.get_page(request.GET.get("pagina"))

    return {
        "categorie": categorie,
        "pagina": pagina,
        "paginator": paginator,
        "taguri_active": taguri_active,
        "coloana": coloana,
        "sortare": sortare,
        "coloane_sortare": COLOANE_SORTARE,
        "stoc_min": settings.STOC_MIN,
    }


def produse(request):
    inregistreaza_accesare(request)
    context = listare_produse(request)
    context["titlu"] = "Toate produsele"
    return render(request, "magazin_bijuterii/produse.html", context)


def categorie(request, nume_categorie):
    inregistreaza_accesare(request)
    try:
        categorie = Categorie.objects.get(nume=nume_categorie)
    except Categorie.DoesNotExist:
        return render(request, "magazin_bijuterii/eroare.html", {
            "titlu": "Categorie inexistentă",
            "mesaj": f"Nu există nicio categorie cu numele \"{nume_categorie}\".",
        }, status=404)
    context = listare_produse(request, categorie)
    context["titlu"] = f"Categoria {categorie.nume}"
    return render(request, "magazin_bijuterii/produse.html", context)


def produs(request, id):
    inregistreaza_accesare(request)
    try:
        produs = Bijuterie.objects.select_related("categorie", "brand", "colectie").get(pk=id)
    except Bijuterie.DoesNotExist:
        return render(request, "magazin_bijuterii/eroare.html", {
            "titlu": "Produs inexistent",
            "mesaj": f"Nu există niciun produs cu id-ul {id}.",
        }, status=404)
    similare = (Bijuterie.objects.filter(categorie=produs.categorie)
                .exclude(pk=produs.pk).order_by("?")[:settings.PRODUSE_SIMILARE])
    return render(request, "magazin_bijuterii/produs.html", {
        "titlu": produs.nume,
        "produs": produs,
        "similare": similare,
        "stoc_min": settings.STOC_MIN,
        "url_lista": reverse("magazin_bijuterii:produse"),
    })
