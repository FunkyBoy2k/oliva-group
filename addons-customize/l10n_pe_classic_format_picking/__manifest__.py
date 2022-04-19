{
    'name': 'Use classic format to print stock picking',
    'version': '14.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Add an additional, classic-style stock picking peruvian format.',
    'Description': """
    Add a peruvian classic format for stock picking, which is requested by many users
    """,
    'category': 'Warehouse',
    'depends': [
        'account',
        'stock',
        'qr_code_stock_picking',
        'l10n_latam_invoice_document',
        'l10n_pe_delivery_note',
        'qr_code_on_sale_invoice',
        'ple_stock_valuation_book',
        'merchandise_carrier',
        'contact_driver_license_number',
        'stock_picking_print_note'
    ],
    'data': [
        "reports/ticket_report.xml",
        "reports/ticket_template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 45.00
}
