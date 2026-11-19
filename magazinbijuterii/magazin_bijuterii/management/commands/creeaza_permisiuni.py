from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

NUME_GRUP = "Gestionari produse"
PERMISIUNI_GRUP = ["view_bijuterie", "change_bijuterie"]

USERNAME = "angajat"
PAROLA = "Angajat244!"
PERMISIUNI_PROPRII = ["view_categorie", "change_categorie"]


class Command(BaseCommand):
    help = "Creeaza grupul 'Gestionari produse', userul 'angajat' si le asociaza permisiuni."

    def handle(self, *args, **options):
        grup, _ = Group.objects.get_or_create(name=NUME_GRUP)
        grup.permissions.set(Permission.objects.filter(
            content_type__app_label="magazin_bijuterii", codename__in=PERMISIUNI_GRUP))

        user, creat = User.objects.get_or_create(username=USERNAME, defaults={
            "first_name": "Ion", "last_name": "Popescu", "email": "angajat@magazin.ro"})
        if creat:
            user.set_password(PAROLA)
        user.is_staff = True
        user.is_superuser = False
        user.save()

        user.groups.add(grup)
        user.user_permissions.set(Permission.objects.filter(
            content_type__app_label="magazin_bijuterii", codename__in=PERMISIUNI_PROPRII))

        self.stdout.write(self.style.SUCCESS(
            f"Grupul '{grup.name}' are permisiunile {sorted(grup.permissions.values_list('codename', flat=True))}"))
        self.stdout.write(self.style.SUCCESS(
            f"Userul '{user.username}' e in grupurile {list(user.groups.values_list('name', flat=True))} "
            f"si are permisiunile proprii {sorted(user.user_permissions.values_list('codename', flat=True))}"))
