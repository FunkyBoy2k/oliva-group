from odoo import models, fields, api


class EpsManagement(models.Model):
    _name = "eps.management"

    star_date = fields.Date(string='Fecha de inicio', required=True)
    finish_date = fields.Date(string='Fecha de finalización', required=True)
    entity = fields.Char(string='Entidad')
    insurance = fields.Char(string='N° de poliza')
    rate_employer = fields.Integer(string='Tasa')
    amount_employer = fields.Integer(string='Importe')
    rate_worker = fields.Integer(string='Tasa')
    amount_worker = fields.Integer(string='Importe')
    employeer_ids = fields.Many2many(
        'hr.employee', string='Empleados')

    def name_get(self):
        res = []
        for _ in self:
            name = "%s-%s" % (_.entity, _.insurance)
            res.append((_.id, name))
        return res


class EpsEmployee(models.Model):
    _inherit = 'hr.employee'

    exists_eps = fields.Boolean(string='EPS',
                                groups="hr.group_hr_user"
                                )
    management_eps = fields.Many2one('eps.management', string='Poliza EPS')

    @api.onchange('management_eps')
    def update_list_employee_eps(self):
        eps_employee = self.env['eps.management'].search([('insurance', '=', self.management_eps.insurance)])
        hr_employee = self.env['hr.employee'].search([('name', '=', self.name)])
        if eps_employee:
            for record in eps_employee:
                record.write({
                    'employeer_ids': [(4, hr_employee.id)]
                })
        else:
            True
