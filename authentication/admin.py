from django.contrib import admin
from .models import Pick,Paid,NFLPlayer,Game,PastPick,Scorer,BaseballPlayer,PromoCode,PromoUser,OfAge,UserVerification, Blog, ChatMessage
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms

class BlogAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Blog
        fields = '__all__'

class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm


class NFLPlayerAdmin(admin.ModelAdmin):
    search_fields = ['name','team_name']

admin.site.register(Pick)
admin.site.register(Paid)
admin.site.register(NFLPlayer, NFLPlayerAdmin)
admin.site.register(Game)
admin.site.register(PastPick)
admin.site.register(Scorer)
admin.site.register(BaseballPlayer)
admin.site.register(PromoCode)
admin.site.register(PromoUser)
admin.site.register(OfAge)
admin.site.register(UserVerification)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ChatMessage)