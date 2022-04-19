from odoo import api, fields, models


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    categorys_ids = fields.Many2one(comodel_name="hr.employee.category", string='Elija Categoria')

    def filter_employees(self):
        self.ensure_one()
        x = []
        lines = self.employee_ids
        self.employee_ids = False
        for i in lines:
            if self.categorys_ids in i.category_ids:
                x.append(i.id)
        self.employee_ids = x

        return {
            'name': 'Generar recibos de nómina',
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def clean_employees(self):
        self.ensure_one()
        self.employee_ids = False

        return {
            'name': 'Generar recibos de nómina',
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
