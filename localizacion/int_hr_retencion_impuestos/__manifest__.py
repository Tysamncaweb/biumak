# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Retención de impuestos',
    'version' : '1.0',
    'summary': 'Genera el comprobante de Retención de impuestos del empleado',
    'description': """
Genera el comprobante de Retención de impuestos del empleado en el modulo de empleados.
Colaboradores: Ing. Yorman Pineda 
    """,

    'category': 'Human Resources',
    'website': 'http://www.tysamnca.com',
    'depends' : ['hr_payroll','hr'],
    'data': [
        'report/hr_retencion_impuesto_report.xml',
        'report/hr_retencion_impuesto.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}