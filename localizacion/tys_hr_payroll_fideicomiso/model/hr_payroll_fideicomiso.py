# coding: utf-8
# from openerp import fields, models, api
from odoo import fields, models, api, exceptions, _
from dateutil import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning

class hr_payslip(models.Model):
    _inherit ='hr.payslip'


    salario_mensual_fi = fields.Float('Salario mensual fideicomiso', digits=(10,2))
    salario_integral_fi = fields.Float('Salario integral fideicomiso', digits=(10,2))
    alic_bono_vac_fi = fields.Float('Alicuota de bono vacacional',digits=(10,2))
    alic_util_fi = fields.Float('Alicuota de utilidades',digits=(10,2))
    dias_adicionales = fields.Integer('Dias Adicionales')
    dias_acumulados = fields.Integer('Dias acumulados')


    @api.multi
    def compute_sheet(self):

        fi_hist_obj = self.env['hr.historico.fideicomiso']
        factor_x_dias_x_mes_adic = dias_adic = dias_acum = 0
        salario_integral_diario = alic_b_v = alic_util = salario_integral = sueldo_promedio = 0.0
        # recalculate = context.get('come_from', False)
        tiempo_servicio = {}
        vacaciones = {}
        #is_special = context.get('is_special', False) ###########se comento
        #special_id = context.get('special_id', False) ########## se comento

        special_struvct_obj = self.env['hr.payroll.structure']
        config_obj = self.env['hr.config.parameter']
        run_obj = self.env['hr.payslip.run']
        active_id = self._context.get('active_id', False)
        payslip_values = {}
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones', True)
        special_fields = run_obj.search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        structure_ids = [special_fields.struct_id.id]
        psr = None
        if active_id:
            psr = run_obj.browse(active_id)

        if is_special and structure_ids:
            if tipo_nomina in psr.struct_id.code:
                for payslip_id in self.ids:
                    payslip = self.search([('id', '=', payslip_id)])

                    date_to = datetime.strptime(payslip.date_to, '%Y-%m-%d')
                    date_from = datetime.strptime(payslip.date_from, '%Y-%m-%d')
                    mes_date_to = str(date_to).split('-')[1]
                    mes_date_from = str(date_from).split('-')[1]
                    ano_date_to = str(date_to).split('-')[0]
                    ano_date_from = str(date_from).split('-')[0]
                    total_ano = int(ano_date_to) - int(ano_date_from)
                    total_mes = int(mes_date_to) - int(mes_date_from)
                    if total_ano > 0 and total_mes > 3:
                        raise exceptions.except_orm(
                            _('Error!'),
                            _('Por favor Verifique el Periodo Seleccionado en la Nómina.\n'
                              ' El periodo se encuentra mal configurado por favor corregir para que pueda continuar.'))

                    elif total_mes > 3:
                        raise Warning((u'El periodo debe ser trimestral por favor verifique.\n'
                                       u' Corrija para poder continuar!'))


                    special_obj = special_struvct_obj.browse(structure_ids)
                    if 'code' in special_obj:
                        if psr.anticipo_check1 == False:
                            dias_str = config_obj._hr_get_parameter('hr.dias.bono.vacacional')
                            tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                            vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)
                            sueldo_promedio = self.calculo_sueldo_promedio(payslip.employee_id, payslip.date_to, 1,
                                                                           'fideicomiso')
                            if not payslip.contract_id:
                                raise Warning((
                                                  u'El Empleado %s no tiene contrato o la fecha de ingreso es posterior al período seleccionado.\n'
                                                  u' Por favor consulte con su supervisor inmediato!') % payslip.employee_id.name)
                            # factor = self.get_days_utilidades(cr, uid) / float(12)
                            salario_integral, factor_x_dias_x_mes, salario_integral_diario, alic_b_v, alic_util = self.calculo_fideicomiso(
                                 sueldo_promedio,
                                vacaciones.get('asignacionR') if int(dias_str) == 0 else int(dias_str),
                                payslip.contract_id.date_start, payslip.date_to)
                            history = fi_hist_obj.get_last_history_fi(payslip.employee_id.id, None)

                            dias_adic = self.get_fi_dias_adicionales( payslip.contract_id.date_start, payslip.date_to,
                                                                     payslip.date_from, history)

                            if dias_adic < 0:
                                raise Warning((u'La fecha de ingreso del empleado %s es posterior al período seleccionado.\n'
                                               u' Por favor consulte con su supervisor inmediato!') % payslip.employee_id.name)
                            elif dias_adic > 0:
                                salario_integral_dias_adic, factor_x_dias_x_mes_adic, salario_integral_diario, alic_b_v, alic_util = self.calculo_fideicomiso(
                                     sueldo_promedio, vacaciones.get('asignacionR'),
                                    payslip.contract_id.date_start, payslip.date_to,
                                    dias_adic)

                            # dias_acum = fi_hist_obj.get_last_history_fi(cr, uid,payslip.employee_id.id, None, context=context).dias_acumuluados
                            payslip_values.update({
                                'salario_mensual_fi': sueldo_promedio,
                                'salario_integral_fi': salario_integral_diario,
                                # 'salario_integral_fi': salario_integral,
                                'dias_adicionales': dias_adic,
                                'dias_acumulados': factor_x_dias_x_mes,
                            })
                            payslip.write(payslip_values)
        res = super(hr_payslip, self).compute_sheet()
        return res

    @api.multi
    def calculo_fideicomiso(self,sueldo_normal, dias_b_v, date_start, fecha_hasta, dias_adic=None):
        monto_diario = 0.0
        alic_b_v = 0.0
        alic_util = 0.0
        factor_x_dias_x_mes = 0
        config_obj = self.env['hr.config.parameter']
        # Total de dias por mes (para calculo del salario d9iario)
        dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')

        # total meses a pagar de fideicomiso
        total_meses_str = config_obj._hr_get_parameter('hr.fideicomiso.total.meses')

        factor = self.get_fact_fidei_x_mes(date_start, fecha_hasta, float(total_meses_str))

        # total de dias a pagar de fideicomiso
        if dias_adic:
            factor_x_dias_x_mes = float(dias_adic)
        else:
            fi_dias_x_mes_str = config_obj._hr_get_parameter('hr.fideicomiso.dias.x.mes')
            factor_x_dias_x_mes = factor * float(fi_dias_x_mes_str)
        alic_b_v = self.calculo_alic_bono_vac(sueldo_normal, dias_b_v)
        alic_util = self.calculo_alic_util(sueldo_normal, alic_b_v)
        monto_diario = (sueldo_normal / float(dias_str)) + alic_b_v + alic_util  # salario integral diario
        return monto_diario * factor_x_dias_x_mes, factor_x_dias_x_mes, monto_diario, alic_b_v, alic_util

    # @api.v7
    def get_fact_fidei_x_mes(self, date_start, fecha_hasta, total_meses):
        factor = 0.0
        diferencia = relativedelta.relativedelta(datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT),
                                                 datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT))
        if diferencia.years > 0:
            factor = total_meses
        elif diferencia.years == 0:
            if diferencia.months >= total_meses:
                factor = total_meses
            else:
                factor = diferencia.months + 1
        else:
            raise Warning((u'La fecha de ingreso del empleado es posterior al período seleccionado.\n'
                           u' Por favor consulte con su supervisor inmediato!'))
        return factor

    def get_fi_dias_adicionales(self,date_start, fecha_hasta, fecha_desde, history =False):
        config_obj = self.env['hr.config.parameter']
        fecha = None
        dias = 0
        anios = 0

        # ULTIMA LIQUIDACION COLECTIVA
       # ult_liqu_colectiva_str = config_obj._hr_get_parameter('hr.payslip.ultima.liquidacion.colectiva', True)

        # Años establecidos por ley para comenzar a pagar los dias adicionales
      #  anios_ley_str = config_obj._hr_get_parameter('hr.fi.antiguedad.ley')

        # Maximo dias a pagar
        maximo_str = config_obj._hr_get_parameter('hr.dias.x.mes')

        if not datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT):
            raise exceptions.except_orm(
                _('Error!'),
                _('Por favor Verifique el La fecha de ingreso del Empleado.\n'
                  ' No posee o se encuentra mal configurada por favor corregir para continuar.'))

        else:
            fecha = date_start
        # años de servicio desde la fecha de ingreso
        anios = self.get_years_service(fecha, fecha_hasta)['anios']
        dias_adic_acum = history.dias_adicionales

        diferencia = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
        diferencia2 = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)

        if int(date_start.split('-')[0]) <= int(fecha_desde.split('-')[0]) <= int(fecha_hasta.split('-')[0]):
            if  int(fecha_desde.split('-')[1])  <= int(date_start.split('-')[1]) <= int(fecha_hasta.split('-')[1]):
                factor_str = config_obj._hr_get_parameter('hr.fi.factor.dias.adicionales')

                if anios > 0 :
                    anios = anios - 1

                dias = int(factor_str) * anios

                if dias > int(maximo_str): dias = int(maximo_str)

            elif diferencia.days < 0:
                dias = -1
            elif diferencia2.days < 0:
                dias = 0
            return dias


'''
    def get_fi_dias_adicionales_inicio(self,date_start, fecha_hasta, fecha_desde, history):
        dias = 0
        config_obj = self.env['hr.config.parameter']
        anios_ley_str = config_obj._hr_get_parameter('hr.fi.antiguedad.ley')
        maximo_str = config_obj._hr_get_parameter('hr.dias.x.mes')
        fecha = date_start
        anios = self.get_years_service(fecha, fecha_hasta)['anios']
        factor_str = config_obj._hr_get_parameter('hr.fi.factor.dias.adicionales')

        if int(date_start.split('-')[0]) <= int(fecha_desde.split('-')[0]) <= int(fecha_hasta.split('-')[0]):
                if anios == 1:
                    dias = 0
                if anios == int(anios_ley_str):
                    anios = 1
                elif anios > 0 and anios > int(anios_ley_str):
                    anios = anios - 2
                if anios == 1:
                    dias = int(factor_str) * anios
                if dias > int(maximo_str): dias = int(maximo_str)
               
                return dias

'''



'''
class hr_contract(models.Model):
    _inherit = 'hr.contract'

    fecha_modificado = fields.Date('Bono Nocturno Valor')
    fideicomiso = fields.Float('Bono Nocturno', digits=(10, 2))
'''