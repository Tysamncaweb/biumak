# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
from io import BytesIO
import xlwt, base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT




class BankReconciliation(models.Model):
    _name = 'bank.reconciliation'
    _description = 'Open bank reconciliation'

    journal_id = fields.Many2one('account.journal', required=True)
    start_date = fields.Date(required=True, default=fields.Datetime.now)
    end_date = fields.Date(required=True, default=fields.Datetime.now)
    currency_id = fields.Many2one('res.currency', required=True)
    company = fields.Many2one('res.company', required=True)



    @api.multi
    def generate_bank_reconciliation_pdf(self, data):
        data = {
            'ids': self.ids,
            'model': 'report.intel_bank_reconciliation.report_bank_reconciliation',
            'form': {
                'date_start': self.start_date,
                'date_stop': self.end_date,
                'company': self.company.id,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
            },
            'context': self._context
        }
        return self.env.ref('intel_bank_reconciliation.action_report_bank_reconciliation').report_action(self, data=data, config=False)


class ReportBankReconciliation(models.AbstractModel):
    _name = 'report.intel_bank_reconciliation.report_bank_reconciliation'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        end_date = data['form']['date_stop']
        company_id = data['form']['company']
        journal_id = data['form']['journal_id']
        currency_id = data['form']['currency_id']
        docs = []
        abono = 0
        cargo = 0
        saldo_final = 0
        diferencia = 0

        today = datetime.now()
        hora = today.hour
        month = format(today.month)
        year = format(today.year)

        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        mes = meses[int(month) - 1]
        if hora >= 13:
            horas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            hora = horas[hora - 13]
            mt = 'PM'
        else:
            mt = 'AM'
        if hora == 12:
            mt = 'PM'

        minute = today.minute
        if minute < 10:
            time = str(hora) + ':' + '0' + str(minute) + ' ' + mt
        else:
            time = str(hora) + ':' + str(minute) + ' ' + mt


        currency = self.env['res.currency'].search([('id', '=', currency_id)])
        company = self.env['res.company'].search([('id', '=', company_id)])
        account_journal = self.env['account.journal'].search([('id', '=', journal_id)])
        account_account = self.env['account.account'].search([('id', '=', account_journal.default_credit_account_id.id)])
        banco = self.env['account.bank.statement'].search([('journal_id', '=', journal_id),
                                                           ('company_id', '=', company_id),
                                                           ('date', '>=', date_start),
                                                           ('date', '<=', end_date)])
        if banco:
            amount_open = banco[-1].balance_start * currency.rate_rounding
            saldo_cuenta = banco[-1].balance_end_real * currency.rate_rounding
        else:
            amount_open = banco.balance_start * currency.rate_rounding
            saldo_cuenta = banco.balance_end_real * currency.rate_rounding

        for banca in banco:
            banco_line = self.env['account.bank.statement.line'].search([('statement_id', '=', banca.id),
                                                                         ('company_id', '=', banca.company_id.id),
                                                                         ('date', '>=', date_start),
                                                                         ('date', '<=', end_date),
                                                                         ('move_name', '=', False)])
            banco_line_all = self.env['account.bank.statement.line'].search([('statement_id', '=', banca.id),
                                                                         ('company_id', '=', banca.company_id.id),
                                                                         ('date', '>=', date_start),
                                                                         ('date', '<=', end_date)])
            for a in banco_line_all:
                if a.amount > 0:
                    abono += a.amount * currency.rate_rounding
                else:
                    cargo += a.amount * currency.rate_rounding
            for b in banco_line:
                docs.append({
                    'description': b.name,
                    'amount': b.amount * currency.rate_rounding,
                    'ref': b.ref,
                    'date': b.date,
                })
        saldo_final = (amount_open + abono + cargo) * currency.rate_rounding
        diferencia = abono + cargo


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'end_date': end_date,
            'start_date': date_start,
            'company': company,
            'account_account': account_account,
            'account_journal': account_journal,
            'today': today,
            'hora': time,
            'mes': mes,
            'ano': year,
            'currency': currency,
            'cargo': cargo,
            'abono': abono,
            'amount_open': amount_open,
            'docs': docs,
            'saldo_final': saldo_final,
            'saldo_cuenta': saldo_cuenta,
            'diferencia': diferencia,
            }

'''
class ReportResultReconciliation(models.AbstractModel):
    _name = 'report.intel_bank_reconciliation.report_result_reconciliation'

    @api.model
    def get_report_values(self, docids, data=None):

        today = datetime.now()
        month = format(today.month)
        year = format(today.year)

        meses = ['Ene.', 'Feb.', 'Mar.', 'Abr.', 'May.', 'Jun.', 'Jul.', 'Ago.', 'Sep.', 'Oct.', 'Nov.', 'Dic.']


        mes = meses[int(month) - 1]

        hora = today.hour
        minute = today.minute
        if minute < 10:
            time = str(hora) + ':' + '0' + str(minute)
        else:
            time = str(hora) + ':' + str(minute)

        return {
            'today': today,
            'hora': time,
            'mes': mes,
            'year': year[2:4],
            }'''

class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"
    _description = "Bank Statement"

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]})
    journal_type = fields.Selection(related='journal_id.type', help="Technical field used for usability purposes")