from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.utils.timezone import now
from django.utils.text import escape
from django.utils.html import strip_tags

from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_backends, update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db import transaction
from django.db.models import Q, Count, Avg, Case, When, FloatField, Min, Max
from django.db.models.functions import Cast

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.conf import settings

from decimal import Decimal
from datetime import datetime, timedelta

import uuid
import json
import base64
import re
import time
import traceback
import threading
import mimetypes
import requests
import razorpay
import openpyxl

from concurrent.futures import ThreadPoolExecutor

from .models import *
from .emal_sender_function import *
from .search_htmlbar import single_templates_data_for_add_to_cart




def Llmsfile_for_ai(request):
    return render(request,"llms.txt")
def product_feed_xml(request):
    products = Product.objects.all()

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">'
    xml += '<channel>'
    xml += '<title>Us Vesta Products</title>'
    xml += '<link>https://www.usvesta.com/</link>'
    xml += '<description>Product Feed</description>'

    for p in products:

        # ESCAPE everything properly
        title = escape(p.product_name or "")
        desc1 = strip_tags(p.product_description or "")
        desc = escape(desc1)
        img = request.build_absolute_uri(p.product_image.url)

        # link for product (if you have get_absolute_url)
        try:
            link = request.build_absolute_uri(f"/products/{p.uuid_product}")
        except:
            link = "https://www.usvesta.com/products"

        xml += (
            "<item>"
            f"<g:id>{p.id}</g:id>"
            f"<g:title>{title}</g:title>"
            f"<g:description>{desc}</g:description>"
            f"<g:link>{link}</g:link>"
            f"<g:image_link>{img}</g:image_link>"
            f"<g:price>{p.b2c_price} INR</g:price>"
            "<g:condition>new</g:condition>"
            "<g:availability>in stock</g:availability>"
            "</item>"
        )

    xml += '</channel></rss>'

    return HttpResponse(xml, content_type="application/xml")



# class Hendling500(View):
#     def get(self,request,exception):
#         return render(request,"500.html",{})
# class Hendling404(View):
#     def get(self,request,exception):
#         return render(request,"404.html",{})
   
   
   
def error_404(request, exception):
    return render(request, "404.html", status=404)

def error_500(request):
    return render(request, "500.html", status=500)  
    


@csrf_exempt
def get_cart_data(request):
    # sirf function call karo
    res=single_templates_data_for_add_to_cart(request)
    
    return render(request,"partials/cart_items.html",res)
class Logout(View):

    def get(self,request):
        logout(request)
        return redirect("/")
    def post(self,request):
        data=json.loads(request.body)
        forget_email=data.get("reset_email")
        if forget_email:
            check_user=CustomUser.objects.filter(username=forget_email).first()
            if check_user:
                check_user.password_reset_requested_at = now()  # Store request time
                check_user.save()
                massage=f"""
                    Welcome To Exalon 
                    Thank You {check_user.first_name}
                    click this link to reset Your password http://127.0.0.1:8000/reset-passsword/{check_user.email_token}
                    """
                sending_email_forget("Reset Your Pasword",massage,forget_email)
                return JsonResponse({"status":200,"mesej":"We Sent Forget Paasword Link On Your Email"})
            else:
                return JsonResponse({"status":400,"mesej":"User Not Found !"})
        else:
            return JsonResponse({"status":500})
                

 
 

class Register_and_login(View):
    def get(self,request):
        if request.user.is_authenticated:
            # Get previous page URL (or home as fallback)
            next_url = request.META.get('HTTP_REFERER', '/')
            return redirect(next_url)
        return render(request,"login-register.html")

    def post(self,request):
        phone=request.POST.get("l_phone")
        otp_from_user=request.POST.get("otp_user")
        rendring_next_url=request.POST.get("rendring_next_url")

        if phone:
            user, created = CustomUser.objects.get_or_create(phone=phone, defaults={'username': phone})
            request.session['phone'] = phone
            return JsonResponse({"res":"OTP Send Successfully"})
        
        elif otp_from_user:
            phone = request.session.get("phone")
            if not phone:
                return JsonResponse({"res": "Session expired, please resend OTP"})
            user = CustomUser.objects.filter(phone=phone).first()
            if user and user.phone_number_otp == otp_from_user and user.is_otp_valid():
                backend = get_backends()[0]
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                login(request, user)
                messages.success(request, "Login successful!")
                return JsonResponse({"status":200})
            else:
                return JsonResponse({"res":"Invalid OTP or OTP expired"})

       


            
    
class Reset_password(View):
    def get(self,request,email_token_url):
        user_exist_token=CustomUser.objects.filter(email_token=email_token_url).first()
        if user_exist_token:   
             # Check if the reset link has expired (valid for 30 minutes)
            if user_exist_token.password_reset_requested_at and now() - user_exist_token.password_reset_requested_at > timedelta(minutes=30):
                return HttpResponse("This reset password link has expired.")
        
            mes="Make A Strong Password"
        else:
            return HttpResponse("Invalide Reset Password Link")

        return render(request,"resetpassword.html",{"token_res":mes})
    
    def post(self,request,email_token_url):
        user_exist_token=CustomUser.objects.filter(email_token=email_token_url).first()
        
        new_pwd=request.POST.get("new_password")
        if user_exist_token:
            if user_exist_token.password_reset_requested_at and now() - user_exist_token.password_reset_requested_at > timedelta(minutes=5):
                return HttpResponse("This reset password link has expired.")
            user_exist_token.set_password(new_pwd)  # Hash the password before saving
            user_exist_token.email_token = uuid.uuid4()  # Reset the token
            user_exist_token.decrypt_password = new_pwd # Reset the token
            user_exist_token.password_reset_requested_at = None  # Clear request time
            user_exist_token.save()
            messages.success(request,"Password Reset Successfully.")
            return redirect("/")           
        else:
            messages.success(request,"Invalid Request.")
            return redirecting_previus_pege(request)
        
class Inner_p_wish_list(View):
    
    def post(self, request):
        try:
            user = request.user
            data = json.loads(request.body)
            product_id = data.get("product_id")
            remove_product_id = data.get("remove_product_id")
            
            session_cart = request.session.get("anonymous_wish_inner", [])

            if user.is_authenticated:
                if remove_product_id:
                    Wishlist.objects.filter(user=user,id=remove_product_id).delete()
                    return JsonResponse({"message": "Product Delete to wishlist"})
                    
                if product_id:
                    bookadd = color_product_Gelery_images.objects.filter(id=product_id).first() 
                    if bookadd:
                        exist_or_not=Wishlist.objects.filter(user=user,inner_products_wishlist=bookadd).first()
                        if exist_or_not :
                            return JsonResponse({"message": "Product already in  to Wishlist"})
                        else:
                            Wishlist(user=user,inner_products_wishlist=bookadd).save()
                            return JsonResponse({"message": "Product added to Wishlist"})
                    else:
                        return JsonResponse({"message": "Ooops Somthig Want Wrong !"})
                for prod_id in session_cart:
                    book = color_product_Gelery_images.objects.filter(id=prod_id).first()
                    if book:
                        Wishlist.objects.get_or_create(user=user, inner_products_wishlist=book)  
                        
                
                request.session["anonymous_wish_inner"] = []  # Clear session cart
                request.session.modified = True 

            else:                    
                if remove_product_id:
                    if remove_product_id in session_cart:
                        session_cart.remove(remove_product_id)  # ✅ Remove item from session
                        request.session["anonymous_wish_inner"] = session_cart
                        request.session.modified = True
                        return JsonResponse({"message": "Product removed from Wishlist", "wishlist": session_cart})

                if product_id:
                    if product_id not in session_cart:
                        session_cart.append(product_id)  # ✅ Add to session list
                        request.session["anonymous_wish_inner"] = session_cart
                        request.session.modified = True
                        return JsonResponse({"message": "Product added to Wishlist", "wishlist": session_cart})
                    else:
                        return JsonResponse({"message": "Product already in Wishlist", "wishlist": session_cart})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)





class Wish_list(View):
    def get(self, request):
        user = request.user
        shopping_wish = []
        shopping_wish_inner = []
        
        session_cart = request.session.get("anonymous_wish", [])            

        session_cart_inner = request.session.get("anonymous_wish_inner", [])            

        if user.is_authenticated:
            for prod_id in session_cart_inner:
                book = color_product_Gelery_images.objects.filter(id=prod_id).first()
                if book:
                    Wishlist.objects.get_or_create(user=user, inner_products_wishlist=book)  
            
            request.session["anonymous_wish_inner"] = []  # Clear session cart
            request.session.modified = True 
            shopping_wish_inner = list(Wishlist.objects.filter(user=user).select_related("product"))  # ✅ Optimized DB query
        else:
            shopping_cart00 = request.session.get("anonymous_wish_inner", [])
            for a in shopping_cart00:  # ✅ Loop over session cart
                pd000 = color_product_Gelery_images.objects.filter(id=a).first()  # ✅ Get single book
                if pd:
                    shopping_wish_inner.append(pd000)  # ✅ Append book object
        
        
        
        if user.is_authenticated:
            for prod_id in session_cart:
                book = Product.objects.filter(id=prod_id).first()
                if book:
                    Wishlist.objects.get_or_create(user=user, product=book)  
            
            request.session["anonymous_wish"] = []  # Clear session cart
            request.session.modified = True 
            shopping_wish = list(Wishlist.objects.filter(user=user).select_related("product"))  # ✅ Optimized DB query
        else:
            shopping_cart0 = request.session.get("anonymous_wish", [])
            for a in shopping_cart0:  # ✅ Loop over session cart
                pd = Product.objects.filter(id=a).first()  # ✅ Get single book
                if pd:
                    shopping_wish.append(pd)  # ✅ Append book object

        data = {
            "shopping_wish": shopping_wish,
            "shopping_wish_inner":shopping_wish_inner
        }
        print(data," *-*-*-**-*-*-**-**")
        return render(request, "my-account.html", data)
 # Return JSON instead of rendering HTML

    def post(self, request):
        try:
            user = request.user
            data = json.loads(request.body)
            product_id = data.get("product_id")
            inner_product_id = data.get("inner_product_id")
            remove_product_id = data.get("remove_product_id")
            remove_product_id_inner = data.get("remove_product_id_inner")
            
            session_cart = request.session.get("anonymous_wish", [])
            session_cart_inner = request.session.get("anonymous_wish_inner", [])

            if user.is_authenticated:
                if remove_product_id:
                    Wishlist.objects.filter(user=user, id=remove_product_id).delete()
                    return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                    
                if product_id:
                    bookadd = Product.objects.filter(id=product_id).first() 
                    if bookadd:
                        exist_or_not = Wishlist.objects.filter(user=user, product=bookadd).first()
                        if exist_or_not:
                            exist_or_not.delete()
                            return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                        else:
                            Wishlist(user=user, product=bookadd).save()
                            return JsonResponse({"message": "Product added to Wishlist", "added": True})
                    else:
                        return JsonResponse({"message": "Oops! Product not found."})

                if inner_product_id:
                    bookadd = color_product_Gelery_images.objects.filter(id=inner_product_id).first()
                    if bookadd:
                        exist_or_not = Wishlist.objects.filter(user=user, inner_products_wishlist=bookadd).first()
                        if exist_or_not:
                            exist_or_not.delete()
                            return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                        else:
                            Wishlist(user=user, inner_products_wishlist=bookadd).save()
                            return JsonResponse({"message": "Product added to Wishlist", "added": True})
                    else:
                        return JsonResponse({"message": "Oops! Variant product not found."})
            else:                    
                if remove_product_id:
                    if remove_product_id in session_cart:
                        session_cart.remove(remove_product_id)
                        request.session["anonymous_wish"] = session_cart
                        request.session.modified = True
                    return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                    
                if remove_product_id_inner:
                    if remove_product_id_inner in session_cart_inner:
                        session_cart_inner.remove(remove_product_id_inner)
                        request.session["anonymous_wish_inner"] = session_cart_inner
                        request.session.modified = True
                    return JsonResponse({"message": "Product removed from Wishlist", "added": False})

                if product_id:
                    if product_id in session_cart:
                        session_cart.remove(product_id)
                        request.session["anonymous_wish"] = session_cart
                        request.session.modified = True
                        return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                    else:
                        session_cart.append(product_id)
                        request.session["anonymous_wish"] = session_cart
                        request.session.modified = True
                        return JsonResponse({"message": "Product added to Wishlist", "added": True})

                if inner_product_id:
                    if inner_product_id in session_cart_inner:
                        session_cart_inner.remove(inner_product_id)
                        request.session["anonymous_wish_inner"] = session_cart_inner
                        request.session.modified = True
                        return JsonResponse({"message": "Product removed from Wishlist", "added": False})
                    else:
                        session_cart_inner.append(inner_product_id)
                        request.session["anonymous_wish_inner"] = session_cart_inner
                        request.session.modified = True
                        return JsonResponse({"message": "Product added to Wishlist", "added": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class Inner_product_cart(View):
    def get(self, request):
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        messages.success(request, "Order placed successfully!")
        return redirect("/thank-you")

    def post(self, request):
        try:

            user = request.user
            data = json.loads(request.body)

            product_id = data.get("Inner_product_id")
            remove_product_id = data.get("remove_product_id_inner")

            size_card_id = data.get("size_card_id")
            size_product = data.get("size_product")

            quantity = data.get("quantity")
            card_id = data.get("card_id")

            session_cart = request.session.get("anonymous_cart_inner", [])

            # =============================
            # LOGIN USER
            # =============================

            if user.is_authenticated:

                # SIZE UPDATE
                if size_card_id and size_product:

                    cart_item = Cart.objects.filter(
                        user=user,
                        id=size_card_id
                    ).first()

                    if cart_item:
                        cart_item.size = size_product
                        cart_item.save()

                    return JsonResponse({"message": "Size updated"})


                # QUANTITY UPDATE
                if card_id and quantity:

                    cart_item = Cart.objects.filter(
                        user=user,
                        id=card_id
                    ).first()

                    if cart_item:
                        cart_item.quantity = quantity
                        cart_item.save()

                    return JsonResponse({"message": "Quantity updated"})


                # REMOVE ITEM
                if remove_product_id:

                    Cart.objects.filter(
                        user=user,
                        id=remove_product_id
                    ).delete()

                    return JsonResponse({"message": "Item removed"})


                # ADD PRODUCT
                if product_id:

                    product = Color_product.objects.filter(
                        id=product_id
                    ).first()

                    if product:

                        exist = Cart.objects.filter(
                            user=user,
                            inner_products_card=product
                        ).first()

                        if exist:
                            return JsonResponse({"message": "Product already in cart"})

                        Cart.objects.create(
                            user=user,
                            inner_products_card=product,
                            size="M"
                        )

                        return JsonResponse({"message": "Product added"})


                # =============================
                # SESSION → DATABASE SYNC
                # =============================

                for item in session_cart:

                    product = Color_product.objects.filter(
                        id=item["product_id"]
                    ).first()

                    if product:

                        exist = Cart.objects.filter(
                            user=user,
                            inner_products_card=product
                        ).first()

                        if not exist:

                            Cart.objects.create(
                                user=user,
                                inner_products_card=product,
                                size=item.get("size", "M")
                            )

                request.session["anonymous_cart_inner"] = []
                request.session.modified = True

                return JsonResponse({"message": "Cart synced"})


            # =============================
            # GUEST USER
            # =============================

            else:

                # REMOVE PRODUCT
                if remove_product_id:

                    session_cart = [
                        item for item in session_cart
                        if str(item.get("product_id")) != str(remove_product_id)
                    ]

                    request.session["anonymous_cart_inner"] = session_cart
                    request.session.modified = True

                    return JsonResponse({"message": "Removed"})


                # ADD PRODUCT
                if product_id:

                    exist = False

                    for item in session_cart:
                        if item["product_id"] == product_id:
                            exist = True

                    if not exist:

                        session_cart.append({
                            "product_id": product_id,
                            "size": None
                        })

                        request.session["anonymous_cart_inner"] = session_cart
                        request.session.modified = True

                        return JsonResponse({"message": "Added to session cart"})

                    else:
                        return JsonResponse({"message": "Already in cart"})



                # UPDATE SIZE
                if size_card_id and size_product:

                    for item in session_cart:

                        if item["product_id"] == size_card_id:
                            item["size"] = size_product

                    request.session["anonymous_cart_inner"] = session_cart
                    request.session.modified = True

                    return JsonResponse({"message": "Size updated in session"})


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
        
        
        
        
        
        
@method_decorator(csrf_exempt, name='dispatch')
class Add_Cart(View):    

    def post(self, request):
        try:

            user = request.user
            data = json.loads(request.body)

            product_id = data.get("product_id")
            remove_product_id = data.get("remove_product_id")

            card_id = data.get("card_id")
            quantity = data.get("quantity")

            size_card_id = data.get("size_card_id")
            size_product = data.get("size_product")

            session_cart = request.session.get("anonymous_cart", [])

            # ==============================
            # LOGIN USER
            # ==============================

            if user.is_authenticated:

                # SIZE UPDATE
                if size_card_id and size_product:

                    adding = Cart.objects.filter(user=user, id=size_card_id).first()

                    if adding:
                        adding.size = size_product
                        adding.save()

                    return JsonResponse({"message": "Size updated"})


                # QUANTITY UPDATE
                if card_id and quantity:

                    increase = Cart.objects.filter(user=user, id=card_id).first()

                    if increase:
                        increase.quantity = quantity
                        increase.save()

                    return JsonResponse({"status": 200})


                # REMOVE PRODUCT
                if remove_product_id:

                    Cart.objects.filter(user=user, id=remove_product_id).delete()

                    return JsonResponse({
                        "message": "Product removed from cart"
                    })


                # ADD PRODUCT
                if product_id:

                    bookadd = Product.objects.filter(id=product_id).first()

                    if bookadd:

                        exist = Cart.objects.filter(
                            user=user,
                            product=bookadd
                        ).first()

                        if exist:
                            return JsonResponse({
                                "message": "Product already in cart"
                            })

                        Cart.objects.create(
                            user=user,
                            product=bookadd,
                            size="M"
                        )

                        return JsonResponse({
                            "message": "Product added to cart"
                        })


                # ==============================
                # SESSION → DATABASE SYNC
                # ==============================

                for item in session_cart:

                    product_id = item.get("product_id")
                    size = item.get("size")

                    book = Product.objects.filter(id=product_id).first()

                    if book:

                        exist = Cart.objects.filter(
                            user=user,
                            product=book
                        ).first()

                        if not exist:

                            Cart.objects.create(
                                user=user,
                                product=book,
                                size=size if size else "M"
                            )

                request.session["anonymous_cart"] = []
                request.session.modified = True

                return JsonResponse({"message": "Cart synced"})


            # ==============================
            # GUEST USER
            # ==============================

            else:

                # REMOVE PRODUCT
                if remove_product_id:

                    session_cart = [
                        item for item in session_cart
                        if str(item.get("product_id")) != str(remove_product_id)
                    ]

                    request.session["anonymous_cart"] = session_cart
                    request.session.modified = True

                    return JsonResponse({"message": "Removed"})


                # ADD PRODUCT
                if product_id:

                    exist = False

                    for item in session_cart:

                        if item["product_id"] == product_id:
                            exist = True

                    if not exist:

                        session_cart.append({
                            "product_id": product_id,
                            "size": None
                        })

                        request.session["anonymous_cart"] = session_cart
                        request.session.modified = True

                        return JsonResponse({"message": "Added to session cart"})

                    else:

                        return JsonResponse({"message": "Already in cart"})


                # SIZE UPDATE
                if size_card_id and size_product:

                    for item in session_cart:

                        if item["product_id"] == size_card_id:

                            item["size"] = size_product

                    request.session["anonymous_cart"] = session_cart
                    request.session.modified = True

                    return JsonResponse({"message": "Size updated"})


        except Exception as e:

            return JsonResponse({"error": str(e)}, status=500) 
         
 
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
        
        
        
        
        
from . search_htmlbar import *


# @method_decorator(cache_page(60 * 10), name='dispatch')  # 10 minutes
class Home(View):
    def get(self,request):
        data = single_templates_data(request)
        data["category"] = Product_category.objects.all()
        target_categories = ["T-Shirt", "T-Shirts Collection", "Shirt", "Shirts Collection", "Caps", "Personalized Caps & Headwea", "Bag", "Custom Corporate Bags", "Towels"]
        categories = Product_category.objects.filter(name__in=target_categories)
        custom_app = Product.objects.filter(category__in=categories)[0:8]
        if not custom_app.exists():
            custom_app = Product.objects.filter(product_status="Publish")[0:8]
        data["custom_Apparel"] = custom_app
        
        cms = data.get("cms")
        item_count = cms.section4_slider_mobile_item_count if (cms and cms.section4_slider_mobile_item_count) else 4
        if item_count < 1 or item_count > 4: item_count = 4

        all_featured = list(Product.objects.filter(product_status="Publish").order_by("-id")[:16])
        if not all_featured:
            all_featured = list(Product.objects.all().order_by("-id")[:16])
        data["featured_products"] = all_featured
        # Dynamic chunking based on Dashboard item count selection (1, 2, 3, or 4 products per slide)
        data["featured_products_chunks"] = [all_featured[i:i+item_count] for i in range(0, len(all_featured), item_count)]

        bags = Product.objects.filter(category__name__icontains="Bag")[0:8]
        data["corporate_Bags"] = bags
        data["testimonials"] = Testimoninal.objects.all()
        return render(request,"index.html",data)


class About_us(View):
    def get(self,request):
        tshirt=Product.objects.filter(category__id=1).order_by("-id")[0:8]
        lower=Product.objects.filter(category__id=2).order_by("-id")[0:8]
        shirt=Product.objects.filter(category__id=3).order_by("-id")[0:8]
        data={
            "t-shirt":tshirt,
            "lowers":lower,
            "shirts":shirt,
        }
        return render(request,"about-us.html",data)


class ContactUs(View):
    def get(self,request):
        return render(request,"contact.html")
    
    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        message = request.POST.get("message")

        if name and email and phone:
            Contact_US.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message
            )
            messages.success(request, "Your request has been submitted successfully. We will connect with you soon.")
            return redirect("/contact-us")
        else:
            messages.error(request, "All fields are required.")
            return redirect("/contact-us")

class Profile(View):
    def update_tracking_background(self, order_ids):
        from .models import Order  # re-import inside thread (important)

        orders = Order.objects.filter(id__in=order_ids)

        for order in orders:

            if not order.awb_number:
                continue

            if order.status in ["Delivered", "Cancelled"]:
                continue

            try:
                delhivery_status = track_shipment(order.awb_number)

                if not delhivery_status:
                    continue

                new_status = map_status(delhivery_status, order)

                # cancel override protection
                if order.status == "Cancelled":
                    continue

                if order.status != new_status or order.shipment_status != delhivery_status:
                    order.status = new_status
                    order.shipment_status = delhivery_status
                    order.save()


            except Exception as e:
                print("Tracking Error:", e)


    def get(self, request):
        user = request.user
        tab = request.GET.get('tab', '')
        address_of_user=Address_user.objects.filter(user=user)
        # ⚡ fast query (limit bhi laga diya)
        all_order = Order.objects.filter(user=user).exclude(status="Pending").order_by("-id")[:10]

        # 🔥 only IDs pass karo (safe for thread)
        order_ids = list(all_order.values_list("id", flat=True))

        # 🔥 background thread (non-blocking)
        threading.Thread(
            target=self.update_tracking_background,
            args=(order_ids,),
            daemon=True  # IMPORTANT
        ).start()

        # 🚀 instant response
        return render(request, "my-account.html", {
            "orders_of_user": all_order,
            "address_of_user":address_of_user.first(),
            "address_of_user_list":address_of_user,
            "active_tab": tab,
        })
    
    
    def post(self, request):
        user = request.user

        # Update basic profile details
        user.first_name = request.POST.get("full_name", user.first_name)
        user.email = request.POST.get("email", user.email)
        user.phone = request.POST.get("phone", user.phone)
        user.about = request.POST.get("about", user.about)
        pwd = request.POST.get("new_pwd")
        user.decrypt_password = request.POST.get("new_pwd", user.decrypt_password)
        if pwd:
            user.set_password(pwd)

        # Handle profile image upload
        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]
        user.save()
        messages.success(request, "Profile Update SuccessFully")
        return redirect("profile")  # Change to your actual profile URL name

        


