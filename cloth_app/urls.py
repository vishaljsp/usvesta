from django.urls import path, re_path, include
from django.conf import settings
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from .views import *
from .api import ProductSyncAPIView
urlpatterns = [
    path('api/v1/products/', ProductSyncAPIView.as_view(), name='api_product_sync'),

    path('',Home.as_view(),name="home"),
    path('track-order', RedirectView.as_view(url='/profile?tab=orders', permanent=False), name='track-order'),
    path('track-order/', RedirectView.as_view(url='/profile?tab=orders', permanent=False), name='track-order-slash'),
    path('our-story',About_us.as_view(),name="about-us"),
    path('shop',Shop.as_view(),name="home"),
    path('products/<slug>',Product_details.as_view(),name="product"),
    path('blogs/<slug>',blogs_details.as_view(),name="blogs"),
    path('contact-us',ContactUs.as_view(),name="contact-us"),
    path('profile',login_required(Profile.as_view()),name="profile"),
    path('3d-custom-design',login_required(Make_design.as_view()),name="3d-custom-design'"),
    path('bhaarat-kshetram',Bhaaratkshetram.as_view(),name="Bhaaratkshetram"),

    path('3d-custom-design-polo-tshirt',login_required(Make_design_polo.as_view()),name="3d-custom-design'"),
    path('logout',Logout.as_view(),name="logout"),
    path('blog',Blogs_post.as_view(),name="blog"),
    path('for-corporates',B2b.as_view(),name="b2b"),
    path('login-register',Register_and_login.as_view(),name="login-register"),
    path('add-to-cart',Add_Cart.as_view(),name="cart"),
    path('add-to-cart_inner',Inner_product_cart.as_view(),name="cart"),
    path('privacy-policy',Privacy_police.as_view(),name="Privacy_police"),
    path('terms-&-conditionst',Turmscunditions.as_view(),name="Turmscunditions"),
    path('shipping-&-delivery-policy',Shipping.as_view(),name="shipping-&-delivery-policy"),
    path('return-&-refund-policy',Returnrefund.as_view(),name="return-&-refund-policy"),
    path('cancellation-policy',Cancellationpolicy.as_view(),name="cancellation-policy"),
    path('payment-policy',Paymentpolicy.as_view(),name="payment-policy"),
    path('wish-list',Wish_list.as_view(),name="wishlist"),
    path('cookies',Cookies.as_view(),name="cookies"),
    path('customer-orders',Web_ouwner.as_view(),name="customer-orders"),
    path('customer-orders/',Web_ouwner.as_view(),name="customer-orders-slash"),
    path('thank-you',Thenkyou.as_view(),name="thank-you"),
    
    path('checkout',login_required(Checkout.as_view()),name="checkout"),
    path('reset-passsword/<str:email_token_url>',Reset_password.as_view(),name="Reset_password"),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('payment/success/', Payment_success.as_view(), name='payment_success'),
    path("Chat_boat_urls_saveing_data",Chat_boat.as_view(),name="chat"),
    path("category",CategoryB2b.as_view(),name="category"),
    path("get-cart-data",get_cart_data,name="get_cart_data"),
    path("collections/<slug:slug>/", Collections_for_men.as_view(), name="collections-t-shirts-for-men"),
    path("t-shirts-for-men", Tshirtcategory.as_view(), name="t-shirts-for-men"),

    path("usvesta-deshboard",login_required(Dahsboardview.as_view()),name="usvesta-deshboard"),
    path("usvesta-deshboard/",login_required(Dahsboardview.as_view()),name="usvesta-deshboard-slash"),
    path("usvesta-deshboard-veriant",login_required(color_django_verint.as_view()),name="usvesta-deshboard-veriant"),
    
    path("usvesta-deshboard/update-product/<slug>",login_required(Update_product.as_view()),name="usvesta-deshboard-update"),
    path("usvesta-deshboard-sending_databdbjajnsjansJnj",login_required(update_dashboard_form_etc_data.as_view()),name="usvesta-deshboard-sending_databdbjajnsjansJnj"),
    path("ordermodel_popup",ordermodel_popup.as_view(),name="ordermodel_popup"),
    path('product-feed.xml', product_feed_xml, name='product_feed_xml'),
    path('llms.txt', Llmsfile_for_ai, name='Llmsfile_for_ai'),
    path('upload-bulk-order',Upload_pd_in_bulk.as_view(), name='upload-bulk-order'),
    path("generate-fake-reviews",GenerateFakeReviewsView.as_view(),name="generate_fake_reviews"),
    path('create-cashfree-order',create_cashfree_order.as_view(),name="create-cashfree-order"),
    path('create-veno-order',create_veno_order.as_view(),name="create-veno-order"),
     
    path('retun_request_cancel_requ',Retun_and_cancel.as_view(), name='retun_request_cancel_requ'),
    path('order-details/<uuid:uu_id>', Order_details_pg.as_view())
] 

# handler404 = Hendling404.as_view()
# handler500 = Hendling500.as_view()

handler404 = 'cloth_app.views.error_404'
handler500 = 'cloth_app.views.error_500'