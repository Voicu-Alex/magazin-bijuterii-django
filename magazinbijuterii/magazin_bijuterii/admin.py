import csv
import json

from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (Ambalaj, Bijuterie, Brand, Categorie, Colectie,
                     PiatraPretioasa, SediuMagazin, Vitrina)

admin.site.site_header = "Administrare Magazin de Bijuterii"
admin.site.site_title = "Admin Bijuterii"
admin.site.index_title = "Panou de administrare al magazinului"
admin.site.site_url = "/magazin_bijuterii/"


@admin.action(description="Exportă produsele selectate în CSV")
def exporta_csv(modeladmin, request, queryset):
    raspuns = HttpResponse(content_type="text/csv; charset=utf-8")
    raspuns["Content-Disposition"] = "attachment; filename=bijuterii.csv"
    scriitor = csv.writer(raspuns)
    scriitor.writerow(["id", "nume", "categorie", "brand", "material", "pret", "stoc", "taguri"])
    for produs in queryset.select_related("categorie", "brand"):
        scriitor.writerow([produs.id, produs.nume, produs.categorie.nume, produs.brand.nume,
                           produs.get_material_display(), produs.pret, produs.stoc,
                           ", ".join(produs.taguri)])
    return raspuns


@admin.action(description="Exportă produsele selectate în JSON")
def exporta_json(modeladmin, request, queryset):
    date = [{
        "id": produs.id,
        "nume": produs.nume,
        "categorie": produs.categorie.nume,
        "brand": produs.brand.nume,
        "material": produs.material,
        "pret": float(produs.pret),
        "stoc": produs.stoc,
        "taguri": produs.taguri,
        "data_adaugare": produs.data_adaugare.isoformat(),
    } for produs in queryset.select_related("categorie", "brand")]
    raspuns = HttpResponse(json.dumps(date, ensure_ascii=False, indent=2),
                           content_type="application/json; charset=utf-8")
    raspuns["Content-Disposition"] = "attachment; filename=bijuterii.json"
    return raspuns


@admin.action(description="Marchează produsele selectate ca epuizate (stoc 0)")
def marcheaza_epuizat(modeladmin, request, queryset):
    numar = queryset.update(stoc=0)
    modeladmin.message_user(request, f"{numar} produse au fost marcate ca epuizate.", messages.SUCCESS)


@admin.action(description="Reaprovizionează produsele selectate (stoc 20)")
def reaprovizioneaza(modeladmin, request, queryset):
    numar = queryset.update(stoc=20)
    modeladmin.message_user(request, f"{numar} produse au fost reaprovizionate.", messages.SUCCESS)


@admin.register(Bijuterie)
class BijuterieAdmin(admin.ModelAdmin):
    list_display = ("nume", "categorie", "pret_formatat", "stoc_formatat", "brand_cu_tara",
                    "material", "data_adaugare")
    list_display_links = ("nume",)
    list_filter = ("categorie", "brand", "material", "colectie", "data_adaugare")
    list_per_page = 5
    ordering = ("-pret",)
    search_fields = ("nume", "descriere")
    search_help_text = "Caută după numele sau descrierea bijuteriei (potrivire parțială, fără diferențe între majuscule și minuscule)."
    date_hierarchy = "data_adaugare"
    filter_horizontal = ("pietre", "vitrine")
    actions = [exporta_csv, exporta_json, marcheaza_epuizat, reaprovizioneaza]
    fieldsets = (
        ("Informații de bază", {
            "fields": ("nume", "categorie", "brand", "pret", "material", "greutate_grame", "stoc"),
        }),
        ("Detalii opționale", {
            "classes": ("collapse",),
            "description": "Câmpuri care nu sunt obligatorii.",
            "fields": ("descriere", "puritate_carate", "taguri", "data_adaugare", "imagine",
                       "colectie", "pietre", "vitrine"),
        }),
    )

    @admin.display(description="Preț", ordering="pret")
    def pret_formatat(self, obj):
        return format_html('<b style="color:#b8860b;">{} lei</b>', obj.pret)

    @admin.display(description="Stoc", ordering="stoc")
    def stoc_formatat(self, obj):
        if obj.stoc_limitat:
            return format_html('<i style="color:#c0392b; font-weight:bold;">{} (stoc limitat)</i>', obj.stoc)
        return format_html('<span style="color:#1e8449;">{}</span>', obj.stoc)

    @admin.display(description="Brand (țara de origine)", ordering="brand__nume")
    def brand_cu_tara(self, obj):
        return f"{obj.brand.nume} ({obj.brand.tara_origine})"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nume", "ordine_afisare", "culoare_formatata", "sigla", "nr_produse")
    search_fields = ("nume", "descriere")
    search_help_text = "Caută după numele sau descrierea categoriei."
    ordering = ("ordine_afisare",)

    @admin.display(description="Culoare")
    def culoare_formatata(self, obj):
        return format_html('<span style="background:{}; color:white; padding:2px 8px; border-radius:4px;">{}</span>',
                           obj.culoare, obj.culoare)

    @admin.display(description="Număr produse")
    def nr_produse(self, obj):
        return obj.bijuterii.count()


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("nume", "tara_origine", "an_infiintare", "premium", "site_web")
    list_filter = ("premium", "tara_origine")
    search_fields = ("nume", "tara_origine")
    search_help_text = "Caută după numele brandului sau țara de origine."
    ordering = ("-an_infiintare",)


@admin.register(Colectie)
class ColectieAdmin(admin.ModelAdmin):
    list_display = ("nume", "sezon", "data_lansare", "editie_limitata")
    list_filter = ("sezon", "editie_limitata")
    search_fields = ("nume", "sezon")
    search_help_text = "Caută după numele colecției sau sezon (primavara, vara, toamna, iarna)."


@admin.register(PiatraPretioasa)
class PiatraPretioasaAdmin(admin.ModelAdmin):
    list_display = ("nume", "tip", "duritate_mohs")
    list_filter = ("tip",)
    search_fields = ("nume", "tip")
    search_help_text = "Caută după numele pietrei sau tip (pretioasa, semipretioasa, sintetica)."


class VitrinaInline(admin.TabularInline):
    model = Vitrina
    extra = 0


@admin.register(SediuMagazin)
class SediuMagazinAdmin(admin.ModelAdmin):
    list_display = ("nume", "adresa", "telefon", "email", "data_deschidere")
    search_fields = ("nume", "adresa")
    search_help_text = "Caută după numele sediului sau adresă."
    inlines = [VitrinaInline]


@admin.register(Vitrina)
class VitrinaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "sediu_adresa", "etaj", "iluminata")
    list_filter = ("sediu", "iluminata")
    search_fields = ("sediu__nume", "sediu__adresa")
    search_help_text = "Caută după numele sau adresa sediului din care face parte vitrina."

    @admin.display(description="Adresa sediului", ordering="sediu__adresa")
    def sediu_adresa(self, obj):
        return obj.sediu.adresa


@admin.register(Ambalaj)
class AmbalajAdmin(admin.ModelAdmin):
    list_display = ("nume", "culoare", "nivel_rezistenta")
    search_fields = ("nume", "descriere")
    search_help_text = "Caută după numele sau descrierea ambalajului."