import threading

def create_orders_background(user, cart, user_address_selected, payment_status,
                             payment_method, transaction_id, transaction_order_id):

    for a in cart:
        uniq_id = uuid.uuid4()

        Order.objects.create(
            user=user,
            product=a.product,
            inner_color_product=a.inner_products_card,
            product_size=a.size,
            quantity=a.quantity,
            order_id=uniq_id,
            transaction_id=transaction_id,
            transaction_order_id=transaction_order_id,
            total_price=a.total_price() if a.total_price() else a.total_inner_product_price(),
            payment_status=payment_status,
            payment_method=payment_method,
            address=f"""
                first_name={user_address_selected.name}
                phone={user_address_selected.phone_numer}
                email={user_address_selected.email}
                state={user_address_selected.state}
                landmark={user_address_selected.landmark}
                pincode={user_address_selected.pin_code}
                address={user_address_selected.user_address}
            """.strip(),
        )

    # 🧹 cart delete bhi background me
    Cart.objects.filter(user=user).delete() 
    

class Checkout(View):
    # 🔥 BACKGROUND FUNCTION ADD करो (CLASS के अंदर)
    def create_orders_background(self, user, cart, user_address_selected,
                                 payment_status, payment_method,
                                 transaction_id, transaction_order_id,total_amount_for_order,sending_price_in_django_view):

        for a in cart:
            uniq_id = uuid.uuid4()
             # 👉 FINAL PRICE LOGIC
            if int(a.quantity) >= 3:
                final_price = int(a.quantity) * 350
            else:
                final_price = a.total_price() if a.total_price() else a.total_inner_product_price()

            Order.objects.create(
                user=user,
                product=a.product,
                inner_color_product=a.inner_products_card,
                product_size=a.size,
                quantity=a.quantity,
                order_id=uniq_id,
                transaction_id=transaction_id,
                transaction_order_id=transaction_order_id,
                # total_price=total_amount_for_order if total_amount_for_order else sending_price_in_django_view,
                total_price=final_price,

                payment_status=payment_status,
                payment_method=payment_method,
                address=f"""
                    first_name={user_address_selected.name}
                    phone={user_address_selected.phone_numer}
                    email={user_address_selected.email}
                    state={user_address_selected.state}
                    landmark={user_address_selected.landmark}
                    pincode={user_address_selected.pin_code}
                    address={user_address_selected.user_address}
                """.strip(),
            )

        # 🧹 cart delete भी background में
        
        Cart.objects.filter(user=user).delete()


    def get(self, request):
        # ❌ SAME AS YOUR CODE (NO CHANGE)
        user = request.user
        product_main=None
        product_inner=None
        size=None
        amount=0
        quanityt=1
        cart_product=None
        encoded_data = request.GET.get("data")

        if encoded_data:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)

            size = data.get("p_size")
            inner_product_id = data.get("inner_product")
            product_id = data.get("product_id_p")
            quanityt = data.get("quent")

            if inner_product_id:
                product_inner=Color_product.objects.filter(id=inner_product_id).first()
                amount=Decimal(quanityt)*Decimal(product_inner.product.b2c_price)

            elif product_id:
                product_main=Product.objects.filter(id=product_id).first()
                amount=Decimal(quanityt)* Decimal(product_main.b2c_price)

        else:
            cart_product = Cart.objects.filter(user=user)

            client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))

            cart_items = Cart.objects.filter(user=user)
            total_amount = sum(item.total_price() for item in cart_items)
            total_amount_inner_products = sum(item.total_inner_product_price() for item in cart_items)

            total_amount_for_online = int(total_amount_inner_products) + int(total_amount)

            if total_amount_for_online < 1:
                messages.error(request, "Cart is empty lor amount is too low to process.")
                return redirect("/")

        user_address=Address_user.objects.filter(user=request.user).order_by("-id")

        data = {
            "cart_products": cart_product,
            "key_id": settings.KEY_ID,
            "product_main":product_main,
            "product_inner":product_inner,
            "amount": amount,
            "quanityt":quanityt,
            "size":size,
            "totalfinal":int(amount)*int(quanityt),
            "user_address":user_address,
        }
        return render(request, "checkout.html", data)


    def post(self,request):
        user=request.user

        # 🔥 ADDRESS FIELDS (IMPORTANT - TOP ME)
        fullname = request.POST.get("fullname")
        address = request.POST.get("address")
        state = request.POST.get("state")
        landmark = request.POST.get("landmark")
        pincode = request.POST.get("zipcode")
        email = request.POST.get("email_if_in_addres")
        phone = request.POST.get("phone_nummber")
        phone_addresS = request.POST.get("phone_addresS")

        address_id=request.POST.get("address_id")
        address_ids=request.POST.get("address_ids")

        # ✅ 1. ADDRESS SAVE (FIXED ✅)
        if fullname and landmark and phone and email and state and pincode and address:
            new_address = Address_user.objects.create(
                user=user,
                name=fullname,
                email=email,
                state=state,
                phone_numer=phone,
                pin_code=pincode,
                landmark=landmark,
                user_address=address,
            )

            user_address = Address_user.objects.filter(user=user).order_by("-id")

            if phone_addresS:
                return render(request, "phone_address_list.html",
                    {"user_address": user_address, "new_id": new_address.id}
                )
            else:
                return render(request, "address_list.html",
                    {"user_address": user_address, "new_id": new_address.id}
                )

        # 🔥 PAYMENT PART (unchanged)
        totalquantity = request.POST.get("totalquantity")

        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")

        cashfree_order_id = request.POST.get("chashfree_payment_id_usingdecstop")
        cashfree_payment_id = request.POST.get("chashfree_order_id_usingdecstop")

        transaction_id = cashfree_payment_id or razorpay_payment_id or ""
        transaction_order_id = cashfree_order_id or razorpay_order_id or ""
        is_paid = bool(transaction_id)

        payment_status = "paid" if is_paid else "Pending"
        payment_method = "Online" if is_paid else "Cash On Delivery"

        total_amount_for_order = request.POST.get("product_total_bill")
        print("*-*-****-***-",total_amount_for_order)
        product_id = request.POST.get("product_id")
        product_size = request.POST.get("product_size")
        inner_product_id=request.POST.get("inner_product_id")
        sending_price_in_django_view=request.POST.get("sending_price_in_django_view")
        print("*-*-****-***-",sending_price_in_django_view)

        product_card_wala_he=request.POST.get("product_card_wala_he")

        # ✅ SINGLE PRODUCT
        if product_id and (address_id or address_ids):
            user_address_selected=Address_user.objects.get(id=address_id or address_ids)
            product=Product.objects.get(id=product_id)

            Order.objects.create(
                user=user,
                product=product,
                product_size=product_size,
                quantity=totalquantity,
                order_id=uuid.uuid4(),
                transaction_id=transaction_id,
                transaction_order_id=transaction_order_id,
                total_price=total_amount_for_order if total_amount_for_order else sending_price_in_django_view,
                payment_status=payment_status,
                payment_method=payment_method,
                address=f"""
                    first_name={user_address_selected.name}
                    phone={user_address_selected.phone_numer}
                    email={user_address_selected.email}
                    state={user_address_selected.state}
                    landmark={user_address_selected.landmark}
                    pincode={user_address_selected.pin_code}
                    address={user_address_selected.user_address}
                """.strip(),
            )

        elif inner_product_id and (address_id or address_ids):
            user_address_selected=Address_user.objects.get(id=address_id or address_ids)
            inner_product=Color_product.objects.get(id=inner_product_id)

            Order.objects.create(
                user=user,
                inner_color_product=inner_product,
                product_size=product_size,
                quantity=totalquantity,
                order_id=uuid.uuid4(),
                transaction_id=transaction_id,
                transaction_order_id=transaction_order_id,
                total_price=total_amount_for_order if total_amount_for_order else sending_price_in_django_view,
                payment_status=payment_status,
                payment_method=payment_method,
                address=f"""
                    first_name={user_address_selected.name}
                    phone={user_address_selected.phone_numer}
                    email={user_address_selected.email}
                    state={user_address_selected.state}
                    landmark={user_address_selected.landmark}
                    pincode={user_address_selected.pin_code}
                    address={user_address_selected.user_address}
                """.strip(),
            )

        # 🔥 CART CASE (FAST + THREAD)
        elif product_card_wala_he and (address_id or address_ids):

            user_address_selected=Address_user.objects.get(id=address_id or address_ids)

            cart = list(Cart.objects.filter(user=user))

            threading.Thread(
                target=self.create_orders_background,
                args=(user, cart, user_address_selected,
                    payment_status, payment_method,
                    transaction_id, transaction_order_id,total_amount_for_order,sending_price_in_django_view),
                daemon=True
            ).start()

            messages.success(request, "Order placed successfully!")
            return redirect("/thank-you")

        messages.success(request, "Order placed successfully!")
        return redirect("/thank-you")



