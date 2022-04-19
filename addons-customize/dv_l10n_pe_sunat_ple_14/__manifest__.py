# -*- coding: utf-8 -*-

{
	'name': """
		PLE Libro Registro de Ventas Reportes Sunat Perú TXT XLS |
        PLE Sale Register Book Sunat Peru TXT XLS Reports
    """,

    'summary': """
        Permite generar los libros de 14.1 y 14.2 PLE de Sunat Perú. |
        Allows to generate the 14.1 y 14.2 PLE of Sunat Peru.
    """,

    'description': """
        Programa de Libros Electrónicos de Perú Sunat.
    """,

	'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demoperu.develogers.com',
    'license': 'LGPL-3',

    'price': 149.99,
    'currency': 'EUR',
	
	'depends': [
     	'base',
		'dv_l10n_pe_sunat_ple',
	],
	'data': [
     	'security/ple_security.xml',
		'security/ir.model.access.csv',
		'views/ple_report_views.xml',
	],
	
	'images': ['static/description/banner.gif'],
 
	'auto_install': False,
	'installable': True,
	'application': True,
}