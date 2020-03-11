# -*- coding: utf-8 -*-
{
    'name': "Intelectra Bank reconciliation",

    'summary': """Intelectra_Module_Bank_reconciliation""",

    'description': """
    permite realizar la conciliación
    bancaria, así como generar los reportes pertinentes.
	Colaborador: Yamile Rayme """,
    'version': '1.0',
    'author': 'Tysamnca',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/res_currency_rate_inherit_.xml',
        'views/bank_reconciliation.xml',
        #'wizard/wizard_bank_reconciliation.xml',
        'report/report_bank_reconciliation_pdf.xml',
        #'report/report_result_reconciliation.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
