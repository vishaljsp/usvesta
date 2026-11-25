from django.db import models
from django.contrib.auth.models import AbstractUser
from .otp import *

from django.core.mail import send_mail
from django.conf import settings
from multiselectfield import MultiSelectField

from autoslug import AutoSlugField
try:
    from froala_editor.fields import FroalaField
except ImportError:
    class FroalaField(models.TextField):
        def __init__(self, *args, **kwargs):
            kwargs.pop('options', None)
            kwargs.pop('theme', None)
            kwargs.pop('image_upload', None)
            super().__init__(*args, **kwargs)
from django.db.models.signals import pre_save,post_save
from .emal_sender_function import *
from django.dispatch import receiver
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import re
from django.utils import timezone
from datetime import timedelta
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from .delhivery_utils import *

from decimal import Decimal
from django.db import models




class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to="user_profile", blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)  # unique hona chahiye

    phone_number_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)  # OTP expiry ke liye
    decrypt_password = models.CharField(max_length=100, blank=True, null=True)
    email_verification = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    about = models.CharField(max_length=300, blank=True, null=True)
    bank_details = models.CharField(max_length=100, blank=True, null=True)
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)

    USER_TYPE = (
        ('B2B', 'B2B'),
        ('B2C', 'B2C'),
        ('Website_own', 'Website_own'),
    )
    user_type = models.CharField(max_length=100, choices=USER_TYPE, default='B2C')

    def is_otp_valid(self):
        if self.otp_created_at:
            return timezone.now() < self.otp_created_at + timedelta(minutes=5)  # OTP 5 min ke liye valid
        return False

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

@receiver(pre_save, sender=CustomUser)
def user_uuid_saver(sender, instance, **kwargs):
    if not instance.email_token:
        instance.email_token = str(uuid.uuid4())


    
