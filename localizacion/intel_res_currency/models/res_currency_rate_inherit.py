# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
#Moneda..
class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    hora = fields.Datetime('Fecha y Hora', default=lambda self: fields.datetime.today(), required=True)
    rate_real = fields.Float(digits=(12, 2), help='se introduce la tasa real del mercado')
    rate = fields.Float(digits=(12, 9), help='The rate of the currency to the currency of rate 1')
    _sql_constraints = [('unique_name_per_day', 'CHECK(1=1)', 'Only one currency rate per day allowed!')]


    @api.onchange('rate_real', 'hora')
    def fecha_y_hora(self):
        self.name = self.hora[0:10]
        if self.rate_real != 0.0:
            rate = (1 / self.rate_real)
            self.rate = rate


class Currency(models.Model):
    _inherit = "res.currency"

    rate_real = fields.Float(compute='_compute_current_rate', digits=(12, 2), help='se introduce la tasa real del mercado')
    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 9),
                        help='The rate of the currency to the currency of rate 1.')
    rate_rounding = fields.Float(compute='_compute_current_rate', digits=(12, 9), help='la tasa inversa del mercado')


    @api.multi
    def _compute_current_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        rate_id = []
        hoy = fields.Date.today()
        for currency in self:
            fecha_next = []
            fecha_dia_rate = []
            rate_id = self.env['res.currency.rate'].search([('company_id','=',company_id),('currency_id', '=', currency.id)])
            if rate_id:
                for a in rate_id:
                    if a.name == hoy:
                        fecha_dia_rate.append(a.id)
                    else:
                        fecha_next.append(a.id)
                fecha_dia_rate.sort(reverse=True)
                fecha_next.sort(reverse=True)
                if fecha_dia_rate:
                    rate_id = self.env['res.currency.rate'].search([('id', '=', fecha_dia_rate[0])])
                    currency.rate = rate_id.rate
                    currency.rate_real = rate_id.rate_real
                    currency.rate_rounding = rate_id.rate
                    currency.write({'rate_real': currency.rate_real,
                                    'rate_rounding':currency.rate_rounding,
                                    })
                else:
                    rate_id_next = self.env['res.currency.rate'].search([('id', '=', fecha_next[0])])
                    currency.rate = rate_id_next.rate
                    currency.rate_real = rate_id_next.rate_real
                    currency.rate_rounding = rate_id_next.rate
                    currency.write({'rate_real': currency.rate_real,
                                    'rate_rounding': currency.rate_rounding,
                                    })


    @api.multi
    @api.depends('rate_ids.name')
    def _compute_date(self):
        fecha = []
        fecha1 = []
        for currency in self:
            if currency.rate_ids:
                for a in currency.rate_ids:
                    fecha.append(a.id)
                fecha.sort(reverse=True)
                fecha_rate = self.env['res.currency.rate'].search([('id', '=', fecha[0])])
                if fecha_rate:
                    currency.date = fecha_rate.name

    def _get_conversion_rate(self, from_currency, to_currency):
        from_currency = from_currency.with_env(self.env)
        to_currency = to_currency.with_env(self.env)
        a = 0
        if from_currency.rate != 0:
            a = to_currency.rate / from_currency.rate
        return a

class account_move(models.Model):
    _inherit = 'account.move'

    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        mlo = self.env['account.move.line'].search([('move_id', '=',self.ids[0])])
        if not mlo.reconcile:
            super(account_move, self).assert_balanced(fields)
        return True
