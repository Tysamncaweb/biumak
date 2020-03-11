# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#import logging
from odoo import api, fields, models

#_logger=logging.getLoger(__name__)

class LoteFactura(models.Model):

    _inherit = 'account.invoice.line'
    nro_lote = fields.Char(string=' Nro Lote')