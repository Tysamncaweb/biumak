# coding: utf-8
from odoo import fields, models, api

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'

    STATES_VALUES = [
            ('draft', 'Draft'),
            ('done', 'Confirmado'),
            ('close', 'Close'),
        ]

    state = fields.Selection(STATES_VALUES, 'Status', select=True, readonly=True, copy=False)

    @api.multi
    def hr_payslip_multi(self):

        for payslip in self.slip_ids:
            payslip.action_payslip_done()
        return self.write({'paid': True, 'state': 'done'})


'''
class hr_sal_men_int(models.Model):
    _inherit = 'hr.payslip'

    sueldo_men_integral = fields.Float('vacaciones dias')


    @api.multi
    def compute_sheet(self):
        res = super(hr_sal_men_int, self).compute_sheet()
        contract = self.contract_id
        salario_mensual = float((((contract.wage)/4)*52)/12)
        tiempo_servicio = self.get_years_service(self.contract_id.date_start, self.date_to)
        vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)
        dias_bv = vacaciones.get('asignacion', False)
        cal_alicuota_bv = self.calculo_alic_bono_vac(salario_mensual,dias_bv)
        cal_alicuota_util = self.calculo_alic_util(salario_mensual, cal_alicuota_bv)
        sueldo_men_integral = float(((salario_mensual/30) + cal_alicuota_bv + cal_alicuota_util)*30)
        self.write({'sueldo_men_integral' : sueldo_men_integral})
        return res
'''
