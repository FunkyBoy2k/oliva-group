from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)
        if self.contract_id.resource_calendar_id:
            payslip_line = self.env['hr.payslip.line']
            # DIAS_010
            utilities_id = self.env['data.utilities'].search([('is_active', '=', True)])
            dias_010_days = 0
            hours_per_day = self.contract_id.resource_calendar_id.hours_per_day or 0.0
            if utilities_id:
                start_y = int(utilities_id[0].date_from.strftime('%Y'))
                start_m = int(utilities_id[0].date_from.strftime('%m'))
                end_y = int(utilities_id[0].date_to.strftime('%Y'))
                end_m = int(utilities_id[0].date_to.strftime('%m'))
                periods = payslip_line._get_periods(start_m, start_y, end_m, end_y)

                worked_lines = self.env['hr.payslip.worked_days'].search([
                    ('date_start', 'in', periods),
                    ('employee_id', '=', self.employee_id.id),
                    ('number_of_days', '>', 0)
                ])
                dias_010_days = sum(
                    line.number_of_days for line in worked_lines.filtered(lambda x: x.code in ['WORK100', 'GLOBAL', 'DDO'] or x.work_entry_type_id.utilities)
                )
            dias_010_hours = dias_010_days * hours_per_day
            dias_010_entry_type_id = self.env.ref('rules_utilities.hr_work_entry_type_dias_010')
            values = [{
                'sequence': dias_010_entry_type_id.sequence, 'work_entry_type_id': dias_010_entry_type_id.id, 'number_of_days': dias_010_days,
                'number_of_hours': dias_010_hours
            }]
            res += values
        return res

    def get_inputs_data(self):
        res = super(HrPayslip, self).get_inputs_data()
        utilities_id = self.env['data.utilities'].search([('is_active', '=', True)])
        if utilities_id and res:
            for result in res:
                if result.get('code') == 'UTL_003':
                    result['amount'] = utilities_id[0].factor_days
                if result.get('code') == 'UTL_004':
                    result['amount'] = utilities_id[0].factor_amount
        return res


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    archive_employee_ids = fields.Char(string='Force generate payslip to archive employees')

    @api.model
    def create(self, vals):
        if vals.get('employee_ids') and isinstance(vals.get('employee_ids')[0], tuple):
            if vals['employee_ids'][0][0] != 5 and len(vals['employee_ids'][0]) == 3:
                vals['archive_employee_ids'] = vals['employee_ids'][0][2]
        return super(HrPayslipEmployees, self).create(vals)

    def write(self, vals):
        if vals.get('employee_ids') and isinstance(vals.get('employee_ids')[0], tuple):
            if vals['employee_ids'][0][0] != 5 and len(vals['employee_ids'][0]) == 3:
                vals['archive_employee_ids'] = vals['employee_ids'][0][2]
        return super(HrPayslipEmployees, self).write(vals)

    def get_hr_payslip_employees_data(self):
        employee_ids = []
        utilities_struct = self.env.ref('rules_utilities.hr_payroll_structure_utilidades')
        if self.structure_id == utilities_struct:
            archive_employee_ids = self.archive_employee_ids.replace('[', '').replace(']', '')
            employee_ids = [int(e) for e in archive_employee_ids.split(',')]
        return employee_ids

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        utilities_struct = self.env.ref('rules_utilities.hr_payroll_structure_utilidades')
        employee_ids = self.employee_ids
        if self.structure_id == utilities_struct:
            employees = self.get_hr_payslip_employees_data()
            employee_ids += self.env['hr.employee'].browse(employees)

        if not employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end, states=['open', 'close', 'cancel'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
