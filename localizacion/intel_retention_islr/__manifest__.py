# -*- coding: utf-8 -*-
{
    'name': "Intelectra Retention ISLR",

    'summary': """Intelectra_Module_Retention_ISLR""",

    'description': """
      Generación de reportes por concepto de retención del ISLR, 
	reportes pdf y xls
	Colaborador: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_ve_withholding_islr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/res_currency_rate_inherit_.xml',
        #'views/account_invoice_inherit.xml',
        'wizard/wizard_retention_islr.xml',
        'report/report_retention_islr_pdf.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
