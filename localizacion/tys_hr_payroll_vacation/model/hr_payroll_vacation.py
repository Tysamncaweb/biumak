# coding: utf-8
# from openerp import fields, models, api
from odoo import fields, models, api, _,exceptions
from dateutil import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError, UserError

class hr_payslip(models.Model):
    _inherit ='hr.payslip'

    dias_a_pagar_va = fields.Integer('Dias a pagar vacaciones')
    tiempo_servicio_va = fields.Integer('Tiempo de servicio vacaciones')
    salario_mensual_va = fields.Float('Salario mensual vacaciones',digits=(10,2))
    domingos = fields.Integer('Domingos vacacioneas')
    dias_porcion =fields.Float('Dias Porcion',digits=(10,2))
    # 'dias_adicional':fields.integer('Dias adicionales'),
    dias_festivos = fields.Integer('Dias festivos')
    dias_a_disfrutar = fields.Integer('Dias a Disfrutar')


    @api.multi
    def compute_sheet(self):
        # res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        special_struct_obj = self.env['hr.payroll.structure']
        run_obj = self.env['hr.payslip.run']
        config_obj = self.env['hr.config.parameter']
        feriados = 0
        sueldo_promedio = 0.0
        active_id = self._context.get('active_id', False)
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        dias_x_periodo = {}
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.vacaciones', True)
        dias_disfrutar = 0

        special_fields = run_obj.search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        structure_ids = [special_fields.struct_id.id]
        #is_special = self._context.get('is_special', False)
        #special_id = self._context.get('special_id', False)
        psr = None
        if active_id:
            psr = run_obj.browse(active_id)
        if is_special and structure_ids:
            if tipo_nomina in psr.struct_id.code:
                for payslip_id in self:
                    sueldo_prom_3 = 0
              #      payslip = self.search([('id', '=', payslip_id)])
                    special_obj = special_struct_obj.browse(structure_ids)
                    if 'code' in special_obj:
    #                if  special_obj.code in tipo_nomina:
                        dias_x_periodo = self.calcula_dias_x_periodo(payslip_id.date_from, payslip_id.date_to)
                        feriados = self.get_feriados_2(payslip_id.date_from, payslip_id.date_to)
                        tiempo_servicio = self.get_years_service(payslip_id.contract_id.date_start, payslip_id.date_to)
                        vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)

                        if payslip_id.contract_id.comision_check == True:
                            sueldo_promedio = self.calculo_sueldo_promedio(payslip_id.employee_id, payslip_id.date_from, 3, 'vacaciones')
                            sueldo_prom_3 = sueldo_promedio/3

                        else:
                            sueldo_prom_3 = self.calculo_sueldo_promedio(payslip_id.employee_id, payslip_id.date_from, 1, 'vacaciones')


                        holidays = self.env['hr.holidays'].search([('employee_id', '=', payslip_id.employee_id.id),('date_from', '>=', payslip_id.date_from),('date_to','<=', payslip_id.date_to)])
                     #   holidays_employee = holidays.search([('date_from', '>=', payslip_id.date_from),('date_to','<=', payslip_id.date_to)])
                        if holidays:
                            for holy in holidays:
                                if holy.bono_vacacional == True:
                                    dias_disfrutar = holy.number_of_days_temp
                                elif holy.vacation == True:
                                    dias_disfrutar = holy.number_of_days_temp
                                else:
                                    dias_disfrutar = 0
                            if dias_disfrutar == 0:
                                raise ValidationError(_(
                                    "No se Posee ningun registro de Tipo de Ausencias: VACACIONES. \n Inicialmente se debe cargar en el Módulo de Ausencias el registro de los Dias de Vacaciones para poder realizar el Pago de la Nómina."))

                        else:
                            raise ValidationError(_("No posee Vacaciones en el periodo seleccionado. \n  Por Favor Verifique el Periodo de la Nómina debe coincidir con el periodo de Vacaciones configurado en el Módulo de Ausencias."))

                    #,('date_from', '<=',payslip_id.date_from),('date_to','>=',payslip_id.date_to)
                    payslip_values.update({
                        'salario_mensual_va':  sueldo_prom_3,
                        'domingos': dias_x_periodo.get('domingos',False),
                        'dias_festivos': feriados,
                        'dias_porcion': vacaciones.get('asignacion',False),
                        'dias_a_pagar_va':vacaciones.get('asignacion',False),
                        'tiempo_servicio_va':tiempo_servicio.get('anios',False),
                        'dias_a_disfrutar' : dias_disfrutar,
                    })
                    payslip_id.write(payslip_values)
        res = super(hr_payslip, self).compute_sheet()
        return res







# class hr_contract(osv.osv):
#     _inherit = 'hr.contract'
#     _columns = {
#         'fecha_modificado': fields.date('Bono Nocturno Valor'),
#         'fideicomiso': fields.float('Bono Nocturno', digits=(10, 2)),
#     }

