{
    'name': """
        Reportes PLE Base Sunat Perú TXT XLS
    """,

    'summary': """
        Permite generar los libros para el PLE de Sunat Perú. |
        Allows to generate the books for the PLE of Sunat Peru.
    """,

    'description': """
        Programa de Libros Electrónicos de Perú Sunat.
        Permite generar reportes de SUNAT en formato TXT y XLS.
        Registro de Facturas Electrónicas generadas en un periodo de tiempo.
    """,

    'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demoperu.develogers.com',
    'license': 'LGPL-3',

    'price': 99.99,
    'currency': 'EUR',
    
    'category': 'Accounting',
    'version': '14.0',

    'depends': [
        'base',
        'l10n_pe',
        'dv_account_invoice_date_currency_rate',
        'dv_account_seat_number',
        'dv_l10n_pe_account_account',
    ],

    'data': [
        'views/ple_report_templ_views.xml',
        'views/menu_item_views.xml',
        'security/ple_security.xml',
        'security/ir.model.access.csv',
    ],
    
    'images': ['static/description/banner.gif'],

    'application': True,
    'installable': True,
    'auto_install': False,
}
