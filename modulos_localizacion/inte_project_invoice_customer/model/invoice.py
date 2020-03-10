# coding: utf-8
###########################################################################
from collections import Counter

from odoo import api
from odoo import fields, models


class AccountInvoice(models.Model):
    '''Esta clase es para crear en la factura el saldo de anticipo del cliente o proveedor'''
    _inherit = 'account.invoice'

    account_analytic_name = fields.Char('Project', compute='_get_account_analytic',
                                      help="Referencia al proyecto a la cual pertenece la factura de cliente")

    @api.onchange('account_analytic_id')
    def _get_account_analytic(self):
        account_analytic= []
        for invoice in self:
            if invoice.type == 'out_invoice' or invoice.type == 'out_refund':
                invoice_lines = invoice.env['account.invoice.line'].search([('invoice_id', '=', invoice.id)])
                project_repetidos = []
                project_unicos = []

                for line in invoice_lines:
                    if line.account_analytic_id.name:
                        account_analytic.append(line.account_analytic_id.name)

                for line in account_analytic:
                    if line not in project_unicos:
                        project_unicos.append(line)
                    else:
                        if line not in project_repetidos:
                            project_repetidos.append(line)

                invoice.account_analytic_name = ",".join(project_unicos)
        return


