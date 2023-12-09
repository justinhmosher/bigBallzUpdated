from django import forms

class PlayerSearchForm(forms.Form):
    player_name = forms.CharField(label='Player Name', max_length=100)
    # Define other form fields if needed
