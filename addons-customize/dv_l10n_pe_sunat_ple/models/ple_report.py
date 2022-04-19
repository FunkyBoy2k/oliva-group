# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

#import base64
from base64 import b64decode, b64encode
import datetime
from io import StringIO, BytesIO
import xlsxwriter
import platform
import logging
_logging = logging.getLogger(__name__)


DEFAULT_PLE_DATA = '%(month)s%(day)s%(ple_id)s%(report_03)s%(operacion)s%(contenido)s%(moneda)s%(ple)s'
DEFAULT_FORMAT_DICT = {
    'header_format': {
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1,
    },
    'text_format': {
        'num_format': '@',
    },
}


def get_last_day(day):
    first_next = day.replace(day=28) + datetime.timedelta(days=4)
    return (first_next - datetime.timedelta(days=first_next.day))


def fill_name_data(name_dict):
    common_data = {
        'month': '00',
        'day': '00',
        'report_03': '00',
        'operacion': '1',
        'contenido': '1',
        'moneda': '1',
        'ple': '1',
    }
    common_data_keys = list(common_data)
    for name in common_data_keys:
        if name in name_dict:
            del common_data[name]
    name_dict.update(common_data)


def number_to_ascii_chr(n):
    try:
        n = int(n)
    except:
        _logging.info('error en lineaaaaaaaaaaaaaa 52')
        n = 0
    digits = []
    if n > 0:
        while n:
            digits.append(int(n % 26))
            n //= 26
    else:
        digits.append(0)
    digits = ''.join(chr(numero+65) for numero in digits[::-1])
    return digits


