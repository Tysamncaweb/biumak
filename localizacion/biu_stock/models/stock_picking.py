# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPickingAdaptation(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    var_id = fields.Char()
    project = fields.Many2one('project.project')
    observations = fields.Char(size=250)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('delivered','Entrega Realizada'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")


    @api.onchange('var_id')
    def assign_string(self):
        if self._context.get('default_picking_type_id'):
            var = self._context.get('default_picking_type_id')
            self.var_id = var

    @api.model
    def create(self,vals):
        vals['var_id'] = vals.get('picking_type_id')
        return super(StockPickingAdaptation, self).create(vals)


