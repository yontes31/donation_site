from django import forms
from .models import DonationCategory, Posts

class CreatePosts(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'content', 'image']

class DonationForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=DonationCategory.objects.all(),
        label="מה תרצי לתרום?"
    )
    radius = forms.IntegerField(
        label='מהו רדיוס התרומה (בקילומטרים)?',
        min_value=1,
        max_value=100,
    )
    address = forms.CharField(
        label='איפה את גרה?',
        widget=forms.TextInput(attrs={'placeholder': 'כתובת מגורים'}),
    )