class PLEReportTempl(models.Model):
    _name = 'ple.report.templ'
    _description = 'Plantilla para Estructuras del PLE'

    @api.model
    def _get_default_date(self):
        date = fields.Date.context_today(self)
        return date

    @api.model
    def _get_default_year(self):
        year = self._get_default_date().year
        return year

    @api.model
    def _get_default_month(self):
        month = str(self._get_default_date().month)
        return month

    @api.model
    def _get_default_day(self):
        day = self._get_default_date().day
        return day

    ple_txt_01 = fields.Text(string='Contenido del TXT')
    ple_txt_01_binary = fields.Binary(string='TXT', readonly=True)
    ple_txt_01_filename = fields.Char(string='Nombre del TXT')
    ple_xls_01_binary = fields.Binary(string='Excel', readonly=True)
    ple_xls_01_filename = fields.Char(string='Nombre del Excel')
    year = fields.Integer(
        string='Año', default=lambda self: self._get_default_year())
    year_char = fields.Char(string='Año (texto)', compute='_compute_year_char')

    month = fields.Selection(
        string='Mes', selection=[
            ('1', 'Enero'),
            ('2', 'Febrero'),
            ('3', 'Marzo'),
            ('4', 'Abril'),
            ('5', 'Mayo'),
            ('6', 'Junio'),
            ('7', 'Julio'),
            ('8', 'Agosto'),
            ('9', 'Setiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ],
        default=lambda self: self._get_default_month(),
    )
    # implement dynamic
    day = fields.Integer(
        string='Día', default=lambda self: self._get_default_day())
    date = fields.Date(string='Fecha', compute='_compute_date',
                       default=lambda self: self._get_default_date(), store=True, readonly=True)
    date_generated = fields.Datetime(
        string='Fecha de generación', readonly=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía',
                                 required=True, default=lambda self: self.env.user.company_id)

    @api.onchange('year', 'month', 'day')
    def _onchange_dates(self):
        year = self.year
        today = self._get_default_date()
        if self.year <= 0:
            self.year = today.year
        else:
            month = self.month
            if not self.month:
                self.month = str(today.month)
            else:
                end = get_last_day(datetime.date(year, int(month), 1))
                day = self.day
                if day < 1:
                    self.day = 1
                elif day > end.day:
                    self.day = end.day

    @api.depends('year', 'month', 'day')
    def _compute_days(self):
        for record in self:
            record._onchange_dates()

    @api.depends('year', 'month', 'day')
    def _compute_date(self):
        default_date = self._get_default_date()
        for record in self:
            year = record.year
            month = record.month
            day = record.day
            if (year > 0) and month and (day > 0):
                date = datetime.date(year, int(month), 1)
                record.date = date + datetime.timedelta(days=day-1)
            else:
                record.date = default_date

    def convert_field_to_string(self,field):
        if field:
            field_str = str(field)
        else:
            field_str = ''
        return field_str
    
    def _generate_xlsx_base64_bytes(self, row_values_array, sheet_name, headers=[], custom_format_dict=dict()):
        if platform.system() == 'Linux':
            filename = ('/tmp/ple_report' + '.xlsx')
        else:
            filename = ('ple_report' + '.xlsx')
            
        workbook = xlsxwriter.Workbook(filename)
        sheet = workbook.add_worksheet(sheet_name)
        #sheet = self.write_report_format_header(sheet,sheet_name)
        column = 0
        for head in headers:
            sheet.write(0, column , head)
            column += 1
        row = 1
        for row_value in row_values_array:
            column = 0
            for field in row_value.split('|'):
                field = self.convert_field_to_string(field)
                sheet.write(row, column, field)
                column += 1
            row += 1
            
        workbook.close()
        fp = open(filename, "rb")
        file_data = fp.read()
        xlsx_file_value = b64encode(file_data).decode()
        return xlsx_file_value
   
    @api.depends('year')
    def _compute_year_char(self):
        for record in self:
            record.year_char = str(record.year)

    def get_default_filename(self):
        self.ensure_one()
        name = 'LE' + str(self.company_id.vat) + \
            str(self.year) + DEFAULT_PLE_DATA
        return name

    def update_report(self):
        self.ensure_one()
        res = True
        return res

    def generate_report(self):
        res = self.update_report()
        return res
    """
    def _generate_xlsx_base64_bytes(self, txt_string, sheet_name, headers=[], custom_format_dict=dict()):
        xlsx_file = BytesIO()
        xlsx_writer = ExcelWriter(xlsx_file, engine='xlsxwriter')
        df = read_csv(StringIO(txt_string), sep='|', header=None, dtype=str)
        df.to_excel(xlsx_writer, sheet_name, startrow=1,
                    index=False, header=False)
        workbook = xlsx_writer.book
        worksheet = xlsx_writer.sheets[sheet_name]
        format_dict = {k: workbook.add_format(
            v) for k, v in DEFAULT_FORMAT_DICT.items()}
        if custom_format_dict and isinstance(custom_format_dict, dict()):
            for custom_format, custom_format_value in custom_format_dict.items():
                format_dict.update({
                    custom_format: workbook.add_format(custom_format_value),
                })
        len_headers = 0
        if headers and isinstance(headers, list):
            len_headers = len(headers)
        for col_num, value in enumerate(df.columns.values):
            col_name = number_to_ascii_chr(col_num)
            header_text = str(value)
            col_format = 'text_format'
            if len_headers:
                if col_num < len_headers:
                    csv_file = headers[col_num]
                    #csv_file = 'Header' or {'header_text': 'Header', 'col_format': 'format_name'}
                    if not isinstance(csv_file, dict):
                        csv_file = {'header_text': str(csv_file)}
                    if 'header_text' in csv_file:
                        header_text = str(csv_file.get('header_text'))
                    if 'col_format' in csv_file:
                        col_format = str(csv_file.get('col_format'))
            if col_format not in format_dict:
                col_format = 'text_format'
            col_format = format_dict.get(col_format)
            csv_file = worksheet.write(
                0, col_num, header_text, format_dict.get('header_format'))
            csv_file = worksheet.set_column(':'.join([col_name, col_name]), max(
                25, len(header_text) // 2), col_format)
        xlsx_writer.save()
        xlsx_file_value = b64encode(xlsx_file.getvalue()).decode()
        return xlsx_file_value
    """