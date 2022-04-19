from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
import base64


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_mail = fields.Char(
        string='Correo',
        related='employee_id.private_email'
    )

    def action_send_mail_employees(self):
        payslip_ids = self.filtered(lambda x: x.state == 'done')
        for rec in payslip_ids:
            if not rec.employee_mail:
                continue
            mail_obj = self.env['mail.compose.message'].with_context({
                'default_template_id': self.env.ref('voucher_sending.mail_template_hr_payslip_by_employee').id,
                'default_model': 'hr.payslip',
                'default_res_id': rec.id
            })
            report_id = self.env['ir.attachment'].search([('res_id', '=', rec.id)])
            if not report_id or len(report_id) != 1:
                report_id = rec.generate_report_manually()
            mail_id = mail_obj.create({'attachment_ids': [report_id.id]})
            mail_id.onchange_template_id_wrapper()
            mail_id.action_send_mail()

    def generate_report_manually(self):
        if not self.struct_id or not self.struct_id.report_id:
            report = self.env.ref('hr_payroll.action_report_payslip', False)
        else:
            report = self.struct_id.report_id
        pdf_content, content_type = report._render_qweb_pdf(self.id)
        if self.struct_id.report_id.print_report_name:
            pdf_name = safe_eval(self.struct_id.report_id.print_report_name, {'object': self})
        else:
            pdf_name = _("Payslip")
        attach_id = self.env['ir.attachment'].create({
            'name': pdf_name,
            'type': 'binary',
            'datas': base64.encodebytes(pdf_content),
            'res_model': self._name,
            'res_id': self.id
        })
        return attach_id
