# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from datetime import datetime, date, timedelta, time
from odoo import models, fields, api,exceptions, _
from odoo.exceptions import UserError, Warning
'''
class hr_liquidacion(models.TransientModel):
    _name = 'hr.liquidacion'
    _description = 'liquidacion del trabajador'
    gerente = fields.Many2one('hr.employee',string="Gerente del área", required=True)

    @api.multi
    def print_report(self, docids):
        res = dict()
        docs = []
        idddd = docids['active_id']
        update = {'slip_id': idddd,'gerente':self.gerente.name}
        docids.update(update)
        return self.env.ref('int_hr_reporte_liquidacion.action_hr_report_liquidacion_reporte').report_action([], data=docids)
'''

class ReportAccountPayment_5(models.AbstractModel):
    _name = 'report.int_hr_reporte_liquidacion.template_liquidacion_trabajo'

    @api.model
    def get_report_values(self, docids, data):
        var = data
        config_obj = self.env['hr.config.parameter']
        code_liq = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.liquidacion', True)

        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip'].browse(docids)}
        slip_id = data['form']

        if slip_id.structure.code != code_liq:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Por favor verifique que la nómina sea de Liquidación'))
        if slip_id.state != 'done':
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Por favor verifique que la nómina de Liquidación este en estado "Realizado"'))

        docs2 = []
        cont = 0
        var2 = 0
        ci_empleado =  str(slip_id.employee_id.nationality) + '-'+ str(slip_id.employee_id.identification_id_2)
        fecha_ingreso = datetime.strptime(slip_id.date_from, '%Y-%m-%d')
        fecha_ingreso = fecha_ingreso.strftime('%d/%m/%Y')
        fecha_actual = date.today()
        fecha_actual = fecha_actual.strftime('%d/%m/%Y')
        fecha_egreso = datetime.strptime(slip_id.date_to, '%Y-%m-%d')
        fecha_egreso = fecha_egreso.strftime('%d/%m/%Y')
        res = dict()
        docs = []
        asignaciones=[]
        deducciones=[]
        if not slip_id.line_ids:
            raise exceptions.except_orm(_('Advertencia!'), (
                "Por favor verifique si tiene cargado los conceptos de la Estructura Salarial "))
        unidad = 0
        cont2 = 0
        for a in slip_id.line_ids:

            cant_sueldo = ' '

            if a.category_id.code == 'ALW':
                '''
                #################################  ASIGNACIONES   ####################################
                '''
                dias_porcentaje = ''
                dias_porcentaje_ded = ''
                salario = ''
                monto = 0
                ''' SALARIO'''
                if a.amount_python_compute.find("cant_dias_labor") != -1:
                    dias_porcentaje = slip_id.cant_dias_labor
                    salario = slip_id.salario_basico_diario
                    salario = self.separador_cifra(salario)

                ''' CESTATICKET'''
                if a.amount_python_compute.find("cestaticket") != -1:
                    dias_porcentaje = slip_id.cant_dias_labor
                    salario = float(slip_id.cestaticket/30)
                    salario = self.separador_cifra(salario)

                ''' GARANTIA DE PRESTACIONES SOCIALES'''
                if a.amount_python_compute.find("monto_gps") != -1:
                    dias_porcentaje = slip_id.dias_prestaciones_acum

                '''DIAS ADICIONALES DE LAS PRESTACIONES SOCIALES'''
                if a.amount_python_compute.find("aporte_dias_adicionales") != -1:
                    dias_porcentaje = slip_id.dias_prestaciones_adi


                ''' BONO NOCTURNO'''
                if a.amount_python_compute.find("night_bonus") != -1:
                    dias_porcentaje = slip_id.night_bonus
                    dias_porcentaje = '{0:,.2f}'.format(dias_porcentaje).replace('.', ',')
                    if slip_id.night_bonus != 0:
                        salario = (a.amount/(slip_id.night_bonus))
                        salario = self.separador_cifra(salario)

                ''' FERIADO TRABAJADO'''
                if a.amount_python_compute.find("holidays_value") != -1:
                    dias_porcentaje = slip_id.holidays_value
                    if slip_id.holidays_value != 0:
                        salario = (a.amount/(slip_id.holidays_value))
                        salario = self.separador_cifra(salario)

                ''' VACACIONES FRACCIONADAS'''
                if a.amount_python_compute.find("vacaciones_fracc") != -1:
                    dias_porcentaje = slip_id.vacaciones_fracc
                    salario = slip_id.salario_integral
                    salario = self.separador_cifra(salario)
                    dias_porcentaje = self.separador_cifra(dias_porcentaje)

                ''' UTILIDADES FRACCIONES'''
                if a.amount_python_compute.find("utilidades_fracc") != -1:
                    dias_porcentaje = slip_id.dias_utili
                    salario = slip_id.sueld_util
                    salario = self.separador_cifra(salario)
                    dias_porcentaje = self.separador_cifra(dias_porcentaje)

                ''' DIAS DE DESCANSO'''
                if  a.amount_python_compute.find("payslip.sundays_value+payslip.saturdays_value") != -1:
                    dias_porcentaje = (slip_id.saturdays_value + slip_id.sundays_value)
                    if slip_id.saturdays_value != 0 or  slip_id.sundays_value != 0:
                        salario = (a.amount/((slip_id.saturdays_value + slip_id.sundays_value)))
                        salario = self.separador_cifra(salario)

                ''' BONO DE VACACIONES ACUMULADAS'''
                if a.amount_python_compute.find("bono_vac_acum") != -1:
                    dias_porcentaje = (slip_id.bono_vac_acum)
                    salario = slip_id.salario_integral
                    salario = self.separador_cifra(salario)


                monto = a.amount
                monto = self.separador_cifra(monto)
                asignaciones.append({
                    'nombre': a.name,
                    'dias_porcentaje': dias_porcentaje,
                    'salario':salario,
                    'monto': monto,
                })

            elif a.category_id.code == 'DED':
                '''
                   ################################  DEDUCCIONES  #################################
                '''
                dias_porcentaje = ''
                dias_porcentaje_ded = ''
                salario = ''
                monto = 0

                ''' ANTICIPO DE PRESTACIONES SOCIALES'''
                if a.amount_python_compute.find("anticipo_prestaciones") != -1:
                    dias_porcentaje_ded = '%'
                    salario =  '75%'

                ''' RETENCION DEL FAOV'''
                if a.amount_python_compute.find("0.01") != -1:
                    dias_porcentaje_ded = '%'
                    salario = '1%'

                ''' RETENCION DEL SSO'''
                if a.amount_python_compute.find("0.04") != -1:
                    dias_porcentaje_ded = '%'
                    salario = '4%'

                ''' RETENCION DEL REGIMEN PRESTACIONAL'''
                if a.amount_python_compute.find("0.005") != -1:
                    dias_porcentaje_ded = '%'
                    salario = '0,5%'

                monto = a.amount
                monto = self.separador_cifra(monto)
                deducciones.append({
                    'nombre': a.name,
                    'dias_porcentaje': dias_porcentaje_ded,
                    'salario': salario,
                    'monto': monto,
                })

            if not slip_id.struct_id:
                totalD_net = 0

            if a.category_id.code == 'BASIC':
                total_asignaciones = a.amount
                total_asignaciones = self.separador_cifra(total_asignaciones)
            if a.category_id.code == 'GROSS':
                total_deducciones = a.amount
                total_deducciones = self.separador_cifra(total_deducciones)
            if a.category_id.code == 'NET':
                neto_pagar = a.amount
                neto_pagar = self.separador_cifra(neto_pagar)

        ''' caso de sueldo variable cuando se gana comision'''
        if slip_id.comisiones_check != 0:
            salario_mensual = slip_id.salario_prom_mensual
            salario_diario = slip_id.salario_prom_diario
        else:
            salario_mensual = slip_id.salario_basico
            salario_diario = slip_id.salario_basico_diario
        segundo_nombre = ' '
        segundo_apellido = ' '
        if slip_id.employee_id.firstname2:
            segundo_nombre = slip_id.employee_id.firstname2
        if slip_id.employee_id.lastname2:
            segundo_nombre = slip_id.employee_id.lastname2
        docs.append({
            'nombres_empleado':slip_id.employee_id.firstname + ' ' +  segundo_nombre,
            'apellidos_empleado': slip_id.employee_id.lastname + ' ' + segundo_apellido,
            'nombre_apellido': slip_id.employee_id.full_name,
            'ci_empleado': ci_empleado,
            'fecha_ingreso': fecha_ingreso,
            'cargo': slip_id.employee_id.job_id.name,
            'ubication_dep': slip_id.employee_id.department_id.ubication_dep,
            'fecha_egreso': fecha_egreso,
            'salario_mensual': self.separador_cifra(salario_mensual),
            'motivo': slip_id.m_egreso.name,
            'salario_diario':  self.separador_cifra(salario_diario),
            'años_servicio': slip_id.tiempo_servicio_year,
            'meses_servicio': slip_id.tiempo_servicio_meses,
            'var1': cont - 1,
            'var2': var2,
            'dias_servicio': slip_id.tiempo_servicio_dias,
            'salario_integral': self.separador_cifra(slip_id.salario_integral),
            'fecha_actual':fecha_actual,
            'total_asignaciones': total_asignaciones,
            'total_deducciones':total_deducciones,
            'neto_pagar':neto_pagar,
            'alicuota_util':self.separador_cifra(slip_id.alic_util_liq),
            'alicuota_bv': self.separador_cifra(slip_id.alic_bono_vac_liq),
            'empresa': slip_id.employee_id.address_id.name,
        })
        var2 = var2 + cont2
        return {
            'model': self.env['report.int_hr_reporte_liquidacion.template_liquidacion_trabajo'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'asignaciones':asignaciones,
            'deducciones':deducciones,


        }

    def separador_cifra(self,valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return  monto