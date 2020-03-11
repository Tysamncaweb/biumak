# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
from io import BytesIO
import xlwt, base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class modificacion_name_get(models.Model):
    _inherit = 'res.currency.rate'

    @api.multi
    def name_get(self):
        result = []
        for res in self:
            name = str(res.rate_real) + ' - ' + str(res.hora)
            result.append((res.id, name))
        return result

class RetentionISLR(models.Model):
    _name = 'checking.balance'
    _description = 'Open checking Balance'

    target_movement = fields.Selection([
        (0, 'Todos los asientos validados'),
        (1, 'Todos los asientos')
    ], required=True, string="Movimientos Destino")

    show_accounts = fields.Selection([
        (0, 'Con movimientos'),
        (1, 'Con saldo distinto a 0')
    ], string="Mostrar Cuentas", required=True)

    report_format = fields.Selection([
        (0, 'PDF'),
        (1, 'XLS')
    ], string="Formato del Reporte", required=True)
    company = fields.Many2one('res.company', required=True)
    start_date = fields.Date(required=True,)
    end_date = fields.Date(required=True, default=fields.Datetime.now)
    balance = fields.Boolean(default=False)
    currency_id = fields.Many2one('res.currency', required=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    tasa = fields.Many2one('res.currency.rate', string="Tasa Monetaria")

    @api.multi
    def amount_initial1(self, account_account, show_accounts, balance, start_date, end_date, company, state, currency, tasa):
        cuentas = []


        if currency.id == 4:
            currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency.id)])
        else:
            currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])

        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in account_account.ids}
        init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=start_date,
                                                                                  date_to=end_date,
                                                                                  initial_bal=True,
                                                                                  state=state,
                                                                                  company_id=company,
                                                                                  strict_range=True)._query_get()
        init_wheres = [""]
        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)
        filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line',
                                                                                  'l')
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
        params = (tuple(account_account.ids),) + tuple(init_where_params)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            move_lines[row.pop('account_id')].append(row)

        sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine.with_context(date_from=start_date, date_to=end_date,
                                                                   initial_bal=False, state=state, company_id=company,
                                                                   strict_range=True)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines..
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                        m.name AS move_name, '' AS move_id, c.symbol AS currency_code, p.name AS partner_name,\
                        l.write_date AS write_date, l.move_id AS move_id\
                        FROM account_move_line l\
                        JOIN account_move m ON (l.move_id=m.id)\
                        LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                        LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                        LEFT JOIN account_analytic_account a ON (l.analytic_account_id = a.id)\
                        JOIN account_journal j ON (l.journal_id=j.id)\
                        JOIN account_account acc ON (l.account_id = acc.id) \
                        WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, a.id, m.id ORDER BY ''' + sql_sort)
        params = (tuple(account_account.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += (line['debit'] - line['credit']) / currency_line.rate_real
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        for account in account_account:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit'] / currency_line.rate_real if line['lname'] != 'Initial Balance' else False
                res['credit'] += line['credit'] / currency_line.rate_real if line['lname'] != 'Initial Balance' else False
                res['balance'] = line['balance'] / currency_line.rate_real

            if show_accounts == 0 and res.get('move_lines'):
                cuentas.append(res)
            if show_accounts == 1 and not currency[0].is_zero(res['balance']):
                cuentas.append(res)
        return cuentas

    @api.multi
    def suma_totales(self, cuentas, currency, tasa):
        if currency.id == 4:
            currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency.id)])
        else:
            currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])

        res_totales = dict((fn, 0.0) for fn in ['credit_total', 'debit_total', 'balance_total'])
        total_credit = 0.0
        total_debit = 0.0
        total_balance = 0.0

        for account in cuentas:
            total_credit += account['credit']
            total_debit += account['debit']
            total_balance += account['balance']

        res_totales['credit_total'] = total_credit / currency_line.rate_real
        res_totales['debit_total'] = total_debit / currency_line.rate_real
        res_totales['balance_total'] = total_balance / currency_line.rate_real

        return res_totales

    @api.multi
    def generate_checking_balance(self, data):
        if self.report_format == False:
            data = {
                'ids': self.ids,
                'model': 'report.intel_checking_balance.report_checking_balance',
                'form': {
                    'date_start': self.start_date,
                    'date_stop': self.end_date,
                    'currency_id': self.currency_id.name,
                    'currency_id1': self.currency_id.id,
                    'target_movement': self.target_movement,
                    'show_accounts': self.show_accounts,
                    'report_format':self.report_format,
                    'company': self.company.id,
                    'balance': self.balance,
                    'tasa': self.tasa.id,
                    },
                'context': self._context
            }
            return self.env.ref('intel_checking_balance.action_report_checking_balance').report_action(self, data=data, config=False)
        else:
            unico = []
            today = datetime.now()
            hoy = date.today()
            format_new = "%d/%m/%Y"
            hoy_date = datetime.strftime(hoy, format_new)
            start_date1 = datetime.strftime(datetime.strptime(self.start_date,DEFAULT_SERVER_DATE_FORMAT),format_new)
            end_date1 = datetime.strftime(datetime.strptime(self.end_date,DEFAULT_SERVER_DATE_FORMAT),format_new)
            hora = today.hour
            minute = today.minute
            if minute < 10:
                time = str(hora) + ':' + '0' + str(minute)
            else:
                time = str(hora) + ':' + str(minute)


            self.ensure_one()
            fp = BytesIO()
            wb = xlwt.Workbook(encoding='utf-8')
            writer = wb.add_sheet('Nombre de hoja')

            header_content_style = xlwt.easyxf("font: name Helvetica size 80 px, bold 1, height 400;")
            sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")
            sub_header_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
            sub_header_style_bold1 = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; align: horiz right;", num_format_str='#,##0.00')
            sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
            line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;", num_format_str='#,##0.00')
            line_content_style_totales = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right;", num_format_str='#,##0.00')

            row = 1
            col = 0

            #writer.write_merge(row, row, 0, header_cols, "Información de contactos",)
            writer.row(row).height = 500
            writer.write_merge(row, row, 2, 4, str(self.company.name), header_content_style)



            row +=1

            writer.write_merge(row, row, 2, 4, "Número de identificación Fiscal:", sub_header_style_bold)
            writer.write_merge(row, row, 5, 6, str(self.company.vat), sub_header_content_style)
            row +=1

            writer.write_merge(row, row, 10,10, "Fecha:", sub_header_style_bold)

            writer.write_merge(row, row, 11, 11, hoy_date, sub_header_content_style)
            row +=1

            writer.write_merge(row, row, 10,10, "Hora:", sub_header_style_bold)
            writer.write_merge(row, row, 11,11,  time, sub_header_content_style)
            row += 2
            writer.row(row).height = 500
            writer.write_merge(row, row, 5, 9, "Balance de Comprobación", header_content_style)
            row +=1

            writer.write_merge(row, row, 5, 5, "Desde:", sub_header_style_bold)
            writer.write_merge(row, row, 6, 6, start_date1, sub_header_content_style)

            writer.write_merge(row, row, 8, 8, "Hasta:", sub_header_style_bold)
            writer.write_merge(row, row, 9, 9, end_date1, sub_header_content_style)
            row += 1
            writer.write_merge(row, row, 7, 7, "Moneda:", sub_header_style_bold)
            writer.write_merge(row, row, 8, 8, str(self.currency_id.name), sub_header_content_style)
            row +=2
            col= 1

            writer.write_merge(row, row, 1, 4, "Cuenta", sub_header_style)
            if self.balance == True:
                writer.write_merge(row, row, 5, 6, "Saldo Inicial", sub_header_style)
            writer.write_merge(row, row, 7, 8, "Débito", sub_header_style)
            writer.write_merge(row, row, 9, 10, "Crédito", sub_header_style)
            writer.write_merge(row, row, 11, 12, "Saldo", sub_header_style)

            account_account = self.env['account.account'].search([('id', '!=', 0)])
            currency = self.env['res.currency'].search([('id', '=', self.currency_id.id)])

            if currency.id == 4:
                currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency.id)])
            else:
                currency_line = self.env['res.currency.rate'].search([('id', '=', self.tasa.id)])

            # TODOS LOS ASIENTOS VALIDADOS CON MOVIMIENTOS
            if self.target_movement == False and self.show_accounts == False:
                state = 'posted'

            # TODOS LOS ASIENTOS VALIDADOS CON SALDO DISTINTO A 0
            if self.target_movement == False and self.show_accounts == 1:
                state = 'posted'

            # TODOS LOS ASIENTOS CON MOVIMIENTOS 0
            if self.target_movement == 1 and self.show_accounts == 0:
                state = 'all'
            # TODOS LOS ASIENTOS CON SALDO DISTINTO A 0
            if self.target_movement == 1 and self.show_accounts == 1:
                state = 'all'
            cuentas = self.amount_initial1(account_account, self.show_accounts, self.balance, self.start_date, self.end_date, self.company.id, state, currency, self.tasa.id)
            suma = self.suma_totales(cuentas, currency, self.tasa.id)

            for a in cuentas:
                row += 1
                writer.write_merge(row, row, 1, 1, a['code'],sub_header_style_bold)
                writer.write_merge(row, row, 2, 6, a['name'], sub_header_style_bold)
                writer.write_merge(row, row, 7, 8, a['debit'], sub_header_style_bold1)
                writer.write_merge(row, row, 9, 10,a['credit'], sub_header_style_bold1)
                writer.write_merge(row, row, 11, 12, a['balance'], sub_header_style_bold1)


                if self.balance == True:
                    row += 1
                    for line in a['move_lines']:
                        if line['lname'] == 'Initial Balance' or line['lname'] == 'Balance Inicial':
                            writer.write_merge(row, row, 1, 4, "Balance Inicial", sub_header_content_style)
                            writer.write_merge(row, row, 5, 6, line['balance'] / currency_line.rate_real,line_content_style)



            row +=1
            writer.write_merge(row, row, 1, 4, "Total", sub_header_style)
            writer.write_merge(row, row, 7, 8, suma['debit_total'], line_content_style_totales)
            writer.write_merge(row, row, 9, 10, suma['credit_total'], line_content_style_totales)
            writer.write_merge(row, row, 11, 12, suma['balance_total'], line_content_style_totales)

            col = 1



            wb.save(fp)

            out = base64.encodestring(fp.getvalue())
            self.write({'state': 'get', 'report': out, 'name': 'balance_Comprobación.xls'})



            return {
                'type': 'ir.actions.act_window',
                'res_model': 'checking.balance',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }


class ReportRetentionISLR(models.AbstractModel):
    _name = 'report.intel_checking_balance.report_checking_balance'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        end_date = data['form']['date_stop']
        currency_id = data['form']['currency_id']
        currency_id1 = data['form']['currency_id1']
        target_movement = data['form']['target_movement']
        show_accounts = data['form']['show_accounts']
        company = data['form']['company']
        balance = data['form']['balance']
        tasa = data['form']['tasa']
        report_format = data['form']['report_format']
        today = datetime.now()
        hora = today.hour
        minute = today.minute
        if minute < 10:
            time = str(hora) + ':' + '0' + str(minute)
        else:
            time = str(hora) + ':' + str(minute)

        unico = []


        account_account = self.env['account.account'].search([('id', '!=', 0)])
        currency = self.env['res.currency'].search([('id', '=', currency_id1)])

        if currency_id1 == 4:
            currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency_id1)])
        else:
            currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])


        # TODOS LOS ASIENTOS VALIDADOS CON MOVIMIENTOS
        if target_movement == False and show_accounts == False:
            state = 'posted'

        # TODOS LOS ASIENTOS VALIDADOS CON SALDO DISTINTO A 0
        if target_movement == False and show_accounts == 1:
            state = 'posted'

        # TODOS LOS ASIENTOS CON MOVIMIENTOS 0
        if target_movement == 1 and show_accounts == 0:
            state = 'all'
        # TODOS LOS ASIENTOS CON SALDO DISTINTO A 0
        if target_movement == 1 and show_accounts == 1:
            state = 'all'
        cuentas = self.amount_initial(account_account, show_accounts, balance, date_start, end_date, company,currency, state, currency_id1, tasa)
        suma = self.suma_totales(cuentas, currency_id1,tasa)



        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'end_date': end_date,
            'start_date': date_start,
            'today': today,
            'currency_id': currency_id,
            'balance': balance,
            'hora': time,
            'cuentas': cuentas,
            'suma': suma,
            'currency_line': currency_line.rate_real,
        }

    @api.multi
    def amount_initial(self, account_account,show_accounts, balance,date_start,end_date,company,currency, state, currency_id1, tasa):
        cuentas = []
        cuentas1 =[]
        if currency_id1 == 4:
            currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency_id1)])
        else:
            currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in account_account.ids}
        init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=date_start,
                                                                                  date_to=end_date,
                                                                                  initial_bal=True,
                                                                                  state=state,
                                                                                  company_id=company,
                                                                                  strict_range=True)._query_get()
        init_wheres = [""]
        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        init_filters = " AND ".join(init_wheres)
        filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line',
                                                                                  'l')
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
        params = (tuple(account_account.ids),) + tuple(init_where_params)
        cr.execute(sql, params)
        for row in cr.dictfetchall():
            move_lines[row.pop('account_id')].append(row)

        sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine.with_context(date_from=date_start, date_to=end_date,
                                                                   initial_bal=False, state=state, company_id=company,
                                                                   strict_range=True)._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
                    m.name AS move_name, '' AS move_id, c.symbol AS currency_code, p.name AS partner_name,\
                    l.write_date AS write_date, l.move_id AS move_id\
                    FROM account_move_line l\
                    JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_analytic_account a ON (l.analytic_account_id = a.id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    JOIN account_account acc ON (l.account_id = acc.id) \
                    WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name, a.id, m.id ORDER BY ''' + sql_sort)
        params = (tuple(account_account.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                #if line['debit'] != 0:
                balance += (line['debit'] - line['credit'])/currency_line.rate_real
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)


        for account in account_account:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']/currency_line.rate_real if line['lname'] != 'Initial Balance' else False
                res['credit'] += line['credit']/currency_line.rate_real if line['lname'] != 'Initial Balance' else False
                res['balance'] = line['balance']/currency_line.rate_real


            if show_accounts == 0 and res.get('move_lines'):
                cuentas.append(res)
            if show_accounts == 1 and not currency[0].is_zero(res['balance']):
                cuentas.append(res)
        return cuentas

    @api.multi
    def suma_totales(self, cuentas, currency_id1,tasa):
        if currency_id1 == 4:
            currency_line = self.env['res.currency.rate'].search([('currency_id', '=', currency_id1)])
        else:
            currency_line = self.env['res.currency.rate'].search([('id', '=', tasa)])

        res_totales = dict((fn, 0.0) for fn in ['credit_total', 'debit_total', 'balance_total'])
        total_credit = 0.0
        total_debit = 0.0
        total_balance = 0.0

        for account in cuentas:
            total_credit += account['credit']
            total_debit += account['debit']
            total_balance += account['balance']

        res_totales['credit_total'] = total_credit/currency_line.rate_real
        res_totales['debit_total'] = total_debit/currency_line.rate_real
        res_totales['balance_total'] = total_balance/currency_line.rate_real
        return res_totales

