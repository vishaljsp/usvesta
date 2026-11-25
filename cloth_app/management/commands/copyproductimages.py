from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

from cloth_app.models import *   # <-- apna MODEL import yahan daalo


class Command(BaseCommand):
    help = "Copy all product images into a new folder without changing their names."

    def handle(self, *args, **kwargs):

        # Target folder jahan images copy hongi
        backup_folder = os.path.join(settings.MEDIA_ROOT, "product_image_b")

        # Folder create ho jayega agar nahi hai
        os.makedirs(backup_folder, exist_ok=True)

        products = product_Gelery_images.objects.all()

        for product in products:
            # Product ke image field ka naam yahan likho:
            image_field = product.image  # <-- Yahan apna field name use karo

            if not image_field:
                continue

            old_path = image_field.path
            filename = os.path.basename(old_path)

            new_path = os.path.join(backup_folder, filename)

            try:
                shutil.copyfile(old_path, new_path)
                self.stdout.write(self.style.SUCCESS(f"Copied → {filename}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error copying {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 All product images copied successfully!"))
