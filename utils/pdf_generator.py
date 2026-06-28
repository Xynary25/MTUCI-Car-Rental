from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
import os

# Глобальная переменная для зарегистрированного шрифта
REGISTERED_FONT = None


def register_fonts():
    """Регистрация шрифтов с поддержкой кириллицы."""
    global REGISTERED_FONT
    if REGISTERED_FONT:
        return REGISTERED_FONT

    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/times.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('CyrillicFont', path))
                REGISTERED_FONT = 'CyrillicFont'
                return REGISTERED_FONT
            except Exception as e:
                print(f"Не удалось зарегистрировать шрифт {path}: {e}")
                continue
    REGISTERED_FONT = 'Helvetica'
    return REGISTERED_FONT


def generate_agreement_pdf(agreement_data: dict, penalties: list = None, filepath: str = None):
    """
    Генерация PDF для одного договора аренды с учетом штрафов.

    Args:
        agreement_data: Словарь с данными договора
        penalties: Список штрафов (может быть None)
        filepath: Путь для сохранения PDF
    """
    return generate_multiple_agreements_pdf([agreement_data], [penalties] if penalties else [[]], filepath)


def generate_multiple_agreements_pdf(agreements_list: list, penalties_list: list = None, filepath: str = None):
    """
    Генерация PDF для одного или нескольких договоров.

    Args:
        agreements_list: Список словарей с данными договоров
        penalties_list: Список списков штрафов для каждого договора (опционально)
        filepath: Путь для сохранения PDF
    """
    try:
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=1.5 * cm, leftMargin=1.5 * cm,
                                topMargin=1.5 * cm, bottomMargin=1.5 * cm)
        styles = getSampleStyleSheet()
        font_name = register_fonts()

        title_style = ParagraphStyle(
            'TitleCyr',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=14,
            alignment=1,
            spaceAfter=12,
            leading=16
        )

        heading_style = ParagraphStyle(
            'HeadingCyr',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=11,
            spaceAfter=8,
            spaceBefore=10,
            leading=13
        )

        body_style = ParagraphStyle(
            'BodyCyr',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=12,
            spaceAfter=4
        )

        # Стиль для текста в ячейках таблицы
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=11,
            spaceAfter=0,
            spaceBefore=0
        )

        # Стиль для заголовков ячеек таблицы
        header_cell_style = ParagraphStyle(
            'HeaderCellStyle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=1,
            spaceAfter=0,
            spaceBefore=0
        )

        story = []

        for idx, agreement_data in enumerate(agreements_list):
            if idx > 0:
                story.append(PageBreak())

            # Заголовок
            story.append(Paragraph("ДОГОВОР АРЕНДЫ ЛЕГКОВОГО АВТОМОБИЛЯ", title_style))
            story.append(Spacer(1, 0.8 * cm))

            # Номер и дата
            agreement_id = agreement_data.get('id', 'N/A')
            agreement_date = agreement_data.get('start_date', '')
            story.append(Paragraph(f"<b>Договор № {agreement_id}</b> от {agreement_date}", body_style))
            story.append(Spacer(1, 0.4 * cm))

            # Основная информация
            story.append(Paragraph("<b>ИНФОРМАЦИЯ О ДОГОВОРЕ</b>", heading_style))

            client_name = agreement_data.get('client_name', 'Не указан')
            car_info = agreement_data.get('car_info', 'Не указан')
            start_date = agreement_data.get('start_date', '')
            end_date = agreement_data.get('end_date', '')
            base_cost = agreement_data.get('total_cost', 0)

            story.append(Paragraph(f"<b>Арендатор:</b> {client_name}", body_style))
            story.append(Paragraph(f"<b>Автомобиль:</b> {car_info}", body_style))
            story.append(Paragraph(f"<b>Срок аренды:</b> с {start_date} по {end_date}", body_style))
            story.append(Paragraph(f"<b>Стоимость аренды:</b> {base_cost} руб.", body_style))
            story.append(Spacer(1, 0.3 * cm))

            # Штрафы (если есть)
            total_penalties = 0
            total_paid_penalties = 0
            total_unpaid_penalties = 0
            penalties = None

            if penalties_list and idx < len(penalties_list):
                penalties = penalties_list[idx]

            if penalties and len(penalties) > 0:
                story.append(Paragraph("<b>ШТРАФЫ И ДОПОЛНИТЕЛЬНЫЕ ПЛАТЕЖИ</b>", heading_style))
                story.append(Spacer(1, 0.2 * cm))

                # используем Table вместо HTML
                # Ширина таблицы: 17см (A4 - отступы)
                # Колонки: №(0.8), Тип(2.8), Описание(6.5), Сумма(2.2), Статус(2.2)
                col_widths = [0.8 * cm, 2.8 * cm, 6.5 * cm, 2.2 * cm, 2.2 * cm]

                # Заголовки таблицы
                table_data = [[
                    Paragraph('№', header_cell_style),
                    Paragraph('Тип', header_cell_style),
                    Paragraph('Описание', header_cell_style),
                    Paragraph('Сумма (руб.)', header_cell_style),
                    Paragraph('Статус', header_cell_style)
                ]]

                for p_idx, penalty in enumerate(penalties, 1):
                    penalty_type = penalty.get('penalty_type', 'Не указан') if isinstance(penalty, dict) else str(
                        penalty)
                    description = penalty.get('description', '') if isinstance(penalty, dict) else ''
                    amount = penalty.get('amount', 0) if isinstance(penalty, dict) else 0

                    # Корректная проверка статуса
                    is_paid = penalty.get('is_paid', False) if isinstance(penalty, dict) else False
                    status = penalty.get('status', '') if isinstance(penalty, dict) else ''

                    total_penalties += amount

                    # Определяем статус
                    if is_paid or status == 'Оплачен' or status == 'PAID':
                        total_paid_penalties += amount
                        status_text = "Оплачен"
                    elif status == 'Отменён' or status == 'CANCELLED':
                        status_text = "Отменён"
                    else:
                        total_unpaid_penalties += amount
                        status_text = "Не оплачен"

                    # Добавляем строку в таблицу с Paragraph для корректного переноса
                    table_data.append([
                        Paragraph(str(p_idx), cell_style),
                        Paragraph(penalty_type, cell_style),
                        Paragraph(description, cell_style),
                        Paragraph(str(amount), cell_style),
                        Paragraph(status_text, cell_style)
                    ])

                # Создаем таблицу
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    # ШРИФТ ДЛЯ ВСЕЙ ТАБЛИЦЫ
                    ('FONTNAME', (0, 0), (-1, -1), font_name),

                    # Шапка таблицы
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('LEFTPADDING', (0, 0), (-1, 0), 4),
                    ('RIGHTPADDING', (0, 0), (-1, 0), 4),

                    # Данные
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF3C7')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1E293B')),
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Номер по центру
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Сумма по правому краю
                    ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Статус по центру
                    ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                    ('LEFTPADDING', (0, 1), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 1), (-1, -1), 4),

                    # Сетка
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94A3B8')),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#334155')),
                ]))

                story.append(table)
                story.append(Spacer(1, 0.4 * cm))

                # Итого штрафов с разбивкой
                story.append(Paragraph(f"<b>Итого штрафов:</b> {total_penalties} руб.", body_style))
                if total_paid_penalties > 0:
                    story.append(Paragraph(f"Оплачено: {total_paid_penalties} руб.", body_style))
                if total_unpaid_penalties > 0:
                    story.append(
                        Paragraph(f"<b>В том числе неоплаченных: {total_unpaid_penalties} руб.</b>", body_style))
                story.append(Spacer(1, 0.5 * cm))

            # Итоговая сумма - ТОЛЬКО С НЕОПЛАЧЕННЫМИ ШТРАФАМИ
            total_amount = base_cost + total_unpaid_penalties
            story.append(Paragraph("<b>ИТОГОВАЯ СТОИМОСТЬ</b>", heading_style))
            story.append(Paragraph(f"<b>Общая сумма к оплате:</b> {total_amount} руб.", body_style))
            if total_penalties > 0:
                story.append(
                    Paragraph(f"(в т.ч. аренда: {base_cost} руб., все штрафы: {total_penalties} руб.)", body_style))
                if total_unpaid_penalties > 0:
                    story.append(
                        Paragraph(f"<b>Из них к оплате (неоплаченные штрафы): {total_unpaid_penalties} руб.</b>",
                                  body_style))
                if total_paid_penalties > 0:
                    story.append(Paragraph(f"Оплачено ранее: {total_paid_penalties} руб.", body_style))

            story.append(Spacer(1, 0.8 * cm))

            # Подписи
            story.append(Paragraph("<b>ПОДПИСИ СТОРОН</b>", heading_style))
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Арендодатель: _______________ / _______________", body_style))
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph("Арендатор: _______________ / _______________", body_style))

        # Создаём PDF
        doc.build(story)
        return {"success": True}

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка генерации PDF: {error_details}")
        return {"success": False, "error": str(e)}