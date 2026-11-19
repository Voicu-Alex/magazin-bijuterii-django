from django.db.models import Count

from .models import Categorie


def meniu_categorii(request):
    categorii = (Categorie.objects.annotate(nr_produse=Count("bijuterii"))
                 .filter(nr_produse__gt=0)
                 .order_by("ordine_afisare", "nume"))
    return {"meniu_categorii": categorii}
