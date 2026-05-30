"""
Rapor views — PDF, Excel ve CSV indirme ve önizleme.
"""
import logging
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .forms import ReportFilterForm
from .services import ReportService
from .generators.pdf_generator import generate_pdf_report
from .generators.excel_generator import generate_excel_report
from .generators.csv_generator import generate_csv_report

logger = logging.getLogger(__name__)


@login_required
def report_index(request):
    """Rapor olusturma formu sayfasi."""
    form = ReportFilterForm(request.user, request.GET or None)
    return render(request, 'reports/index.html', {'form': form})


@login_required
def download_report(request):
    """Filtrelere gore raporu belirtilen formatta indir."""
    form = ReportFilterForm(request.user, request.GET)
    field_id = None
    date_from = None
    date_to = None
    report_type = 'general'
    export_format = 'pdf'

    if form.is_valid():
        field = form.cleaned_data.get('field')
        field_id = field.id if field else None
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        report_type = form.cleaned_data.get('report_type', 'general')
        export_format = form.cleaned_data.get('export_format', 'pdf')
    else:
        # Fallback to request parameters directly
        field_id = request.GET.get('field')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        report_type = request.GET.get('report_type', 'general')
        export_format = request.GET.get('export_format', 'pdf')

        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if date_to_str:
            try:
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if field_id:
            try:
                field_id = int(field_id)
            except ValueError:
                field_id = None

    report_data = ReportService.get_report_data(
        user=request.user,
        field_id=field_id,
        date_from=date_from,
        date_to=date_to,
        report_type=report_type,
    )

    filename_prefix = {
        'general': 'Genel_Rapor',
        'irrigation': 'Sulama_Raporu',
        'fertilization': 'Gubreleme_Raporu',
        'yield': 'Verim_Analizi',
        'sensor': 'Sensor_Ozeti',
    }.get(report_type, 'Tarimsal_Rapor')

    if export_format == 'pdf':
        pdf_buffer = generate_pdf_report(report_data)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ATYS_{filename_prefix}.pdf"'
        logger.info("PDF rapor indirildi: user=%s, type=%s", request.user, report_type)
        return response

    elif export_format == 'excel':
        excel_buffer = generate_excel_report(report_data)
        response = HttpResponse(
            excel_buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="ATYS_{filename_prefix}.xlsx"'
        logger.info("Excel rapor indirildi: user=%s, type=%s", request.user, report_type)
        return response

    elif export_format == 'csv':
        csv_buffer = generate_csv_report(report_data)
        response = HttpResponse(csv_buffer.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ATYS_{filename_prefix}.csv"'
        logger.info("CSV rapor indirildi: user=%s, type=%s", request.user, report_type)
        return response

    return HttpResponse("Gecersiz format", status=400)


@login_required
def report_preview(request):
    """Rapor onizleme verisini JSON olarak doner (Arayuzde dinamik yukleme icin)."""
    field_id = request.GET.get('field')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    report_type = request.GET.get('report_type', 'general')

    date_from = None
    date_to = None

    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if field_id:
        try:
            field_id = int(field_id)
        except ValueError:
            field_id = None

    report_data = ReportService.get_report_data(
        user=request.user,
        field_id=field_id,
        date_from=date_from,
        date_to=date_to,
        report_type=report_type,
    )
    return JsonResponse(report_data)
