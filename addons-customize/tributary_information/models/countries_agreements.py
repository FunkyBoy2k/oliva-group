from odoo import api, fields, models


class CountriesAgreements(models.Model):
    _name = 'countries.agreements'
    _description = 'Convenios tributarios'

    code = fields.Char(
        string='Código'
    )
    name = fields.Char(
        string='Descripción'
    )
