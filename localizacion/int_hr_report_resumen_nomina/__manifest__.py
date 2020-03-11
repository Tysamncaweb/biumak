# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Resumen de Nómina',
    'version' : '2.0',
    'summary': 'Resumen Nomina de INTELECTRA',
    'sequence': 30,
    'description': """
This module generates a SUMARY payroll report for BIUMAK company
Colaboradores: ING. María Carreño 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll'],
    'data': [
        'report/int_hr_report_resumen_nomina.xml',

    ],
    'qweb': [
        #"static/src/xml/account_reconciliation.xml",
        #"static/src/xml/account_payment.xml",
        #"static/src/xml/account_report_backend.xml",
        #"static/src/xml/account_dashboard_setup_bar.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}