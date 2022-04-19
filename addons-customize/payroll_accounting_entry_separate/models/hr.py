from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _prepare_adjust_line(self, line_ids, adjust_type, debit_sum, credit_sum, date):
        if self.journal_id.type == 'general':
            if (0.0 if adjust_type == 'credit' else credit_sum - debit_sum) > 0:
                acc_id = self.journal_id.default_debit_account_id.id
            else:
                acc_id = self.journal_id.default_credit_account_id.id
        else:
            acc_id = self.journal_id.default_account_id.id

        if not acc_id:
            raise UserError(_('The Expense Journal "%s" has not properly configured the default Account!') % (self.journal_id.name))
        existing_adjustment_line = (
            line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
        )
        adjust_credit = next(existing_adjustment_line, False)

        if not adjust_credit:
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'partner_id': self.employee_id.address_home_id.id,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0 if adjust_type == 'credit' else credit_sum - debit_sum,
                'credit': debit_sum - credit_sum if adjust_type == 'credit' else 0.0,
            }
            line_ids.append(adjust_credit)
        else:
            adjust_credit['credit'] = debit_sum - credit_sum

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda x: not x.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                for slip in slip_mapped_data[journal_id][slip_date]:
                    line_ids = []
                    debit_sum = 0.0
                    credit_sum = 0.0
                    date = slip_date
                    move_dict = {
                        'narration': slip.number or '' + ' - ' + slip.employee_id.name or '',
                        'journal_id': journal_id,
                        'date': date,
                        'ref': slip.number
                    }
                    slip_lines = slip._prepare_slip_lines(date, line_ids)
                    line_ids.extend(slip_lines)
                    for line_id in line_ids:  # Get the debit and credit sum and partner_id.
                        line_id['partner_id'] = slip.employee_id.address_home_id.id
                        debit_sum += line_id['debit']
                        credit_sum += line_id['credit']

                    # The code below is called if there is an error in the balance between credit and debit sum.
                    if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                        slip._prepare_adjust_line(line_ids, 'credit', debit_sum, credit_sum, date)
                    elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                        slip._prepare_adjust_line(line_ids, 'debit', debit_sum, credit_sum, date)
                    # Add accounting lines in the move
                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self._create_account_move(move_dict)
                    slip.write({'move_id': move.id, 'date': date})
        return True
