from .models import ReceivedMessage
from django import forms

class ReceivedMessageForm(forms.ModelForm):
    class Meta:
        model = ReceivedMessage
