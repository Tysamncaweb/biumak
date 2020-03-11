# -*- coding: utf-8 -*-
{
    'name': "Intelectra checking Balance",

    'summary': """Intelectra_Module_checking_Balance""",

    'description': """
      Generación del informe financiero Balance de Comprobación, en
formato PDF y en XLS.
Colaboradores: Yamile Rayme
    """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly.
    'depends': ['base', 'account', 'l10n_ve_withholding_islr', 'intel_retention_islr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/res_currency_rate_inherit_.xml',
        #'views/account_invoice_inherit.xml',
        'wizard/wizard_checking_balance.xml',
        'report/report_checking_balance_pdf.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
