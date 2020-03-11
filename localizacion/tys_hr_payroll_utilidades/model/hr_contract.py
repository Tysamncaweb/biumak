# coding: utf-8
from odoo import fields, models, api

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = "hr.contract"

    total_anticipo = fields.Float('Total monto solicitado anticipo',digits=(10,4))
    ultimo_anticipo =  fields.Float('Ultimo anticipo', digits=(10,4))
    struct_id_anticipo = fields.Many2one('hr.payroll.structure', 'Tipo de Nomina Especial')
    start_date = fields.Date('Inicio Periodo Anticipo')
    end_date = fields.Date('fin Periodo Anticipoi')

    @api.multi
    def set_anticipo_data(self, monto, date_from, date_to, special_id):
        anticipo_acumulado = monto + self.total_anticipo
        values = {
            'total_anticipo':anticipo_acumulado,
            'ultimo_anticipo': monto,
            'struct_id_anticipo':special_id,
            'start_date':date_from,
            'end_date':date_to,
        }
        res =self.write(values)
        return res

    @api.multi
    def get_anticipo_acum(self):
       values = {'total_anticipo':self.total_anticipo}
       res= self.write(values)
       return res

