{
    'name': "Biumak Reporte factura con lote",

    'summary': """ Biumak - Modulo en la cual se incluye en la fatura el nro de lote del producto""",

    'description': """
       Biumak - Modulo en la cual se incluye en la fatura el nro de lote del producto.
    """,
    'version': '2.0',
    'author': 'Ing. Darrell Sojo',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale_management','biu_account_invoice_report'],

    # always loaded
    'data': [        
       'vista/vista_view.xml'
    ],
    'application': True,
}
