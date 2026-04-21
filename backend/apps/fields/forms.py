"""
Fields forms — Tarla oluşturma ve güncelleme formları.
"""

from django import forms

from .models import Field


class FieldForm(forms.ModelForm):
    """Tarla ekleme/düzenleme formu."""

    class Meta:
        model = Field
        fields = ('name', 'location', 'area_decar', 'soil_type')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tarla adı'}),
            'location': forms.TextInput(attrs={'placeholder': 'Konum (il/ilçe)'}),
            'area_decar': forms.NumberInput(attrs={'placeholder': 'Alan (dekar)', 'step': '0.01'}),
        }