class Shop(View):
    
    def get(self, request):
        min_max = Product.objects.annotate(
            price_float=Cast('b2b_price', FloatField())
        ).aggregate(
            
            min_price=Min('price_float'),
            max_price=Max('price_float')
        )

        innre_product=Color_product.objects.all()
        search_val = request.GET.get("searchbar")
        categories = request.GET.get("categories")
        page_number = request.GET.get('page')
        cats = Product_sub_category.objects.annotate(
            product_count=Count('product')
        )
        categories_main = Product_category.objects.annotate(
            sub_count=Count('product_sub_category')
        )
        breadclum=Product_sub_category.objects.filter(category_slug=categories).first()



        if categories:
            products = Product.objects.filter(
                sub_category__category_slug=categories
            ).annotate(
                avg_rating=Avg("user_reviews__star"),
                review_count=Count("user_reviews")
            )

        elif search_val:
            products = Product.objects.filter(
                product_name__icontains=search_val
            ).annotate(
                avg_rating=Avg("user_reviews__star"),
                review_count=Count("user_reviews")
            )

        else:
            products = Product.objects.all().annotate(
                avg_rating=Avg("user_reviews__star"),
                review_count=Count("user_reviews")
            ).order_by("-id")


        # paginator = Paginator(products,7)  # 9 products per page
        # page_obj = paginator.get_page(page_number)

        data = {
            "products_all": products,  # Use in template
            "inner_products_all": innre_product,  # Use in template
            "sub_ct": cats,
            "categories_main":categories_main,
            "breade_clum_cat":breadclum,
            'min_price': min_max['min_price'] or 0,
            'max_price': min_max['max_price'] or 10000,
            # 'page_obj': page_obj,  # For pagination controls
        }
        return render(request, "shop.html", data)







class Product_details(View):
    def get(self, request, slug):
        inner_gallery_image_list = []
        product_color = None
        inner_singal_main_product = None
        product_innner_size = None
        reviews = User_Reviews.objects.none()

        # 1️⃣ Get product or color variant by uuid, slug, or id
        if not slug or str(slug).strip() in ('None', 'null', ''):
            return redirect('/shop')

        product = Product.objects.filter(uuid_product=slug).first()
        inner_product = None
        if not product:
            inner_product = Color_product.objects.filter(uuid_product=slug).first()
        if not product and not inner_product:
            product = Product.objects.filter(product_slug=slug).first()
        if not product and not inner_product and str(slug).isdigit():
            product = Product.objects.filter(id=int(slug)).first()

        if not product and not inner_product:
            return redirect('/shop')

        # 2️⃣ Product sizes
        target_prod = inner_product.product if inner_product else product
        if product:
            reviews = User_Reviews.objects.filter(product=product, show=True)
            product_innner_size = Size_price_par_post.objects.filter(product=product).exclude(size__in=['1', '0', 'on', 'true', 'false', '']).exclude(size__regex=r'^\d+$')
        elif inner_product:
            reviews = User_Reviews.objects.filter(inner_product_rew=inner_product, show=True)
            product_innner_size = Size_price_par_post.objects.filter(product=inner_product.product).exclude(size__in=['1', '0', 'on', 'true', 'false', '']).exclude(size__regex=r'^\d+$')

        if target_prod and (not product_innner_size or product_innner_size.count() == 0):
            for s in ["S", "M", "L", "XL", "XXL"]:
                Size_price_par_post.objects.get_or_create(product=target_prod, size=s)
            product_innner_size = Size_price_par_post.objects.filter(product=target_prod).exclude(size__in=['1', '0', 'on', 'true', 'false', '']).exclude(size__regex=r'^\d+$')

        # 3️⃣ Gallery images
        gelery_images = []
        if product:
            gelery_images = product_Gelery_images.objects.filter(product=product)
        elif inner_product:
            inner_singal_main_product = inner_product.product
            inner_product_gelery = color_product_Gelery_images.objects.filter(color_product=inner_product)
            inner_gallery_image_list = [a.image.url for a in inner_product_gelery]

        # 4️⃣ Product colors
        if product:
            product_color = Color_product.objects.filter(product=product)
        elif inner_product:
            product_color = Color_product.objects.filter(product=inner_product.product)

        # 5️⃣ Handle color filter from query param
        color_id = request.GET.get("color-id-filter")
        if color_id:
            inner_gallery_image_list.clear()
            inner_product = Color_product.objects.filter(id=color_id).first()
            if inner_product:
                inner_product_gelery = color_product_Gelery_images.objects.filter(color_product=inner_product)
                inner_gallery_image_list = [a.image.url for a in inner_product_gelery]

        # 6️⃣ Reviews & related data
        count_review = reviews.count()
        total_stars = 0
        for review in reviews:
            try:
                total_stars += float(review.star)
            except (ValueError, TypeError):
                pass
        avg_rating = round(total_stars / count_review, 1) if count_review > 0 else 0.0

        star_counts = {
            5: reviews.filter(star='5').count(),
            4: reviews.filter(star='4').count(),
            3: reviews.filter(star='3').count(),
            2: reviews.filter(star='2').count(),
            1: reviews.filter(star='1').count(),
        }
        total_rev = count_review if count_review > 0 else 1
        rating_bars = []
        for s in [5, 4, 3, 2, 1]:
            cnt = star_counts[s]
            pct = round((cnt / total_rev) * 100)
            rating_bars.append({'star': s, 'count': cnt, 'percent': pct})

        related_product = Product.objects.all()
        aplus = A_plus_listing.objects.all()

        # 7️⃣ RECENTLY VIEWED LOGIC (Fixed and Unified)
        recently_viewed_products = []
        INNERrecently_viewed_products = []

        # --- For main product ---
        if product:
            rv = request.session.get('recently_viewed', [])
            if product.id in rv:
                rv.remove(product.id)
            rv.insert(0, product.id)
            rv = rv[:10]
            request.session['recently_viewed'] = rv
            request.session.modified = True

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(rv)])
            recently_viewed_products = list(
                Product.objects.filter(pk__in=rv).exclude(pk=product.id).order_by(preserved)
            )

        # --- For color variant ---
        if inner_product:
            irv = request.session.get('innerrecently_viewed', [])
            if inner_product.id in irv:
                irv.remove(inner_product.id)
            irv.insert(0, inner_product.id)
            irv = irv[:10]
            request.session['innerrecently_viewed'] = irv
            request.session.modified = True

            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(irv)])
            INNERrecently_viewed_products = list(
                Color_product.objects.filter(pk__in=irv).exclude(pk=inner_product.id).order_by(preserved)
            )

        # 8️⃣ Combine if you want to show all together (optional)
        # combined_recent = recently_viewed_products + [x.product for x in INNERrecently_viewed_products]

        # 9️⃣ Send data to template
        active_product = inner_product.product if inner_product else product
        data = {
            "product": product,
            "active_product": active_product,
            "inner_product": inner_product,
            "inner_singal_main_product": inner_singal_main_product,
            "gelery_images": gelery_images,
            "gallery_image_list": inner_gallery_image_list,
            "product_color": product_color,
            "product_innner_size": product_innner_size,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "count_review": count_review,
            "rating_bars": rating_bars,
            "related_product": related_product,
            "aplus": aplus,
            "color_id_set_active": color_id,
            "recently_viewed": recently_viewed_products,
            "innerrecently_viewed_products": INNERrecently_viewed_products,
        }
            
        return render(request, "product-details.html", data)

    
    def post(self,request,slug):
        user=request.user
        name=request.POST.get("r_name")
        email=request.POST.get("r_email")
        reviw=request.POST.get("review")
        rate=request.POST.get("rating")
        product_id=request.POST.get("product_id")
        inner_product_id=request.POST.get("inner_product_id")

        if name and email and reviw:
            if inner_product_id:
                if user.is_authenticated:
                    User_Reviews(
                        inner_product_rew = Color_product.objects.filter(id=inner_product_id).first(),
                        user = user,
                        name =name,
                        email =email,
                        msg = reviw,
                        star = rate,
                    ).save()
                    messages.success(request,"Thank you for review")
                    return redirect(request.path)

                else:
                    User_Reviews(
                        inner_product_rew = Color_product.objects.filter(id=inner_product_id).first(),
                        name =name,
                        email =email,
                        msg = reviw,
                        star = rate,
                    ).save()
                    messages.success(request,"Thank you for reviewd")
                    return redirect(request.path)
            else:
                if user.is_authenticated:
                    User_Reviews(
                        product = Product.objects.filter(id=product_id).first(),
                        user = user,
                        name =name,
                        email =email,
                        msg = reviw,
                        star = rate,
                    ).save()
                    messages.success(request,"Thank you for review")
                    return redirect(request.path)

                else:
                    User_Reviews(
                        product = Product.objects.filter(id=product_id).first(),
                        name =name,
                        email =email,
                        msg = reviw,
                        star = rate,
                    ).save()
                    messages.success(request,"Thank you for reviewd")
                    return redirect(request.path)
                    
                
   








class B2b(View):
    def get(self,request):
        page_number = request.GET.get('page')
        products=Product.objects.filter(product_status="Publish")
        colors=Color_product.objects.all()
        cateegory=Product_category.objects.all()

        paginator = Paginator(products,10)  # 9 products per page
        page_obj = paginator.get_page(page_number)
        data={
            "category":cateegory,
            "all_products_b2b":page_obj,
            "colors":colors,
        }
        return render(request,"b2b.html",data)

class Orderspage(View):
    def get(self,request):
        user=request.user
        order_product=Order.objects.filter(user=user)
        data={
            "orders":order_product
        }
        return render(request,"order.html",data)




class Blogs_post(View):
    def get(self, request):
        page_number = request.GET.get('page')
        blog_post = Blog_post.objects.all().order_by('-date')
        
        # Category Filter
        category_slug = request.GET.get('category')
        if category_slug:
            blog_post = blog_post.filter(category__ct_slug=category_slug)
            
        # Search Filter
        search_query = request.GET.get('q')
        if search_query:
            blog_post = blog_post.filter(meta_title__icontains=search_query)
            
        paginator = Paginator(blog_post, 10)
        page_obj = paginator.get_page(page_number)
        b_cat = Blog_Category.objects.all()
        recent_blogs = Blog_post.objects.all().order_by('-date')[:5]
        
        data = {
            "all_blog": page_obj,
            "b_cat": b_cat,
            "recent_blogs": recent_blogs,
            "selected_category": category_slug,
            "search_query": search_query or ""
        }
        return render(request, "blog.html", data)
class blogs_details(View):
    def get(self, request, slug):
        blog_details = Blog_post.objects.filter(slug=slug).first()
        b_cat = Blog_Category.objects.all()
        recent_blogs = Blog_post.objects.all().order_by('-date')[:5]
        
        data = {
            "blog_details": blog_details,
            "b_cat": b_cat,
            "recent_blogs": recent_blogs
        }
        return render(request, "blogs.html", data)


class Make_design(View):
    def get(self, request):
        price = request.GET.get('product-price')  # in paise
        product_id = request.GET.get('product-id')
        product_id_inner = request.GET.get('inner-product-id')
        inner_products=None
        product=None
        if product_id:
            product = Product.objects.filter(id=product_id).first()
        if product_id_inner:
            inner_products=color_product_Gelery_images.objects.filter(id=product_id_inner).first()
            
        data = {
            "product_main": product,
            "price": price,
            "inner_product":inner_products,
            "product_id": product_id,
            "product_id_inner": product_id_inner,
            "key_id": settings.KEY_ID,
          
        }
        

        return render(request, "3dmokup.html",data)
    def post(self,request):
        
        data=request.POST
        pdf_design=request.FILES.get("pdf_design")
        customer_name=data.get("customer_name")
        product_id=data.get("proid")
        product_id_inner=data.get("product_id_inner")

        emailid=data.get("emailid")
        phone=data.get("phonenumber")
        quantity=data.get("quantity")
        address=data.get("address")
        meseg=data.get("meseg")
        amount_totalrz=data.get("totalAmount")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")

        if pdf_design and customer_name and emailid and phone and quantity and address:
            if product_id:
                produ=Product.objects.filter(id=product_id).first()
                if produ:
                    Order(
                        user=request.user,
                        product=produ,
                        custom_name=customer_name,
                        custom_email=emailid,
                        custom_number=phone,
                        custom_design=pdf_design,
                        quantity=quantity,
                        total_price=amount_totalrz,
                        address=address,
                        messag=meseg,
                        transaction_id =razorpay_payment_id if razorpay_payment_id else "",
                        transaction_order_id=razorpay_order_id if razorpay_order_id else "",
                        payment_status="paid" if razorpay_payment_id else "Pending",
                        payment_method="Online" if razorpay_payment_id else "Cash On Delivery"
                    ).save()
                    
                    return redirect("/profile")
            if product_id_inner:
                produ_inner=color_product_Gelery_images.objects.filter(id=product_id_inner).first()
                Order(
                    user=request.user,
                    inner_color_product=produ_inner,
                    custom_name=customer_name,
                    custom_email=emailid,
                    custom_number=phone,
                    custom_design=pdf_design,
                    quantity=quantity,
                    total_price=amount_totalrz,
                    address=address,
                    messag=meseg,
                    transaction_id =razorpay_payment_id if razorpay_payment_id else "",
                    transaction_order_id=razorpay_order_id if razorpay_order_id else "",
                    payment_status="paid" if razorpay_payment_id else "Pending",
                    payment_method="Online" if razorpay_payment_id else "Cash On Delivery"
                ).save()
                
                return redirect("/profile")
                    
        else:
            return HttpResponse("Please Try Again")
            
            




class Make_design_polo(View):
    def get(self, request):
        price = request.GET.get('product-price')  # in paise
        product_id = request.GET.get('product-id')
        product_id_inner = request.GET.get('inner-product-id')
        inner_products=None
        product=None
        if product_id:
            product = Product.objects.filter(id=product_id).first()
        if product_id_inner:
            inner_products=color_product_Gelery_images.objects.filter(id=product_id_inner).first()
            
        data = {
            "product_main": product,
            "price": price,
            "inner_product":inner_products,
            "product_id": product_id,
            "product_id_inner": product_id_inner,
            "key_id": settings.KEY_ID,
          
        }
        return render(request, "kolar3d.html",data)
    def post(self,request):
        
        data=request.POST
        pdf_design=request.FILES.get("pdf_design")
        customer_name=data.get("customer_name")
        product_id=data.get("proid")
        product_id_inner=data.get("product_id_inner")

        emailid=data.get("emailid")
        phone=data.get("phonenumber")
        quantity=data.get("quantity")
        address=data.get("address")
        meseg=data.get("meseg")
        amount_totalrz=data.get("totalAmount")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")

        if pdf_design and customer_name and emailid and phone and quantity and address:
            if product_id:
                produ=Product.objects.filter(id=product_id).first()
                if produ:
                    Order(
                        user=request.user,
                        product=produ,
                        custom_name=customer_name,
                        custom_email=emailid,
                        custom_number=phone,
                        custom_design=pdf_design,
                        quantity=quantity,
                        total_price=amount_totalrz,
                        address=address,
                        messag=meseg,
                        transaction_id =razorpay_payment_id if razorpay_payment_id else "",
                        transaction_order_id=razorpay_order_id if razorpay_order_id else "",
                        payment_status="paid" if razorpay_payment_id else "Pending",
                        payment_method="Online" if razorpay_payment_id else "Cash On Delivery"
                    ).save()
                    
                    return redirect("/profile")
            if product_id_inner:
                produ_inner=color_product_Gelery_images.objects.filter(id=product_id_inner).first()
                Order(
                    user=request.user,
                    inner_color_product=produ_inner,
                    custom_name=customer_name,
                    custom_email=emailid,
                    custom_number=phone,
                    custom_design=pdf_design,
                    quantity=quantity,
                    total_price=amount_totalrz,
                    address=address,
                    messag=meseg,
                    transaction_id =razorpay_payment_id if razorpay_payment_id else "",
                    transaction_order_id=razorpay_order_id if razorpay_order_id else "",
                    payment_status="paid" if razorpay_payment_id else "Pending",
                    payment_method="Online" if razorpay_payment_id else "Cash On Delivery"
                ).save()
                
                return redirect("/profile")
                    
        else:
            return HttpResponse("Please Try Again")
            
            




