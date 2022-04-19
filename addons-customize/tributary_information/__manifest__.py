{
    'name': 'Tributary Information',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Create two fields in the employee contracts where it is indicated if the worker applies for the double taxation agreement.',
    'category': 'Human Resources/Payroll',
    'depends': [
        'localization_menu',
        'hr_contract'
    ],
    'data': [
        'data/countries_agreements_data.xml',
        'security/ir.model.access.csv',
        'views/countries_agreements_views.xml',
        'views/hr_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 10.00
}
