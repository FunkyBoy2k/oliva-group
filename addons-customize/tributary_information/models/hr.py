from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    countries_agreements_id = fields.Many2one(
        comodel_name='countries.agreements',
        string='Convenio para evitar la doble tributación'
    )
    is_fifth_income = fields.Boolean(
        string='¿Percibe rentas de 5ta exoneradas (Inc. e) Art. 19 de la LIR?'
    )
