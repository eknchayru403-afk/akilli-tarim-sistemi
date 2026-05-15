"""
Rapor views — PDF ve Excel indirme ve onizleme.
"""
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .forms import ReportFilterForm
from .services import ReportService
from .generators.pdf_generator import generate_pdf_report
from .generators.excel_generator import generate_excel_report

logger = logging.getLogger(__name__)


@login_required
def report_index(request):
    """Rapor olusturma formu sayfasi."""
    form = ReportFilterForm(request.user, request.GET or None)
    return render(request, 'reports/index.html', {'form': form})


@login_required
def download_pdf(request):
    """PDF rapor indir."""
    form = ReportFilterForm(request.user, request.GET)
    field_id = None
    date_from = None
    date_to = None

    if form.is_valid():
        field = form.cleaned_data.get('field')
        field_id = field.id if field else None
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

    report_data = ReportService.get_report_data(
        user=request.user,
        field_id=field_id,
        date_from=date_from,
        date_to=date_to,
    )

    pdf_buffer = generate_pdf_report(report_data)

    response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ATYS_Tarimsal_Rapor.pdf"'
    logger.info("PDF rapor indirildi: user=%s", request.user)
    return response


@login_required
def download_excel(request):
    """Excel rapor indir."""
    form = ReportFilterForm(request.user, request.GET)
    field_id = None
    date_from = None
    date_to = None

    if form.is_valid():
        field = form.cleaned_data.get('field')
        field_id = field.id if field else None
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

    report_data = ReportService.get_report_data(
        user=request.user,
        field_id=field_id,
        date_from=date_from,
        date_to=date_to,
    )

    excel_buffer = generate_excel_report(report_data)

    response = HttpResponse(
        excel_buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="ATYS_Tarimsal_Rapor.xlsx"'
    logger.info("Excel rapor indirildi: user=%s", request.user)
    return response
