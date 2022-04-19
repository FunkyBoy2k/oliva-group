{
    'name': 'Catálogos SUNAT',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Create the catalogs established by Peruvian legislation.',
    'depends': [
        'document_type_validation',
        'localization_menu',
        'l10n_pe_edi',
        'purchase_document_type_validation'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/charge_discount_codes_data.xml',
        'data/document_type_data.xml',
        'data/isc_calculation_system_data.xml',
        'data/l10n_latam_document_type_data.xml',
        'data/transfer_reason_codes_data.xml',
        'data/transfer_type_codes_data.xml',
        'views/account_views.xml',
        'views/charge_discount_codes_views.xml',
        'views/isc_calculation_system_views.xml',
        'views/l10n_latam_identification_type_views.xml',
        'views/product_template_views.xml',
        'views/transfer_reason_codes_views.xml',
        'views/transfer_type_codes_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
