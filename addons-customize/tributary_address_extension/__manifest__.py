{
    'name': 'Tributary address extension',
    'version': '14.0.1.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': """
    Este módulo agregar los campos "Ubigeo" y "Establecimiento Anexo" en el formulario de contacto.
    Estos campos son dependencia para muchos módulos de la localización peruana como la facturación electrónica.
    """,
    'depends': ['l10n_country_filter'],
    'data': ['views/partner_views.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
