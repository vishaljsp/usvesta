from cloth_app.models import (
    Product,
    product_Gelery_images,
    Color_product,
    color_product_Gelery_images
)
from .drive_utils import get_drive_image


def process_images_async():
    print("🔥 Image processing started")

    # Product main image
    for p in Product.objects.filter(
        product_image__isnull=True,
        temp_product_image_url__isnull=False
    ):
        img = get_drive_image(p.temp_product_image_url)
        if img:
            p.product_image = img
            p.save(update_fields=["product_image"])

    # Product gallery
    for g in product_Gelery_images.objects.filter(
        image__isnull=True,
        temp_image_url__isnull=False
    ):
        img = get_drive_image(g.temp_image_url)
        if img:
            g.image = img
            g.save(update_fields=["image"])

    # Color main image
    for c in Color_product.objects.filter(
        color_images__isnull=True,
        temp_color_image_url__isnull=False
    ):
        img = get_drive_image(c.temp_color_image_url)
        if img:
            c.color_images = img
            c.save(update_fields=["color_images"])

    # Color gallery
    for cg in color_product_Gelery_images.objects.filter(
        image__isnull=True,
        temp_image_url__isnull=False
    ):
        img = get_drive_image(cg.temp_image_url)
        if img:
            cg.image = img
            cg.save(update_fields=["image"])

    print("✅ Image processing completed")
