# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, api, fields,_, exceptions
from logging import getLogger

class hr_payslip_run_total(models.Model):
    _inherit ='hr.payslip.run'

    total_asig = fields.Float (string= 'Total de Asignaciones', compute='calculosprocesamiento')
    total_deduc = fields.Float(string='Total de Deducciones', compute='calculosprocesamiento')
    total = fields.Float(string='Total', compute='calculosprocesamiento')


    @api.multi
    def calculosprocesamiento(self):
        sumaasig = sumaded = sumatotal = 0
        busqueda = self.env['hr.salary.rule.category'].search([('id', '!=', 0)])
        if busqueda:
            for a in busqueda:
                if a.code == 'BASIC':
                    tasig = a.id
                if a.code == 'GROSS':
                    tdeduc = a.id
                if a.code == 'NET':
                    ttotal = a.id
                if  self.check_special_struct == True:
                    if a.code == 'ESP':
                        tasig = a.id
                        tdeduc = 0
                        ttotal = a.id
        else:
            tasig = tdeduc = ttotal = 0

        busqueda2 = self.env['hr.payslip.line'].search([('id', '!=', 0)])
        for var in self.slip_ids:
            for b in var.line_ids:
                if b.category_id.id == tasig:
                    sumaasig += b.total
                if b.category_id.id == tdeduc:
                    sumaded += b.total
                if b.category_id.id == ttotal:
                    sumatotal += b.total
        self.total_asig = sumaasig
        self.total_deduc = sumaded
        self.total = sumatotal
        return

class hr__days_period(models.Model):
    _inherit = 'hr.payslip'

    alicuota_bv = fields.Float('Alicuota de bono vacacional')
    alicuota_util = fields.Float('Alicuota de utilidades')
    number_of_days1 = fields.Float('dias de periodos')
    salario_minimo = fields.Float('Salario Minimo parametro')
    reintegro_nomina = fields.Float('Reintegro Faltante de Nomina parametro')



    @api.multi
    def compute_sheet(self):

        cont_dias = 0
        worked_days = self.env['hr.payslip.worked_days']


        for b in self:
            cont_dias1 = 0
            date_to = datetime.strptime(b.date_to, '%Y-%m-%d')
            date_from = datetime.strptime(b.date_from, '%Y-%m-%d')
            difb = date_to - date_from
            diferencia = difb.days + 1
            for var6 in b.worked_days_line_ids:
                if var6.code != 'WORK100':
                    cont_dias1 += var6.number_of_days
            for var4 in b.worked_days_line_ids:
                if var4.code == 'WORK100':
                    var4.write({'number_of_days': (diferencia - cont_dias1)})
                    var4.write({'number_of_days1':(diferencia - cont_dias1)})


            config_obj = self.env['hr.config.parameter']
            salario_minimo = config_obj._hr_get_parameter('hr.payroll.salario.minimo')
            reintegro_nomina = config_obj._hr_get_parameter('reintegro.faltante.nomina')
            code_liq = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.liquidacion', True)


            if b.employee_id :
                    tiempo_servicio = self.get_years_service(b.contract_id.date_start, b.date_to)
                    vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)
                    dias_bv = vacaciones.get('asignacion')
                    dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')

                    dias_x_anio = config_obj._hr_get_parameter('hr.payroll.max.dias.año')
                    dias_max_str = config_obj._hr_get_parameter('hr.payroll.max.utili.days.year')

                    fac_utilidades = float(dias_max_str) / float(dias_x_anio)
                    wage = b.contract_id.wage
                    alicuota_bv = (float(wage) / float(dias_str)) * (float(15) / float(dias_x_anio))
                    alicuota_util = ((float(wage) / (float(dias_str))) * float(fac_utilidades))

                    b.write({'alicuota_bv': alicuota_bv})
                    b.write({'alicuota_util': alicuota_util})
            b.update({'salario_minimo': salario_minimo})
            b.update({'reintegro_nomina': reintegro_nomina})




        for a in self:
            payslip_run = worked_days.search([('payslip_id', '=', a.id)])
            check_struct = self[0].payslip_run_id.check_special_struct
            if check_struct == False:
                for var in payslip_run:
                    if var.code == 'WORK100':
                        if var.number_of_days > 16:
                            raise exceptions.except_orm(_('Advertencia!'), (u'El Período seleccionado para la nómina que esta intentando generar es mayor al Período de una Quincena.\n \
                                                Por favor recuerde que las Reglas Salariales estan basadas en una Quincena.'))
                        if var.number_of_days > 15:
                            var.write({'number_of_days': '15'})
                        if var.number_of_days < 15:
                            if a.date_from[5:7] == '02':
                                if (a.date_from[8:10] == '16') and ((a.date_to[8:10]== '28')or (a.date_to[8:10]== '29')):
                                    var.write({'number_of_days': '15'})
            else:
                if a.payslip_run_id.struct_id.code == 'C-7000':
                    for var2 in a.worked_days_line_ids:
                        if var2.code != 'WORK100':
                            cont_dias += var2.number_of_days
                    for var3 in a.worked_days_line_ids:
                        if var3.code == 'WORK100':
                            var3.write({'number_of_days': 30 - cont_dias})


            if a.payslip_run_id.struct_id.code :
                dias_vacaciones = 0
                #vacacion =   self.env['hr.holidays'].search([('employee_id', '=', a.employee_id.id),('vacation','=',True),('date_from','<=',a.date_to),('date_to','>=',a.date_from)])
                for vac1 in a.worked_days_line_ids:
                    if (vac1.code.find("acacion") != -1) or (vac1.code.find("ACACION") != -1):
                        dias_vacaciones = vac1.number_of_days
                for vac1 in a.worked_days_line_ids:
                    if dias_vacaciones > 0:
                        for var33 in a.worked_days_line_ids:
                            if var33.code == 'WORK100':
                                var33.write({'number_of_days': dias_vacaciones + var33.number_of_days})
                                dias_vacaciones = 0





        res = super(hr__days_period, self).compute_sheet()
        return res


