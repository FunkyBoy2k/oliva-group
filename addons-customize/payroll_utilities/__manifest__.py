{
    'name': 'Payroll utilites',
    'version': '14.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': '',
    'depends': [
        'setting_rules_payroll',
        'hr_holidays',
        'payroll_fields',
        'absence_day',
        'hr_localization_menu'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/data_utilities_views.xml',
        'views/hr_views.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
