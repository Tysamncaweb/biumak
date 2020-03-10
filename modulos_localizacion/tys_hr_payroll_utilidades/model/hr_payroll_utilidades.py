# coding: utf-8
# from openerp import fields, models, api
from odoo import models,fields, api , exceptions
from odoo.exceptions import Warning
from datetime import datetime, time, date
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    salario_mensual_util = fields.Float('Salario Mensual Utilidades', digits=(10, 2))
    salario_integral_util =fields.Float('Salario Integral Utilidades', digits=(10, 2))
    total_util = fields.Float('Total a pagar', digits=(10, 2))
    alic_bono_vac_util = fields.Float('Alicuota Bono Vacacional', digits=(10, 2))
    anticipos_util = fields.Float('Anticipos Utilidades', digits=(10, 2))
    util_days_to_pay_ps = fields.Integer('Dias a pagar utilidades')
    dias_x_anio= fields.Char('Dias por año')


    _defaults = {
        'sueldo_promedio':True,
    }

    @api.multi
    def compute_sheet(self):
        # res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        special_struct_obj = self.env['hr.payroll.structure']
        run_obj = self.env['hr.payslip.run']
        config_obj = self.env['hr.config.parameter']
        util_obj = self.env['hr.payroll.utilidades']
        res_config_obj = self.env['periodo.utilidades']
        contract_obj = self.env['hr.contract']
        active_id = self._context.get('active_id', False)
        config_values = {}
        factor_x_dias_x_mes_adic = dias_adic = dias_acum = dias_util = 0
        salario_integral_diario = alic_b_v = alic_util = salario_integral = sueldo_promedio = total_a_pagar = 0.0
        period_init = period_end = None
        special_fields = run_obj.search([('id', '=', active_id)])
        is_special = special_fields.check_special_struct
        structure_ids = [special_fields.struct_id.id]
        tiempo_servicio = {}
        vacaciones = {}
        payslip_values = {}
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.utilidades', True)
      #  is_special = self._context.get('is_special', False)
        special_id = self._context.get('special_id', False)
        recalculate = self._context.get('come_from', False)
        config_data = False
        is_anticipo = False
        if is_special and structure_ids and active_id:
            psr = run_obj.browse(active_id)
            is_anticipo = psr.is_anticipo
            if tipo_nomina in psr.struct_id.code:
                for payslip in self:
               #     payslip = self.search([('id', '=', payslip_id)])
                #    if payslip.contract_id.date_end:    #Si el contrato no esta ctivo no ss hace nomina de utilidades
                #       continue
                    dias_str = config_obj._hr_get_parameter('hr.dias.bono.vacacional')
                    tiempo_servicio = self.get_years_service(payslip.contract_id.date_start, payslip.date_to)
                    vacaciones = self.get_dias_bono_vacacional(tiempo_servicio)
                    config_values = res_config_obj.get_config_values()
                    # max_days_year = float(config_obj._hr_get_parameter(cr, uid, 'hr.payroll.max.days.year', True))
                    if config_values and config_values[0]['module_hr_utilidades_add_calculo'] == True:
                        if is_anticipo:
                            dias_util = psr.util_days_to_pay
                            period_init = payslip.date_from
                            period_end = payslip.date_to
                            max_day_util = util_obj.get_last_util_max_days(
                                                                           int(payslip.date_from.split('-')[0]))
                        else:
                            period_init = config_values[0]['module_hr_utilidades_add_date_start']
                            period_end = config_values[0]['module_hr_utilidades_add_date_end']
                            max_day_util = util_obj.get_last_util_max_days( int(period_init.split('-')[0]))
                            dias_util = max_day_util
                        config_data = True
                    else:
                        #TODO proceso para calculo de utilidades utilizando el ultimo salario del mes
                        period_end = None
                        max_day_util = util_obj.get_last_util_max_days(int(payslip.date_from.split('-')[0]))
                        if is_anticipo:
                            dias_util = psr.util_days_to_pay
                        else:
                            dias_util = max_day_util
                        period_init = payslip.date_from
                        period_end = payslip.date_to
                    if is_anticipo:
                        if dias_util > max_day_util:
                            raise exceptions.except_orm(('Advertencia!'), (
                                u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifie e intente nuevamente.'))
                        elif dias_util == 0:
                            raise exceptions.except_orm(('Advertencia!'), (
                                u'El Número de días a pagar no puede ser 0! Por favor verifique e intente nuevamente.'))

                    sueldo_promedio = self.calculo_sueldo_promedio(payslip.employee_id, period_init, 1, 'utilidad')
                    #sueldo_promedio = self.calculo_sueldo_promedio_util(payslip.employee_id, period_init,
                     #                                                   period_end, config_data, is_anticipo,
                      #                                                  payslip.contract_id.date_start)
                    salario_integral, salario_integral_diario, alic_b_v= self.calculo_salrio_integral(
                        sueldo_promedio, vacaciones.get('asignacion')
                        if int(dias_str) == 0
                        else int(dias_str), dias_util)
                    #total_a_pagar = salario_integral_diario*dias_util
                    total_a_pagar = float(salario_integral_diario)*(int(dias_util))

                    #if is_anticipo:
                     #   contract_obj.set_anticipo_data(total_a_pagar, payslip.date_from, payslip.date_to, special_id)
                   # else:
                    #    payslip.contract_id.write({'total_anticipo': 0})
                   # total_anticipos = contract_obj.get_anticipo_acum()
                    #dias_x_anio = config_obj._hr_get_parameter('hr.payroll.max.dias.año')
                 #   salario_utilidades_prom = sueldo_promedio.replace('.', '')
                 #   salario_utilidades_prom = float(salario_utilidades_prom)
                 #   salario_util_mensual = '{0:,.2f}'.format(sueldo_promedio)

                    payslip_values.update({
                        'salario_mensual_util':  sueldo_promedio,
                        'salario_integral_util': salario_integral_diario,
                        'util_days_to_pay_ps': dias_util,
                        'total_util': total_a_pagar,
                        'alic_bono_vac_util':alic_b_v,
                        #'alic_bono_util': alic_util,
                    #    'anticipos_util':total_anticipos if not period_end else 0.0,
                        #'dias_x_anio':dias_x_anio
                    })
                    payslip.write(payslip_values)
        res = super(hr_payslip, self).compute_sheet()
        return res

    # @api.v7
   # def get_days_util_to_pay(self):
    #    local_obj = self.id
    #    return local_obj.util_days_to_pay

    # @api.v7
    def calculo_salrio_integral(self, sueldo_normal, dias_b_v, dias_adic=None):
        monto_diario = 0.0
        alic_b_v = 0.0
        config_obj = self.env['hr.config.parameter']
        # Total de dias por mes (para calculo del salario diario)
        dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')

        alic_b_v = self.calculo_alic_bono_vac( sueldo_normal, dias_b_v)#/ float(dias_str)
        monto_diario = (sueldo_normal / float(dias_str)) + alic_b_v # salario integral diario
        return monto_diario * float(dias_adic), monto_diario, alic_b_v,

    # @api.v7
    def calculo_sueldo_promedio_util(self, employee_id, fecha_desde, fecha_hasta, config_data=False, is_anticipo=False, contract_date_start=None):
        config_obj = self.env['hr.config.parameter']
        ultimo_sueldo = sueldo_x_mes = sueldo_temp = 0.0
        mes_ult_sueldo = 0
        date_start = None
        if self._context is None: context = {}

        codes_str = config_obj._hr_get_parameter( 'hr.payroll.codigos.salario.integral.utilidades',True)  # salario normal
        code = str(codes_str).strip().split(',')  # para obtener los conceptos a agregar al salario integrarel monto BRUTO a cobrar
        dias_hab_periodo = config_obj._hr_get_parameter( 'hr.payroll.utilidades.dias.habiles',True)  # dias habiles de utilidades

        periodo = relativedelta.relativedelta(datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT),
                                              datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT))
       # if is_anticipo:
        if config_data and not is_anticipo:
            mes_pago = int(config_obj._hr_get_parameter('hr.payroll.utilidades.mes.pago',False))
            fecha_desde = datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT)
            fecha_hasta = datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT)
            #EL PERIODO INICIA EN LA FECHA DE INGRESO DEL EMPLEADO SI TIENE MENOS DE UN AÑO DE ANTIGÜEDAD
            if contract_date_start:
                date_start = datetime.strptime(contract_date_start, DEFAULT_SERVER_DATE_FORMAT)
                if date_start > fecha_desde:
                    fecha_desde = date_start
            while fecha_desde.month <= fecha_hasta.month and mes_pago > fecha_desde.month:
                rango = self.rango_mes_anterior( datetime.strftime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT), 0, 'utilidad')
                sueldo_temp = self.get_amount_util(code, employee_id.id, rango[0],rango[1], is_anticipo, True)  # ultimo sueldo
                fecha_desde = fecha_desde + relativedelta.relativedelta(months=+1)
                ultimo_sueldo += sueldo_temp
                mes_ult_sueldo = fecha_desde.month
                if fecha_desde.month == 12:
                    ultimo_sueldo += sueldo_temp
                if sueldo_temp == 0:
                    break
                sueldo_x_mes = sueldo_temp

            ultimo_sueldo = ultimo_sueldo + sueldo_x_mes*(mes_pago - mes_ult_sueldo)
        else:
            fecha_desde = datetime.strftime(
                datetime.strptime(fecha_desde, DEFAULT_SERVER_DATE_FORMAT) + relativedelta.relativedelta(months=-1),
                DEFAULT_SERVER_DATE_FORMAT)
            fecha_hasta = datetime.strftime(
                datetime.strptime(fecha_hasta, DEFAULT_SERVER_DATE_FORMAT) + relativedelta.relativedelta(months=-1),
                DEFAULT_SERVER_DATE_FORMAT)
            ultimo_sueldo = self.get_amount_util(code, employee_id.id, fecha_desde, fecha_hasta, is_anticipo)  # ultimo sueldo

        return ultimo_sueldo
       # return ultimo_sueldo / (periodo.months if periodo.months > 0 else 1)

    # @api.v7
    def get_amount_util(self, code=None, employee_id=None, fecha_desde=None, fecha_hasta=None, is_anticipo=False, config_data=False):
        amount = 0.0
        amount_month = 0.0
        domain_ps = []
        domain_psl = []
        p_ids = []
        pl_ids = []
        rango = []
        payslip_line_obj = self.env['hr.payslip.line']
        payslip_obj = self.env['hr.payslip']
        payslip_run_obj = self.env['hr.payslip.run']
        config_obj = self.env['hr.config.parameter']
        if employee_id:
            domain_ps.append(('employee_id', '=', employee_id))
            domain_psl.append(('employee_id', '=', employee_id))

        domain_ps.append(('state', '=', 'done'))
        fecha_desde = fecha_desde or datetime.now().strftime('%Y-%m-%d')

        domain_ps.append(('date_from', '>=', fecha_desde))
        domain_ps.append(('date_from', '<=', fecha_hasta))
        #domain_ps.append(('payslip_run_id', '!=', False))
        payslip_ids = payslip_obj.search( domain_ps)
        for pid in payslip_ids:
            p_ids.append(pid.id)
        if len(p_ids) == 0:
            if not is_anticipo and not config_data:
                raise exceptions.except_orm(('Advertencia!'), ('No se han confirmado las nóminas correspondientes al mes anterior.\n \
                                                Por favor verifique y proceda a realizar la confirmación de las nóminas\n \
                                                correspondientes.'))
        domain_psl.append(('slip_id', 'in', p_ids))
        if code:
            domain_psl.append(('code', 'in', code))
        for line in payslip_line_obj.search(domain_psl):
            pl_ids.append(line.id)
        for i in  payslip_line_obj.browse(pl_ids):
            amount += i.amount

        return amount


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
    #def get_days_util_to_pay(self):
    #    local_obj = self.id
    #    return local_obj.util_days_to_pay

    # @api.v7
    def validate_util_days_to_pay(self, values):
        fecha =None
   #     dias1 = self.util_days_to_pay
        dias = values.get('util_days_to_pay', False)
        especial = values.get('check_special_struct', False)
        struct_obj = self.env['hr.payroll.structure']
        struct_id = values.get('struct_id', False)
        is_anticipo = values.get('is_anticipo', False)
        if especial or struct_id:
            struct = struct_obj.browse(struct_id)
            struct_name = struct.name
          #  if 'UTILIDAD' in struct_name.upper() and is_anticipo and dias == 0:
           #     raise exceptions.except_orm(('Advertencia!'), (
            #        u'El Número de días a pagar no puede ser 0! Por favor verifique e intente nuevamente.'))
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
                    u'El Número de días a pagar es mayor que el máximo establecido! Por favor verifique e intente nuevamente.'))
            # elif dias == 0:
            #     raise Warning(('Advertencia!'), (
            #         u'El Número de días a pagar no puede ser 0! Por favor verifie e intente nuevamente.'))

        return True

    @api.multi
    def write(self, values):
        if self._context is None: context = {}
        if not hasattr(self._ids, '__iter__'): ids = [self._ids]
        if values.get('check_special_struct', False) or values.get('struct_id', False):
            self.validate_util_days_to_pay(values)
        res = super(hr_payslip_run, self).write(values)
        return res

    @api.model
    def create(self, values):
        if self._context is None: context = {}
        res = {}
        if values.get('check_special_struct',False):
            self.validate_util_days_to_pay(values)
        res = super(hr_payslip_run, self).create(values)
        return res