@method_decorator(csrf_exempt, name='dispatch')
class Payment_success(View):
    def get(self, request):
        order_id = request.GET.get("order_id")
        if order_id:
            Order.objects.filter(transaction_order_id=order_id).update(payment_status="paid", status="Ordered")
            
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect("/thank-you")

    def post(self, request):
        try:
            data = json.loads(request.body)

            razorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_payment_id")
            amount = int(data.get("amount", 0)) / 100  # in INR
            product_id = data.get("product_id")

            if not product_id:
                return JsonResponse({"error": "Product ID is missing"}, status=400)

            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found"}, status=404)

            try:
                address = Address_user.objects.filter(user=request.user).first()
                if not address:
                    return JsonResponse({"error": "No address found for user"}, status=404)
            except:
                return JsonResponse({"error": "Address fetch error"}, status=500)

            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=1,
                total_price=amount,
                order_id=razorpay_order_id,
                transaction_order_id=razorpay_order_id,
                transaction_id=razorpay_payment_id,
                payment_status='paid',
                payment_method='Online',
                status='Ordered',
                order_user_address=address
            )

            return JsonResponse({"message": "Payment successful", "order_id": order.id})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        

class Privacy_police(View):
    def get(self, request):
        return render(request,"privacy.html")
    
    
class Turmscunditions(View):
    def get(self, request):
        return render(request,"terms.html")
    
    
class Shipping(View):
    def get(self, request):
        return render(request,"shipingpolcy.html")
    

class Returnrefund(View):
    def get(self,request):
        return render(request,"retunrefundpolcy.html")

class Cancellationpolicy(View):
    def get(self, request):
        return render(request,"cancellationpolicy.html")

class Paymentpolicy(View):
    
    def get(self, request):
        return render(request,"paymentpolicy.html")

class Cookies(View):
    def get(self, request):
        return render(request,"cookie.html")
        



        



class Bhaaratkshetram(View):
    def get(self, request):
        return render(request,"bhaaratkshetram.html")
    

class Thenkyou(View):
    def get(self,request):
        return render(request,"thenks.html")

class Chat_boat(View):
    def post(self,request):
        name=request.POST.get("name")
        email=request.POST.get("email")
        number=request.POST.get("number")
        if name and email and number:
            Chatbot_users(name=name,email=email,phone=number).save()
            return JsonResponse({"status":200})
            
            
            
class CategoryB2b(View):
    def get(self,request):
      

        categories = request.GET.get("categories")
        page_number = request.GET.get('page')
        
        
        breadclum=Product_category.objects.filter(uuid_product=categories).first()
        if categories:
            products = Product.objects.filter(product_status="Publish",category__uuid_product=categories)
        paginator = Paginator(products,10)  # 9 products per page
        page_obj = paginator.get_page(page_number)

        data = {
            "products_all": page_obj,  # Use in template
            "breade_clum_cat":breadclum,
           
            'page_obj': page_obj,  # For pagination controls
        }
        return render(request,"b2b_category_flt.html",data)




class Collections_for_men(View):
    def get(self, request,slug):
        innre_product=color_product_Gelery_images.objects.all()
        sub_cat_=Product_sub_category.objects.filter(category_slug=slug).first()
        
        products = Product.objects.filter(
            sub_category__category_slug=slug
        ).annotate(
            avg_rating=Avg("user_reviews__star"),
            review_count=Count("user_reviews")
        ).order_by("-id")
       
        page_number = request.GET.get("page")

        paginator = Paginator(products, 12)   # 8 products per page
        page_obj = paginator.get_page(page_number)
        data = single_templates_data(request)
        data.update({
            "products_all": products,  # Use in template
            "page_obj": page_obj,
            "inner_products_all": innre_product,  # Use in template
            "sub_cat_":sub_cat_
        })
        return render(request,"colections/alltype_tshirts.html", data)
    

class Tshirtcategory(View):
    def get(self, request):
        return render(request,"colections/category_mens_t_shoirt.html")
    
    
    
# ###################### Dash board code  
class Web_ouwner(View):
    def get(self, request):
        return redirect("/usvesta-deshboard/")
      
    def post(self, request):
        order_id = request.POST.get("o_id")
        order_status = request.POST.get("o_status")
    
        if order_id and order_status:
            order = Order.objects.filter(id=order_id).first()
            if order:
                order.status = order_status
                order.save()
            return redirect("/customer-orders")
        else:
            return HttpResponse("Invalid Order Id or Status")


