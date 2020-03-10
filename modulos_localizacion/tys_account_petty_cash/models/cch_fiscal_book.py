# coding: utf-8
###########################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo import fields, models, api, exceptions


class Invoice_petty_cash(models.Model):
    _name = 'invoice.fiscal.book'
    _description = 'Invoice petty cash'

    def _get_company(self):
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        return res_company

    @api.multi
    def sin_fiscal_book(self, cr):

        """
        Añadir Factura en libro de compras"""
        invoice = self.env['invoice.petty.cash'].search([('id', '=', cr['active_id'])])
        invoice.write({'sin_cred': True})

        if invoice.tax:
            iva = invoice.iva
            tax = invoice.tax
            id = invoice.id
        else:
            iva = 0
            tax = self.env['account.tax'].search([('amount', '=', 0),
                                                  ('type_tax_use', '=', 'purchase')])

        val_invoice = {
            'number': invoice.type_petty_cash,
            'move_name': invoice.type_petty_cash,
            'supplier_invoice_number': invoice.name,
            'partner_id': invoice.petty_cash_partner.id,
            # 'rif': invoice.rif,
            'nro_ctrl': invoice.invoice_nro_ctrl,
            'date_document': invoice.date_petty_cash,
            'date_invoice': invoice.date_account,
            'amount_total': invoice.amount_total,
            'residual': invoice.amount_gravable + invoice.amount_exento + iva,
            'residual_signed': invoice.amount_total,
            'residual_company_signed': invoice.amount_total,
            'amount_untaxed': invoice.amount_total - iva,
            'amount_tax': iva,
            'state': 'open',
            'sin_cred': False,
            'type': 'in_invoice',
            'factura_id': invoice.id,
            'reference': 'CAJA CHICA',
        }
        move_obj_invoice = self.env['account.invoice']
        invoice_petty_cash = move_obj_invoice.create(val_invoice)
        company_id = self._get_company()
        invoice.factura_move = invoice_petty_cash
        uid = self._uid

        invoice_tax = {
            'invoice_id': invoice_petty_cash.id,
            'name': tax.name,
            'tax_id': tax.id,
            'account_id': tax.account_id.id,
            'account_analytic_id': invoice.cuenta_analitica.id,
            'amount': iva,
            'company_id': company_id.id,
            'base': invoice.amount_total - iva,
        }
        move_obj_invoice_tax = self.env['account.invoice.tax']
        invoice_tax_petty_cash = move_obj_invoice_tax.create(invoice_tax)

        self.move_invoice_petty_cash_ = {
            'name': invoice.name,
            'origin': invoice.name,
            'invoice_id': invoice_petty_cash.id,
            'company_id': company_id.id,
            'account_id': invoice.petty_cash_gastos.id,
            'ref': invoice.code.name,
            'account_analytic_id': invoice.cuenta_analitica.id,
            # 'invoice_line_tax_id': [(6, 0, invoice.tax.id)],
            'price_unit': invoice.amount_gravable + invoice.amount_exento,
            'price_subtotal': invoice.amount_gravable + invoice.amount_exento,
            'price_total': invoice.amount_exento + invoice.amount_gravable + iva,
        }

        asiento = self.move_invoice_petty_cash_
        move_line_obj = self.env['account.invoice.line']
        move_line_id1 = move_line_obj.create(asiento)

        invoice = self.env['invoice.petty.cash'].search([('id', '=', cr['active_id'])])
        invoice.write({'sin_cred': True})

        self.env.cr.execute(
            """INSERT INTO account_invoice_line_tax
               (invoice_line_id, tax_id)
               VALUES (%s, %s)""", (move_line_id1.id, tax.id))

        if invoice.etiqueta_analitica:
            self.env.cr.execute(
                """INSERT INTO account_analytic_tag_account_invoice_line_rel
                   (account_invoice_line_id, account_analytic_tag_id)
                   VALUES (%s, %s)""", (move_line_id1.id, invoice.etiqueta_analitica.id))



