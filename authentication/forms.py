from django import forms
from .models import Pick

class PlayerSearchForm(forms.Form):
    player_name = forms.CharField(label='Player Name', max_length=100)
    # Define other form fields if needed

class Pickform(forms.ModelForm):
    class Meta:
        model = Pick
        fields = ['team_name','isin','pick']

class Pick1Form(forms.ModelForm):
    class Meta:
        model = Pick
        fields = ['pick']
    #def __init__(self,*args,**kwargs):
    #super(Pick1Form, self).__init__(*args,**kwargs)

class CreateTeam(forms.ModelForm):
    class Meta:
        model = Pick
        fields = ['team_name']
