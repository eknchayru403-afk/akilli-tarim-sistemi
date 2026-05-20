"""
Rapor filtreleme formu.

Rapor tipi, tarih aralığı, tarla seçimi ve export formatı.
"""

from django import forms

from apps.fields.models import Field


REPORT_TYPE_CHOICES = [
    ('general', 'Genel Rapor'),
    ('irrigation', 'Sulama Raporu'),
    ('fertilization', 'Gübreleme Raporu'),
    ('yield', 'Verim Analizi'),
    ('sensor', 'Sensör Özeti'),
]

EXPORT_FORMAT_CHOICES = [
    ('pdf', 'PDF'),
    ('excel', 'Excel (.xlsx)'),
    ('csv', 'CSV'),
]


class ReportFilterForm(forms.Form):
    """Rapor filtre formu — rapor tipi, tarih aralığı, tarla ve format seçimi."""

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        initial='general',
        label='Rapor Tipi',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
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
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMAT_CHOICES,
        initial='pdf',
        label='İndirme Formatı',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, user, *args, **kwargs):
        """Formda sadece kullanıcının tarlalarını göster."""
        super().__init__(*args, **kwargs)
        self.fields['field'].queryset = Field.objects.filter(user=user)