class Product_category(models.Model):
    MOKUPS=(
        ("T-shirt","T-shirt"),
        ("Shirt","Shirt"),
        ("Mug","Mug"),
        ("Polo T-shirt","Polo T-shirt"),
    )
    category_image = models.ImageField(upload_to="cat_image", null=True, blank=True)
    name = models.CharField(max_length=500)
    mokups_type = models.CharField(max_length=500, choices=MOKUPS,null=True,blank=True)
    uuid_product = models.CharField(max_length=100, null=True, blank=True, editable=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/category?categories={self.uuid_product}"
    
    def save(self, *args, **kwargs):
        if not self.uuid_product:
            self.uuid_product = str(uuid.uuid4())
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

@receiver(pre_save, sender=Product_category)
def product_category_uuid_pre_save(sender, instance, **kwargs):
    if not instance.uuid_product:
        instance.uuid_product = str(uuid.uuid4())

class Product_sub_category(models.Model):
    category = models.ForeignKey(Product_category,blank=True,null=True, on_delete=models.CASCADE)

    category_image = models.ImageField(upload_to="cat_image", null=True, blank=True)
    name = models.CharField(max_length=50)
    uuid_product = models.CharField(max_length=100, null=True, blank=True, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    customcode=models.TextField( null=True, blank=True,)
    category_slug = AutoSlugField(populate_from="name",unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.uuid_product:
            self.uuid_product = str(uuid.uuid4())
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Product Sub Category"
        verbose_name_plural = "Product Sub Categories"
        

    def get_absolute_url(self):
        return f"/collections/{self.category_slug}"
    


@receiver(pre_save, sender=Product_sub_category)
def product_sub_category_uuid_pre_save(sender, instance, **kwargs):
    if not instance.uuid_product:
        instance.uuid_product = str(uuid.uuid4())
        
    # if instance.category_slug:
    #     instance.category_slug = slugify(instance.name)
    
    
class Product(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Product_category, on_delete=models.CASCADE,blank=True,null=True)
    sub_category = models.ForeignKey(Product_sub_category,blank=True,null=True, on_delete=models.CASCADE)
    brand = models.CharField(max_length=500, default="US Vesta")
    top_eight_products=models.BooleanField(default=False)
    ratings=models.CharField(blank=True,null=True,max_length=500)
    product_sku=models.CharField(blank=True,null=True,max_length=500)
    total_sale_products=models.CharField(blank=True,null=True,max_length=500)
    # Product
    temp_product_image_url = models.URLField(blank=True, null=True)
    STATUS = (
        ("Publish", "Publish"),
        ('Draft','Draft')
    )
    SELECT_PAGE = (
        ("For Corporates", "For Corporates"),
        ('Shop', 'Shop'),
        ('Both','Both')
    )
    select_page = models.CharField(choices=SELECT_PAGE, max_length=100,blank=True,null=True)

   
    TTYPE = (
        ( "Collar Neck T Shirt", "Collar Neck T Shirt"),
        ('Round Neck T Shirt','Round Neck T Shirt')
    )
    t_shirt_type = models.CharField(choices=TTYPE, max_length=500, blank=True, null=True)
    product_name = models.CharField(max_length=500)
    product_image = models.ImageField(upload_to="product_image") #  pendig 
    key_words = models.CharField(max_length=500)
    product_image_alt = models.CharField(max_length=500) #  pendig 
    product_description = FroalaField()
    
    product_status = models.CharField(choices=STATUS, max_length=100,default="Publish")
    discount_price = models.CharField(max_length=500,verbose_name="Regular price")
    product_slug = AutoSlugField(populate_from="product_name", unique=True)
    uuid_product = models.CharField(max_length=100, null=True, blank=True, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    b2b_price = models.DecimalField(max_digits=10, decimal_places=2,max_length=500, null=True, blank=True)
    b2c_price = models.DecimalField(max_digits=10, decimal_places=2,max_length=500,verbose_name="Sale price")
    color = models.CharField(max_length=500)
    color_code = models.CharField(max_length=500)
    product_quantity_offer=models.IntegerField(null=True,blank=True)
    product_amount_offer=models.DecimalField(max_digits=10, decimal_places=2,max_length=50,null=True,blank=True)

    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    
    @property
    def average_rating(self):
        reviews = self.user_reviews_set.filter(show=True)
        count = reviews.count()
        if count == 0:
            return 0.0
        total = 0
        for r in reviews:
            try:
                total += float(r.star)
            except:
                pass
        return round(total / count, 1)

    @property
    def dynamic_review_count(self):
        return self.user_reviews_set.filter(show=True).count()

    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        return f"/products/{self.uuid_product}"
    
    # ✅ Discount Percentage Function
    def get_discount_percentage(self):
        try:
            reg_price = float(self.discount_price)
            sale_price = float(self.b2c_price)
            if reg_price > 0 and reg_price > sale_price:
                discount = ((reg_price - sale_price) / reg_price) * 100
                return int(round(discount))
            return 0
        except:
            return 0

    def get_b2c_price_int(self):
        try:
            val = float(self.b2c_price)
            return f"{int(round(val))}"
        except:
            return self.b2c_price

    def get_discount_price_int(self):
        try:
            val = float(self.discount_price)
            return f"{int(round(val))}"
        except:
            return self.discount_price

    def save(self, *args, **kwargs):
        if not self.uuid_product:
            self.uuid_product = str(uuid.uuid4())
        super().save(*args, **kwargs)

@receiver(pre_save, sender=Product)
def product_uuid_pre_save(sender, instance, **kwargs):
    if not instance.uuid_product:
        instance.uuid_product = str(uuid.uuid4())
        
        

class Hightlight_for_product(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    highlight = FroalaField(null=True,blank=True)


class Color_product(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    color = models.CharField(max_length=200)
    color_code = models.CharField(max_length=200)
    color_images = models.ImageField(upload_to="color_images", blank=True, null=True, max_length=500)
    uuid_product = models.CharField(max_length=100, null=True, blank=True, editable=False)
    # Color
    temp_color_image_url = models.URLField(blank=True, null=True)

    
    @property
    def average_rating(self):
        reviews = self.user_reviews_set.filter(show=True)
        count = reviews.count()
        if count == 0:
            return 0.0
        total = 0
        for r in reviews:
            try:
                total += float(r.star)
            except:
                pass
        return round(total / count, 1)

    @property
    def dynamic_review_count(self):
        return self.user_reviews_set.filter(show=True).count()

    def __str__(self):
        return self.color

    def save(self, *args, **kwargs):
        if not self.uuid_product:
            self.uuid_product = str(uuid.uuid4())
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Color Product"
        verbose_name_plural = "Color Products"


@receiver(pre_save, sender=Color_product)
def color_product_uuid_pre_save(sender, instance, **kwargs):
    if not instance.uuid_product:
        instance.uuid_product = str(uuid.uuid4())


class color_product_Gelery_images(models.Model):
    color_product = models.ForeignKey(Color_product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_image")
    alt = models.CharField(max_length=500,null=True,blank=True)
    # Color
     # ✅ ADD THIS
    temp_image_url = models.URLField(blank=True, null=True)
    class Meta:

        verbose_name = "Inner Product Gallery Image"
        verbose_name_plural = "Inner Product Gallery Images"
    
    





class product_Gelery_images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_image")
    alt = models.CharField(max_length=500)
    temp_image_url = models.URLField(blank=True, null=True)
    class Meta:
        verbose_name = "Product Gallery Image"
        verbose_name_plural = "Product Gallery Images"
    
    

class Size_price_par_post(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=200)
    
    def __str__(self):
        return self.size
    
    class Meta:
        verbose_name = "Product Size"
        verbose_name_plural = "Product Sizes"





class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    inner_products_card = models.ForeignKey(Color_product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(auto_now=True)
    size = models.CharField(max_length=200, blank=True, null=True)

    def total_price(self):
        if not self.product:
            return 0

        qty = Decimal(self.quantity)

        if self.user.user_type == "B2B":
            price = Decimal(self.product.b2b_price)
        else:
            price = Decimal(self.product.b2c_price)

        return qty * price

    def total_price_int(self):
        val = self.total_price()
        return int(round(val)) if val else 0

    def total_inner_product_price(self):
        if not self.inner_products_card:
            return 0

        qty = Decimal(self.quantity)

        if self.user.user_type == "B2B":
            price = Decimal(self.inner_products_card.product.b2b_price)
        else:
            price = Decimal(self.inner_products_card.product.b2c_price)

        return qty * price

    def total_inner_product_price_int(self):
        val = self.total_inner_product_price()
        return int(round(val)) if val else 0

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"







class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    inner_products_wishlist = models.ForeignKey(Color_product, on_delete=models.CASCADE, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"

class Address_user(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    phone_numer = models.CharField(max_length=200)
    pin_code = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    user_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Address"



class Order(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    inner_color_product = models.ForeignKey(Color_product, on_delete=models.CASCADE, null=True, blank=True)
    custom_name = models.CharField(max_length=500 , blank=True, null=True)
    custom_email = models.CharField(max_length=500 , blank=True, null=True)
    custom_number = models.CharField(max_length=500 , blank=True, null=True)
    custom_design = models.ImageField(upload_to="customdesign", null=True, blank=True)
    product_size = models.CharField(max_length=200)
    quantity = models.CharField(max_length=200)
    order_id = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    transaction_order_id = models.CharField(max_length=200, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(null=True, blank=True)
    messag = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Ordered', 'Ordered'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'),
            ('Out for Delivery','Out for Delivery'),
            ("Return in process", "Return in process"),
            ("Return Accepte", "Return Accepte"),
            ("Return reject", "Return reject"),
            ("Return", "Return"),
            ("Refund", "Refund"),
        ],
        default='Ordered'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
        default='pending'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=[('Online', 'Online'), ('Cash On Delivery', 'Cash On Delivery')],
        default='Cash On Delivery'
    )
    awb_number = models.CharField(max_length=100, null=True, blank=True)
    shipment_id = models.CharField(max_length=100, null=True, blank=True)
    shipment_status = models.CharField(max_length=50, default="Pending")

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD{self.id or uuid.uuid4().hex[:8].upper()}"
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
        if not self.transaction_order_id:
            self.transaction_order_id = f"TOID{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"



def extract_full_address(address):
    data = {}

    if not address:
        return data

    lines = address.split("\n")

    for line in lines:
        line = line.strip()

        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()

    return data
@receiver(post_save, sender=Order)
def create_delhivery_shipment(sender, instance, created, **kwargs):

    if created and not instance.awb_number:

        data = extract_full_address(instance.address)

        name = data.get("first_name", instance.custom_name or "Customer")
        phone = data.get("phone", instance.custom_number or "9999999999")
        pincode = data.get("pincode", "110001")
        state = data.get("state", "Delhi")

        # 👇 city address से निकाल सकते हो (simple logic)
        full_address = data.get("address", "")
        city = full_address.split()[-1] if full_address else "Delhi"

        response, awb, ref = create_shipment(
            instance,
            name,
            phone,
            pincode,
            city,
            state
        )

        if awb:
            Order.objects.filter(id=instance.id).update(
                awb_number=awb,
                shipment_id=ref,
                shipment_status="Created"
            )
        else:
            Order.objects.filter(id=instance.id).update(
                shipment_status="Failed"
            )






def extract_name_and_phone(address):
    name = None
    phone = None

    if not address:
        return name, phone

    lines = address.split("\n")  # Break into lines

    for line in lines:
        line = line.strip()

        if line.startswith("first_name="):
            name = line.replace("first_name=", "").strip()

        if line.startswith("phone="):
            phone = line.replace("phone=", "").strip()

    return name, phone

# OWNER/Admin WhatsApp Number



class Return_and_Cancel_products(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    orders=models.ForeignKey(Order,on_delete=models.CASCADE)
    product_image_retun = models.ImageField(upload_to="retun_p_image", blank=True, null=True,)
    reason=models.CharField( max_length=500)
    reason_mesej=models.TextField()
    cancel_request=models.BooleanField(default=False)

    create_at=models.DateTimeField(auto_now_add=True)
# ---------------------------------------------------------
# 1️⃣ NEW ORDER CREATED — Admin + Customer ko message bhejo
# ---------------------------------------------------------
# @receiver(post_save, sender=Order)
# def send_new_order_notification(sender, instance, created, **kwargs):
#     ADMIN_NUMBER = "+918700242627"   # <-- yahan owner ka number
#     # ADMIN_NUMBER = "+919625012433"   # <-- yahan owner ka number

#     customer_name, customer_number = extract_name_and_phone(instance.address)
#     if created:
     
#         # ---- ADMIN MESSAGE ----
#         admin_msg = f"""
# 📦          NEW ORDER RECEIVED 😊🎊🎉

#             Order-ID: {instance.order_id}
#             Quantity: {instance.quantity}
#             Total: ₹{instance.total_price}

#             Payment: {instance.payment_status} ({instance.payment_method})
#             Address: {instance.address}

#             Date: {instance.created_at}

#             Check admin panel.
#             """

#                     # ---- CUSTOMER MESSAGE ----
#         customer_msg = f"""
#             Hi {customer_name}, 👋

#             Your order has been placed successfully! 🎉

#             Order-ID: {instance.order_id}
#             Amount: ₹{instance.total_price}
#             Payment: {instance.payment_status}
#             Date: {instance.created_at.strftime('%d-%m-%Y %I:%M %p')}

#             Thank you for shopping with Us Vesta 
#             """

      



# ---------------------------------------------------------
# 2️⃣ ORDER UPDATED — Customer ko status update message bhejo
# ---------------------------------------------------------
# @receiver(post_save, sender=Order)
# def send_order_update_notification(sender, instance, created, **kwargs):
#     customer_name, customer_number = extract_name_and_phone(instance.address)

#     if not created: 

#         status_messages = {
#             "Ordered": "Your order has been placed successfully! 🎉",
#             "Shipped": "Your order has been shipped 🚚",
#             "Delivered": "Your order has been delivered 📦✔️",
#             "Cancelled": "Your order has been cancelled ❌",
#             "Return in process": "Your return request is being processed 🔄",
#             "Return Accepte": "Your return request has been approved ✔️",
#             "Return reject": "Your return request has been rejected ❗",
#             "Return": "Your order has been returned 🔄",
#             "Refund": "Your refund has been processed 💰",
#         }

#         msg = f"""
#             Hi {customer_name},

#             Order Update 🔔

#             Order-ID: {instance.order_id}
#             Status: {instance.status}
#             Update: {status_messages.get(instance.status, "Your order has been updated")}

#             Amount: ₹{instance.total_price}
#             Updated At: {timezone.now().strftime('%d-%m-%Y %I:%M %p')}

#             Thank you for shopping with Us Vesta ❤️
#         """

#         if customer_number:
#             send_whatsapp(customer_number, msg)

#         print("🔄 Order Update Notification Sent to Customer")


class User_Reviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    inner_product_rew = models.ForeignKey(Color_product, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    msg = models.TextField()
    star = models.CharField(max_length=50)
    show = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "User Review"
        verbose_name_plural = "User Reviews"

class Contact_US(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

class Blog_Category(models.Model):
    category = models.CharField(max_length=1000)
    ct_slug = AutoSlugField(populate_from='category', unique=True, max_length=800, default="")
    
    def __str__(self) -> str:
        return self.category
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

class Blog_post(models.Model):
    author = models.CharField(max_length=550)
    category = models.ForeignKey(Blog_Category, on_delete=models.CASCADE, db_index=True)
    blog_image = models.ImageField(upload_to="media/letestblog/")
    image_alt_name = models.CharField(max_length=500)
    meta_title = models.CharField(max_length=250, db_index=True)
    meta_keyword = models.CharField(max_length=500, null=True, blank=True)
    meta_description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now=True)
    blog_content = FroalaField()
    slug = AutoSlugField(populate_from='meta_title', unique=True, max_length=1000, default='')
    date = models.DateTimeField()
    
    search_blogs_dt = ["meta_title", "category__category"]
    
    def __str__(self) -> str:
        return self.slug
    
    def get_absolute_url(self):
        return f"/{self.slug}"
    
    class Meta:
        indexes = [models.Index(fields=["id", "slug", "meta_title", "meta_description", "meta_keyword"])]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    
        

class A_plus_listing(models.Model):
    image = models.ImageField(upload_to="media/apluslisting/")
    image_alt_name = models.CharField(max_length=500)

   
    

PAGE_CHOICES = (
    ('/', 'Home Page'),
    ('/our-story', 'Our Story Page'),
    ('/shop', 'Shop Page'),
    ('/contact-us', 'Contact US'),
    ('/for-corporates', 'For Corporates Page B2B'),
    ('/blog', 'Blogs'),
)

class Banners(models.Model):
    image = models.ImageField(upload_to="media/banners_all/", null=True, blank=True)
    image_phone = models.ImageField(upload_to="media/phone-banners_all/", null=True, blank=True)
    
    video = models.FileField(upload_to="media/banners_video_all/", null=True, blank=True)
    image_alt_name = models.CharField(max_length=500)
    category_images_slider=models.ForeignKey(Product_sub_category,on_delete=models.CASCADE,null=True, blank=True)
    show_on_pages = MultiSelectField(choices=PAGE_CHOICES, max_length=100 ,null=True, blank=True)

    def __str__(self):
        return f"Banner for: {', '.join(self.show_on_pages)}"
   


class Insta_images(models.Model):
    
    image = models.ImageField(upload_to="media/insta_images/", null=True, blank=True)
    
    
class Testimoninal(models.Model):
    image = models.ImageField(upload_to="media/testimonial/")
    image_alt_name = models.CharField(max_length=500)
    name = models.CharField(max_length=500)
    company_name = models.CharField(max_length=500)
    content = models.CharField(max_length=500)
    date=models.DateTimeField(auto_now_add=True)
    
    
class Our_trusted_client(models.Model):
    image = models.ImageField(upload_to="media/trustedclient/")
    image_alt_name = models.CharField(max_length=500)

   


class Leave_checkout_page_billing_details(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    phone = models.CharField(max_length=500)
    email = models.EmailField(max_length=500)
    address=models.TextField()
    country = models.CharField(max_length=500)
    landmark  = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    pincode  = models.CharField(max_length=500)
    payment_method  = models.CharField(max_length=500)
    amount = models.CharField(max_length=500)
    date=models.DateTimeField(auto_now=True)

    
class Chatbot_users(models.Model):
    name=models.CharField(max_length=500)
    email=models.EmailField()
    phone=models.CharField(max_length=50)
    

    def __str__(self):
        return self.name
    
    
 
class sub_category_coordinator(models.Model):
    sub_category = models.ForeignKey(Product_sub_category,blank=True,null=True, on_delete=models.CASCADE)
    name=models.CharField(max_length=500) 
    containt=FroalaField()
    show_on_pages = MultiSelectField(choices=PAGE_CHOICES, max_length=100 ,null=True, blank=True)

    def __str__(self):
        return self.name


# ==============================================================================
# CUSTOM UPI PAYMENT GATEWAY & QR COLLECTION PLATFORM MODELS
# ==============================================================================
import hashlib
import uuid

class Merchant(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'ACTIVE'),
        ('DISABLED', 'DISABLED'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='merchant_profile', null=True, blank=True)
    business_name = models.CharField(max_length=255, default="US VESTA Merchant")
    merchant_vpa = models.CharField(max_length=255, default="vishaljsp69@oksbi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    daily_amount_limit = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    daily_transaction_limit = models.IntegerField(default=1000)
    priority = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} ({self.merchant_vpa})"

class APIKey(models.Model):
    MODE_CHOICES = (
        ('TEST', 'TEST'),
        ('LIVE', 'LIVE'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='gateway_api_keys', null=True, blank=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='TEST')
    public_key = models.CharField(max_length=100, null=True, blank=True)
    secret_key_hash = models.CharField(max_length=64, default='')
    secret_key_preview = models.CharField(max_length=100, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_key_pair(cls, merchant, mode='TEST'):
        """
        Key Rotation Rule: When a new API Key is generated for a mode (TEST or LIVE),
        automatically deactivate (is_active = False) all previous keys of that mode for the merchant.
        """
        cls.objects.filter(merchant=merchant, mode=mode, is_active=True).update(is_active=False)

        suffix = uuid.uuid4().hex
        pub_prefix = "pub_test_" if mode == 'TEST' else "pub_live_"
        sec_prefix = "sec_test_" if mode == 'TEST' else "sec_live_"

        public_key = f"{pub_prefix}{suffix[:16]}"
        raw_secret = f"{sec_prefix}{suffix}"

        secret_hash = hashlib.sha256(raw_secret.encode('utf-8')).hexdigest()
        secret_preview = f"{sec_prefix}{suffix[:6]}...{suffix[-4:]}"

        key_obj = cls.objects.create(
            merchant=merchant,
            mode=mode,
            public_key=public_key,
            secret_key_hash=secret_hash,
            secret_key_preview=secret_preview,
            is_active=True
        )

        return key_obj, raw_secret

    def __str__(self):
        return f"{self.merchant.business_name} [{self.mode}] - {self.public_key}"

class PaymentOrder(models.Model):
    MODE_CHOICES = (
        ('TEST', 'TEST'),
        ('LIVE', 'LIVE'),
    )
    STATUS_CHOICES = (
        ('CREATED', 'CREATED'),
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('EXPIRED', 'EXPIRED'),
    )
    payment_id = models.CharField(max_length=100, primary_key=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='payment_orders')
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='TEST')
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CREATED')
    payment_provider = models.CharField(max_length=50, default='UPI_INTENT')
    provider_reference = models.CharField(max_length=100, null=True, blank=True)
    qr_payload = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField()
    success_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        if self.status in ['SUCCESS', 'FAILED']:
            return False
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.payment_id} | {self.order_id} | ₹{self.amount} | {self.status}"

class WebhookEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='webhook_endpoints')
    target_url = models.URLField(max_length=500)
    secret_key = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100, default='payment.success')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant.business_name} -> {self.target_url}"

class WebhookDelivery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='deliveries')
    payment_order = models.ForeignKey(PaymentOrder, on_delete=models.CASCADE, related_name='webhook_deliveries')
    event_type = models.CharField(max_length=100)
    request_payload = models.JSONField()
    response_status = models.IntegerField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery to {self.webhook_endpoint.target_url} - Delivered: {self.delivered}"

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.JSONField(default=dict)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at} | {self.action}"


# ==============================================================================
# HOMEPAGE CMS EDITOR MODEL (Full Home Page, Header, Footer, Links & Image Management)
# ==============================================================================
class HomePageEditor(models.Model):
    # Header & Announcement
    header_logo = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    header_announcement_text = models.CharField(max_length=500, default="FREE SHIPPING ON ALL ORDERS OVER ₹999")
    
    # Footer & Social Settings
    footer_logo = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    footer_tagline = models.TextField(default="Thoughtfully designed and built to endure. US Vesta merges modern luxury with functional simplicity.")
    footer_facebook_url = models.URLField(default="https://www.facebook.com/profile.php?id=61581390461341")
    footer_instagram_url = models.URLField(default="https://www.instagram.com/usvesta25/")
    footer_linkedin_url = models.URLField(default="https://www.linkedin.com/company/us-vesta/")
    footer_copyright = models.CharField(max_length=255, default="© 2013 — 2026 US Vesta. Designed for modern living. All rights reserved.")

    # Hero Banner Settings
    hero_subtitle = models.CharField(max_length=255, default="THE STREET IS OUR STAGE")
    hero_title = models.CharField(max_length=255, default="COLLECTIVE DROP")
    hero_description = models.CharField(max_length=255, default="EXPLORE THE UNTAMED.")
    hero_button_text = models.CharField(max_length=100, default="COLLECTION")
    hero_button_link = models.CharField(max_length=255, default="/shop")
    hero_bg_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)

    # Section 4 - Fit & Craft Showcase Settings
    fit_section_badge = models.CharField(max_length=100, default="US VESTA | NEW ARRIVAL")
    fit_card1_title = models.CharField(max_length=255, default="MULTI-DIMENSIONAL FIT")
    fit_card1_desc = models.TextField(default="HEAVYWEIGHT 300 GSM COTTON. TAILORED DITTO STRUCTURE.")
    fit_card2_title = models.CharField(max_length=255, default="ENGINEERED COMFORT")
    fit_card2_desc = models.TextField(default="BREATHABLE WEAVE FOR ALL-DAY URBAN MOBILITY.")
    fit_hero_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_section_bg_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_img1 = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_img2 = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_img3 = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_img5 = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    fit_img6 = models.ImageField(upload_to="cms_images/", null=True, blank=True)

    # Dedicated Standalone Featured Product Slider Section (Below Section 4)
    section4_slider_enabled = models.BooleanField(default=True)
    section4_slider_desktop_enabled = models.BooleanField(default=True)
    section4_slider_mobile_enabled = models.BooleanField(default=True)
    section4_slider_mobile_item_count = models.IntegerField(default=4)
    section4_slider_title = models.CharField(max_length=255, default="FEATURED PRODUCTS")

    # Country & Currency Selector Settings (Gucci Style)
    enable_country_modal = models.BooleanField(default=True)
    usd_conversion_rate = models.FloatField(default=0.012)
    eur_conversion_rate = models.FloatField(default=0.011)
    gbp_conversion_rate = models.FloatField(default=0.0095)
    aed_conversion_rate = models.FloatField(default=0.044)

    # Section 5 - 2x2 Showcase Grid Settings
    grid_tile1_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    grid_tile1_link = models.CharField(max_length=255, default="/shop")
    grid_tile2_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    grid_tile2_link = models.CharField(max_length=255, default="/shop")
    grid_tile3_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    grid_tile3_link = models.CharField(max_length=255, default="/shop")
    grid_tile4_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    grid_tile4_link = models.CharField(max_length=255, default="/shop")
    grid_center_button_text = models.CharField(max_length=100, default="COLLECTIONS →")
    grid_center_button_link = models.CharField(max_length=255, default="/shop")

    # Typography & Font Customization Settings
    hero_title_font_size = models.CharField(max_length=50, default="clamp(2rem, 4.2vw, 3.6rem)")
    hero_title_color = models.CharField(max_length=50, default="#ffffff")
    hero_title_font_family = models.CharField(max_length=100, default="'Playfair Display', serif")
    hero_subtitle_font_size = models.CharField(max_length=50, default="clamp(0.85rem, 1.4vw, 1.1rem)")
    hero_subtitle_color = models.CharField(max_length=50, default="#ffffff")
    
    # Announcement Bar Settings
    announcement_enabled = models.BooleanField(default=True)
    announcement_bg_color = models.CharField(max_length=50, default="#0d0d0d")
    announcement_text_color = models.CharField(max_length=50, default="#ffffff")
    announcement_font_size = models.CharField(max_length=50, default="0.75rem")
    announcement_font_weight = models.CharField(max_length=50, default="600")

    # Header & Logo Styling
    logo_width = models.CharField(max_length=50, default="140px")
    logo_height = models.CharField(max_length=50, default="auto")
    logo_link = models.CharField(max_length=255, default="/")
    header_bg_color = models.CharField(max_length=50, default="#ffffff")
    header_text_color = models.CharField(max_length=50, default="#000000")
    mobile_header_bg_color = models.CharField(max_length=50, default="#ffffff")
    mobile_header_text_color = models.CharField(max_length=50, default="#0d0d0d")
    mobile_header_logo = models.ImageField(upload_to="cms_images/", null=True, blank=True)

    # Hero Extra Controls
    hero_bg_mobile_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    hero_title_font_weight = models.CharField(max_length=50, default="500")
    hero_description_font_size = models.CharField(max_length=50, default="clamp(0.8rem, 1.3vw, 1.05rem)")
    hero_description_color = models.CharField(max_length=50, default="#ffffff")
    hero_button_bg_color = models.CharField(max_length=50, default="#c5a059")
    hero_button_text_color = models.CharField(max_length=50, default="#ffffff")
    hero_overlay_opacity = models.CharField(max_length=50, default="0.3")

    # Homepage Section Visibility Controls
    section2_enabled = models.BooleanField(default=True)  # Feature Ticker Strip
    section3_enabled = models.BooleanField(default=True)  # 3D Product Carousel
    section3_desktop_enabled = models.BooleanField(default=True)
    section3_mobile_enabled = models.BooleanField(default=False)

    section3_card1_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    section3_card1_title = models.CharField(max_length=255, default="Fears Heavyweight")
    section3_card1_price = models.CharField(max_length=100, default="₹ 1199")
    section3_card1_desc = models.CharField(max_length=255, default="300 GSM cotton | Limited run")
    section3_card1_link = models.CharField(max_length=255, default="/shop")

    section3_card2_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    section3_card2_title = models.CharField(max_length=255, default="Print Gprint")
    section3_card2_price = models.CharField(max_length=100, default="₹ 1199")
    section3_card2_desc = models.CharField(max_length=255, default="300 GSM cotton | Limited run")
    section3_card2_link = models.CharField(max_length=255, default="/shop")

    section3_card3_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    section3_card3_title = models.CharField(max_length=255, default="Maroon Oversized")
    section3_card3_price = models.CharField(max_length=100, default="₹ 1199")
    section3_card3_desc = models.CharField(max_length=255, default="300 GSM cotton | Limited run")
    section3_card3_link = models.CharField(max_length=255, default="/shop")

    section3_card4_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    section3_card4_title = models.CharField(max_length=255, default="Rhythmic Resonance")
    section3_card4_price = models.CharField(max_length=100, default="₹ 1199")
    section3_card4_desc = models.CharField(max_length=255, default="300 GSM cotton | Limited run")
    section3_card4_link = models.CharField(max_length=255, default="/shop")

    section3_card5_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    section3_card5_title = models.CharField(max_length=255, default="US VESTA Essential")
    section3_card5_price = models.CharField(max_length=100, default="₹ 1199")
    section3_card5_desc = models.CharField(max_length=255, default="300 GSM cotton | Limited run")
    section3_card5_link = models.CharField(max_length=255, default="/shop")
    section4_enabled = models.BooleanField(default=True)  # Fit & Craft Showcase
    section5_enabled = models.BooleanField(default=True)  # 2x2 Quad Grid
    section6_enabled = models.BooleanField(default=True)  # Customer Reviews

    # Section 4 Extra Styling
    fit_section_bg_color = models.CharField(max_length=50, default="#0d0d0d")

    # Section 5 Extra Styling & Alt Tags
    grid_tile1_alt = models.CharField(max_length=255, default="Make Dope Stuff Tee")
    grid_tile2_alt = models.CharField(max_length=255, default="Black Joker Graphic Tee")
    grid_tile3_alt = models.CharField(max_length=255, default="Black Panda Polo Shirt")
    grid_tile4_alt = models.CharField(max_length=255, default="Black Fears Biker Graphic Tee")
    grid_center_button_bg = models.CharField(max_length=50, default="rgba(255, 255, 255, 0.15)")
    grid_center_button_color = models.CharField(max_length=50, default="#ffffff")

    # Footer & Social Extra Styling
    footer_logo_height = models.CharField(max_length=50, default="45px")
    footer_bg_color = models.CharField(max_length=50, default="#0d0d0d")
    footer_text_color = models.CharField(max_length=50, default="#ffffff")
    footer_youtube_url = models.URLField(default="", blank=True)
    footer_twitter_url = models.URLField(default="", blank=True)

    # WordPress-Style Header & Footer Navigation Builder JSON
    header_nav_json = models.JSONField(default=list, blank=True)
    mobile_nav_json = models.JSONField(default=list, blank=True)
    footer_nav_json = models.JSONField(default=list, blank=True)

    # Mega Menu Dropdown Cards & Featured Links Customization
    mega_menu_cards_json = models.JSONField(default=dict, blank=True)
    mega_menu_featured_links_json = models.JSONField(default=list, blank=True)

    # Mega Menu Card Image Uploads (Direct file upload support)
    mega_card1_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    mega_card2_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    mega_card3_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    mega_card4_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)
    mega_card5_image = models.ImageField(upload_to="cms_images/", null=True, blank=True)

    # Express Shipping Banner Customization
    express_shipping_title = models.CharField(max_length=255, default="EXPRESS SHIPPING")
    express_shipping_subtitle = models.CharField(max_length=255, default="Complimentary priority delivery on orders over ₹1,999.")
    express_shipping_icon = models.CharField(max_length=100, default="fa-truck-fast")

    # Women's Collection 'Coming Soon' Modal Control
    women_coming_soon_enabled = models.BooleanField(default=True)

    # Extra JSON field for custom links & buttons
    custom_links_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Homepage CMS Content (Last Updated: {self.updated_at.strftime('%d %b %Y %H:%M')})"

    class Meta:
        verbose_name = "Homepage CMS Content"
        verbose_name_plural = "Homepage CMS Content"

@receiver(pre_save)
def auto_optimize_model_images(sender, instance, **kwargs):
    # Auto-compress and convert images to WebP for CMS, Products, and Gallery
    from cloth_app.models import HomePageEditor, Product, product_Gelery_images, color_product_Gelery_images
    if sender in [HomePageEditor, Product, product_Gelery_images, color_product_Gelery_images]:
        for field in instance._meta.fields:
            if isinstance(field, models.ImageField):
                file_obj = getattr(instance, field.name)
                if file_obj and hasattr(file_obj, 'file') and not getattr(file_obj, '_is_optimized', False):
                    try:
                        name = file_obj.name
                        if not name:
                            continue
                        ext = os.path.splitext(name)[1].lower()
                        if ext in ['.png', '.jpg', '.jpeg']:
                            img = Image.open(file_obj)
                            img = ImageOps.exif_transpose(img)
                            max_dim = 1920 if sender == HomePageEditor else 1200
                            w, h = img.size
                            if max(w, h) > max_dim:
                                scale = max_dim / float(max(w, h))
                                img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                            if img.mode not in ('RGB', 'RGBA'):
                                img = img.convert('RGB')
                            buf = BytesIO()
                            img.save(buf, format='WEBP', quality=82, method=6)
                            buf.seek(0)
                            webp_name = os.path.splitext(name)[0] + '.webp'
                            new_file = ContentFile(buf.read(), name=webp_name)
                            new_file._is_optimized = True
                            setattr(instance, field.name, new_file)
                    except Exception:
                        pass