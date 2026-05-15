"""
Rapor filtreleme formu.

Tarih aralığı ve tarla seçimi ile rapor oluşturma formu.
"""

from django import forms

from apps.fields.models import Field


class ReportFilterForm(forms.Form):
    """Rapor filtre formu — tarih aralığı ve tarla seçimi."""

    field = forms.ModelChoiceField(
        queryset=Field.objects.none(),
        required=False,
        empty_label='Tüm Tarlalar',
        label='Tarla',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date_from = forms.DateField(
        required=False,
        label='Başlangıç Tarihi',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
    )
    date_to = forms.DateField(
        required=False,
        label='Bitiş Tarihi',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
    )

    def __init__(self, user, *args, **kwargs):
        """Formda sadece kullanıcının tarlalarını göster."""
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = Field.objects.filter(user=user)
