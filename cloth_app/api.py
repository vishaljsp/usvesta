from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Product, APIKey, Color_product, product_Gelery_images, color_product_Gelery_images, Size_price_par_post

class ProductSyncAPIView(View):
    def get(self, request, *args, **kwargs):
        # 1. Authenticate Request
        api_key_str = request.headers.get("X-API-KEY") or request.GET.get("api_key")
        if not api_key_str:
            return JsonResponse({"error": "Authentication credentials were not provided. Use X-API-KEY header or api_key query parameter."}, status=401)
        
        try:
            api_key = APIKey.objects.get(key=api_key_str, is_active=True)
        except APIKey.DoesNotExist:
            return JsonResponse({"error": "Invalid or inactive API Key."}, status=403)
            
        # 2. Build absolute URI prefix
        host = request.build_absolute_uri('/')[:-1] # e.g. "http://127.0.0.1:8000"
        
        # 3. Retrieve Published Products
        products = Product.objects.filter(product_status="Publish").order_by("-id")
        
        serialized_products = []
        for p in products:
            # Main image absolute URL
            main_image_url = host + p.product_image.url if p.product_image else ""
            
            # Fetch sizes
            sizes = list(Size_price_par_post.objects.filter(product=p).values_list("size", flat=True))
            
            # Fetch gallery images
            gallery = []
            for g_img in product_Gelery_images.objects.filter(product=p):
                if g_img.image:
                    gallery.append({
                        "image_url": host + g_img.image.url,
                        "alt": g_img.alt or ""
                    })
                    
            # Fetch color variants
            variants = []
            for col_var in Color_product.objects.filter(product=p):
                variant_image = host + col_var.color_images.url if col_var.color_images else ""
                
                # Variant gallery images
                var_gallery = []
                for vg in color_product_Gelery_images.objects.filter(color_product=col_var):
                    if vg.image:
                        var_gallery.append({
                            "image_url": host + vg.image.url,
                            "alt": vg.alt or ""
                        })
                        
                variants.append({
                    "id": col_var.id,
                    "color": col_var.color,
                    "color_code": col_var.color_code,
                    "color_image": variant_image,
                    "gallery": var_gallery
                })
                
            serialized_products.append({
                "id": p.id,
                "uuid": p.uuid_product,
                "name": p.product_name,
                "slug": p.product_slug,
                "sku": p.product_sku or "",
                "brand": p.brand,
                "category": p.category.name if p.category else "",
                "sub_category": p.sub_category.name if p.sub_category else "",
                "description": p.product_description,
                "keywords": p.key_words or "",
                "regular_price": p.discount_price,
                "sale_price": str(p.b2c_price),
                "b2b_price": str(p.b2b_price) if p.b2b_price else "",
                "t_shirt_type": p.t_shirt_type or "",
                "ratings": p.ratings or "0",
                "quantity_offer": p.product_quantity_offer or 0,
                "amount_offer": str(p.product_amount_offer) if p.product_amount_offer else "",
                "main_image": main_image_url,
                "sizes": sizes,
                "gallery": gallery,
                "color_variants": variants,
                "date_created": p.date.isoformat()
            })
            
        return JsonResponse({
            "status": "success",
            "count": len(serialized_products),
            "products": serialized_products
        }, safe=False)
