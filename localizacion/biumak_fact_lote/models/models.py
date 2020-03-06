# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class LoteFactura(models.Model):

    _inherit = 'account.invoice.line'
    lot_id = fields.Many2one('stock.production.lot', string='Lote de producto')

    def get_numero_lote(self):


        pass