class Dahsboardview(View):
    def get(self, request):
        if not (request.user.is_authenticated and request.user.is_superuser):
            raise Http404()
        category = Product_category.objects.all().order_by("id")
        coordinator = sub_category_coordinator.objects.all().order_by("id")
        all_orders = Order.objects.exclude(status="Pending").order_by("-id")
        products_all = Product.objects.filter().order_by("-id")
        reviews = User_Reviews.objects.all().order_by("-id")
        color_products = Color_product.objects.all()
        sub_cat = Product_sub_category.objects.all()
        
        # Additional Models for Pro Dashboard Settings Control
        banners = Banners.objects.all().order_by("-id")
        testimonials = Testimoninal.objects.all().order_by("-id")
        trusted_clients = Our_trusted_client.objects.all().order_by("-id")
        insta_images = Insta_images.objects.all().order_by("-id")
        aplus_listings = A_plus_listing.objects.all().order_by("-id")
        blog_categories = Blog_Category.objects.all().order_by("-id")
        blog_posts = Blog_post.objects.all().order_by("-id")
        contact_messages = Contact_US.objects.all().order_by("-id")
        abandoned_checkouts = Leave_checkout_page_billing_details.objects.all().order_by("-id")
        chatbot_leads = Chatbot_users.objects.all().order_by("-id")
        api_keys = APIKey.objects.filter(merchant__user=request.user).order_by("-created_at") if hasattr(request.user, 'merchant_profile') else APIKey.objects.all().order_by("-created_at")
        return_requests = Return_and_Cancel_products.objects.all().order_by("-id")
        customers = CustomUser.objects.all().order_by("-id")

        # --- Live Analytics Calculation ---
        from django.db.models import Sum, Count
        from django.db.models.functions import ExtractMonth
        import datetime
        import json
        
        valid_orders = Order.objects.exclude(status="Pending")
        total_orders = valid_orders.count()
        
        # Calculate Revenue safely (sum total_price from orders)
        revenue_agg = Order.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum']
        if not revenue_agg:
            revenue_agg = Order.objects.aggregate(Sum('total_price'))['total_price__sum']
        total_revenue = float(revenue_agg or 0)
        
        total_customers = CustomUser.objects.filter(is_superuser=False).count()
        total_products = Product.objects.count()
        
        # Average Product Price
        avg_price_agg = Product.objects.aggregate(Sum('b2c_price'))['b2c_price__sum']
        avg_price = float(avg_price_agg or 0) / max(total_products, 1)
        
        # Monthly sales tracking for current year
        current_year = datetime.datetime.now().year
        monthly_orders_list = [0] * 12
        monthly_sales_list = [0] * 12
        
        db_monthly = valid_orders.filter(created_at__year=current_year)\
            .annotate(month=ExtractMonth('created_at'))\
            .values('month')\
            .annotate(count=Count('id'), total=Sum('total_price'))
            
        for item in db_monthly:
            m_idx = int(item['month']) - 1
            if 0 <= m_idx < 12:
                monthly_orders_list[m_idx] = item['count']
                monthly_sales_list[m_idx] = float(item['total'] or 0)
        
        data = {
            "category": category,
            "all_orders": all_orders,
            "products_all": products_all,
            "coordinator": coordinator,
            "reviews": reviews,
            "color_productskkx": color_products,
            "sub_cat": sub_cat,
            
            # New Context Keys
            "banners": banners,
            "testimonials": testimonials,
            "trusted_clients": trusted_clients,
            "insta_images": insta_images,
            "aplus_listings": aplus_listings,
            "blog_categories": blog_categories,
            "blog_posts": blog_posts,
            "contact_messages": contact_messages,
            "abandoned_checkouts": abandoned_checkouts,
            "chatbot_leads": chatbot_leads,
            "api_keys": api_keys,
            "return_requests": return_requests,
            "customers": customers,

            # Live Metrics Context
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_customers": total_customers,
            "total_products": total_products,
            "avg_price": avg_price,
            
            # Chart JSON arrays
            "monthly_orders_json": json.dumps(monthly_orders_list),
            "monthly_sales_json": json.dumps(monthly_sales_list),
        }
        return render(request, "dashboard/dashboard.html", data)

    def post(self, request):
        if not (request.user.is_authenticated and request.user.is_superuser):
            raise Http404()

        # ================= UPDATE HOMEPAGE CMS EDITOR =================
        if request.POST.get("update_homepage_cms"):
            cms = HomePageEditor.objects.first()
            if not cms:
                cms = HomePageEditor.objects.create()

            # Announcement Bar
            if "announcement_enabled" in request.POST:
                cms.announcement_enabled = request.POST.get("announcement_enabled") == "1"
            if "header_announcement_text" in request.POST:
                cms.header_announcement_text = request.POST.get("header_announcement_text")
            if "announcement_bg_color" in request.POST:
                cms.announcement_bg_color = request.POST.get("announcement_bg_color")
            if "announcement_text_color" in request.POST:
                cms.announcement_text_color = request.POST.get("announcement_text_color")
            if "announcement_font_size" in request.POST:
                cms.announcement_font_size = request.POST.get("announcement_font_size")

            # Header & Logo
            if "logo_width" in request.POST:
                cms.logo_width = request.POST.get("logo_width")
            if "logo_height" in request.POST:
                cms.logo_height = request.POST.get("logo_height")
            if "logo_link" in request.POST:
                cms.logo_link = request.POST.get("logo_link")
            if "header_bg_color" in request.POST:
                cms.header_bg_color = request.POST.get("header_bg_color")
            if "header_text_color" in request.POST:
                cms.header_text_color = request.POST.get("header_text_color")
            if "mobile_header_bg_color" in request.POST:
                cms.mobile_header_bg_color = request.POST.get("mobile_header_bg_color")
            if "mobile_header_text_color" in request.POST:
                cms.mobile_header_text_color = request.POST.get("mobile_header_text_color")
            if "header_logo" in request.FILES:
                cms.header_logo = request.FILES["header_logo"]
            if "mobile_header_logo" in request.FILES:
                cms.mobile_header_logo = request.FILES["mobile_header_logo"]

            # Mega Menu Cards File Uploads & Express Shipping
            if "mega_card1_image" in request.FILES:
                cms.mega_card1_image = request.FILES["mega_card1_image"]
            if "mega_card2_image" in request.FILES:
                cms.mega_card2_image = request.FILES["mega_card2_image"]
            if "mega_card3_image" in request.FILES:
                cms.mega_card3_image = request.FILES["mega_card3_image"]
            if "mega_card4_image" in request.FILES:
                cms.mega_card4_image = request.FILES["mega_card4_image"]
            if "mega_card5_image" in request.FILES:
                cms.mega_card5_image = request.FILES["mega_card5_image"]

            if "express_shipping_title" in request.POST:
                cms.express_shipping_title = request.POST.get("express_shipping_title")
            if "express_shipping_subtitle" in request.POST:
                cms.express_shipping_subtitle = request.POST.get("express_shipping_subtitle")

            # Hero Banner & Typography
            if "hero_subtitle" in request.POST:
                cms.hero_subtitle = request.POST.get("hero_subtitle")
            if "hero_subtitle_font_size" in request.POST:
                cms.hero_subtitle_font_size = request.POST.get("hero_subtitle_font_size")
            if "hero_subtitle_color" in request.POST:
                cms.hero_subtitle_color = request.POST.get("hero_subtitle_color")
            if "hero_title" in request.POST:
                cms.hero_title = request.POST.get("hero_title")
            if "hero_title_font_size" in request.POST:
                cms.hero_title_font_size = request.POST.get("hero_title_font_size")
            if "hero_title_color" in request.POST:
                cms.hero_title_color = request.POST.get("hero_title_color")
            if "hero_title_font_family" in request.POST:
                cms.hero_title_font_family = request.POST.get("hero_title_font_family")
            if "hero_description" in request.POST:
                cms.hero_description = request.POST.get("hero_description")
            if "hero_description_font_size" in request.POST:
                cms.hero_description_font_size = request.POST.get("hero_description_font_size")
            if "hero_button_text" in request.POST:
                cms.hero_button_text = request.POST.get("hero_button_text")
            if "hero_button_link" in request.POST:
                cms.hero_button_link = request.POST.get("hero_button_link")
            if "hero_button_bg_color" in request.POST:
                cms.hero_button_bg_color = request.POST.get("hero_button_bg_color")
            if "hero_button_text_color" in request.POST:
                cms.hero_button_text_color = request.POST.get("hero_button_text_color")
            if "hero_overlay_opacity" in request.POST:
                cms.hero_overlay_opacity = request.POST.get("hero_overlay_opacity")
            if "hero_bg_image" in request.FILES:
                cms.hero_bg_image = request.FILES["hero_bg_image"]
            if "hero_bg_mobile_image" in request.FILES:
                cms.hero_bg_mobile_image = request.FILES["hero_bg_mobile_image"]

            # Homepage Section Visibility Controls
            cms.section2_enabled = request.POST.get("section2_enabled") == "1"
            cms.section3_enabled = request.POST.get("section3_enabled") == "1"
            cms.section3_desktop_enabled = request.POST.get("section3_desktop_enabled") == "1"
            cms.section3_mobile_enabled = request.POST.get("section3_mobile_enabled") == "1"
            cms.women_coming_soon_enabled = request.POST.get("women_coming_soon_enabled") == "1"

            # Section 3 Mega Cards Content & Image Uploads
            for i in range(1, 6):
                t_key = f"section3_card{i}_title"
                p_key = f"section3_card{i}_price"
                d_key = f"section3_card{i}_desc"
                l_key = f"section3_card{i}_link"
                img_key = f"section3_card{i}_image"
                if t_key in request.POST: setattr(cms, t_key, request.POST.get(t_key))
                if p_key in request.POST: setattr(cms, p_key, request.POST.get(p_key))
                if d_key in request.POST: setattr(cms, d_key, request.POST.get(d_key))
                if l_key in request.POST: setattr(cms, l_key, request.POST.get(l_key))
                if img_key in request.FILES: setattr(cms, img_key, request.FILES[img_key])

            cms.section4_enabled = request.POST.get("section4_enabled") == "1"
            cms.section4_slider_enabled = request.POST.get("section4_slider_enabled") == "1"
            cms.section4_slider_desktop_enabled = request.POST.get("section4_slider_desktop_enabled") == "1"
            cms.section4_slider_mobile_enabled = request.POST.get("section4_slider_mobile_enabled") == "1"
            if "section4_slider_mobile_item_count" in request.POST:
                try: cms.section4_slider_mobile_item_count = int(request.POST.get("section4_slider_mobile_item_count"))
                except: pass
            if "section4_slider_title" in request.POST:
                cms.section4_slider_title = request.POST.get("section4_slider_title")
            cms.section5_enabled = request.POST.get("section5_enabled") == "1"
            cms.section6_enabled = request.POST.get("section6_enabled") == "1"

            # Country & Currency Selector
            cms.enable_country_modal = request.POST.get("enable_country_modal") == "1"
            if "usd_conversion_rate" in request.POST:
                try: cms.usd_conversion_rate = float(request.POST.get("usd_conversion_rate"))
                except: pass
            if "eur_conversion_rate" in request.POST:
                try: cms.eur_conversion_rate = float(request.POST.get("eur_conversion_rate"))
                except: pass
            if "gbp_conversion_rate" in request.POST:
                try: cms.gbp_conversion_rate = float(request.POST.get("gbp_conversion_rate"))
                except: pass
            if "aed_conversion_rate" in request.POST:
                try: cms.aed_conversion_rate = float(request.POST.get("aed_conversion_rate"))
                except: pass

            # Section 4 - Fit & Craft
            if "fit_section_badge" in request.POST:
                cms.fit_section_badge = request.POST.get("fit_section_badge")
            if "fit_card1_title" in request.POST:
                cms.fit_card1_title = request.POST.get("fit_card1_title")
            if "fit_card1_desc" in request.POST:
                cms.fit_card1_desc = request.POST.get("fit_card1_desc")
            if "fit_card2_title" in request.POST:
                cms.fit_card2_title = request.POST.get("fit_card2_title")
            if "fit_card2_desc" in request.POST:
                cms.fit_card2_desc = request.POST.get("fit_card2_desc")
            if "fit_section_bg_color" in request.POST:
                cms.fit_section_bg_color = request.POST.get("fit_section_bg_color")
            if "fit_section_bg_image" in request.FILES:
                cms.fit_section_bg_image = request.FILES["fit_section_bg_image"]
            if "fit_hero_image" in request.FILES:
                cms.fit_hero_image = request.FILES["fit_hero_image"]
            if "fit_img1" in request.FILES:
                cms.fit_img1 = request.FILES["fit_img1"]
            if "fit_img2" in request.FILES:
                cms.fit_img2 = request.FILES["fit_img2"]
            if "fit_img3" in request.FILES:
                cms.fit_img3 = request.FILES["fit_img3"]
            if "fit_img5" in request.FILES:
                cms.fit_img5 = request.FILES["fit_img5"]
            if "fit_img6" in request.FILES:
                cms.fit_img6 = request.FILES["fit_img6"]

            # Section 5 - 2x2 Quad Grid
            if "grid_tile1_link" in request.POST:
                cms.grid_tile1_link = request.POST.get("grid_tile1_link")
            if "grid_tile2_link" in request.POST:
                cms.grid_tile2_link = request.POST.get("grid_tile2_link")
            if "grid_tile3_link" in request.POST:
                cms.grid_tile3_link = request.POST.get("grid_tile3_link")
            if "grid_tile4_link" in request.POST:
                cms.grid_tile4_link = request.POST.get("grid_tile4_link")
            if "grid_center_button_text" in request.POST:
                cms.grid_center_button_text = request.POST.get("grid_center_button_text")
            if "grid_center_button_link" in request.POST:
                cms.grid_center_button_link = request.POST.get("grid_center_button_link")
            if "grid_center_button_bg" in request.POST:
                cms.grid_center_button_bg = request.POST.get("grid_center_button_bg")
            if "grid_center_button_color" in request.POST:
                cms.grid_center_button_color = request.POST.get("grid_center_button_color")

            if "grid_tile1_image" in request.FILES:
                cms.grid_tile1_image = request.FILES["grid_tile1_image"]
            if "grid_tile2_image" in request.FILES:
                cms.grid_tile2_image = request.FILES["grid_tile2_image"]
            if "grid_tile3_image" in request.FILES:
                cms.grid_tile3_image = request.FILES["grid_tile3_image"]
            if "grid_tile4_image" in request.FILES:
                cms.grid_tile4_image = request.FILES["grid_tile4_image"]

            # Footer & Social
            if "footer_tagline" in request.POST:
                cms.footer_tagline = request.POST.get("footer_tagline")
            if "footer_facebook_url" in request.POST:
                cms.footer_facebook_url = request.POST.get("footer_facebook_url")
            if "footer_instagram_url" in request.POST:
                cms.footer_instagram_url = request.POST.get("footer_instagram_url")
            if "footer_linkedin_url" in request.POST:
                cms.footer_linkedin_url = request.POST.get("footer_linkedin_url")
            if "footer_youtube_url" in request.POST:
                cms.footer_youtube_url = request.POST.get("footer_youtube_url")
            if "footer_twitter_url" in request.POST:
                cms.footer_twitter_url = request.POST.get("footer_twitter_url")
            if "footer_copyright" in request.POST:
                cms.footer_copyright = request.POST.get("footer_copyright")
            if "footer_bg_color" in request.POST:
                cms.footer_bg_color = request.POST.get("footer_bg_color")
            if "footer_logo" in request.FILES:
                cms.footer_logo = request.FILES["footer_logo"]

            # Navigation Builder & Mega Menu Cards JSON Data
            if "header_nav_json" in request.POST:
                try:
                    cms.header_nav_json = json.loads(request.POST.get("header_nav_json"))
                except:
                    pass
            if "mobile_nav_json" in request.POST:
                try:
                    cms.mobile_nav_json = json.loads(request.POST.get("mobile_nav_json"))
                except:
                    pass
            if "mega_menu_cards_json" in request.POST:
                try:
                    cms.mega_menu_cards_json = json.loads(request.POST.get("mega_menu_cards_json"))
                except:
                    pass
            if "mega_menu_featured_links_json" in request.POST:
                try:
                    cms.mega_menu_featured_links_json = json.loads(request.POST.get("mega_menu_featured_links_json"))
                except:
                    pass
            if "footer_nav_json" in request.POST:
                try:
                    cms.footer_nav_json = json.loads(request.POST.get("footer_nav_json"))
                except:
                    pass

            cms.save()
            return JsonResponse({"res": "Homepage CMS Editor updated successfully!"})

        # ================= ONBOARD NEW MERCHANT =================
        if request.POST.get("onboard_merchant"):
            b_name = request.POST.get("business_name")
            vpa = request.POST.get("merchant_vpa")
            d_limit = request.POST.get("daily_amount_limit", 100000)
            if b_name and vpa:
                new_m = Merchant.objects.create(
                    business_name=b_name,
                    merchant_vpa=vpa,
                    daily_amount_limit=float(d_limit or 100000),
                    status='ACTIVE'
                )
                APIKey.generate_key_pair(new_m, mode='TEST')
                APIKey.generate_key_pair(new_m, mode='LIVE')
                messages.success(request, f"Merchant '{b_name}' onboarded successfully!")
                return redirect("/usvesta-deshboard/#paymentgateway-section")

        # ================= TOGGLE MERCHANT STATUS =================
        if request.POST.get("toggle_merchant_status"):
            m_id = request.POST.get("merchant_id")
            m = Merchant.objects.filter(id=m_id).first()
            if m:
                m.status = 'DISABLED' if m.status == 'ACTIVE' else 'ACTIVE'
                m.save()
                messages.success(request, f"Merchant status changed to {m.status}")
                return redirect("/usvesta-deshboard/#paymentgateway-section")

        # ================= DELETE MERCHANT =================
        if request.POST.get("delete_merchant"):
            m_id = request.POST.get("merchant_id")
            Merchant.objects.filter(id=m_id).delete()
            messages.success(request, "Merchant deleted successfully")
            return redirect("/usvesta-deshboard/#paymentgateway-section")
        # ================= TOGGLE REVIEW VISIBILITY =================
        toggle_review_id = request.POST.get("toggle_review_id")
        if toggle_review_id:
            review = User_Reviews.objects.filter(id=toggle_review_id).first()
            if review:
                review.show = not review.show
                review.save()
                return JsonResponse({"res": "Review status updated successfully", "show": review.show})
            return JsonResponse({"error": "Review not found"}, status=404)

        # ================= API KEY OPERATIONS =================
        create_api_key = request.POST.get("create_api_key")
        delete_api_key_id = request.POST.get("delete_api_key")
        if create_api_key:
            name = request.POST.get("key_name", "My API Key")
            APIKey.objects.create(user=request.user, key_name=name)
            return JsonResponse({"res": "API Key Created Successfully"})
        if delete_api_key_id:
            APIKey.objects.filter(id=delete_api_key_id, user=request.user).delete()
            return JsonResponse({"res": "API Key Revoked Successfully"})

        # ================= BANNER OPERATIONS =================
        banner_action = request.POST.get("banner_action")
        if banner_action == "add":
            img = request.FILES.get("banner_image")
            img_phone = request.FILES.get("banner_image_phone")
            vid = request.FILES.get("banner_video")
            alt = request.POST.get("banner_alt", "")
            pages = request.POST.getlist("banner_pages")
            sub_cat_id = request.POST.get("banner_sub_cat")
            sub_cat = Product_sub_category.objects.filter(id=sub_cat_id).first() if sub_cat_id else None
            
            Banners.objects.create(
                image=img,
                image_phone=img_phone,
                video=vid,
                image_alt_name=alt,
                category_images_slider=sub_cat,
                show_on_pages=pages
            )
            return JsonResponse({"res": "Banner Added Successfully"})
        elif banner_action == "delete":
            banner_id = request.POST.get("banner_id")
            Banners.objects.filter(id=banner_id).delete()
            return JsonResponse({"res": "Banner Deleted Successfully"})

        # ================= TESTIMONIAL OPERATIONS =================
        testimonial_action = request.POST.get("testimonial_action")
        if testimonial_action == "add":
            img = request.FILES.get("testimonial_image")
            alt = request.POST.get("testimonial_alt", "")
            name = request.POST.get("testimonial_name", "")
            company = request.POST.get("testimonial_company", "")
            content = request.POST.get("testimonial_content", "")
            Testimoninal.objects.create(
                image=img,
                image_alt_name=alt,
                name=name,
                company_name=company,
                content=content
            )
            return JsonResponse({"res": "Testimonial Added Successfully"})
        elif testimonial_action == "delete":
            test_id = request.POST.get("testimonial_id")
            Testimoninal.objects.filter(id=test_id).delete()
            return JsonResponse({"res": "Testimonial Deleted Successfully"})

        # ================= TRUSTED CLIENT OPERATIONS =================
        client_action = request.POST.get("client_action")
        if client_action == "add":
            img = request.FILES.get("client_image")
            alt = request.POST.get("client_alt", "")
            Our_trusted_client.objects.create(image=img, image_alt_name=alt)
            return JsonResponse({"res": "Trusted Client Logo Added"})
        elif client_action == "delete":
            client_id = request.POST.get("client_id")
            Our_trusted_client.objects.filter(id=client_id).delete()
            return JsonResponse({"res": "Trusted Client Logo Deleted"})

        # ================= INSTAGRAM IMAGE OPERATIONS =================
        insta_action = request.POST.get("insta_action")
        if insta_action == "add":
            img = request.FILES.get("insta_image")
            Insta_images.objects.create(image=img)
            return JsonResponse({"res": "Instagram Image Added"})
        elif insta_action == "delete":
            insta_id = request.POST.get("insta_id")
            Insta_images.objects.filter(id=insta_id).delete()
            return JsonResponse({"res": "Instagram Image Deleted"})

        # ================= A+ LISTING OPERATIONS =================
        aplus_action = request.POST.get("aplus_action")
        if aplus_action == "add":
            img = request.FILES.get("aplus_image")
            alt = request.POST.get("aplus_alt", "")
            A_plus_listing.objects.create(image=img, image_alt_name=alt)
            return JsonResponse({"res": "A+ Listing Image Added"})
        elif aplus_action == "delete":
            aplus_id = request.POST.get("aplus_id")
            A_plus_listing.objects.filter(id=aplus_id).delete()
            return JsonResponse({"res": "A+ Listing Image Deleted"})

        # ================= BLOG CATEGORY OPERATIONS =================
        blog_cat_action = request.POST.get("blog_cat_action")
        if blog_cat_action == "add":
            name = request.POST.get("blog_category_name")
            Blog_Category.objects.create(category=name)
            return JsonResponse({"res": "Blog Category Created"})
        elif blog_cat_action == "delete":
            blog_cat_id = request.POST.get("blog_category_id")
            Blog_Category.objects.filter(id=blog_cat_id).delete()
            return JsonResponse({"res": "Blog Category Deleted"})

        # ================= BLOG POST OPERATIONS =================
        blog_post_action = request.POST.get("blog_post_action")
        if blog_post_action == "add":
            author = request.POST.get("blog_author", "")
            cat_id = request.POST.get("blog_category")
            cat = Blog_Category.objects.get(id=cat_id)
            img = request.FILES.get("blog_image")
            alt = request.POST.get("blog_alt", "")
            title = request.POST.get("blog_title", "")
            keyword = request.POST.get("blog_keyword", "")
            desc = request.POST.get("blog_desc", "")
            content = request.POST.get("blog_content", "")
            dt = request.POST.get("blog_date") or timezone.now()
            
            Blog_post.objects.create(
                author=author,
                category=cat,
                blog_image=img,
                image_alt_name=alt,
                meta_title=title,
                meta_keyword=keyword,
                meta_description=desc,
                blog_content=content,
                date=dt
            )
            return JsonResponse({"res": "Blog Post Published"})
        elif blog_post_action == "delete":
            blog_id = request.POST.get("blog_id")
            Blog_post.objects.filter(id=blog_id).delete()
            return JsonResponse({"res": "Blog Post Deleted"})

        # ================= CONTACT MESSAGE OPERATIONS =================
        contact_action = request.POST.get("contact_action")
        if contact_action == "delete":
            contact_id = request.POST.get("contact_id")
            Contact_US.objects.filter(id=contact_id).delete()
            return JsonResponse({"res": "Contact Message Deleted"})

        # ================= BULK DELETE OPERATIONS =================
        bulk_delete_products = request.POST.get("bulk_delete_products")
        if bulk_delete_products:
            ids = request.POST.getlist("product_ids[]")
            if ids:
                Product.objects.filter(id__in=ids).delete()
                Color_product.objects.filter(id__in=ids).delete()
                return JsonResponse({"res": f"{len(ids)} product(s) deleted successfully"})
            return JsonResponse({"res": "No products selected"}, status=400)

        bulk_delete_orders = request.POST.get("bulk_delete_orders")
        if bulk_delete_orders:
            ids = request.POST.getlist("order_ids[]")
            if ids:
                Order.objects.filter(id__in=ids).delete()
                return JsonResponse({"res": f"{len(ids)} order(s) deleted successfully"})
            return JsonResponse({"res": "No orders selected"}, status=400)

        delete_single_order = request.POST.get("delete_single_order")
        if delete_single_order:
            order_id = request.POST.get("order_id")
            if order_id:
                Order.objects.filter(id=order_id).delete()
                return JsonResponse({"res": "Order deleted successfully"})
            return JsonResponse({"res": "Order not found"}, status=400)

        # ================= ORIGINAL DASHBOARD OPERATIONS =================
        order_id=request.POST.get("o_id")
        order_status=request.POST.get("o_status")
        remove_category=request.POST.get("remove_category")
        edit_category=request.POST.get("editcategoryid")
        category_value=request.POST.get("editcategory")
        editcategory_image = request.FILES.get("editcategory_image")
        category_name = request.POST.get("category_name")
        category_image = request.FILES.get("category_image")
        remove_sub_category=request.POST.get("remove_sub_category")
        subeditcategoryid=request.POST.get("subeditcategoryid")
        subeditcategory_name=request.POST.get("subeditcategory")
        subeditcategory_image = request.FILES.get("subeditcategory_image")
        sub_category_name = request.POST.get("sub_category_name")
        sub_category_image = request.FILES.get("sub_category_image")
        del_product=request.POST.get("remove_product_from_crm")
        iner_product_delte=request.POST.get("inner_remove_product_from_crm")
         
        if sub_category_name and sub_category_image:
            Product_sub_category(category_image=sub_category_image,name=sub_category_name).save()
            return JsonResponse({"res":"Category Added Successfully"})
        if subeditcategoryid:
            a=Product_sub_category.objects.filter(id=subeditcategoryid).first()
            if subeditcategory_image:
                a.category_image=subeditcategory_image
            a.name=subeditcategory_name
            a.save()
        if remove_sub_category:
            c=Product_sub_category.objects.filter(id=remove_sub_category).first()
            c.delete()

        if category_name and category_image:
            Product_category(category_image=category_image,name=category_name).save()
            return JsonResponse({"res":"Category Added Successfully"})

        if order_id and order_status:
            order=Order.objects.filter(id=order_id).first()
            order.status=order_status
            order.save()
            return redirect("/usvesta-deshboard")
        if remove_category:
            c=Product_category.objects.filter(id=remove_category).first()
            c.delete()
            return JsonResponse({"res":"Category Remove Successfully"})

        if edit_category:
            a=Product_category.objects.filter(id=edit_category).first()
            if editcategory_image:
                a.category_image=editcategory_image
            a.name=category_value
            a.save()
            return JsonResponse({"res":"Category Update Successfully"})
        
        if del_product:
            p=Product.objects.filter(id=del_product).first()
            if p:
                p.delete()
                return JsonResponse({"res":"Product Remove Successfully"})
            
        elif iner_product_delte:
            p=Color_product.objects.filter(id=iner_product_delte).first()
            if p:
                p.delete()
                return JsonResponse({"res":"Product Remove Successfully"})

        # #################33end
        try:
            # ---------- BASIC PRODUCT INFO ----------
            product_name = request.POST.get("name")
            sub_category_id = request.POST.get("category")
            product_description = request.POST.get("description")
            highlight = request.POST.get("highlight")

            # Strip any Froala Editor attribution/watermark
            def _clean_froala(txt):
                if not txt:
                    return txt
                import re
                pats = [
                    re.compile(r'<p[^>]*data-f-id=["\']pbf["\'][^>]*>[\s\S]*?</p>', re.IGNORECASE),
                    re.compile(r'<p[^>]*>[\s\S]*?Powered by\s*<a[^>]*froala\.com[^>]*>[\s\S]*?</a>[\s\S]*?</p>', re.IGNORECASE),
                    re.compile(r'Powered by\s*<a[^>]*froala\.com[^>]*>[\s\S]*?</a>', re.IGNORECASE),
                    re.compile(r'<a[^>]*froala\.com[^>]*>[\s\S]*?</a>', re.IGNORECASE),
                ]
                for p in pats:
                    txt = p.sub('', txt)
                return txt.strip()

            product_description = _clean_froala(product_description)
            highlight = _clean_froala(highlight)

            brand = request.POST.get("brand")
            top_eight_product = request.POST.get("show_at_home")
            ratings = request.POST.get("ratings")
            total_sale_product = request.POST.get("total_sale_product")
            key_words = request.POST.get("keywords")
            product_status = request.POST.get("is_active")
            b2c_price = request.POST.get("sale_price")
            discount_price = request.POST.get("regular_price")
            t_shirt_type = request.POST.get("tshirt_type")
            color = request.POST.get("color")
            color_code = request.POST.get("color_code")
            product_image = request.FILES.get("main_image")
            sizes_json = request.POST.get("sizes")
            product_quantity_offer = request.POST.get("product_quantity_offer")
            product_amount_offer = request.POST.get("product_amount_offer")
            
            
            

            # ✅ Convert "true"/"false" strings to Python booleans
            def to_bool(val):
                return True if val == "true" else False

            top_eight_product = to_bool(top_eight_product)
            product_status = to_bool(product_status)
            p_status = None
            if product_status:
                p_status = "Publish"
            else:
                p_status = "Draft"

            # ---------- CREATE MAIN PRODUCT ----------
            subcategory = None
            if sub_category_id and str(sub_category_id).strip() not in ('None', 'null', ''):
                try:
                    subcategory = Product_sub_category.objects.filter(id=int(str(sub_category_id).strip())).first()
                except (ValueError, TypeError):
                    subcategory = None
            if not subcategory:
                subcategory = Product_sub_category.objects.first()
            category = subcategory.category if subcategory else None

            p_qty_offer = None
            if product_quantity_offer and str(product_quantity_offer).strip() not in ('None', 'null', ''):
                try:
                    p_qty_offer = int(str(product_quantity_offer).strip())
                except (ValueError, TypeError):
                    p_qty_offer = None

            p_amt_offer = None
            if product_amount_offer and str(product_amount_offer).strip() not in ('None', 'null', ''):
                try:
                    p_amt_offer = float(str(product_amount_offer).strip())
                except (ValueError, TypeError):
                    p_amt_offer = None

            b2c_price_clean = 0.0
            if b2c_price and str(b2c_price).strip() not in ('None', 'null', ''):
                try:
                    b2c_price_clean = float(str(b2c_price).strip())
                except (ValueError, TypeError):
                    b2c_price_clean = 0.0

            discount_price_clean = str(discount_price).strip() if discount_price and str(discount_price).strip() not in ('None', 'null', '') else "0"
            ratings_clean = str(ratings).strip() if ratings and str(ratings).strip() not in ('None', 'null', '') else "0"
            total_sale_clean = str(total_sale_product).strip() if total_sale_product and str(total_sale_product).strip() not in ('None', 'null', '') else "0"

            product = Product.objects.create(
                user=request.user,
                category=category,
                sub_category=subcategory,
                product_name=product_name,
                brand=brand or "US Vesta",
                top_eight_products=top_eight_product,
                total_sale_products=total_sale_clean,
                ratings=ratings_clean,
                product_description=product_description,
                key_words=key_words or "",
                b2c_price=b2c_price_clean,
                discount_price=discount_price_clean,
                product_status=p_status,
                t_shirt_type=t_shirt_type or "",
                color=color or "",
                color_code=color_code or "",
                product_quantity_offer=p_qty_offer,
                product_amount_offer=p_amt_offer,
                product_image=product_image,
                product_image_alt=request.POST.get("image_alt", product_name) or product_name,
            )

            if highlight:
                Hightlight_for_product.objects.create(product=product, highlight=highlight)

            # ---------- GALLERY IMAGES ----------
            gallery_images = request.FILES.getlist("gallery_images", [])
            for img in gallery_images:
                product_Gelery_images.objects.create(
                    product=product,
                    image=img,
                    alt=f"{product_name} gallery"
                )

            # ---------- SIZES ----------
            if sizes_json and str(sizes_json).strip() not in ('None', 'null', ''):
                try:
                    sizes = json.loads(sizes_json)
                    if isinstance(sizes, list):
                        for sz in sizes:
                            sz_str = str(sz).strip().upper()
                            if sz_str and sz_str not in ['1', '0', 'ON', 'TRUE', 'FALSE'] and not sz_str.isdigit():
                                Size_price_par_post.objects.get_or_create(
                                    product=product,
                                    size=sz_str
                                )
                except Exception as e:
                    print("Error parsing sizes:", e)

            # ---------- COLOR VARIANTS ----------
            color_variants_json = request.POST.get("color_variants")

            if color_variants_json and str(color_variants_json).strip() not in ('None', 'null', ''):
                try:
                    color_variants = json.loads(color_variants_json)
                    if isinstance(color_variants, list):
                        for cvar in color_variants:
                            color_name = cvar.get("color_name") or ""
                            color_code = cvar.get("color_code") or ""
                            color_alt = cvar.get("image_alt") or color_name
                            variant_index = cvar.get("variant_index")

                            try:
                                gallery_count = int(cvar.get("gallery_count", 0) or 0)
                            except (ValueError, TypeError):
                                gallery_count = 0

                            # Get variant main image
                            variant_image_key = f"variant_image_{variant_index}"
                            color_image = request.FILES.get(variant_image_key)

                            print(f"Processing color variant: {color_name}, Index: {variant_index}")
                            print(f"Variant image: {color_image}")
                            print(f"Gallery count: {gallery_count}")

                            # Create Color_product
                            color_obj = Color_product.objects.create(
                                product=product,
                                color=color_name,
                                color_code=color_code,
                                color_images=color_image,
                            )

                            # Create color_product_Gelery_images
                            inner_product = color_product_Gelery_images.objects.create(
                                color_product=color_obj,
                                image=color_image,
                                alt=color_alt
                            )

                            # Process gallery images for this variant
                            for i in range(gallery_count):
                                gallery_key = f"variant_gallery_{variant_index}_{i}"
                                gallery_image = request.FILES.get(gallery_key)
                                if gallery_image:
                                    color_product_Gelery_images.objects.create(
                                        color_product=color_obj,
                                        image=gallery_image,
                                        alt=color_alt,
                                    )
                                    print(f"Added gallery image: {gallery_key}")
                except Exception as e:
                    print("Error parsing color variants:", e)

            # ---------- SUCCESS RESPONSE ----------
            return JsonResponse({
                "status": "success",
                "message": "Product created successfully",
                "product_id": product.id
            })

        except Exception as e:
            print("Error while saving product:", e)
            import traceback
            print("Traceback:", traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)})


