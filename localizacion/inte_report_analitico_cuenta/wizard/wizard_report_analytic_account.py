# coding: utf-8

###############################################################################

from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt, base64
from decimal import *


class WizardReportAnalytic(models.TransientModel):
    _name = 'wizard.report.analytic.account'
    _description = "Wizard Report Analytic Account"

    move_dest = fields.Selection(selection=[('all', 'Todos asientos'),
                                            ('validate', _('Todos los asientos validados'))],
        string='Destiny Move',
        required=True,
        default='all',
        help="Destiny Move help")

    cuentas_contables = fields.Selection(
        string= "Mostrar Cuenta",
        selection=[('all', 'Todas las cuentas'),
                   ('move', 'Cuentas con movimiento'),
                   ('saldo_cero','Con saldo distinto a cero')
                  ], default='all'
    )

    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    num_cuenta_contables = fields.Many2one('account.account')
    cuenta_especifica = fields.Boolean(string="Cuenta especifica")
    company = fields.Many2one('res.company')
    saldo_inicial = fields.Boolean('Saldo inicial',default=False)
    currency_id = fields.Many2one('res.currency')
    ordenado_fecha = fields.Boolean(string="Ordenado por:")
    #report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)


    @api.onchange('cuentas_contables','cuenta_especifica')
    def _onchange_cuentas(self):
        if self.cuentas_contables == 'all' and self.cuenta_especifica== True:
            self.cuenta_especifica = False
            self.num_cuenta_contables = ""

    def _get_date_analitico(self):
        if self.date_start == False and self.date_end == False:

            self.date_start = '1900-01-01'
            self.date_end = fields.Date.today()

        elif self.date_start == False and self.date_end != False:
            self.date_start = '1900-01-01'

        elif self.date_start != False and self.date_end == False:
            self.date_end = fields.Date.today()

    def _get_cuentas_contables(self):
        num_cuentas_contables_obj = self.env['account.account']
        if self.cuentas_contables == 'all':
            #num_cuentas_contables_obj = num_cuentas_contables_obj.search([])
            pass
        else:
            num_cuentas_contables_obj = self.num_cuenta_contables
        return num_cuentas_contables_obj

    @api.model
    def _datos_cuentas_contables(self, num_cuenta_contables, cuenta_especifica):
        '''Se obtienen los datos de las cuentas contables para la cabecera del reporte'''
        datos_cuentas = []
        if not cuenta_especifica:
            if not num_cuenta_contables:
                datos_cuentas.append({'codigo': "Todos los códigos",
                                      'nombre': "Todas las cuentas"})
            else:
                account_obj = self.env['account.account']
                account_brw = account_obj.browse(num_cuenta_contables.id)

                datos_cuentas.append({'codigo': account_brw.code,
                                      'nombre': account_brw.name})
        else:
            if not num_cuenta_contables:
                datos_cuentas.append({'codigo': "Todos los códigos",
                                      'nombre': "Todas las cuentas"})
            else:
                account_obj = self.env['account.account']
                account_brw = account_obj.browse(num_cuenta_contables.id)

                datos_cuentas.append({'codigo': account_brw.code,
                                      'nombre': account_brw.name})
        return datos_cuentas

    @api.model
    def _get_orden(self, ordenado_fecha):
        if ordenado_fecha == True:
            ordenado_fecha = "Fecha"
        else:
            ordenado_fecha = "ninguno"
        return ordenado_fecha

    @api.model
    def _get_moneda(self, currency_id):
        currency_brw = []
        if not currency_id:
            currency_obj = self.env['res.currency'].search([])
            for c in currency_obj:
                currency_brw.append(c)
        else:
            currency_obj = self.env['res.currency'].browse(currency_id)
            for c in currency_obj:
                currency_brw.append(c)
        return currency_brw

    def _get_datos_moneda(self,currency_obj):
        currency_name = []
        if currency_obj:
            for currency in currency_obj:
                currency_name.append(" " +currency.name)
        return currency_name

    def print_analitico_xls(self):

        saldo_inicial = self.saldo_inicial
        ordenado_fecha = self.ordenado_fecha
        cuentas_contables = self.cuentas_contables
        move_dest = self.move_dest
        date_start = self.date_start
        date_end = self.date_end
        empresa = self.company
        currency = self.currency_id
        today = fields.Date.today()

        report_obj = self.env['report.inte_report_analitico_cuenta.report_analytic_por_cuenta']
        num_cuenta_contables_obj = self.env['account.account']
        # Todas las cuentas
        if cuentas_contables == 'all':
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        # todas las cuentas con cuentas con movimiento
        elif cuentas_contables == 'move' and self.cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        # todas las cuentas con saldo diferente a cero
        elif cuentas_contables == 'saldo_cero' and self.cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        # cuenta especifica con movimiento
        elif cuentas_contables == 'move' and self.cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(self.num_cuenta_contables.id)
        # cuenta especifica con saldo distinto a cero
        elif cuentas_contables == 'saldo_cero' and self.cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(self.num_cuenta_contables.id)

        # Validacion cuando se toman las monedas vacio (El reporte tiene que ser con todas la monedas)
        if not self.currency_id:
            currency_obj = self._get_moneda(self.currency_id)
            currency_name = self._get_datos_moneda(currency_obj)
        else:
            currency_obj = self.currency_id
            currency_name = self._get_datos_moneda(currency_obj)

        account_res = []
        account_res = report_obj._get_account_move_entry(num_cuenta_contables_obj, saldo_inicial, ordenado_fecha, cuentas_contables,move_dest,date_start,date_end,empresa.id,currency_obj)
        # cambiar formato fecha:
        formato_fecha = "%d/%m/%Y"
        date_now = today
        date_now = datetime.strftime(datetime.strptime(date_now, DATE_FORMAT), formato_fecha)
        date_start = datetime.strftime(datetime.strptime(date_start, DATE_FORMAT), formato_fecha)
        date_end = datetime.strftime(datetime.strptime(date_end, DATE_FORMAT), formato_fecha)
        # suma de debit, credit, balance para calcular los totales
        res_totales = dict((fn, 0.0) for fn in ['credit_total_bs', 'debit_total_bs', 'balance_total_bs',
                                                'credit_total_usd', 'debit_total_usd', 'balance_total_bs',
                                                'credit_total_eur', 'debit_total_eur', 'balance_total_eur'])
        total_credit_bs = 0.0
        total_debit_bs = 0.0
        total_balance_bs = 0.0
        total_credit_usd = 0.0
        total_debit_usd = 0.0
        total_balance_usd = 0.0
        total_credit_eur = 0.0
        total_debit_eur = 0.0
        total_balance_eur = 0.0

        if not self.currency_id:
            for account in account_res:
                    # totales en bs
                    total_credit_bs += account['credit']
                    total_debit_bs += account['debit']
                    total_balance_bs += account['balance']

                    # totales en dolares
                    total_credit_usd += account['credit_usd']
                    total_debit_usd += account['debit_usd']
                    total_balance_usd += account['balance_usd']

                    # totales en euros
                    total_credit_eur += account['credit_eur']
                    total_debit_eur += account['debit_eur']
                    total_balance_eur += account['balance_eur']

        elif self.currency_id.id == 4:
            for account in account_res:
                # totales en bs
                total_credit_bs += account['credit']
                total_debit_bs += account['debit']
                total_balance_bs += account['balance']

        elif self.currency_id.id == 3:
            for account in account_res:
                # totales en dolares
                total_credit_usd += account['credit_usd']
                total_debit_usd += account['debit_usd']
                total_balance_usd += account['balance_usd']
        elif self.currency_id.id == 1:
            for account in account_res:
                # totales en euros
                total_credit_eur += account['credit_eur']
                total_debit_eur += account['debit_eur']
                total_balance_eur += account['balance_eur']

        res_totales['credit_total_bs'] = total_credit_bs
        res_totales['debit_total_bs'] = total_debit_bs
        res_totales['balance_total_bs'] = total_balance_bs

        res_totales['credit_total_usd'] = total_credit_usd
        res_totales['debit_total_usd'] = total_debit_usd
        res_totales['balance_total_usd'] = total_balance_usd

        res_totales['credit_total_eur'] = total_credit_eur
        res_totales['debit_total_eur'] = total_debit_eur
        res_totales['balance_total_eur'] = total_balance_eur

        #currency_name = self._get_datos_moneda(currency_obj)
        num_cuenta_contable = self._datos_cuentas_contables(self.num_cuenta_contables, self.cuenta_especifica)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_analitico = wb.add_sheet('Analítico por cuenta')
        #formato del reporte
        title_format = xlwt.easyxf("font: name Tahoma size 14 px, bold 1;")
        sub_title_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")

        sub_title_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, height 170, bold 1;",num_format_str='#,##0.00')
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;",num_format_str='#,##0.00')

        row = 1
        col = 0

        sheet_analitico.row(row).height = 500
        #sheet_name.write_merge(fila_inicial, fila_final, columna_inicial, columna_final,)

        #impresion de la fecha del reporte:
        sheet_analitico.write(0,0,"Fecha:")
        sheet_analitico.write(0,1,str(date_now))
        #impresion del nombre de la empresa:
        sheet_analitico.write_merge(0,0,5,7,str(self.company.name))
        #titulo del reporte

        sheet_analitico.write_merge(1,1,0,3, "Reporte Analítico por Cuenta",title_format)
        #Fecha desde y hasta
        sheet_analitico.write(2, 0, "Fecha desde:", sub_title_style)
        sheet_analitico.write_merge(2,2,1,1,str(date_start))
        sheet_analitico.write(3, 0, "Fecha hasta:", sub_title_style)
        sheet_analitico.write_merge(3,3,1,1,str(date_end))
        #Mostrar cuenta
        sheet_analitico.write_merge(2,2,4,5,"Mostrar cuenta:", sub_title_style)
        sheet_analitico.write_merge(3,3,4,5,str(self.cuentas_contables))
        #Movimiento destino
        sheet_analitico.write_merge(2,2,7,8, "Movimiento destino:", sub_title_style)
        sheet_analitico.write_merge(3,3,7,8, str(self.move_dest))
        # Ordenado por Fecha
        sheet_analitico.write_merge(2, 2, 10, 11, "Ordenado por:", sub_title_style)
        sheet_analitico.write_merge(3, 3, 10, 11, "Fecha")

        # número de cuenta contable
        sheet_analitico.write_merge(5, 5 , 0, 1, "Nro de Cuenta de Contable:", sub_title_style)
        sheet_analitico.write_merge(5, 5, 2, 3, num_cuenta_contable[0].get('codigo'))
        sheet_analitico.write_merge(5, 5, 6, 6, "Nombre: ", sub_title_style)
        sheet_analitico.write_merge(5, 5, 8, 10, num_cuenta_contable[0].get('nombre'))
        sheet_analitico.write_merge(5, 5, 11, 11, "Moneda:", sub_title_style)
        sheet_analitico.write_merge(5, 5, 12, 12, currency_name)

        #Lineas del Reporte###############################
        row += 6
        col = 1
        sheet_analitico.write_merge(row, row, 0, 0, "Fecha", sub_title_style)
        sheet_analitico.write_merge(row, row, 1, 1, "JRNL", sub_title_style)
        sheet_analitico.write_merge(row, row, 2, 2, "Empresa", sub_title_style)
        sheet_analitico.write_merge(row, row, 3, 3, "Ref", sub_title_style)
        sheet_analitico.write_merge(row, row, 4, 4, "Move", sub_title_style)
        if self.saldo_inicial == True:
            sheet_analitico.write_merge(row, row, 5, 5, "Entry Label", sub_title_style)
        else:
            sheet_analitico.write_merge(row, row, 5, 5, "", sub_title_style)
        sheet_analitico.write_merge(row, row, 6, 6, "Cuenta Analítica", sub_title_style)
        if not self.currency_id:
            sheet_analitico.write_merge(row, row, 7, 7, "Débito Bs", sub_title_style)
            sheet_analitico.write_merge(row, row, 8, 8, "Crédito Bs", sub_title_style)
            sheet_analitico.write_merge(row, row, 9, 9, "Saldo Bs", sub_title_style)

            sheet_analitico.write_merge(row, row, 10, 10, "Tasa USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 11, 11, "Débito USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 12, 12, "Crédito USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 13, 13, "Saldo USD", sub_title_style)

            sheet_analitico.write_merge(row, row, 14, 14, "Tasa EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 15, 15, "Débito EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 16, 16, "Crédito EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 17, 17, "Saldo EUR", sub_title_style)
        elif self.currency_id.id == 3:
            sheet_analitico.write_merge(row, row, 7, 7, "Tasa USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 8, 8, "Débito USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 9, 9, "Crédito USD", sub_title_style)
            sheet_analitico.write_merge(row, row, 10, 10, "Saldo USD", sub_title_style)
        elif self.currency_id.id == 1:
            sheet_analitico.write_merge(row, row, 7, 7, "Tasa EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 8, 8, "Débito EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 9, 9, "Crédito EUR", sub_title_style)
            sheet_analitico.write_merge(row, row, 10, 10, "Saldo EUR", sub_title_style)
        elif self.currency_id.id == 4:
            sheet_analitico.write_merge(row, row, 7, 7, "Débito Bs", sub_title_style)
            sheet_analitico.write_merge(row, row, 8, 8, "Crédito Bs", sub_title_style)
            sheet_analitico.write_merge(row, row, 9, 9, "Saldo Bs", sub_title_style)

        for a in account_res:
            row += 1
            if not self.currency_id:
                sheet_analitico.write_merge(row, row, 0, 0, a['code'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 2, 2, a['name'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 7, 7, a['debit'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 8, 8, a['credit'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 9, 9, a['balance'], sub_title_style_bold)

                sheet_analitico.write_merge(row, row, 10, 10, a['tasa_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 11, 11, a['debit_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 12, 12, a['credit_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 13, 13, a['balance_usd'], sub_title_style_bold)

                sheet_analitico.write_merge(row, row, 14, 14, a['debit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 15, 15, a['debit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 16, 16, a['credit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 17, 17, a['balance_eur'], sub_title_style_bold)

            elif self.currency_id.id == 3:
                sheet_analitico.write_merge(row, row, 0, 0, a['code'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 2, 2, a['name'], sub_title_style_bold)

                sheet_analitico.write_merge(row, row, 7, 7, a['tasa_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 8, 8, a['debit_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 9, 9, a['credit_usd'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 10, 10, a['balance_usd'], sub_title_style_bold)

            elif self.currency_id.id == 1:
                sheet_analitico.write_merge(row, row, 0, 0, a['code'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 2, 2, a['name'], sub_title_style_bold)

                sheet_analitico.write_merge(row, row, 7, 7, a['debit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 8, 8, a['debit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 9, 9, a['credit_eur'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 10, 10, a['balance_eur'], sub_title_style_bold)

            elif self.currency_id.id == 4:
                sheet_analitico.write_merge(row, row, 0, 0, a['code'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 2, 2, a['name'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 7, 7, a['debit'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 8, 8, a['credit'], sub_title_style_bold)
                sheet_analitico.write_merge(row, row, 9, 9, a['balance'], sub_title_style_bold)

            for line in a.get('move_lines'):
                row += 1
                if not self.currency_id:
                    sheet_analitico.write_merge(row, row, 0, 0, line['ldate'])
                    sheet_analitico.write_merge(row, row, 1, 1, line['lcode'])
                    sheet_analitico.write_merge(row, row, 2, 2, line['partner_name'])
                    sheet_analitico.write_merge(row, row, 3, 3, line['lref'])
                    sheet_analitico.write_merge(row, row, 4, 4, line['move_name'])
                    sheet_analitico.write_merge(row, row, 5, 5, line['lname'])
                    if line['lname'] == 'Initial Balance' or line['lname'] == 'Balance Inicial':
                        sheet_analitico.write_merge(row, row, 6, 6, " ")
                    else:
                        sheet_analitico.write_merge(row, row, 6, 6, line['analytic_account_name'])

                    sheet_analitico.write_merge(row, row, 7, 7, line['debit'], line_content_style)
                    sheet_analitico.write_merge(row, row, 8, 8, line['credit'], line_content_style)
                    sheet_analitico.write_merge(row, row, 9, 9, line['balance'],line_content_style)

                    sheet_analitico.write_merge(row, row, 10, 10, line['tasa_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 11, 11, line['debit_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 12, 12, line['credit_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 13, 13, line['balance_usd'], line_content_style)

                    sheet_analitico.write_merge(row, row, 14, 14, line['tasa_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 15, 15, line['debit_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 16, 16, line['credit_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 17, 17, line['balance_eur'], line_content_style)

                elif self.currency_id.id == 3:
                    sheet_analitico.write_merge(row, row, 0, 0, line['ldate'])
                    sheet_analitico.write_merge(row, row, 1, 1, line['lcode'])
                    sheet_analitico.write_merge(row, row, 2, 2, line['partner_name'])
                    sheet_analitico.write_merge(row, row, 3, 3, line['lref'])
                    sheet_analitico.write_merge(row, row, 4, 4, line['move_name'])
                    sheet_analitico.write_merge(row, row, 5, 5, line['lname'])

                    if line['lname'] == 'Initial Balance' or line['lname'] == 'Balance Inicial':
                        sheet_analitico.write_merge(row, row, 6, 6, " ")
                        sheet_analitico.write_merge(row, row, 6, 6, " ")
                    else:
                        sheet_analitico.write_merge(row, row, 6, 6, line['analytic_account_name'])

                    sheet_analitico.write_merge(row, row, 7, 7, line['tasa_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 8, 8, line['debit_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 9, 9, line['credit_usd'], line_content_style)
                    sheet_analitico.write_merge(row, row, 10, 10, line['balance_usd'], line_content_style)
                elif self.currency_id.id == 1:
                    sheet_analitico.write_merge(row, row, 0, 0, line['ldate'])
                    sheet_analitico.write_merge(row, row, 1, 1, line['lcode'])
                    sheet_analitico.write_merge(row, row, 2, 2, line['partner_name'])
                    sheet_analitico.write_merge(row, row, 3, 3, line['lref'])
                    sheet_analitico.write_merge(row, row, 4, 4, line['move_name'])
                    sheet_analitico.write_merge(row, row, 5, 5, line['lname'])
                    if line['lname'] == 'Initial Balance' or line['lname'] == 'Balance Inicial':
                        sheet_analitico.write_merge(row, row, 6, 6, " ")
                    else:
                        sheet_analitico.write_merge(row, row, 6, 6, line['analytic_account_name'])

                    sheet_analitico.write_merge(row, row, 7, 7, line['tasa_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 8, 8, line['debit_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 9, 9, line['credit_eur'], line_content_style)
                    sheet_analitico.write_merge(row, row, 10, 10, line['balance_eur'], line_content_style)
                elif self.currency_id.id == 4:
                    sheet_analitico.write_merge(row, row, 0, 0, line['ldate'])
                    sheet_analitico.write_merge(row, row, 1, 1, line['lcode'])
                    sheet_analitico.write_merge(row, row, 2, 2, line['partner_name'])
                    sheet_analitico.write_merge(row, row, 3, 3, line['lref'])
                    sheet_analitico.write_merge(row, row, 4, 4, line['move_name'])
                    sheet_analitico.write_merge(row, row, 5, 5, line['lname'])
                    if line['lname'] == 'Initial Balance' or line['lname'] == 'Balance Inicial':
                        sheet_analitico.write_merge(row, row, 6, 6, " ")
                    else:
                        sheet_analitico.write_merge(row, row, 6, 6, line['analytic_account_name'])

                    sheet_analitico.write_merge(row, row, 7, 7, line['debit'], line_content_style)
                    sheet_analitico.write_merge(row, row, 8, 8, line['credit'], line_content_style)
                    sheet_analitico.write_merge(row, row, 9, 9, line['balance'], line_content_style)
        col = 1
        row += 1
        if not self.currency_id:
            sheet_analitico.write_merge(row, row, 6, 6, "Totales", sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 7, 7, res_totales['debit_total_bs'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 8, 8, res_totales['credit_total_bs'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 9, 9, res_totales['balance_total_bs'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 11, 11, res_totales['debit_total_usd'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 12, 12, res_totales['credit_total_usd'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 13, 13, res_totales['balance_total_usd'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 15, 15, res_totales['debit_total_eur'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 16, 16, res_totales['credit_total_eur'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 17, 17, res_totales['balance_total_eur'], sub_title_style_bold)
        elif self.currency_id.id == 3:
            sheet_analitico.write_merge(row, row, 6, 6, "Totales Dólares", sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 8, 8, res_totales['debit_total_usd'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 9, 9, res_totales['credit_total_usd'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 10, 10, res_totales['balance_total_usd'], sub_title_style_bold)
        elif self.currency_id.id == 1:
            sheet_analitico.write_merge(row, row, 6, 6, "Totales Euros", sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 8, 8, res_totales['debit_total_eur'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 9, 9, res_totales['credit_total_eur'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 10, 10, res_totales['balance_total_eur'], sub_title_style_bold)
        elif self.currency_id.id == 4:
            sheet_analitico.write_merge(row, row, 6, 6, "Totales Bolivares", sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 7, 7, res_totales['debit_total_bs'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 8, 8, res_totales['credit_total_bs'], sub_title_style_bold)
            sheet_analitico.write_merge(row, row, 9, 9, res_totales['balance_total_bs'], sub_title_style_bold)

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'analitico_por_cuenta.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.report.analytic.account',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def print_analitico_pdf(self):
        self._get_date_analitico()
        #currency = self._get_currency_analitico()
        num_cuentas_contables = self._get_cuentas_contables()

        fecha_inicio = self.date_start
        fecha_fin = self.date_end

        if datetime.strptime(fecha_inicio, DATE_FORMAT) > datetime.strptime(fecha_fin, DATE_FORMAT):
            raise ValidationError('Advertencia! La fecha de inicio no puede ser superior a la fecha final')

        datas = [] #self.read(self.ids)[0]
        ids = []
        data = {
            'ids': ids,
            'model': 'report.inte_report_analitico_cuenta.report_analytic_por_cuenta',
            'form': {
                'datas': datas,
                'move_dest': self.move_dest,
                'cuentas_contables': self.cuentas_contables,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'num_cuenta_contables': num_cuentas_contables.id,
                'empresa': self.company.id,
                'saldo_inicial': self.saldo_inicial,
                'currency_id': self.currency_id.id,
                'ordenado_fecha': self.ordenado_fecha,
                'cuenta_especifica': self.cuenta_especifica
                },
        }
        return self.env.ref('inte_report_analitico_cuenta.action_reporte_analitico').report_action(self, data=data, config=False)


class ReportAnalyticForAccount(models.AbstractModel):

    _name = 'report.inte_report_analitico_cuenta.report_analytic_por_cuenta'

    @api.model
    def get_report_values(self, docids, data=None):

        ids = data['ids']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        move_dest = data['form']['move_dest']
        cuentas_contables = data['form']['cuentas_contables']
        num_cuenta_contables = data['form']['num_cuenta_contables']
        empresa = data['form']['empresa']
        saldo_inicial = data['form']['saldo_inicial']
        currency_id = data['form']['currency_id']
        ordenado_fecha = data['form']['ordenado_fecha']
        cuenta_especifica = data['form']['cuenta_especifica']

        docs = []
        num_cuenta_contables_obj = self.env['account.account']

        # Todas las cuentas
        if cuentas_contables == 'all':
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #todas las cuentas con cuentas con movimiento
        elif cuentas_contables == 'move' and cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #todas las cuentas con saldo diferente a cero
        elif cuentas_contables == 'saldo_cero' and cuenta_especifica == False:
            num_cuenta_contables_obj = num_cuenta_contables_obj.search([])
        #cuenta especifica con movimiento
        elif cuentas_contables == 'move' and cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(num_cuenta_contables)
        #cuenta especifica con saldo distinto a cero
        elif cuentas_contables == 'saldo_cero' and cuenta_especifica == True:
            num_cuenta_contables_obj = num_cuenta_contables_obj.browse(num_cuenta_contables)

        # accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        currency = self._get_moneda(currency_id)
        accounts_res = self._get_account_move_entry(num_cuenta_contables_obj, saldo_inicial, ordenado_fecha, cuentas_contables,move_dest,date_start,date_end,empresa,currency)
        datos_cuentas = self._datos_cuentas_contables(num_cuenta_contables)
        ordenado_fecha = self._get_orden(ordenado_fecha)
        #cambiar formato fecha
        formato_fecha = "%d/%m/%Y"
        fecha_actual = date.today()
        date_start = datetime.strftime(datetime.strptime(date_start, DATE_FORMAT), formato_fecha)
        date_end = datetime.strftime(datetime.strptime(date_end, DATE_FORMAT), formato_fecha)
        fecha_actual = datetime.strftime(datetime.strptime(str(fecha_actual), DATE_FORMAT), formato_fecha)

        # suma de debit, credit, balance para calcular los totales
        res_totales = dict((fn, 0.0) for fn in ['credit_total_bs', 'debit_total_bs', 'balance_total_bs',
                                                'credit_total_usd', 'debit_total_usd', 'balance_total_usd',
                                                'credit_total_eur', 'debit_total_eur', 'balance_total_eur'])
        total_credit_bs = 0.0
        total_debit_bs = 0.0
        total_balance_bs = 0.0
        total_credit_usd = 0.0
        total_debit_usd = 0.0
        total_balance_usd = 0.0
        total_credit_eur = 0.0
        total_debit_eur = 0.0
        total_balance_eur = 0.0
        for c in currency:
            for account in accounts_res:
                    # totales en bs
                if c.id == 4:
                    total_credit_bs += account['credit']
                    total_debit_bs += account['debit']
                    total_balance_bs += account['balance']
                    # totales en dolares
                elif c.id == 3:
                    total_credit_usd += account['credit_usd']
                    total_debit_usd += account['debit_usd']
                    total_balance_usd += account['balance_usd']
                elif c.id == 1:
                    # totales en euros
                    total_credit_eur += account['credit_eur']
                    total_debit_eur += account['debit_eur']
                    total_balance_eur += account['balance_eur']

        res_totales['credit_total_bs'] = total_credit_bs
        res_totales['debit_total_bs'] = total_debit_bs
        res_totales['balance_total_bs'] = total_balance_bs

        res_totales['credit_total_usd'] = total_credit_usd
        res_totales['debit_total_usd'] = total_debit_usd
        res_totales['balance_total_usd'] = total_balance_usd

        res_totales['credit_total_eur'] = total_credit_eur
        res_totales['debit_total_eur'] = total_debit_eur
        res_totales['balance_total_eur'] = total_balance_eur

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_now':fecha_actual,
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'move_dest': move_dest,
            'cuentas_contables': cuentas_contables,
            'num_cuenta_contables': num_cuenta_contables,
            'empresa': empresa,
            'saldo_inicial': saldo_inicial,
            'currency': currency,
            'ordenado_fecha': ordenado_fecha,
            'datos_cuentas': datos_cuentas[0],
            'Account': accounts_res,
            'Totales': res_totales
        }

    @api.model
    def _datos_cuentas_contables(self, num_cuenta_contables):
        '''Se obtienen los datos de las cuentas contables para la cabecera del reporte'''
        datos_cuentas = []
        if not num_cuenta_contables:
            datos_cuentas.append({'codigo': "Todos los códigos",
                                  'nombre': "Todas las cuentas"})
        else:
            account_obj = self.env['account.account']
            account_brw = account_obj.browse(num_cuenta_contables)

            datos_cuentas.append({'codigo': account_brw.code,
                                  'nombre':account_brw.name})
        return datos_cuentas

    @api.model
    def _get_orden(self,ordenado_fecha):
        if ordenado_fecha == True:
            ordenado_fecha = "Fecha"
        else:
            ordenado_fecha = "ninguno"
        return ordenado_fecha

    @api.model
    def _get_moneda(self,currency_id):
        currency_brw = []
        if not currency_id:
            currency_obj = self.env['res.currency'].search([])
            for c in currency_obj:
                currency_brw.append(c)
        else:
            currency_obj = self.env['res.currency'].browse(currency_id)
            for c in currency_obj:
                currency_brw.append(c)
        return currency_brw

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account, move_dest,date_start,date_end,empresa,currency):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)
                move_dest : tipo de asientos (validados=validate y todos=all)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """

        # seleccionar los tipos de asientos (todos o solo validados)
        if move_dest == 'all':
            state = 'all'
        else:
            state= 'posted'

        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=date_start, date_to=date_end, initial_bal=True, state=state,company_id=empresa, strict_range=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'


        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine.with_context(date_from=date_start, date_to=date_end, initial_bal=False, state=state, company_id=empresa, strict_range=True)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, '' AS move_id, c.symbol AS currency_code, p.name AS partner_name, a.id AS analytic_id, l.analytic_account_id AS analytic_account_id, a.code AS analytic_account_code, a.name AS analytic_account_name,\
            l.write_date AS write_date, l.move_id AS move_id\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            LEFT JOIN account_analytic_account a ON (l.analytic_account_id = a.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, a.id, l.analytic_account_id, m.id ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                if line.get('lname') == 'Initial Balance' or line.get('lname') == 'Balance Inicial':
                    pass
                else:
                    res['debit'] += line['debit']
                    res['credit'] += line['credit']
                    res['balance'] = line['balance']

            if display_account == 'all':
                account_res.append(res)
            if display_account == 'move' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'saldo_cero' and not currency[0].is_zero(res['balance']):
                account_res.append(res)

        for currency in currency:
            if currency.id == 3: # Si la moneda es dolar
                for account in account_res:
                    res = dict((fn, 0.0) for fn in ['credit_usd', 'debit_usd', 'balance_usd','tasa_usd'])
                    balance_usd = 0
                    credit_usd = 0
                    debit_usd = 0
                    for line in account.get('move_lines'):
                        res_line = dict((fn, 0.0) for fn in ['credit_usd', 'debit_usd', 'balance_usd','tasa_usd'])
                        if line.get('lname') == 'Initial Balance' or line.get('lname') == 'Balance Inicial':
                            fecha_movimiento = fields.Date.today()

                        else:
                            fecha_movimiento = line.get('write_date')

                        tasa_me = self._get_currency_rate(fecha_movimiento, currency)
                        res_line['credit_usd'] = line['credit']/ tasa_me
                        res_line['debit_usd'] = line['debit'] / tasa_me
                        res_line['balance_usd'] = line['balance'] / tasa_me
                        res_line['tasa_usd'] = tasa_me

                        credit_usd += res_line['credit_usd']
                        debit_usd += res_line['debit_usd']
                        balance_usd += res_line['debit_usd'] - res_line['credit_usd']
                        line.update(res_line)

                    res['balance_usd'] += balance_usd
                    res['credit_usd'] += credit_usd
                    res['debit_usd'] += debit_usd
                    account.update(res)
            elif currency.id == 1: #si la moneda es euro
                for account in account_res:
                    res = dict((fn, 0.0) for fn in ['credit_eur', 'debit_eur', 'balance_eur','tasa_eur'])
                    balance_usd = 0
                    credit_usd = 0
                    debit_usd = 0
                    for line in account.get('move_lines'):
                        res_line = dict((fn, 0.0) for fn in ['credit_eur', 'debit_eur', 'balance_eur','tasa_eur'])
                        if line.get('lname') == 'Initial Balance' or line.get('lname') == 'Balance Inicial':
                            fecha_movimiento = fields.Date.today()

                        else:
                            fecha_movimiento = line.get('write_date')

                        tasa_me = self._get_currency_rate(fecha_movimiento, currency)
                        res_line['credit_eur'] = line['credit']/ tasa_me
                        res_line['debit_eur'] = line['debit'] / tasa_me
                        res_line['balance_eur'] = line['balance'] / tasa_me
                        res_line['tasa_eur'] = tasa_me

                        credit_usd += res_line['credit_eur']
                        debit_usd += res_line['debit_eur']
                        balance_usd += res_line['debit_eur'] - res_line['credit_eur']
                        line.update(res_line)

                    res['balance_eur'] += balance_usd
                    res['credit_eur'] += credit_usd
                    res['debit_eur'] += debit_usd
                    account.update(res)

        return account_res

    @api.multi
    def _get_currency_rate(self,fecha_movimiento, currency_obj):
        tasa_me = 1
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id

        for currency in currency_obj:

            fecha_dia_rate = []
            fecha_dia_rate_ord = []
            rate_id = self.env['res.currency.rate'].search(
                [('company_id', '=', company_id), ('currency_id', '=', currency.id)])

            if rate_id:
                for a in rate_id:
                    fecha_rate = a.hora
                    fecha_dia_rate.append(fecha_rate)
                fecha_dia_rate.append(fecha_movimiento)
                fecha_dia_rate_ord = sorted(fecha_dia_rate)
                posicion = fecha_dia_rate_ord.index(fecha_movimiento)
                if posicion == 0:
                    fecha_anterior = fecha_dia_rate_ord[posicion +1]
                    rate_id = self.env['res.currency.rate'].search(
                        [('company_id', '=', company_id), ('hora', '=', fecha_anterior)])
                    if rate_id:
                        for r in rate_id:
                            tasa_me = r.rate_real
                    else:
                        tasa_me = 1
                elif posicion >= 1:
                    fecha_anterior = fecha_dia_rate_ord[posicion-1]
                    rate_id = self.env['res.currency.rate'].search(
                        [('company_id', '=', company_id), ('hora', '=', fecha_anterior)])
                    if rate_id:
                        for r in rate_id:
                            tasa_me = r.rate_real
                    else:
                        tasa_me = 1
            else:
                pass
        return tasa_me






