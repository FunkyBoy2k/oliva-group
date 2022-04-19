{
    "name": "Employee certificate for employee",
    'version': '14.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    "description": """
This module enables the issuance of work certificates for employees
    """,
    "depends": ['hr_payroll','base'],
    "data": [
            'views/certificate_view.xml',
            'report/certification_employee_report.xml',
            'report/certification_employee_template.xml',
    ],

}