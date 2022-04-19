from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tags = ['l10n_latam_identification_type_id']
            latam_countries = [self.env.ref('base.pe'), self.env.ref('base.ar'), self.env.ref('base.cl'), self.env.ref('base.cr')]
            res = self.tags_invisible_per_country(tags, res, latam_countries)
        return res
