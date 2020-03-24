# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Cambios, rsosa:
#
#    - Se sobreescribe el metodo 'first_move_line_get' para incluir el ID de la
#      cuenta transitoria de Banco a la hora de realizar un pago con cheque
#
##############################################################################

from odoo import fields, models, api, exceptions,_
from email.utils import formataddr
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning
import re
from ast import literal_eval



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    Rif_prueba = fields.Char(string="R.I.F", size=15, required=True, related='partner_id.vat')
    phone = fields.Char(related='partner_id.phone', store=True, string="Telefono" )
    adress_purchase = fields.Char(size=60 , string="Dirección Fiscal", related='partner_id.street')
    zip_purchase = fields.Char(related='partner_id.zip')
    city_purchase = fields.Char(related='partner_id.city')
    state_purchase = fields.Many2one("res.country.state", string='State', ondelete='restrict', related='partner_id.state_id')
    country_purchase =fields.Many2one('res.country', string='Country', ondelete='restrict', related='partner_id.country_id')
    amount_untaxed = fields.Monetary(string='Subtotal', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='I.V.A. (16%)', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Precio Total', store=True, readonly=True, compute='_amount_all')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    pres_id = fields.Char(string='Presentación')
    num_product = fields.Char(string='Nro.', size=4)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('product.uom', string='Unit', required=True)
    product_image = fields.Binary(
        'Product Image', related="product_id.image",
        help="Non-stored related field to allow portal user to see the image of the product he has ordered")
    move_ids = fields.One2many('stock.move', 'purchase_line_id', string='Reservation', readonly=True,
                               ondelete='set null', copy=False)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    state = fields.Selection(related='order_id.state', store=True)
    invoice_lines = fields.One2many('account.invoice.line', 'purchase_line_id', string="Bill Lines", readonly=True,
                                    copy=False)
    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty",
                                digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty",
                                digits=dp.get_precision('Product Unit of Measure'), store=True)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    move_dest_ids = fields.One2many('stock.move', 'created_purchase_line_id', 'Downstream Moves')
    product_id = fields.Many2one('product.product', string='Cod. producto', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    num_product_sale = fields.Integer()
    num_lot = fields.Char()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    num_product_sale = fields.Integer(string='Nro.')
    num_lot = fields.Char(string='Nro.')


class Partner(models.Model):
    _description = 'Contact'
    _inherit ="res.partner"


    country_id = fields.Many2one('res.country', string='Country')
    vat = fields.Char(string='Rif', help="Tax Identification Number. "
                                         "Fill  it if the company is subjected to taxes. "
                                         "Used by the some of the legal statements.")


    @api.onchange('country_id')
    def _compute_country(self):
        if not self.country_id:
            country_id = self.env['res.country'].search([('code', 'like', 'VE')])
            self.country_id =country_id.id
        return


    