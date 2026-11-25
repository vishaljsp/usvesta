
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
import nested_admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportMixin


# =============================================================================
# ADMIN CUSTOM FILTERS
# =============================================================================

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportMixin,admin.ModelAdmin):
    """Admin interface for custom user management"""
    
    search_fields = ['username', 'email', 'phone']
    
    list_filter = ['email_verification', 'user_type']
    
    list_display = ('username', 'email', 'phone_number_otp','phone', 'user_type', 'email_verification')
    
    readonly_fields = ('email_token', 'date_joined', 'last_login')
    
    fieldsets = (
        ('🔐 Authentication', {
            'fields': ('username', 'email', 'password')
        }),
        
        ('👤 Profile', {
            'fields': ('profile_image', 'phone_number_otp','phone', 'about', 'bank_details')
        }),
        ('🛡️ Permissions', {
            'fields': ('user_type', 'email_verification', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('📅 Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('🔒 Security', {
            'fields': ('email_token', 'decrypt_password')
        }),
    )

# =============================================================================

class UserProductFilter(SimpleListFilter):
    """Filter products by current user (for non-superusers)"""
    title = 'user products'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return []

    def queryset(self, request, queryset):
        return queryset if request.user.is_superuser else queryset.filter(user=request.user)

# =============================================================================
# USER MANAGEMENT
# =============================================================================

class ProductForm(forms.ModelForm):
    """Custom form for product with status validation"""
    class Meta:
        model = Product
        fields = '__all__'
    
    def clean_product_status(self):
        status = self.cleaned_data.get('product_status')
        if status not in dict(Product.STATUS).keys():
            raise forms.ValidationError("Invalid status selected")
        return status

@admin.register(Product_category)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin for product categories with UUID tracking"""
    
    search_fields = ['name']
    list_filter = ['date']
    list_display = ('name', 'date', 'uuid_product')
    readonly_fields = ('uuid_product',)
    list_per_page = 25

# -------------------------------
# Product Gallery Inlines
# -------------------------------

class GalleryImagesInline(nested_admin.NestedTabularInline):
    """Inline for product gallery images with preview"""
    model = product_Gelery_images
    extra = 1
    fields = ('image', 'alt', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Preview'

class InnerGalleryImagesInline(nested_admin.NestedTabularInline):
    """Inline for inner product gallery images"""
    model = color_product_Gelery_images
    extra = 1
    fields = ('image', 'alt', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 4px;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Preview'

# -------------------------------
# Color & Variant Management
# -------------------------------



class ColorProductInline(ImportExportMixin,nested_admin.NestedStackedInline):
    """Inline for product colors with visual preview"""
    model = Color_product
    extra = 1
    inlines = [InnerGalleryImagesInline]
    fields = ('color', 'color_code', 'color_images', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        return format_html(
            '<div style="width:50px;height:50px;background-color:{};border:1px solid #ddd;"></div>',
            obj.color_code if obj.color_code else '#fff'
        ) if obj.color_code else "-"
    image_preview.short_description = 'Color Preview'

# -------------------------------
# Size Management
# -------------------------------

class SizePriceInline(nested_admin.NestedTabularInline):
    """Inline for size variations"""
    model = Size_price_par_post
    extra = 1
    fields = ('size',)
    verbose_name = "Available Size"
    verbose_name_plural = "Product Sizes"

# -------------------------------
# Main Product Admin

class Hightlight_for_productInline(nested_admin.NestedTabularInline):
    """Inline for Hightlight_for_product variations"""
    model = Hightlight_for_product
    
    extra = 1
    
# -------------------------------
class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = True


@admin.register(Product)
class ProductAdmin(ImportExportMixin,nested_admin.NestedModelAdmin):
    """Comprehensive product management with nested inlines"""
    form = ProductForm
    search_fields = ['product_name', 'b2c_price']
    list_filter = ['product_status','select_page', 'date', UserProductFilter]
    list_display = ('product_name','select_page','product_status','t_shirt_type', 'category','top_eight_products','total_sale_products','ratings', 'user', 'price_range', 'status_badge', 'date', 'image_preview')
    readonly_fields = ('uuid_product', 'product_slug', 'image_preview', 'date')
    autocomplete_fields = ['user', 'category']
    inlines = [Hightlight_for_productInline,SizePriceInline, ColorProductInline, GalleryImagesInline]
    list_per_page = 20
    list_editable = ('product_status','select_page')
    actions = ['make_published', 'make_draft']
    

    def status_badge(self, obj):
        color = '#2ecc71' if obj.product_status == 'Publish' else '#95a5a6'
        return format_html(
            '<span style="background-color:{};color:white;padding:3px 8px;border-radius:4px;">{}</span>',
            color, obj.get_product_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'product_status'

    def make_published(self, request, queryset):
        updated = queryset.update(product_status='Publish')
        self.message_user(request, f'{updated} products published successfully')
    make_published.short_description = "Mark selected products as Published"

    def make_draft(self, request, queryset):
        updated = queryset.update(product_status='Draft')
        self.message_user(request, f'{updated} products marked as Draft')
    make_draft.short_description = "Mark selected products as Draft"

    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 4px;"/>', obj.product_image.url) if obj.product_image else "-"
    image_preview.short_description = 'Thumbnail'


    def price_range(self, obj):
        try:
            b2b = int(obj.b2b_price) if obj.b2b_price else 0
            b2c = int(obj.b2c_price) if obj.b2c_price else 0
            return format_html('B2B: ₹{}<br>B2C: ₹{}', b2b, b2c)
        except (ValueError, TypeError):
            return format_html('<span style="color:red;">Invalid Price</span>')
    price_range.short_description = 'Pricing'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['user'].initial = request.user
            form.base_fields['user'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        """Ensure status is properly saved"""
        if 'product_status' in form.cleaned_data:
            obj.product_status = form.cleaned_data['product_status']
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return (not obj or obj.user == request.user or request.user.is_superuser) and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (not obj or obj.user == request.user or request.user.is_superuser) and super().has_delete_permission(request, obj)

# =============================================================================
# ORDER MANAGEMENT
# =============================================================================
class CustomNameNullFilter(SimpleListFilter):
    title = 'B2b and B2c'
    parameter_name = 'custom_name_null'

    def lookups(self, request, model_admin):
        return (
            ('B2B', 'B2B'),
            ('B2C', 'B2C'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'B2B':
            return queryset.exclude(custom_name__isnull=True).exclude(custom_name__exact='')
        if self.value() == 'B2C':
            return queryset.filter(models.Q(custom_name__isnull=True) | models.Q(custom_name__exact=''))
        return queryset
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order processing and tracking interface"""
    
    search_fields = ['user__username', 'product__product_name', 'order_id', 'transaction_id']
    list_filter = ['status',CustomNameNullFilter,'payment_status', 'payment_method', 'created_at']
    list_display = ('order_id', 'user', 'product', 'quantity', 'total_price', 'payment_status', 'colored_status', 'created_at')
    readonly_fields = ('order_id', 'transaction_id', 'transaction_order_id', 'created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📦 Order Information', {
            'fields': ('order_id', 'user', 'product', 'inner_color_product')
        }),
        ('👤 Customer Details', {
            'fields': ('custom_name', 'custom_email', 'custom_number', 'custom_design'),
            'classes': ('collapse',)
        }),
        ('💰 Order Details', {
            'fields': ('product_size', 'quantity', 'total_price', 'address', 'messag','awb_number','shipment_id','shipment_status')
        }),
        ('💳 Payment Information', {
            'fields': ('transaction_id', 'transaction_order_id', 'payment_status', 'payment_method')
        }),
        ('📊 Status', {
            'fields': ('status',)
        }),
        ('📅 Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    STATUS_COLORS = {
        'Ordered': '#3498db',
        'Shipped': '#f39c12',
        'Delivered': '#2ecc71',
        'Cancelled': '#e74c3c',
        'Return': '#9b59b6',
        'Refund': '#95a5a6',
    }

    def colored_status(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#000')
        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 3px 8px; border-radius: 4px; background-color: {}20;">{}</span>',
            color, color, obj.status
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

# =============================================================================
# CUSTOMER INTERACTIONS
# =============================================================================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Shopping cart monitoring"""
    
    search_fields = ['user__username', 'product__product_name']
    list_filter = ['date']
    list_display = ('user', 'product', 'quantity', 'size', 'date', 'total_price')
    readonly_fields = ('date',)
    list_select_related = True
    
    def total_price(self, obj):
        if obj.product:
            # Safely get the price or fallback to 0
            price = obj.product.b2b_price if obj.user.user_type == 'B2B' else obj.product.b2c_price
            price = price or 0  # Replace None with 0
            qty = obj.quantity or 0  # Replace None with 0
            total = int(qty) * int(price)
            return format_html('<strong>₹{}</strong>', total)
        return "₹0"

    total_price.short_description = 'Total'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Customer wishlist tracking"""
    
    search_fields = ['user__username', 'product__product_name']
    list_display = ('user', 'product', 'added_at')
    list_filter = ['added_at']
    readonly_fields = ('added_at',)

@admin.register(User_Reviews)
class UserReviewsAdmin(admin.ModelAdmin):
    """Product review moderation"""
    
    search_fields = ['user__username', 'product__product_name', 'name', 'email']
    list_filter = ['created_at', 'show', 'star']
    list_display = ('name', 'product', 'star_rating', 'show', 'created_at')
    readonly_fields = ('created_at',)
    list_editable = ('show',)
    
    def star_rating(self, obj):
        try:
            stars = int(obj.star) if obj.star is not None else 0
            stars = max(0, min(5, stars))
            return format_html(
                '<span title="{} star rating" style="color: gold; font-size: 1.1em;">{}</span>',
                stars,
                '★' * stars + '☆' * (5 - stars)
            )
        except (ValueError, TypeError):
            return format_html('<span style="color: red;" title="Invalid rating">⚠</span>')
    star_rating.short_description = 'Rating'
    star_rating.admin_order_field = 'star'

# =============================================================================
# CUSTOMER MANAGEMENT
# =============================================================================

@admin.register(Address_user)
class AddressUserAdmin(admin.ModelAdmin):
    """Customer address book"""
    
    search_fields = ['user__username', 'name', 'email', 'phone_numer', 'state']
    list_filter = ['state']
    list_display = ('user', 'name', 'state', 'phone_numer', 'created_at')
    readonly_fields = ('created_at',)

# =============================================================================
# COMMUNICATION
# =============================================================================

@admin.register(Contact_US)
class ContactUSAdmin(admin.ModelAdmin):
    """Customer contact messages"""
    
    search_fields = ['name', 'email', 'phone', 'message']
    list_filter = ['date']
    list_display = ('name', 'email', 'phone', 'date', 'truncated_message')
    readonly_fields = ('date',)
    
    def truncated_message(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    truncated_message.short_description = 'Message'

# =============================================================================
# CONTENT MANAGEMENT
# =============================================================================

@admin.register(Blog_post)
class BlogsAdminPost(admin.ModelAdmin):
    """Blog content management"""
    
    search_fields = ['meta_title', 'category__category', 'author']
    list_filter = ['date', 'category']
    list_display = ('meta_title', 'category', 'author', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Blog_Category)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Blog category organization"""
    
    list_display = ('category',)
    search_fields = ['category']

# =============================================================================
# REGISTER REMAINING MODELS
# =============================================================================

admin.site.register([
    Size_price_par_post, 
    product_Gelery_images, 
    color_product_Gelery_images
])
@admin.register(Color_product)
class ColorProductAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('color', 'color_code')

# =============================================================================
# ADMIN SITE CONFIGURATION
# =============================================================================

# =============================================================================
# MARKETING & CONTENT MODELS
# =============================================================================

@admin.register(A_plus_listing)
class APlusListingAdmin(admin.ModelAdmin):
    """Admin for A+ Listing content"""
    list_display = ('id', 'image_preview', 'image_alt_name')
    search_fields = ['image_alt_name']
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Preview'

@admin.register(Banners)
class BannersAdmin(admin.ModelAdmin):
    """Admin interface for managing banners"""
    list_display = ('id', 'image_preview', 'video_preview', 'image_alt_name', 'pages_display')
    list_filter = ['show_on_pages']
    search_fields = ['image_alt_name']
    readonly_fields = ('image_preview', 'video_preview')
    # Remove filter_horizontal as it's not for MultiSelectField
    
    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Image Preview'
    
    def video_preview(self, obj):
        return format_html('<video width="50" height="50" controls><source src="{}"></video>', obj.video.url) if obj.video else "-"
    video_preview.short_description = 'Video Preview'
    
    def pages_display(self, obj):
        return ", ".join(obj.show_on_pages)
    pages_display.short_description = 'Shown On Pages'

@admin.register(Testimoninal)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for customer testimonials"""
    list_display = ('name', 'company_name', 'image_preview', 'date', 'truncated_content')
    search_fields = ['name', 'company_name', 'content']
    list_filter = ['date']
    readonly_fields = ('image_preview', 'date')
    
    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Image'
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'

@admin.register(Our_trusted_client)
class OurTrustedClientAdmin(admin.ModelAdmin):
    """Admin for trusted client logos"""
    list_display = ('id', 'image_preview', 'image_alt_name')
    search_fields = ['image_alt_name']
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;"/>', obj.image.url) if obj.image else "-"
    image_preview.short_description = 'Logo'

@admin.register(Leave_checkout_page_billing_details)
class LeaveCheckoutBillingAdmin(admin.ModelAdmin):
    """Admin for abandoned checkout data"""
    list_display = ('email', 'full_name', 'phone', 'city', 'date')
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'city']
    list_filter = ['date', 'country', 'city']
    readonly_fields = ('date',)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
# admin.site.register(A_plus_listing)
admin.site.site_header = "E-Commerce Admin Dashboard"
admin.site.site_title = "E-Commerce Administration"
admin.site.index_title = "Welcome to E-Commerce Portal"

admin.site.register(Chatbot_users)
admin.site.register(Insta_images)
admin.site.register(Product_sub_category)
admin.site.register(sub_category_coordinator)
admin.site.register(Return_and_Cancel_products)
admin.site.register(HomePageEditor)