# coding: utf-8

{
    'name': 'Reporte Analítico por cuenta',
    'version': '1.0',
    'author': 'TYSAMNCA',
    'category': 'Localization',
    'description': """
    
        Agrega reporte de analitico por cuenta exigidos por las leyes venezolanas

        Colaborador: Nathaly Partidas
    """,

    'depends': [
        'account',
        'base_vat',

    ],
    'data': [

        'wizard/wizard_report_analytic_view.xml',
        'report/report_analitico_por_cuenta.xml',

    ],
    'installable': True,
}

