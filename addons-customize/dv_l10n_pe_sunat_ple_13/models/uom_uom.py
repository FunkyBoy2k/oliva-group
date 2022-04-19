from odoo import models, fields, api, _


class ProductUoM(models.Model):
    _inherit = "uom.uom"

    sunat_code = fields.Selection(
        selection="_get_sunat_code", string="Código de unidad SUNAT")

    @api.model
    def _get_sunat_code(self):
        return self.env['pe.datas'].get_selection("PE.TABLA06")
