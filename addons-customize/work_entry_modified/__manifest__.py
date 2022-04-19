{
    'name': 'Work Entry Modified',
    'version': '14.0.2.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
    Este modulo modifica los tipos de entrada de trabajo para que aparezcan llenos predeterminadamente.
    """,
    'depends': ['hr_payroll', 'voucher_lbs', 'payroll_utilities', 'voucher_payroll', 'basic_rule', 'holiday_rule',
                'legal_benefits_rule', 'rules_utilities'],
    'data': [
        'data/hr_work_entry_type_data.xml',
        'data/hr_salary_rule_category_data.xml'
    ],
    'post_init_hook': '_entry_change',
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
