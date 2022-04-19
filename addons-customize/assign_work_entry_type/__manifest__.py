{
    'name': 'Assign work entry type',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'depends': [
        'hr_payroll',
        'hr_work_entry'
    ],
    'data': ['views/resource_calendar_attendance_views.xml',
             'security/hr_work_entry_validated.xml',
             ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.0
}