class Update_product(View):
    def get(self, request, slug):
        product_type = request.GET.get("product-type")
        category = Product_sub_category.objects.all()
        all_sizes = ['S', 'M', 'L', 'XL', 'XXL']
        target_p = None
        if product_type == "product":
            product = Product.objects.filter(uuid_product=slug).first()
            target_p = product
            color_product = Color_product.objects.filter(product=product)
            product_gellery_image = product_Gelery_images.objects.filter(product=product)
            products_size = Size_price_par_post.objects.filter(product=product)
            available_sizes = [ps.size for ps in products_size]

        elif product_type == "inner-product":
            product = Color_product.objects.filter(uuid_product=slug).first()
            if product:
                target_p = product.product
                color_product = Color_product.objects.filter(product=product.product)
                product_gellery_image = product_Gelery_images.objects.filter(product=product.product)
                
                products_size = Size_price_par_post.objects.filter(product=product.product)
                available_sizes = [ps.size for ps in products_size]
            else:
                available_sizes = []
                products_size = []
                color_product = []
                product_gellery_image = []
        
        highlight_obj = Hightlight_for_product.objects.filter(product=target_p).first() if target_p else None
        highlight_val = highlight_obj.highlight if highlight_obj else ""

        data = {
            "subcategory": category,
            "a": product,
            "slug": slug,
            "color_product":color_product,
            "products_size": products_size,
            "product_gellery_image": product_gellery_image,
            "available_sizes": available_sizes,
            "all_sizes": all_sizes,
            "product_type": product_type,
            "highlight_val": highlight_val,
        }
        return render(request, "dashboard/update_product.html",data)
    
    def post(self, request, slug):
        try:
            # ---------- BASIC PRODUCT INFO ----------
            product_name = request.POST.get("name")
            subcategory_id = request.POST.get("category")
            product_description = request.POST.get("description")
            highlight = request.POST.get("highlight")

            # Strip any Froala Editor attribution/watermark
            def _clean_froala(txt):
                if not txt:
                    return txt
                import re
                pats = [
                    re.compile(r'<p[^>]*data-f-id=["\']pbf["\'][^>]*>[\s\S]*?</p>', re.IGNORECASE),
                    re.compile(r'<p[^>]*>[\s\S]*?Powered by\s*<a[^>]*froala\.com[^>]*>[\s\S]*?</a>[\s\S]*?</p>', re.IGNORECASE),
                    re.compile(r'Powered by\s*<a[^>]*froala\.com[^>]*>[\s\S]*?</a>', re.IGNORECASE),
                    re.compile(r'<a[^>]*froala\.com[^>]*>[\s\S]*?</a>', re.IGNORECASE),
                ]
                for p in pats:
                    txt = p.sub('', txt)
                return txt.strip()

            product_description = _clean_froala(product_description)
            highlight = _clean_froala(highlight)

            brand = request.POST.get("brand")
            top_eight_product = request.POST.get("show_at_home")
            ratings = request.POST.get("ratings")
            total_sale_product = request.POST.get("total_sale_product")
            key_words = request.POST.get("keywords")
            product_status = request.POST.get("is_active")
            b2c_price = request.POST.get("sale_price")
            discount_price = request.POST.get("regular_price")
            t_shirt_type = request.POST.get("tshirt_type")
            color = request.POST.get("color")
            color_code = request.POST.get("color_code")
            product_amount_offer = request.POST.get("product_amount_offer")
            product_quantity_offer = request.POST.get("product_quantity_offer")
            product_image = request.FILES.get("main_image")
            sizes_json = request.POST.get("sizes")
            product_type = request.POST.get("product_type")
            main_product_id_for_color_variant_id = request.POST.get("main_product_id_for_color_variant_id")
            product_image_name=request.POST.get("image_alt")
            
            
            # ✅ Convert to boolean
            def to_bool(val):
                if isinstance(val, str):
                    return val.lower() == "true"
                return bool(val)

            top_eight_product = to_bool(top_eight_product)
            product_status = to_bool(product_status)
            p_status = "Publish" if product_status else "Draft"

            # ---------- UPDATE MAIN PRODUCT ----------
            if product_type == "product":
                
                subcat = None
                if subcategory_id and str(subcategory_id).strip() not in ('None', 'null', ''):
                    try:
                        subcat = Product_sub_category.objects.filter(id=int(str(subcategory_id).strip())).first()
                    except (ValueError, TypeError):
                        subcat = None

                product = Product.objects.filter(uuid_product=slug).first()

                if not product:
                    return JsonResponse({"status": "error", "message": "Product not found"})

                product.user = request.user
                product.sub_category = subcat
                if subcat and subcat.category:
                    product.category = subcat.category
                product.product_name = product_name
                product.brand = brand
                product.top_eight_products = top_eight_product
                product.total_sale_products = total_sale_product
                product.ratings = ratings
                product.product_description = product_description
                product.key_words = key_words
                product.b2c_price = b2c_price
                product.discount_price = discount_price
                product.product_status = p_status
                product.t_shirt_type = t_shirt_type
                product.color = color
                product.color_code = color_code
                
                if product_amount_offer and product_amount_offer.strip() != "":
                    try:
                        product.product_amount_offer = float(product_amount_offer)
                    except Exception:
                        product.product_amount_offer = None
                else:
                    product.product_amount_offer = None

                if product_quantity_offer and product_quantity_offer.strip() != "":
                    try:
                        product.product_quantity_offer = int(product_quantity_offer)
                    except Exception:
                        product.product_quantity_offer = None
                else:
                    product.product_quantity_offer = None
                
                if product_image:
                    product.product_image = product_image
                
                if highlight:
                    Hightlight_for_product.objects.filter(product=product).delete()
                    Hightlight_for_product.objects.create(product=product, highlight=highlight)
                
                product.product_image_alt = product_image_name if product_image_name else product_name 
                product.save()

                # ---------- UPDATE GALLERY IMAGES ----------
               
                Size_price_par_post.objects.filter(product=product).delete()
                        
                if isinstance(sizes_json, str):
                    try:
                        sizes_list = json.loads(sizes_json)
                    except json.JSONDecodeError:
                        sizes_list = []
                else:
                    sizes_list = sizes_json  # already a list

                for sz in sizes_list:
                    sz_str = str(sz).strip().upper()
                    if sz_str and sz_str not in ['1', '0', 'ON', 'TRUE', 'FALSE'] and not sz_str.isdigit():
                        Size_price_par_post.objects.get_or_create(product=product, size=sz_str)

                gallery_images = request.FILES.getlist("gallery_images")
                if gallery_images:
                    # Delete existing gallery images
                    product_Gelery_images.objects.filter(product=product).delete()
                    
                    # Create new gallery images
                    for img in gallery_images:
                        product_Gelery_images.objects.create(
                            product=product,
                            image=img,
                            alt=f"{product_name} gallery"
                        )

                # ---------- UPDATE SIZES ----------
              


                # ---------- UPDATE EXISTING AND NEW COLOR VARIANTS ----------
                color_variants_json = request.POST.get("color_variants", "[]")
                try:
                    color_variants = json.loads(color_variants_json)
                    
                    for cvar in color_variants:
                        color_name = cvar.get("color_name")
                        color_code = cvar.get("color_code")
                        color_alt = cvar.get("image_alt", f"{color_name} variant")
                        variant_index = cvar.get("variant_index")
                        gallery_count = cvar.get("gallery_count", 0)
                        is_new = cvar.get("is_new", True)
                        existing_id = cvar.get("existing_id")

                        if not color_name:
                            continue

                        # Get variant main image
                        variant_image_key = f"variant_image_{variant_index}"
                        color_image = request.FILES.get(variant_image_key)

                        if not is_new and existing_id:
                            # Update existing color product
                            try:
                                color_obj = Color_product.objects.get(id=existing_id, product=product)
                                color_obj.color = color_name
                                color_obj.color_code = color_code
                                if color_image:
                                    color_obj.color_images = color_image
                                color_obj.save()
                                
                                # Get or create inner product
                                inner_product, created = color_product_Gelery_images.objects.get_or_create(
                                    color_product=color_obj,
                                    defaults={
                                        'image': color_image,
                                        'alt': color_alt
                                    }
                                )
                                if not created:
                                    inner_product.alt = color_alt
                                    if color_image:
                                        inner_product.image = color_image
                                    inner_product.save()
                                    
                            except Color_product.DoesNotExist:
                                # Create new if existing not found
                                color_obj = Color_product.objects.create(
                                    product=product,
                                    color=color_name,
                                    color_code=color_code,
                                    color_images=color_image
                                )
                                inner_product = color_product_Gelery_images.objects.create(
                                    color_product=color_obj,
                                    image=color_image,
                                    alt=color_alt
                                )
                        else:
                            # Create new color product
                            color_obj = Color_product.objects.create(
                                product=product,
                                color=color_name,
                                color_code=color_code,
                                color_images=color_image
                            )
                        # Process gallery images for this variant
                        if gallery_count > 0:
                            # For existing variants, we don't delete old images, we add new ones
                            # For new variants, we just add the new images
                            for i in range(gallery_count):
                                gallery_key = f"variant_gallery_{variant_index}_{i}"
                                gallery_image = request.FILES.get(gallery_key)
                                if gallery_image:
                                    color_product_Gelery_images.objects.create(
                                        color_product=color_obj,
                                        image=gallery_image,   # ✅ Correct variable
                                        alt=color_alt
                                    )


                except json.JSONDecodeError:
                    print("Invalid color variants JSON")

                return JsonResponse({
                    "status": "success",
                    "message": "Product updated successfully",
                    "product_id": product.id
                })

            elif product_type == "inner-product":
                # Handle inner product update
                sbcategory = None
                if subcategory_id and str(subcategory_id).strip() not in ('None', 'null', ''):
                    try:
                        sbcategory = Product_sub_category.objects.filter(id=int(str(subcategory_id).strip())).first()
                    except (ValueError, TypeError):
                        sbcategory = None

                inner_product = Color_product.objects.filter(uuid_product=slug).first()
                if not inner_product:
                    return JsonResponse({"status": "error", "message": "Inner product not found"})

                # Get the main product from inner product
                main_product = inner_product.product

                # Update main product
                main_product.user = request.user
                main_product.sub_category = sbcategory
                main_product.product_name = product_name
                main_product.brand = brand
                main_product.top_eight_products = top_eight_product
                main_product.total_sale_products = total_sale_product
                main_product.ratings = ratings
                main_product.product_description = product_description
                main_product.key_words = key_words
                main_product.b2c_price = b2c_price
                main_product.discount_price = discount_price
                main_product.product_status = p_status
                main_product.t_shirt_type = t_shirt_type
                main_product.color = color
                main_product.color_code = color_code
                
                if product_amount_offer and product_amount_offer.strip() != "":
                    try:
                        main_product.product_amount_offer = float(product_amount_offer)
                    except Exception:
                        main_product.product_amount_offer = None
                else:
                    main_product.product_amount_offer = None

                if product_quantity_offer and product_quantity_offer.strip() != "":
                    try:
                        main_product.product_quantity_offer = int(product_quantity_offer)
                    except Exception:
                        main_product.product_quantity_offer = None
                else:
                    main_product.product_quantity_offer = None
                
                if product_image:
                    main_product.product_image = product_image
                
                if highlight:
                    Hightlight_for_product.objects.filter(product=main_product).delete()
                    Hightlight_for_product.objects.create(product=main_product, highlight=highlight)
                
                main_product.product_image_alt = request.POST.get("image_alt", product_name)
                main_product.save()
                
                
                Size_price_par_post.objects.filter(product=main_product).delete()
                        
                if isinstance(sizes_json, str):
                    try:
                        sizes_list = json.loads(sizes_json)
                    except json.JSONDecodeError:
                        sizes_list = []
                else:
                    sizes_list = sizes_json  # already a list

                for sz in sizes_list:
                    sz_str = str(sz).strip().upper()
                    if sz_str and sz_str not in ['1', '0', 'ON', 'TRUE', 'FALSE'] and not sz_str.isdigit():
                        Size_price_par_post.objects.get_or_create(product=main_product, size=sz_str)

                # Update gallery images for main product
                gallery_images = request.FILES.getlist("gallery_images")
                if gallery_images:
                    product_Gelery_images.objects.filter(product=main_product).delete()
                    for img in gallery_images:
                        product_Gelery_images.objects.create(
                            product=main_product,
                            image=img,
                            alt=f"{product_name} gallery"
                        )

            
            
                 # ---------- UPDATE EXISTING AND NEW COLOR VARIANTS ----------
                color_variants_json = request.POST.get("color_variants", "[]")
                try:
                    color_variants = json.loads(color_variants_json)
                    
                    for cvar in color_variants:
                        color_name = cvar.get("color_name")
                        color_code = cvar.get("color_code")
                        color_alt = cvar.get("image_alt", f"{color_name} variant")
                        variant_index = cvar.get("variant_index")
                        gallery_count = cvar.get("gallery_count", 0)
                        is_new = cvar.get("is_new", True)
                        existing_id = cvar.get("existing_id")

                        if not color_name:
                            continue

                        # Get variant main image
                        variant_image_key = f"variant_image_{variant_index}"
                        color_image = request.FILES.get(variant_image_key)

                        if not is_new and existing_id:
                            # Update existing color product
                            try:
                                color_obj = Color_product.objects.get(id=existing_id, product=main_product)
                                color_obj.color = color_name
                                color_obj.color_code = color_code
                                if color_image:
                                    color_obj.color_images = color_image
                                color_obj.save()
                                
                                # Get or create inner product
                                inner_product, created = color_product_Gelery_images.objects.get_or_create(
                                    color_product=color_obj,
                                    defaults={
                                        'image': color_image,
                                        'alt': color_alt
                                    }
                                )
                                if not created:
                                    inner_product.alt = color_alt
                                    if color_image:
                                        inner_product.image = color_image
                                    inner_product.save()
                                    
                            except Color_product.DoesNotExist:
                                # Create new if existing not found
                                color_obj = Color_product.objects.create(
                                    product=main_product,
                                    color=color_name,
                                    color_code=color_code,
                                    color_images=color_image
                                )
                                inner_product = color_product_Gelery_images.objects.create(
                                    color_product=color_obj,
                                    image=color_image,
                                    alt=color_alt
                                )
                        else:
                            # Create new color product
                            color_obj = Color_product.objects.create(
                                product=main_product,
                                color=color_name,
                                color_code=color_code,
                                color_images=color_image
                            )
                        # Process gallery images for this variant
                        if gallery_count > 0:
                            # For existing variants, we don't delete old images, we add new ones
                            # For new variants, we just add the new images
                            for i in range(gallery_count):
                                gallery_key = f"variant_gallery_{variant_index}_{i}"
                                gallery_image = request.FILES.get(gallery_key)
                                if gallery_image:
                                    color_product_Gelery_images.objects.create(
                                        color_product=color_obj,
                                        image=gallery_image,   # ✅ Correct variable
                                        alt=color_alt
                                    )


                except json.JSONDecodeError:
                    print("Invalid color variants JSON")

                return JsonResponse({
                    "status": "success",
                    "message": "Product updated successfully",
                    "product_id": main_product.id
                })


        except Exception as e:
            print("Error while updating product:", e)
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)})     
        


