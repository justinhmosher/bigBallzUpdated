from django.contrib.sitemaps import Sitemap
from .models import Blog
from django.urls import reverse

class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Blog.objects.all().order_by('-updated_at')  # Ordering by updated_at field

    def lastmod(self, obj):
        return obj.updated_at

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return ['home']  # Add your static views here

    def location(self, item):
        return reverse(item)