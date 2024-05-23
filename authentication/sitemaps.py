from django.contrib.sitemaps import Sitemap
from .models import Blog

class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Blog.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # Ensure your Blog model has an updated_at field

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return ['home']  # Add your static views here

    def location(self, item):
        return reverse(item)