class update_dashboard_form_etc_data(View):
    def post(self, request):
        # ################## reviews 

        reviews_name = request.POST.get("review_name")
        reviews_email = request.POST.get("review_email")
        reviews_message = request.POST.get("reviews_meseje")
        reviews_showhide = request.POST.get("reviews_showhide") 
        reviews_rating = request.POST.get("rating")  # <-- comes directly from form
        product_id_for_Rewive = request.POST.get("product_id_for_Rewive")  # <-- comes directly from form


        update_review_name = request.POST.get("update_review_name")
        update_review_id = request.POST.get("update_review_id")
        update_review_email = request.POST.get("update_review_email")
        update_reviews_showhide = request.POST.get("update_reviews_showhide") == "on"
        update_reviews_rating = request.POST.get("update_reviews_rating")  # <-- comes directly from form
        update_reviews_meseje = request.POST.get("update_reviews_meseje")  # <-- comes directly from form

        review_delete_id = request.POST.get("review_delete_id")  # <-- comes directly from form
        
        # men's t shirt codinator 
        previous_url = request.META.get('HTTP_REFERER', '/')

        coordinator_sub_category = request.POST.get("coordinator_sub_category")
        codinator_name = request.POST.get("coordinator_name")
        coordinator_sub_category_update = request.POST.get("coordinator_sub_category_update")

        codinator_containt = request.POST.get("coordinator_content")
        show_pages = request.POST.getlist("show_on_pages")
        coordinator_name_update = request.POST.get("coordinator_name_update")
        coordinator_update_id = request.POST.get("coordinator_update_id")
        coordinator_content_update = request.POST.get("coordinator_content_update")
        coordinator_delete_id = request.POST.get("coordinator_delete_id")
        show_pages_update = request.POST.getlist("show_on_pages_update")
        
        if codinator_name and codinator_containt and coordinator_sub_category:
            sub_c=Product_sub_category.objects.filter(id=coordinator_sub_category).first()

            sub_category_coordinator(name=codinator_name,sub_category=sub_c,containt=codinator_containt,show_on_pages=",".join(show_pages)).save()
            messages.success(request, "Coordinator Added Successfully!")
            return redirect(previous_url)
        elif coordinator_update_id:
            sub_c = Product_sub_category.objects.filter(id=coordinator_sub_category_update).first() if coordinator_sub_category_update else None
            update = sub_category_coordinator.objects.filter(id=coordinator_update_id).first()
            if update:
                if coordinator_name_update: update.name = coordinator_name_update
                if coordinator_content_update: update.containt = coordinator_content_update
                if sub_c: update.sub_category = sub_c
                if show_pages_update is not None: update.show_on_pages = ",".join(show_pages_update)
                update.save()
            messages.success(request, "Coordinator Update Successfully!")
            return redirect(previous_url)
        elif coordinator_delete_id:
            sub_category_coordinator.objects.filter(id=coordinator_delete_id).first().delete()

            return JsonResponse({"res": "Coordinator Delete Successfully!"})
            
        # End  men's t shirt codinator 

        # #####################review 
        
        if update_review_name and update_review_id and update_review_email  and update_reviews_rating and update_reviews_meseje:
            reviews=User_Reviews.objects.filter(id=update_review_id).first()
            if reviews:
                reviews.name =update_review_name
                reviews.email =update_review_email
                reviews.msg =update_reviews_meseje
                reviews.show =True if update_reviews_showhide =="on" else False
                reviews.star=update_reviews_rating
                reviews.save()
                messages.success(request, "Review Update Successfully!")
                return redirect(previous_url)
        elif review_delete_id:
            
            User_Reviews.objects.filter(id=review_delete_id).first().delete()

            return JsonResponse({"res": "Review Delete Successfully!"})
                
        
        
        
        
        # if reviews_name and reviews_email and reviews_message and reviews_showhide and reviews_rating:
        #     User_Reviews(
        #         product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
        #         inner_product_rew = models.ForeignKey(Color_product, on_delete=models.CASCADE, blank=True, null=True)
        #         user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
        #         name = models.CharField(max_length=200)
        #         email = models.EmailField(max_length=254)
        #         msg = models.TextField()
        #         star = models.CharField(max_length=50)
        #         show = models.BooleanField(default=False)
        #         created_at = models.DateTimeField(auto_now_add=True)
        #     )
        




class color_django_verint(View):
    def post(self, request):
       
        main_product_id_for_color_variant_id = request.POST.get("main_product_id_for_color_variant_id")
        product_type = request.POST.get("product_type")

        color_names = request.POST.getlist("color_name[]")
        color_variant_ids = request.POST.getlist("color_variant_id[]")
        color_codes = request.POST.getlist("color_code[]")

        

        if product_type == "product":

            if not (main_product_id_for_color_variant_id and color_names and color_variant_ids):
                return JsonResponse({"status": "error", "res": "Missing data."})

            product = Product.objects.filter(id=main_product_id_for_color_variant_id).first()
            if not product:
                return JsonResponse({"status": "error", "res": "Product not found."})

            # 🟩 Loop through each color variant
            for index, variant_id in enumerate(color_variant_ids):
                color_obj = Color_product.objects.filter(id=variant_id).first()
                if not color_obj:
                    continue

                color_obj.product = product
                color_obj.color = color_names[index]
                color_obj.color_code = color_codes[index] if len(color_codes) > index else ""

                # 🟩 Handle color image per color index
                color_image_key = f"color_image_{index}"
                if color_image_key in request.FILES:
                    color_obj.color_images = request.FILES[color_image_key]

                color_obj.save()

                # 🟩 Handle gallery images for this color
                gallery_key = f"gallery_images_{index}[]"
                color_gallery_images = request.FILES.getlist(gallery_key)

                print(f"Gallery key for index {index}: {gallery_key}")
                print(f"Gallery images received: {color_gallery_images}")

                if color_gallery_images:
                    # Only delete + replace if new gallery images uploaded
                    color_product_Gelery_images.objects.filter(color_product=color_obj).delete()

                    for g_img in color_gallery_images:
                        color_product_Gelery_images.objects.create(
                            color_product=color_obj,
                            image=g_img,
                        )
            return JsonResponse({"status": "success", "res": "Color variants updated successfully!"})

        elif product_type == "inner-product":
            if not (main_product_id_for_color_variant_id and color_names and color_variant_ids):
                return JsonResponse({"status": "error", "res": "Missing data."})

            # ✅ Fixed spelling of "product"
            product = Color_product.objects.filter(product__id=main_product_id_for_color_variant_id).first()
            if not product:
                return JsonResponse({"status": "error", "res": "Product not found."})

            # 🟩 Loop through each color variant
            for index, variant_id in enumerate(color_variant_ids):
                color_obj = Color_product.objects.filter(id=variant_id).first()
                if not color_obj:
                    continue

                color_obj.product = product.product
                color_obj.color = color_names[index]
                color_obj.color_code = color_codes[index] if len(color_codes) > index else ""

                # 🟩 Handle color image per color index
                color_image_key = f"color_image_{index}"
                if color_image_key in request.FILES:
                    color_obj.color_images = request.FILES[color_image_key]

                color_obj.save()

                # 🟩 Handle gallery images for this color
                gallery_key = f"gallery_images_{index}[]"
                color_gallery_images = request.FILES.getlist(gallery_key)

                print(f"Gallery key for index {index}: {gallery_key}")
                print(f"Gallery images received: {color_gallery_images}")

                if color_gallery_images:
                    # Only delete + replace if new gallery images uploaded
                    color_product_Gelery_images.objects.filter(color_product=color_obj).delete()

                    for g_img in color_gallery_images:
                        color_product_Gelery_images.objects.create(
                            color_product=color_obj,
                            image=g_img,
                        )

            return JsonResponse({"status": "success", "res": "Color variants updated successfully!"})



class ordermodel_popup(View):
    def post(self, request):
        order_id = request.POST.get("order_id")
        if order_id:
            order = Order.objects.filter(id=order_id).first()
            if order:
                return render(request, "dashboard/order_popup.html", {"a": order})
        return HttpResponse("Invalid Order ID", status=400)
    
    
    
    




def get_drive_image(image_url):

    try:

        if not image_url:
            return None

        image_url = str(image_url).strip()

        match = re.search(r"/d/([^/]+)", image_url)

        if not match:
            return None

        file_id = match.group(1)

        url = f"https://drive.google.com/uc?export=download&id={file_id}"

        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            return None

        # return ContentFile(
        #     response.content,
        #     name=f"{file_id}.jpg"
        # )
        return ContentFile(
            response.content,
            name=f"{file_id}.jpg"
        ), file_id

    except Exception as e:

        print("Image download error:", e)

        return None


def process_bulk_products(file_path, user):

    try:

        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        # FIX 1: normalize headers
        headers = [
            str(c.value).strip().replace(" ", "_") if c.value else ""
            for c in sheet[1]
        ]
        gallery_cols = [
            h for h in headers if h.startswith("Product_Gallery_Image")
        ]

        color_gallery_cols = [
            h for h in headers if h.startswith("color_variant_gallery_image")
        ]

        highlight_cols = [
            h for h in headers if h.startswith("Highlight")
        ]

        created_products = {}   # store created products

        for row in sheet.iter_rows(min_row=2, values_only=True):

            data = dict(zip(headers, row))

            sku = data.get("Products_SKU")

            if not sku:
                continue

            sku = str(sku).strip()

            product_code = None
            size_from_sku = None

            if "-" in sku:

                parts = sku.split("-")

                product_code = parts[0].strip()

                size_from_sku = parts[1].strip() if len(parts) > 1 else None

            else:
                product_code = sku

            product_name = data.get("Products_Title")

            # GET OR CREATE PRODUCT
            if product_code not in created_products:

                existing_product = Product.objects.filter(
                    product_sku=product_code
                ).first()

                if existing_product:

                    current_product = existing_product

                else:

                    category_name = (data.get("category") or "").strip()

                    category = Product_category.objects.filter(
                        name__iexact=category_name
                    ).first()

                    sub_category_name = (data.get("sub_category") or "").strip()

                    sub_category = Product_sub_category.objects.filter(
                        name__iexact=sub_category_name
                    ).first()

                    
                    result0 = get_drive_image(data.get("Main_Products_Image"))

                    image_file = None
                    if result0:
                        image_file, _ = result0

                    current_product = Product.objects.create(

                        user=user,

                        product_sku=product_code,

                        category=category,

                        sub_category=sub_category,

                        brand=data.get("brand") or "US Vesta",

                        top_eight_products=str(
                            data.get("top_eight_products")
                        ).lower() in ["1", "true", "yes"],

                        ratings=data.get("ratings"),

                        total_sale_products=data.get(
                            "total_sale_products"
                        ),

                        product_name=product_name,

                        product_image=image_file,

                        product_image_alt=data.get(
                            "Products_Title"
                        ) or "",

                        key_words=data.get("SEO_Keywords") or "",

                        product_description=data.get(
                            "Products_Description"
                        ) or "",

                        discount_price=data.get(
                            "Regular_Price"
                        ) or 0,

                        b2b_price=data.get("b2b_price") or 0,

                        b2c_price=data.get("Sale_Price") or 0,

                        color=data.get("Product_Color") or "",

                        product_quantity_offer=data.get(
                            "product_quantity_offer"
                        ),

                        product_amount_offer=data.get(
                            "product_amount_offer"
                        ),

                        t_shirt_type=data.get("t_shirt_type"),

                        select_page=data.get("select_page"),

                        product_status=data.get(
                            "product_status"
                        ) or "Publish",
                    )

                    

                    # SAVE HIGHLIGHTS
                    for hcol in highlight_cols:

                        hvalue = data.get(hcol)

                        if hvalue:

                            Hightlight_for_product.objects.create(
                                product=current_product,
                                highlight=str(hvalue).strip()
                            )

                created_products[product_code] = current_product

            else:

                current_product = created_products[product_code]

            # PRODUCT GALLERY
           
            for col in gallery_cols:

                img_url = data.get(col)

                if img_url:

                    result = get_drive_image(img_url)

                    if result:

                        gimg, file_id = result

                        # ✅ duplicate रोकने के लिए
                        already_exists = product_Gelery_images.objects.filter(
                            product=current_product,
                            image__icontains=file_id
                        ).exists()

                        if not already_exists:

                            product_Gelery_images.objects.create(
                                product=current_product,
                                image=gimg,
                                alt=current_product.product_name
                            )
                            
                            
                
                

                
            # SIZE
            size = size_from_sku or data.get("Product_Size")

            if size:

                Size_price_par_post.objects.get_or_create(

                    product=current_product,

                    size=str(size).strip()
                )

            # COLOR VARIANT
            # COLOR VARIANT
            color = data.get("color_variant")

            if color:

                # ✅ STEP 1: color image get karo
                color_result = get_drive_image(data.get("color_variant_image"))

                color_image = None
                if color_result:
                    color_image, _ = color_result

                # ✅ STEP 2: color object create/get
                color_obj, _ = Color_product.objects.get_or_create(
                    product=current_product,
                    color=str(color).strip(),
                    defaults={
                        "color_images": color_image
                    }
                )

                # ✅ STEP 3: color gallery images handle
                for col in color_gallery_cols:

                    img_url = data.get(col)

                    if img_url:

                        result = get_drive_image(img_url)

                        if result:

                            gimg, file_id = result

                            # ✅ duplicate रोकने के लिए
                            already_exists = color_product_Gelery_images.objects.filter(
                                color_product=color_obj,
                                image__icontains=file_id
                            ).exists()

                            if not already_exists:

                                color_product_Gelery_images.objects.create(
                                    color_product=color_obj,
                                    image=gimg,
                                    alt=f"{current_product.product_name} - {color}"
                                )
            time.sleep(0.02)

    except Exception:

        print("Bulk Import Error")
        print(traceback.format_exc())      




