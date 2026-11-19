import random
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from magazin_bijuterii.models import Bijuterie


class Command(BaseCommand):
    help = "Generează imagini placeholder pentru o parte dintre produsele fără imagine."

    def add_arguments(self, parser):
        parser.add_argument("--procent", type=int, default=70)
        parser.add_argument("--seed", type=int, default=None)

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 40)
        except OSError:
            font = ImageFont.load_default()
        numar = 0
        for produs in Bijuterie.objects.filter(imagine="").select_related("categorie"):
            if random.randint(1, 100) > options["procent"]:
                continue
            culoare = produs.categorie.culoare
            img = Image.new("RGB", (400, 400), culoare)
            desen = ImageDraw.Draw(img)
            desen.ellipse((80, 80, 320, 320), outline="white", width=8)
            desen.polygon([(200, 120), (270, 190), (200, 290), (130, 190)], outline="white", width=6)
            initiale = "".join(cuvant[0] for cuvant in produs.nume.split()[:2]).upper()
            desen.text((200, 345), initiale, fill="white", font=font, anchor="mm")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            produs.imagine.save(f"produs_{produs.id}.png", ContentFile(buffer.getvalue()), save=True)
            numar += 1
        self.stdout.write(self.style.SUCCESS(f"{numar} imagini generate."))
