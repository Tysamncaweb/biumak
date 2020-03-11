# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details..
{
    'name': 'vacaciones calculo',
    'version': '1.0',
    'summary': 'Calculo de vacaciones del empleado',


    'description': """
    """,
    'author': 'Tysamnca',
    'collaborator': 'Yorman Pineda',
    'category': 'vacation',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base','hr_contract','hr_holidays','hr_contract_add_fields'],
    'data': [

        'views/int_hr_vacation_calcule_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
