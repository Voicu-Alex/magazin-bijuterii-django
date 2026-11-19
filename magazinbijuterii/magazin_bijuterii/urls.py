from django.urls import path, re_path

from . import views

app_name = "magazin_bijuterii"

urlpatterns = [
    path("", views.index, name="index"),
    path("info", views.info, name="info"),
    path("log", views.log, name="log"),
    path("istoric", views.istoric, name="istoric"),
    path("despre", views.despre, name="despre"),
    re_path(r'^accesare(?P<id>\d+)$', views.afis_accesare, name="accesare"),
    path("produse", views.produse, name="produse"),
    path("produse/<int:id>", views.produs, name="produs"),
    path("categorii/<str:nume_categorie>", views.categorie, name="categorie"),
]
