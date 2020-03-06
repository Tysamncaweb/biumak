# -*- coding: utf-8 -*-
{
    'name': "Intelectra Account People Type",

    'summary': """Intelectra_Module_Account_People_Type""",

    'description': """
       Campo que permite registrar el tipo de persona en clientes y proveedores.
       Colaboradores: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_people_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}