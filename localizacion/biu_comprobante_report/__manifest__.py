# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Comprobante Contable',
    'version' : '1.0',
    'summary': 'Genera el comprobante Contable',
    'sequence': 30,
    'description': """
    Genera el reporte de Comprobante Contable
Colaboradores: Ing. Yorman Pineda 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['base', 'account'],
    'data': [
        'report/biu_comprobante_report.xml',

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}