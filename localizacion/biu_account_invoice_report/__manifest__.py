# -*- coding: utf-8 -*-
{
    'name': "Biumak Account Invoice Report",

    'summary': """Biumak_Module_Account_Invoice_Report""",

    'description': """
       Reporte para facturas y facturas sin pago en Facturas de Clientes.
       Modificado por: Ing. Yorman Pineda, corregido por Darrell Sojo
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','res_partner_clienteproveedor','intel_account_people_type','l10n_ve_fiscal_requirements','intel_res_currency'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/reporte_biumak_cliente.xml',
        #'report/account_invoice_report.xml',
        #'report/account_invoice_report_me.xml',
        #'report/account_invoice_with_payment_report.xml',
        #'report/account_invoice_with_payment_report_me.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
