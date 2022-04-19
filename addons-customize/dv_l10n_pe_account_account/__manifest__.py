{
    'name': """
        Campos de Localizacion peruana en facturas de proveedores Peru
    """,

    'summary': """
        Agrega campos en facturas de proveedores e interface en Point of Sale.
    """,

    'description': """
        Agrega campos en facturas de proveedores e interface en Point of Sale.
    """,

	'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demoperu.develogers.com',
    'license': 'LGPL-3',

    'category': 'Accounting',
    'version': '14.0',
    
    'price': 49.99,
    'currency': 'EUR',

    'depends': [
        'l10n_latam_invoice_document',
        'l10n_pe',
        'dv_l10n_pe_edi_table',
    ],

    'data': [
        'views/account_account_views.xml',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
        'views/l10n_latam_identification_type_views.xml',
        'views/product_template_views.xml',
        'views/menu_item_views.xml',
        'data/res.partner.csv',
        'data/l10n_latam.document.type.csv',
        #'data/account_tax_data.xml',
    ],
    
    'images': ['static/description/banner.gif'],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
