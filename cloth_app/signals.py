from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models.fields.files import ImageFieldFile

from cloth_app.models import Banners, Product
from cloth_app.utils import convert_to_webp
import threading
from cloth_app.utilsauto.image_processor import process_images_async


def image_changed(instance, field_name):
    """
    Returns True only when file is new or changed.
    """
    if not instance.pk:
        return True

    old_value = type(instance).objects.filter(pk=instance.pk).values_list(field_name, flat=True).first()
    new_file = getattr(instance, field_name, None)
    new_name = getattr(new_file, "name", None)

    return old_value != new_name


@receiver(pre_save)
def auto_convert_all_images_to_webp(sender, instance, **kwargs):
    """
    Convert ImageFields to WEBP for cloth_app models,
    but skip Banners because they have separate settings.
    """
    if sender.__module__.split('.')[0] != "cloth_app":
        return

    if sender is Banners:
        return

    for field in instance._meta.get_fields():
        try:
            if field.get_internal_type() != "ImageField":
                continue

            if not image_changed(instance, field.name):
                continue

            value = getattr(instance, field.name, None)
            if isinstance(value, ImageFieldFile) and value:
                convert_to_webp(value, quality=90)

        except Exception as e:
            print("⚠️ Image convert error:", e)


@receiver(pre_save, sender=Banners)
def banner_convert_to_webp(sender, instance, **kwargs):
    """
    Banner images need higher quality and larger width.
    """
    if image_changed(instance, "image") and instance.image:
        convert_to_webp(instance.image, max_width=1920, quality=94)

    if image_changed(instance, "image_phone") and instance.image_phone:
        convert_to_webp(instance.image_phone, max_width=1080, quality=92)


@receiver(post_save, sender=Product)
def trigger_image_processing(sender, instance, created, **kwargs):
    if created and instance.temp_product_image_url:
        threading.Thread(
            target=process_images_async,
            daemon=False
        ).start()