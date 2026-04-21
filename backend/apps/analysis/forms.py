"""
Analysis forms — Toprak analizi giriş formu.
"""

from django import forms

from .models import SoilAnalysis


class SoilAnalysisForm(forms.ModelForm):
    """Manuel toprak analizi giriş formu."""

    class Meta:
        model = SoilAnalysis
        fields = ('nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall')
        widgets = {
            'nitrogen': forms.NumberInput(attrs={'placeholder': 'Azot (N)', 'step': '0.01', 'min': '0', 'max': '200'}),
            'phosphorus': forms.NumberInput(attrs={'placeholder': 'Fosfor (P)', 'step': '0.01', 'min': '0', 'max': '200'}),
            'potassium': forms.NumberInput(attrs={'placeholder': 'Potasyum (K)', 'step': '0.01', 'min': '0', 'max': '300'}),
            'temperature': forms.NumberInput(attrs={'placeholder': 'Sıcaklık °C', 'step': '0.1', 'min': '-10', 'max': '50'}),
            'humidity': forms.NumberInput(attrs={'placeholder': 'Nem %', 'step': '0.1', 'min': '0', 'max': '100'}),
            'ph': forms.NumberInput(attrs={'placeholder': 'pH', 'step': '0.01', 'min': '0', 'max': '14'}),
            'rainfall': forms.NumberInput(attrs={'placeholder': 'Yağış mm', 'step': '0.1', 'min': '0', 'max': '2000'}),
        }
