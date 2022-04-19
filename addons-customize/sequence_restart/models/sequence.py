from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    monthly_date_range = fields.Boolean(
        string='Crear periodos mensuales automáticos'
    )

    @api.onchange('use_date_range')
    def onchange_monthly_date_range(self):
        self.monthly_date_range = False

    def get_last_day_str(self, date):
        new_date = datetime.strptime(date, '%Y-%m-%d') + relativedelta(day=31)
        return new_date.strftime('%Y-%m-%d')

    def str_to_date(self, date):
        if isinstance(date, str):
            new_date = datetime.strptime(date, '%Y-%m-%d')
            return new_date.date()
        return date

    def _create_date_range_seq(self, date):
        if self.monthly_date_range:
            year = fields.Date.from_string(date).strftime('%Y')
            date_from = '{}-01-01'.format(year)
            date_to = self.get_last_day_str(date_from)
            flag = False
            seq_date_range = False
            while not flag:
                date_range = self.env['ir.sequence.date_range'].search(
                    [('sequence_id', '=', self.id), ('date_from', '>=', date), ('date_from', '<=', date_to)],
                    order='date_from desc', limit=1)
                if date_range:
                    date_to = date_range.date_from + timedelta(days=-1)
                    year = fields.Date.from_string(date).strftime('%Y')
                    month = fields.Date.from_string(date).strftime('%m')
                    date_from = '{}-{}-01'.format(year, month)
                date_range = self.env['ir.sequence.date_range'].search(
                    [('sequence_id', '=', self.id), ('date_to', '>=', date_from), ('date_to', '<=', date)],
                    order='date_to desc', limit=1)
                if date_range:
                    date_from = date_range.date_to + timedelta(days=1)
                    date_to = self.get_last_day_str(date_from.strftime('%Y-%m-%d'))
                seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
                    'date_from': date_from,
                    'date_to': date_to,
                    'sequence_id': self.id,
                })
                date_from = self.str_to_date(date_from)
                date_to = self.str_to_date(date_to)
                if date_from <= date <= date_to:
                    flag = True
            return seq_date_range
        return super(IrSequence, self)._create_date_range_seq(date)
