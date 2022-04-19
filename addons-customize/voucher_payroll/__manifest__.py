{
    'name': 'Voucher payroll',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'depends': [
        'employee_service',
        'absence_day',
        'filter_payroll',
        'additional_fields_voucher',
        'holiday_field_payroll',
        'payment_conditions',
        'types_system_pension'
    ],
    'data': [
        'data/hr_work_entry_type_data_ballots.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/reports.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
