from .models import *
from django.conf import settings
from django.db.models import Avg, Count


def single_templates_data(request):
    user=request.user
    autocomplate=Product.objects.all().order_by("id")
    categorys=Product_category.objects.all().order_by("-id")
    sub_category=Product_sub_category.objects.all()
    banners=Banners.objects.all()
    testimonial=Testimoninal.objects.all().order_by("-id")
    trusted_brans=Our_trusted_client.objects.all().order_by("-id")
    insta_images=Insta_images.objects.all().order_by("-id")
    products = Product.objects.filter(top_eight_products=False).order_by("-id")
    if not products.exists():
        products = Product.objects.all().order_by("-id")
    # products_all_index_page_top = Product.objects.filter(product_status="Publish",top_eight_products=True).order_by("-id")
    current_url = request.build_absolute_uri()

    products_all_index_page_top = Product.objects.filter(
        # product_status="Publish",
        top_eight_products=True
    ).annotate(
        avg_rating=Avg("user_reviews__star"),
        review_count=Count("user_reviews")

    ).order_by("-id")
    courdinators=sub_category_coordinator.objects.all().order_by("-id")

    
    homepage_cms = HomePageEditor.objects.first()
    if not homepage_cms:
        homepage_cms = HomePageEditor.objects.create()

    data={
        "courdinators":courdinators,
        "courdinators_pages":courdinators,
        "cms": homepage_cms,
        "homepage_cms": homepage_cms,
        
        "products_all_index_page": products[:8],  # Use in template
        "search_data":autocomplate,
        "products_all_index_page_top":products_all_index_page_top,
        "categorys":categorys[0:4],
        "nev_cat":categorys,
        "sub_category":sub_category,
        "banners":banners,
        "user":user,
        "product_sh":autocomplate,
        "testimonial":testimonial,
        "trusted_brans":trusted_brans,
        "appid":settings.APP_ID,
        "appkey":settings.APP_KEY,
        "current_url":current_url,
        'insta_images':insta_images,
       
    }

    return data



def single_templates_data_for_add_to_cart(request):

    user = request.user
    shopping_cart = []
    shopping_cart_inner = []

    session_cart = request.session.get("anonymous_cart", [])
    session_cart_inner = request.session.get("anonymous_cart_inner", [])


    # =============================
    # INNER PRODUCT CART
    # =============================

    if user.is_authenticated:

        for item in session_cart_inner:

            product_id = item.get("product_id")
            size = item.get("size")

            book = Color_product.objects.filter(id=product_id).first()

            if book:

                cart_obj, created = Cart.objects.get_or_create(
                    user=user,
                    inner_products_card=book
                )

                if size:
                    cart_obj.size = size
                    cart_obj.save()


        request.session["anonymous_cart_inner"] = []
        request.session.modified = True

        shopping_cart_inner = list(
            Cart.objects.filter(user=user, inner_products_card__isnull=False)
            .select_related("inner_products_card")
        )

    else:

        for item in session_cart_inner:

            product_id = item.get("product_id")
            size = item.get("size")

            pd0 = Color_product.objects.filter(id=product_id).first()

            if pd0:
                pd0.size = size
                shopping_cart_inner.append(pd0)



    # =============================
    # NORMAL PRODUCT CART
    # =============================

    if user.is_authenticated:

        for item in session_cart:

            product_id = item.get("product_id")
            size = item.get("size")

            book = Product.objects.filter(id=product_id).first()

            if book:

                cart_obj, created = Cart.objects.get_or_create(
                    user=user,
                    product=book
                )

                if size:
                    cart_obj.size = size
                    cart_obj.save()


        request.session["anonymous_cart"] = []
        request.session.modified = True

        shopping_cart = list(
            Cart.objects.filter(user=user, product__isnull=False)
            .select_related("product")
        )

    else:

        for item in session_cart:

            product_id = item.get("product_id")
            size = item.get("size")

            pd = Product.objects.filter(id=product_id).first()

            if pd:
                pd.size = size
                shopping_cart.append(pd)


    data = {
        "shopping_cart": shopping_cart,
        "shopping_cart_inner": shopping_cart_inner,
    }

    return data