# coding: utf-8
# from openerp import fields, models, api
from odoo import models, fields, api, exceptions
#from openerp.exceptions import Warning
from datetime import datetime, time, date

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'


    util_days_to_pay = fields.Integer('Dias a pagar utilidades', size=3)
    is_util = fields.Boolean('Es Utilidades')
    is_anticipo = fields.Boolean('Anticipos')



    @api.onchange('struct_id')
    def onchange_struct_id(self):
        res = {}
        is_util = False
        struct_obj = self.env['hr.payroll.structure']
        for s in struct_obj.browse(self.id):
            if s.struct_category == 'especial' and 'utilidad' in s.struct_id_payroll_category:
                is_util = True
        res = {'value': {'is_util': is_util}}
        return res

    # @api.v7
   # def get_days_util_to_pay(self):
    #    local_obj = self.browse(self.id)
     #   return local_obj.util_days_to_pay

    # @api.v7
    def validate_util_days_to_pay(self, values, come_from):
        fecha =None
        dias = values.get('util_days_to_pay',False)
        especial = values.get('check_special_struct', False)
        struct_obj = self.pool.get('hr.payroll.structure')
        struct_id = values.get('struct_id', False)
        is_anticipo = values.get('is_anticipo', False)
        if especial or struct_id:
            struct = struct_obj.browse(self, struct_id, ['name'])
            if 'UTILIDAD' in struct['name'].upper() and is_anticipo and dias == 0:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Número de días a pagar no puede ser 0! Por favor verifique e intente nuevamente.'))
        else:
            hr_util_obj = self.env['hr.payroll.utilidades']
            # for psr in self.browse(cr, uid, id, context=context):
            #     fecha = psr.date_start
            fecha = values['date_start'].split('-')[0]
            year = fecha if fecha else datetime.now().strftime('%Y-%m-%d').split('-')[0]
            total = hr_util_obj.get_last_util_max_days(year)
            # d = total - dias
            if dias > total:
                raise exceptions.except_orm(('Advertencia!'), (
                    u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifie e intente nuevamente.'))
            # elif dias == 0:
            #     raise Warning(('Advertencia!'), (
            #         u'El Número de días a pagar no puede ser 0! Por favor verifie e intente nuevamente.'))

        return True

    @api.multi
    def write(self, values):
        if self._context is None: context = {}
        if not hasattr(self._ids, '__iter__'): ids = [self._ids]
        if values.get('check_special_struct', False) or values.get('struct_id', False):
            self.validate_util_days_to_pay(self, values, 'write')
        res = super(hr_payslip_run, self).write(values)
        return res

    @api.model
    def create(self, values):
        if self._context is None: context = {}
        res = {}
        if values.get('check_special_struct',False):
            self.validate_util_days_to_pay(self, values, 'create')
        res = super(hr_payslip_run, self).create(values)
        return res