class Upload_pd_in_bulk(View):

    def post(self, request):

        excel_file = request.FILES.get("xl_file_name_for_bluk_upload")

        if not excel_file:

            return JsonResponse({
                "status": "error",
                "message": "No Excel file found"
            })

        
        # folder create karo (media/bulk_uploads)
        upload_dir = os.path.join(settings.MEDIA_ROOT, "bulk_uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # file name clean karo
        file_name = excel_file.name.replace(" ", "_")

        # final path
        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, "wb+") as destination:

            for chunk in excel_file.chunks():
                destination.write(chunk)

        thread = threading.Thread(
            target=process_bulk_products,
            args=(file_path, request.user)
        )

        thread.start()

        return JsonResponse({

            "status": "success",
            "message": "Bulk upload started in background"
        })








import random
from faker import Faker


fake = Faker("en_IN")

CLOTHING_REVIEWS = [
    "Fabric quality is really good and feels premium.",
    "T-shirt fitting is perfect and very comfortable to wear.",
    "Material is soft and breathable, best for daily use.",
    "Color looks exactly same as shown on US VESTA website.",
    "Very good stitching and finishing, totally worth the price.",
    "Loved the oversized fit, looks very stylish.",
    "T-shirt fabric is thick and premium quality.",
    "Comfortable for long hours, fabric is skin friendly.",
    "Perfect casual wear t-shirt, great quality.",
    "Quality is amazing, will definitely buy again from US VESTA.",
    "Print quality is nice and fabric feels durable.",
    "Good value for money, fabric is really comfortable.",
    "Nice fitting and premium fabric, recommended.",
    "Color did not fade after wash, quality is top-notch.",
    "US VESTA never disappoints in quality."
    "osom",
    "Good Quality",
    "nice",
]


class GenerateFakeReviewsView(View):

    def post(self, request):

        products = Product.objects.all()
        if not products.exists():
            return JsonResponse({
                "status": "error",
                "message": "No products found"
            })

        created = 0

        for product in products:
            colors = Color_product.objects.filter(product=product)

            for _ in range(5):  # 5 reviews per product

                color = random.choice(colors) if colors.exists() else None

                User_Reviews.objects.create(
                    product=product,
                    inner_product_rew=color,
                    user=request.user,
                    name=fake.name(),
                    email=fake.email(),
                    msg=random.choice(CLOTHING_REVIEWS),  # 🔥 FIX HERE
                    star=str(random.choice([4, 5])),
                    show=True   # ya False, jaise chaho
                )

                created += 1

        return JsonResponse({
            "status": "success",
            "created": created,
            "message": f"{created} clothing-related reviews created"
        })
 
        
        
        
      

from django.shortcuts import get_object_or_404

class Retun_and_cancel(View):
    def post(self, request):

        return_id = request.POST.get("retun_model")
        return_reason = request.POST.get("retun_selectreason")
        return_msg = request.POST.get("retun_message")
        return_return_image = request.FILES.get("return_image")

        cancel_order_id = request.POST.get("cancel_order_id")
        cancel_reason = request.POST.get("cancel_reason")
        cancel_message = request.POST.get("cancel_message")

        # ================= RETURN =================
        if return_id and return_reason and return_msg:

            od = get_object_or_404(Order, id=return_id)

            if od.user != request.user:
                messages.error(request, "Unauthorized action")
                return redirect("/profile")

            rq_exist = Return_and_Cancel_products.objects.filter(orders=od).first()
            if rq_exist:
                messages.success(request, "Return request already submitted")
                return redirect("/profile")

            od.status = "Return in process"
            od.save()

            Return_and_Cancel_products.objects.create(
                user=request.user,
                orders=od,
                product_image_retun=return_return_image,
                reason=return_reason,
                reason_mesej=return_msg,
            )

            messages.success(request, "Return request submitted successfully")
            return redirect("/profile")

        # ================= CANCEL =================
        elif cancel_order_id and cancel_reason and cancel_message:

            od = get_object_or_404(Order, id=cancel_order_id)

            if od.user != request.user:
                messages.error(request, "Unauthorized action")
                return redirect("/profile")

            if od.status in ["Cancelled", "Delivered"]:
                messages.error(request, "Order already processed")
                return redirect("/profile")

            od.status = "Cancelled"
            od.save()

            Return_and_Cancel_products.objects.create(
                user=request.user,
                orders=od,
                reason=cancel_reason,
                reason_mesej=cancel_message,
                cancel_request=True
            )

            # ✅ API cancel safe call
            if od.awb_number:
                try:
                    cancel_shipment(od.awb_number)
                except Exception as e:
                    print("Cancel API Error:", e)

            messages.success(request, "Cancel request submitted successfully")
            return redirect("/profile")

        # ================= ERROR =================
        else:
            messages.error(request, "Oops something went wrong, please try again later")
            return redirect("/profile")
            








from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta

def create_online_order_in_db(request, order_id, amount_val):
    try:
        if not request.user.is_authenticated:
            return None
        
        user = request.user
        address_id = request.POST.get("address_id") or request.POST.get("address_ids")
        product_id = request.POST.get("product_id")
        inner_product_id = request.POST.get("inner_product_id")
        product_size = request.POST.get("product_size") or "M"
        totalquantity = request.POST.get("totalquantity") or 1
        
        user_address_selected = None
        if address_id:
            user_address_selected = Address_user.objects.filter(id=address_id).first()
        if not user_address_selected:
            user_address_selected = Address_user.objects.filter(user=user).first()
            
        addr_str = ""
        if user_address_selected:
            addr_str = f"""
                first_name={user_address_selected.name}
                phone={user_address_selected.phone_numer}
                email={user_address_selected.email}
                state={user_address_selected.state}
                landmark={user_address_selected.landmark}
                pincode={user_address_selected.pin_code}
                address={user_address_selected.user_address}
            """.strip()

        if product_id and str(product_id).strip() != "":
            prod = Product.objects.filter(id=product_id).first()
            if prod:
                return Order.objects.create(
                    user=user,
                    product=prod,
                    product_size=product_size,
                    quantity=totalquantity,
                    order_id=uuid.uuid4(),
                    transaction_id=order_id,
                    transaction_order_id=order_id,
                    total_price=amount_val,
                    payment_status="Pending",
                    payment_method="Online",
                    status="Pending",
                    address=addr_str
                )
        elif inner_product_id and str(inner_product_id).strip() != "":
            iprod = Color_product.objects.filter(id=inner_product_id).first()
            if iprod:
                return Order.objects.create(
                    user=user,
                    inner_color_product=iprod,
                    product_size=product_size,
                    quantity=totalquantity,
                    order_id=uuid.uuid4(),
                    transaction_id=order_id,
                    transaction_order_id=order_id,
                    total_price=amount_val,
                    payment_status="Pending",
                    payment_method="Online",
                    status="Pending",
                    address=addr_str
                )
        else:
            cart_items = list(Cart.objects.filter(user=user))
            if cart_items:
                for item in cart_items:
                    target_prod = item.product
                    target_inner = item.color_product
                    item_price = amount_val or (target_prod.b2c_price if target_prod else (target_inner.product.b2c_price if target_inner else 999))
                    Order.objects.create(
                        user=user,
                        product=target_prod,
                        inner_color_product=target_inner,
                        product_size=item.size or "M",
                        quantity=item.quantity or 1,
                        order_id=uuid.uuid4(),
                        transaction_id=order_id,
                        transaction_order_id=order_id,
                        total_price=item_price,
                        payment_status="Pending",
                        payment_method="Online",
                        status="Pending",
                        address=addr_str
                    )
                # Removed Cart delete from here; it will be deleted on successful payment.
    except Exception as e:
        print("Online Order DB Save Error:", e)

class create_cashfree_order(View):
    def post(self, request):
        import requests, uuid
        from django.conf import settings
        
        amount = request.POST.get("chasfreeamount") or request.POST.get("amount", "999.00")
        try:
            amount_val = float(amount)
        except Exception:
            amount_val = 999.00

        order_id = f"ORDER_{uuid.uuid4().hex[:12].upper()}"
        
        user_id = f"cust_{request.user.id}" if (request.user.is_authenticated and request.user.id) else f"cust_{uuid.uuid4().hex[:8]}"
        user_name = request.user.username if request.user.is_authenticated else "US VESTA Customer"
        user_email = request.user.email if (request.user.is_authenticated and request.user.email) else "customer@usvesta.com"
        user_phone = getattr(request.user, "phone_number", "9876543210") or "9876543210"
        
        payload = {
            "order_id": order_id,
            "order_amount": round(amount_val, 2),
            "order_currency": "INR",
            "customer_details": {
                "customer_id": str(user_id),
                "customer_name": str(user_name),
                "customer_email": str(user_email),
                "customer_phone": str(user_phone)
            },
            "order_meta": {}
        }
        
        app_id = getattr(settings, "CASHFREE_APP_ID", "")
        secret_key = getattr(settings, "CASHFREE_SECRET_KEY", "")
        
        headers = {
            "x-client-id": app_id,
            "x-client-secret": secret_key,
            "x-api-version": "2023-08-01",
            "Content-Type": "application/json"
        }

        api_url = "https://sandbox.cashfree.com/pg/orders" if app_id.startswith("TEST") else "https://api.cashfree.com/pg/orders"

        try:
            res = requests.post(api_url, json=payload, headers=headers, timeout=10)
            res_data = res.json()
            
            if res.status_code in [200, 201] and "payment_session_id" in res_data:
                create_online_order_in_db(request, order_id, amount_val)
                session_id = res_data["payment_session_id"]
                checkout_url = f"https://payments.cashfree.com/order/#/{session_id}"
                return JsonResponse({
                    "status": "success",
                    "payment_session_id": session_id,
                    "order_id": order_id,
                    "checkout_url": checkout_url
                })
            else:
                err_msg = res_data.get("message", "Unable to create Cashfree order")
                return JsonResponse({"status": "error", "message": err_msg}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    
class create_veno_order(View):
    def post(self, request):
        import requests, uuid
        from django.conf import settings
        
        amount = request.POST.get("chasfreeamount") or request.POST.get("amount", "999.00")
        try:
            amount_val = float(amount)
        except Exception:
            amount_val = 999.00

        order_id = f"ORDER_PY_{uuid.uuid4().hex[:8].upper()}"
        
        user_email = request.user.email if (request.user.is_authenticated and request.user.email) else "customer@example.com"
        user_phone = getattr(request.user, "phone_number", "9876543210") or "9876543210"
        
        redirect_url = request.build_absolute_uri('/payment/success/') + f"?order_id={order_id}"
        if redirect_url.startswith("http://") and not "127.0.0.1" in redirect_url and not "localhost" in redirect_url:
            redirect_url = "https://" + redirect_url[7:]

        gateway_url = getattr(settings, "VENO_GATEWAY_URL", "https://payzen.cloud/api/v1/payment/orders/")
        master_key = getattr(settings, "VENO_MASTER_API_KEY", "pub_live_c5c00d0a2bd29678528aca4a929d0ae8")

        headers = {
            "x-api-key": master_key,
            "Content-Type": "application/json"
        }

        # Fetch CMS settings for dynamic branding
        brand_name = "US VESTA"
        logo_url = ""
        try:
            cms = HomePageEditor.objects.first()
            if cms:
                if cms.store_name:
                    brand_name = cms.store_name
                if cms.footer_logo:
                    logo_url = request.build_absolute_uri(cms.footer_logo.url)
                elif cms.header_logo:
                    logo_url = request.build_absolute_uri(cms.header_logo.url)
        except Exception:
            pass

        if not logo_url:
            logo_url = request.build_absolute_uri('/static/images/logo2.png')

        # Ensure logo_url is publicly accessible on live server for payzen.cloud
        if "127.0.0.1" in logo_url or "localhost" in logo_url or "testserver" in logo_url or logo_url.startswith("http://"):
            if "127.0.0.1" in logo_url or "localhost" in logo_url or "testserver" in logo_url:
                logo_url = "https://usvesta.com/static/images/logo2.png"
            else:
                logo_url = "https://" + logo_url[7:]

        payload = {
            "amount": f"{amount_val:.2f}",
            "order_id": order_id,
            "currency": "INR",
            "customer_email": str(user_email),
            "customer_phone": str(user_phone),
            "redirect_url": redirect_url,
            "business_name": brand_name,
            "merchant_name": brand_name,
            "brand_name": brand_name,
            "logo_url": logo_url
        }

        try:
            res = requests.post(gateway_url, json=payload, headers=headers, timeout=12)
            data = res.json()
            if res.status_code in [200, 201] or data.get("checkout_url"):
                create_online_order_in_db(request, order_id, amount_val)
                return JsonResponse({
                    "status": "success",
                    "checkout_url": data["checkout_url"],
                    "payment_id": data.get("payment_id"),
                    "order_id": order_id
                })
            else:
                err_msg = data.get("message") or data.get("error") or "Veno Gateway Order Creation Failed"
                return JsonResponse({"status": "error", "message": err_msg}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class Order_details_pg(View):
    def get(self, request, uu_id):
        from django.db.models import Q
        order = Order.objects.filter(user=request.user).filter(
            Q(product__uuid_product=uu_id) | Q(inner_color_product__product__uuid_product=uu_id)
        ).order_by("-id").first()

        if not order:
            order = Order.objects.filter(user=request.user).filter(
                Q(id=uu_id if str(uu_id).isdigit() else None) | Q(transaction_id=uu_id) | Q(transaction_order_id=uu_id)
            ).order_by("-id").first()

        if not order:
            return redirect("/profile")

        target_product = order.inner_color_product.product if order.inner_color_product else order.product

        unit_listing = float(target_product.discount_price) if (target_product and target_product.discount_price) else 0.0
        unit_selling = float(target_product.b2c_price) if (target_product and target_product.b2c_price) else 0.0
        qty = int(order.quantity) if order.quantity else 1
        total_price = float(order.total_price) if order.total_price else (unit_selling * qty)

        total_mrp = (unit_listing * qty) if unit_listing > 0 else total_price
        if total_mrp < total_price:
            total_mrp = total_price

        discount_amount = max(0.0, total_mrp - total_price)
        discount_percent = round((discount_amount / total_mrp) * 100) if total_mrp > 0 else 0

        parsed_address = {}
        if order.address:
            for part in order.address.split("\n"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    parsed_address[k.strip()] = v.strip()

        data = {
            "orderd_product": order,
            "target_product": target_product,
            "unit_listing": unit_listing,
            "unit_selling": unit_selling,
            "qty": qty,
            "total_mrp": total_mrp,
            "total_price": total_price,
            "discount_amount": discount_amount,
            "discount_percent": discount_percent,
            "parsed_address": parsed_address
        }

        return render(request, "order_details.html", data)
