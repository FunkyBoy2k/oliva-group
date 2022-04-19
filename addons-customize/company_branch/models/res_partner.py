from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    branch_office = fields.Char(
        string='Código Sucursal',
        help='Este código de sucursal será utilizado para la generación de archivos a presentar al MINTRA, Sunafil y SUNAT',
        default='-1'
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tags = [('page', 'branch_office')]
            res = self.tags_invisible_per_country(tags, res, [self.env.ref('base.pe')])
        return res
