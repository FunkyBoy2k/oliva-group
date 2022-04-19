{
    "name": u"Additional fields payroll",
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    "description": """
Crea un campo en el hr.contract llamado Motivo de baja,el cual se muestra una cuando indicas la fecha de baja.""",
    "depends": [
        'localization_menu',
        'hr_payroll'
    ],
    "data": [
        'data/low_reason_data.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/low_reason_views.xml',
        'views/mintra_contract_views.xml'
    ],
    "installable": True,
    "active": False,
}
