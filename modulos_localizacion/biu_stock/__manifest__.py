# -*- coding: utf-8 -*-
{
    'name': "Adecuaciones de Inventario",

    'description': """
        Adecuaciones del modulo Stock base de odoo, al cual se le añade cambios en la vista de los productos en los almacenes y la inclusión de reportes a la medida para el cliente Intelectra \n
        
        Modulo desarrollado por el Ing. José A. Colmenares B.
    """,

    'author': "TYSAMNCA",
    'website': "https://www.tysamnca.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'report/report_deliveryslip.xml',
    ],
    'installable': True,
    'application':True,
    'auto_install': False,
}