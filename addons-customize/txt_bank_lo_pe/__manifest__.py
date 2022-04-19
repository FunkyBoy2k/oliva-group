{
    'name': 'TXT Bank',
    'version': '14.0.1.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "",
    'depends': [
        'hr_localization_menu',
        'type_bank_accounts',
        'hr_payroll',
        'account_payment_order',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_massive_payment_views.xml',
        'views/res_partner_bank_views.xml',
        'views/hr_payslip_net_others.xml',
    ],
    'installable': True,
    'auto_install': False,
}
