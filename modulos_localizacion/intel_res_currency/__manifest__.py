# -*- coding: utf-8 -*-
{
    'name': "Intelectra Currency Rate",

    'summary': """Intelectra_Module_Res_Currency_Rate""",

    'description': """
      Añadir hora en la tasa que aplica para la moneda.
      Colaboradores: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded ...
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_inherit.xml',
        'views/res_currency_rate_inherit_.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
