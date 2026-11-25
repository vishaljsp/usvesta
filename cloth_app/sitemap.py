from typing import Union
from django.contrib.sitemaps import Sitemap
from . models import *
from . import views
class TodoSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return [
            "/",
            "/shop",
            "/3d-custom-design",
            "/blog",
            "/for-corporates",
            "/contact-us",
            "/t-shirts-for-men",
            "/our-story",
            "/terms-&-conditions",
            "/cookies",
            "/payment-policy",
            "/cancellation-policy",
            "/return-&-refund-policy",
            "/shipping-&-delivery-policy",
            "/privacy-policy",
        ]

    def location(self, item):
        return item

class TodoSitemap001(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(product_status="Publish").exclude(uuid_product__isnull=True).exclude(uuid_product='').exclude(uuid_product='None')

    def lastmod(self, obj):
        return obj.date
    
class TodoSitemap003(Sitemap):
    changefreq ="daily"
    priority=0.9

    def items(self):
        return Blog_post.objects.all()

    def lastmod(self,obj):
        return obj.date
    
    
class TodoSitemap004(Sitemap):
    changefreq ="daily"
    priority=0.9

    def items(self):
        a=Product_sub_category.objects.all()
        return a

    def lastmod(self,obj):
        return obj.date


class TodoSitemap005(Sitemap):
    changefreq ="daily"
    priority=0.9

    def items(self):
        a=Product_category.objects.all()
        return a

    def lastmod(self,obj):
        return obj.date