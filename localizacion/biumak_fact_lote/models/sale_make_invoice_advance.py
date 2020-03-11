import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    @api.multi
    def create_invoices(self):
        super().create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        id_orden= self._context.get('active_ids', [])

        lista_stock_picking=self.env['stock.picking'].search([('sale_id','=',id_orden)])
        for detalle_picking in lista_stock_picking:
            id_picking=detalle_picking.id
        #raise UserError(_('hola id_picking %s')%id_picking)

        lista_linea_orden=self.env['sale.order.line'].search([('order_id','=',id_orden)])
        for detalle_linea in lista_linea_orden:
            producto_id=detalle_linea.product_id.id # sirve
            cantidad=detalle_linea.product_uom_qty
            #raise UserError(_('cantidad = %s')%cantidad)
            lista_move_line=self.env['stock.move.line'].search([('picking_id','=',id_picking),('product_id','=',producto_id),('ordered_qty','=',cantidad)])
            #raise UserError(_('lista_move_line = %s')%lista_move_line)
            for detalle_move_line in lista_move_line:
                nro_lote=detalle_move_line.lot_id.name
                #_logger.info("\n\n nro_lote %s \n\n",nro_lote)
               
                lista_account_invoice_line = self.env['account.invoice.line'].search([('origin','=',sale_orders.name),('product_id','=',producto_id),('quantity','=',cantidad)])
                #raise UserError(_('lista_account_invoice_line = %s')%lista_account_invoice_line)
                #_logger.info(" \n\n\n\n lista_account_invoice_line  %s \n\n\n\n",lista_account_invoice_line)
                for det_account_invoice_line in lista_account_invoice_line:
                    self.env['account.invoice.line'].browse(det_account_invoice_line.id).write({'nro_lote': nro_lote})
                    #_logger.info("\n\n self.env['account.invoice.line'] nro_lote %s \n\n",nro_lote)
            #lista.append(detalle_linea.product_id.id)            
            #_logger.info("\n\n var %s \n\n",var)
        #raise UserError(_('stop'))