# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Recibo de Pago Cestatickets',
    'version' : '1.0',
    'summary': 'Generate payroll receipt report',
    'sequence': 30,
    'description': """
This module generates a payroll receipt report for INTELECTRA company
Colaboradores: Ing. Yorman Pineda 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll'],
    'data': [
        'report/int_hr_recibo_cestaticket.xml',

    ],
    'qweb': [
        #"static/src/xml/account_reconciliation.xml",
        #"static/src/xml/account_payment.xml",
        #"static/src/xml/account_report_backend.xml",
        #"static/src/xml/account_dashboard_setup_bar.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}