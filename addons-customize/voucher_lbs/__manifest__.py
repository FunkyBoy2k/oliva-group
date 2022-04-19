{
    'name': 'Voucher LBS',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'This module creates the voucher LBS report.',
    'depends': [
        'holiday_field_payroll',
        'identification_type_employee',
        'additional_fields_payroll',
        'additional_fields_voucher',
        'legal_benefits_rule',
    ],
    'data': [
        'data/section_lbs_data.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/section_lbs_views.xml',
        'views/reports.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
