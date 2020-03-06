# coding: utf-8
from odoo import models, fields, api
from odoo.tools.translate import _
from datetime import datetime,date
from dateutil import relativedelta


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nro_ctrl = fields.Char(
        'Control Number', size=32,
        help="Number used to manage pre-printed invoices, by law you will"
             " need to put here this number to be able to declarate on"
             " Fiscal reports correctly.", store=True)

    @api.multi
    def _get_company(self):
        uid = self._uid
        res_company = self.env['res.company'].search([('id', '=', uid)])
        return res_company

    @api.multi
    def action_invoice_open(self):
        var = super(AccountInvoice, self).action_invoice_open()
        if self.type in ('out_invoice', 'out_refund'):
            if not self.nro_ctrl:
                self.nro_ctrl = self._get_sequence_code()
                self.write({'nro_ctrl_sale': self.nro_ctrl})

        return var

    @api.multi
    def _get_sequence_code(self):
        '''metodo que crea la secuencia del número de control, si no esta creada crea una con el
        nombre: 'l10n_nro_control'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_nro_control_sale'
        company_id= self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        self.nro_ctrl = IrSequence.next_by_code(SEQUENCE_CODE)

        # if a sequence does not yet exist for this company create one
        #if not self.nro_ctrl:
        #    IrSequence.sudo().create({
        #        'prefix' : '00--',
        #        'name': 'Localización Venezolana numero de control %s' % company_id.id,
        #        'code': SEQUENCE_CODE,
        #        'implementation': 'no_gap',
        #        'padding': 6,
        #        'number_increment': 1,
        #        'company_id': company_id.id,
        #    })
        #    self.nro_ctrl_sale = IrSequence.next_by_code(SEQUENCE_CODE)
        return self.nro_ctrl