# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Reporte Liquidacion',
    'version' : '1.0',
    'summary': 'Genera el reporte de liquidacion',
    'description': """
Genera el reporte de Liquidación en la nomina
Colaboradores: Ing. MARIA CARREÑO 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll','hr_contract'],
    'data': [
        'report/int_liquidacion_report.xml',
       # 'report/hr_liquidacion_wizard.xml',

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
