# coding: utf-8
from odoo import fields, models, api, exceptions
from odoo.exceptions import Warning
from datetime import datetime , timedelta
from dateutil import relativedelta, rrule
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_historico_fideicomiso(models.Model):
    _name= 'hr.historico.fideicomiso'
    _description = 'Historico de Fideicomiso'

    TYPE_RECORD =[('inicial','Inicial'),
                  ('fideicomiso','Fideicomiso'),
                  ('anticipo','Anticipo'),
                  ('intereses','Intereses')]
    MESES = [('1', 'Enero'),
             ('2', 'Febrero'),
             ('3', 'Marzo'),
             ('4', 'Abril'),
             ('5', 'Mayo'),
             ('6', 'Junio'),
             ('7', 'Julio'),
             ('8', 'Agosto'),
             ('9', 'Septiembre'),
             ('10', 'Octubre'),
             ('11', 'Noviembre'),
             ('12', 'Diciembre')]

    employee_id = fields.Many2one('hr.employee', 'Empleado')
    cedula_identidad = fields.Char('Cedula', size=8)
    monto_incremento = fields.Float('Aporte', digits=(10,2))
    fecha_inicio = fields.Date('Fecha Inicio', help='Fecha de ingreso del empleado')
    fecha_fin = fields.Date('fecha Fin', help='fecha de corte')
    salario_diario = fields.Float('Salario Integral Diario', digits=(10,2))
    dias_aporte = fields.Integer('Dias de aporte')
    fecha_aporte = fields.Date('Fecha del aporte')
    aporte_dias_adic = fields.Float('Aporte Dias Adicionales', digits=(10, 2))
    monto_acumulado = fields.Float('Monto Acumulado', digits=(10,2))
    dias_acumuluados = fields.Integer('Dias de Aporte')
    dias_adicionales = fields.Integer('Dias Adicionales')
    fecha_anticipo = fields.Date('Fecha del Anticipo')
    anticipo_intereses = fields.Float('Anticipo de Interesas', digits=(10,2))
    monto_total_intereses = fields.Float('Monto Total Intereses', digits=(10,2))
    monto_intereses = fields.Float('Monto Intereses (historico)',digits=(10,2))
    anticipo = fields.Float('Anticipo de fideicomiso', digits=(10, 2))
    total_anticipos = fields.Float('Total Anticipos de fideicomiso', digits=(10, 2))
    monto_tri_ant = fields.Float('Monto trimestre anterior', digits=(10, 2))
    fecha_anticipo_intereses = fields.Date('Fecha del Anticipo de intereses')
    type_record = fields.Selection(TYPE_RECORD,'Tipo de Registro',help='utiliza los siguientes valores:\n'
                                                       'inicial: creado por la carga inicial de datos\n'
                                                       'fideicomiso:creado por el procesamiento de una nomina de fideicomiso\n'
                                                       'intereses: creado por la carga de los intereses\n'
                                                       'anticipo: creado por el procesamiento de una nomina de anticipo')

    history_id = fields.Many2one('hr.historico.fideicomiso','Calculode Intereses (many2one)')
    intereses_ids = fields.One2many('hr.historico.fideicomiso', 'history_id', string='Calculod de Intereses (one2many)')
    mes_intereses = fields.Selection(MESES,'Mes de calculo de los intereses')
    tasa_intereses = fields.Float('tasa de interes', digits=(3,2))
    intereses_acum_tri_ant =fields.Float('Intereses trimestre anterior', digits=(10,2))
    intereses_acum_tri = fields.Float('Intereses trimestre', digits=(10, 2))
    tasa= fields.Float('Tasa Interes', digits=(10, 2))
    interes_a_pagar = fields.Float('Interes a pagar', digits=(10, 2))
    GPS_dias_adicionales = fields.Float('Dias Adicionales de la GPS')

    @api.model
    def create(self, vals):
        if vals:
            new_id = super(hr_historico_fideicomiso, self).create(vals)
            return new_id
        else:
            raise Warning((u'Disculpe, pero no está permitido crear registros en ésta vista.\n'
                           u' Por favor consulte con su supervisor inmediato!'))

    @api.multi
    def write(self, values):
        if values:
            return super(hr_historico_fideicomiso, self).write(values)
        else:
            raise Warning((u'Disculpe, pero no está permitido modificar registros en ésta vista.\n'
                           u' Por favor consulte con su supervisor inmediato!'))

    @api.multi
    def get_last_history_fi(self, employee_id, id =None):
        dominio = [('employee_id', '=', employee_id)]
        fecha = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
      #  fechita = emplo.contract_id.fecha22

        dominio.append(('fecha_fin', '<', fecha))
        # if record_type == 'fideicomiso':
        #     dominio.append(('monto_acumulado','!=',None),('monto_acum_tri_ant','!=',None))
        # elif record_type == 'anticipo':
        #     dominio.append(('monto_acumulado', '!=', None), ('total_anticipos', '!=', None))
        # elif record_type == 'intereses':
        #     dominio.append(('monto_acumulado', '!=', None), ('monto_acum_tri', '!=', None))
        fi_hist_obj = self.env['hr.historico.fideicomiso'].search([('id','!=', 0)])
        if id:
            history_obj = fi_hist_obj
        else:
            history_id = fi_hist_obj.search(dominio,
                                        order='fecha_fin desc', limit=1)
            history_obj = self.browse(history_id.id)
        return history_obj

    @api.multi
    def calculate_acum(self, history_vals=None, payslip_vals=None):
        acumulados = {}
        fi_hist_obj = self.env['hr.historico.fideicomiso']
        m_t_a = m_a = p_m_i = 0.0
        d_a = p_d_a = 0
        if payslip_vals:
            if history_vals:
                # history_obj = fi_hist_obj.browse(cr, uid, history_vals.id, context=context)
                for ho in history_vals:
                    m_t_a = ho.monto_acumulado + payslip_vals['monto_incremento']
                    d_a = ho.dias_acumuluados + payslip_vals['dias_acumulados'] + payslip_vals['dias_adicionales']
                    # d_a = (ho.dias_acumuluados + payslip_vals['dias_adicionales']) if payslip_vals['dias_adicionales'] > 0 else 0
                    # m_a = ho.monto_acumulado
            else:
                m_t_a = payslip_vals['monto_incremento']
                d_a = payslip_vals['dias_adicionales']
                # m_a = m_t_a
            p_m_i = payslip_vals['monto_incremento']
            p_d_a = payslip_vals['dias_adicionales']
        acumulados.update({'monto_acumulado':m_t_a,
                        # 'monto_acumulado':m_a,
                        'monto_incremento':p_m_i,
                        'dias_acumuluados':d_a,
                        'dias_adicionales':p_d_a if p_d_a > 0 else 0})
        return acumulados

    def calcula_intereses(self, employee_id, fecha_inicio, fecha_fin, historico=None, sal_diario=0.0, payslip_values=None):
        offset = 0
        history_new_values = {}
        intereses_obj = self.env['hr.payroll.fideicomiso.intereses']
        config_obj = self.env['hr.config.parameter']
        contract_obj = self.env['hr.contract']
        mes_ini_tri = int(config_obj._hr_get_parameter('hr.payroll.mes.inicio.trimestre', True))
        if 1 <= mes_ini_tri <= 3:
            offset = mes_ini_tri - 1
        else:
            raise exceptions.except_orm(('Advertencia!'), (
                u'El mes de de inicio del trimestre esta mal configurado.\n'
                u'Debe tener un valor entre 1(Enero) y 3(Marzo).\n'
                u'Por favor verifique el parámetro hr.payroll.mes.inicio.trimestre\n'
                u' y coloque el valor correspondiente.'))
        # historico = self.get_last_history_fi(cr, uid, employee_id, None, context=context)
        # hoy = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        mes_hoy = int(fecha_inicio.split('-')[1])
        if (mes_hoy - offset)%3 == 0:
            #ULTIMO MES DEL TRIMESTRE:
            acumulado = payslip_values.get('monto_incremento')
            acumulado_ant = historico.monto_acumulado
            anticipo = historico.anticipo

            calculo_dias_adic = sal_diario * (payslip_values.get('dias_adicionales'))

     #   elif historico:
      #      #CUALQUIR OTRO MES DEL TRIMESTRE:
       #     acumulado = historico.monto_tri_ant
        else:
            acumulado = sal_diario * (payslip_values.get('dias_aporte'))
            acumulado_ant = historico.monto_acumulado
            anticipo = historico.anticipo

            calculo_dias_adic= sal_diario *(payslip_values.get('dias_adicionales'))
        tasa1 = tasa2 =0.0
        monto = 0.0
        if fecha_inicio and fecha_fin :
            cont= 0
            if  fecha_inicio[0:4] < fecha_fin[0:4]:
                cant_meses = 12 - int(fecha_inicio[5:7]) +  int(fecha_fin[5:7])
            else:
                cant_meses = int(fecha_fin[5:7]) - int(fecha_inicio[5:7])

            for a in range(cant_meses):
                cont += 1
              #  fecha_inicio_inc = datetime(fecha_inicio) + datetime(fecha_inicio).month + 1
                mes_posterior = datetime.strptime(fecha_inicio, DEFAULT_SERVER_DATE_FORMAT) + relativedelta.relativedelta(
                    months=a)
                tasa1 = intereses_obj.get_tasa(str(mes_posterior)[0:10])
                tasa2 += tasa1
                if cont != 3:
                     monto += acumulado_ant*tasa1/1200
                else:

                        monto += (acumulado + acumulado_ant + calculo_dias_adic) * tasa1 / 1200

                    #REGISTRO DE LOS INTERESES CALCULADOS EN EL HISTORICO PARA EL MES EN CURSO
        contract_id = contract_obj.search([('employee_id','=',employee_id)])
        contract = contract_obj.browse(contract_id.id)
        history_new_values.update({'monto_intereses':monto,
                                   'monto_total_intereses':historico.monto_total_intereses + monto,
                                   'mes_intereses': str(mes_hoy),
                                   'salario_diario': sal_diario if sal_diario>0 else historico.salario_diario,
                                   'tasa': tasa2
                                   })

        return history_new_values

    @api.multi
    def procesar_anticipo(self, lds, employee_id, values):
        line_obj = self.env['hr.payslip.line']
        contract_obj = self.env['hr.contract']
        history_values = {}
        cedula = values.get('cedula','')
        monto = acumulado =0.0
        hoy = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        contract_id = contract_obj.search([('employee_id','=',employee_id),('date_end','=',None)])
        for line in lds:
            monto = line.amount
            contract_values = {}
            if line.code == values.get('code_anticipo',False):
                history = self.get_last_history_fi( employee_id, None)
                if history:
                    acumulado = history.monto_acumulado
                if acumulado > 0 and  acumulado >= monto:
                    acumulado -= monto
                else:
                    raise exceptions.except_orm(('Advertencia!'), ('El monto del anticipo es mayor al total acumulado.\n'
                                                            'No se puede procesar la solicitud, \n'
                                                            'por favor comuníquese con su supervisor.'))
                history_values.update({'employee_id': employee_id,
                                       'cedula_identidad': cedula,
                                       'type_record': 'anticipo',
                                       'fecha_anticipo_intereses':history.fecha_anticipo_intereses,
                                       'monto_acumulado': acumulado,
                                       'monto_total_intereses': history.monto_total_intereses,
                                       'fecha_anticipo': hoy,
                                       'anticipo': monto,
                                       'salario_diario': history.salario_diario,
                                       'fecha_inicio':values.get('fecha_inicio', False),
                                       'fecha_fin': values.get('fech_fin', False),
                                       'fecha_aporte': history.fecha_aporte,
                                       'dias_aporte': 0,
                                       'dias_acumuluados': history.dias_acumuluados,
                                       'dias_adicionales': history.dias_adicionales,
                                       'aporte_dias_adic': 0.0,
                                       'GPS_dias_adicionales': history.GPS_dias_adicionales,
                                       'monto_tri_ant': history.monto_tri_ant,
                                       'total_anticipos': history.total_anticipos + monto,
                                       'anticipo_intereses': history.anticipo_intereses,
                                       'interes_a_pagar': 0.0,
                                       'tasa': 0.0,
                                       })

                self.create(history_values)
                contract_values.update(
                    {'anticipo_check': False, 'anticipo_value': acumulado * 0.75, 'monto_acumulado': acumulado,  'interes_acumulado_value': history_values['monto_total_intereses'],
                                        'interes_acumulado_check': False,})
                contract_id.write(contract_values)
        return monto

    @api.multi
    def procesar_interes_anticipo(self, lds, employee_id, values,fecha_inicio, monto_anticipo1):
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        ahora = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
  #      contract_data = employee_id.contract_id
        history_values = {}
        cedula = employee_obj.get_employee_cedula(employee_id)
        intereses_obj = self.env['hr.payroll.fideicomiso.intereses']
        for line in lds:
            contract_values = {}
            if line.code == values.get('code_intereses', False):
                history = self.get_last_history_fi( employee_id.id, None)
                if history:
                    anticipo_ultimo = monto_anticipo1
                    tasa = intereses_obj.get_tasa(fecha_inicio)
                    contract_id = contract_obj.search([('employee_id','=',employee_id.id)])
                    valor_interes= contract_id.interes_acumulado_value
     #               anticipo_interes = anticipo_ultimo*tasa/1200
    #                act_total_intereses = history.monto_total_intereses - anticipo_interes
                    history_values.update({'employee_id': employee_id.id,
                                           'cedula_identidad': cedula,
                                           'type_record': 'intereses',
                                           'fecha_anticipo_intereses': ahora,
                                           'monto_acumulado': history.monto_acumulado - valor_interes ,
                                           'monto_total_intereses': history.monto_total_intereses - valor_interes,
                                           'fecha_anticipo': history.fecha_anticipo,
                                           'anticipo': anticipo_ultimo,
                                           'salario_diario': history.salario_diario,
                                           'fecha_inicio': fecha_inicio,
                                           'fecha_fin': values.get('fech_fin', False),
                                           'fecha_aporte': history.fecha_aporte,
                                           'dias_aporte': 0,
                                           'dias_acumuluados': history.dias_acumuluados,
                                           'dias_adicionales': history.dias_adicionales,
                                           'aporte_dias_adic': 0.0,
                                           'GPS_dias_adicionales': history.GPS_dias_adicionales,
                                           'monto_tri_ant': history.monto_tri_ant,
                                           'total_anticipos': history.total_anticipos + anticipo_ultimo,
                                           'anticipo_intereses': history.anticipo_intereses + valor_interes,
                                           'interes_a_pagar': valor_interes,
                                           'tasa': tasa,
                                           })
                    contract_values.update({'interes_acumulado_check': False, 'interes_acumulado_value': history_values['monto_total_intereses'],
                                       })
                    contract_id.write(contract_values)

                    self.create(history_values)




class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'

    anticipo_check1= fields.Boolean('Anticipo prestaciones')
    tipo_nomina1 = fields.Text('tipo de nomina')
    struct_id_code = fields.Text('tipo de nomina')

    @api.onchange('struct_id')
    def _onchage_tipo_nomina(self):
        self.tipo_nomina1= False
        tipo_nomina1 = self.env['hr.config.parameter']._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones', True)
        if tipo_nomina1 == self.struct_id.code:
            self.tipo_nomina1 = True
        return


    @api.multi
    def close_payslip_run(self):
        payslip_obj = self.env['hr.payslip']
        contract_obj = self.env['hr.contract']
        fi_hist_obj = self.env['hr.historico.fideicomiso']
        config_obj = self.env['hr.config.parameter']
        line_obj = self.env['hr.payslip.line']
        history = None
        history_values = {}
        history_new_values = {}
        intereses_values = {}
        payslip_values = {}
        contract_values = {}
        values = {}
        sal_int_diario = 0.0
        tipo_nomina = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones',True)
    #    tipo_anticipo = config_obj._hr_get_parameter('hr.payroll.anticipo.prestaciones.code', True)

        dias_str = config_obj._hr_get_parameter('hr.dias.x.mes')
        psr = self.browse(self._ids[0])
        payslip_ids = payslip_obj.search([('payslip_run_id', '=', self._ids[0])])
        payslips = payslip_obj.browse(self._ids[0])
        if psr.check_special_struct and self.anticipo_check1 == False and tipo_nomina in psr.struct_id.code :
            for p in payslip_ids:
                contract_id = p.contract_id
                sal_int_diario = p.salario_integral_fi
                # REGISTRO DEL HISTORICO DE PRESTACIONES SOCIALES
                history = fi_hist_obj.get_last_history_fi(p.employee_id.id, None)
                history_new_values.update({'monto_acum_tri_ant':history.monto_acumulado})
                payslip_values.update({'monto_incremento':sal_int_diario*p.dias_acumulados,'dias_acumulados':p.dias_acumulados,'dias_adicionales':p.dias_adicionales , 'dias_aporte':p.dias_acumulados })
                history_new_values = fi_hist_obj.calculate_acum(history, payslip_values)

                if history.aporte_dias_adic:
                    GPS_dias_adicionales =(sal_int_diario * p.dias_adicionales)
                else:
                    GPS_dias_adicionales = (sal_int_diario * p.dias_adicionales)
                history_new_values.update({'employee_id':p.employee_id.id,
                                           'cedula_identidad':p.employee_id.identification_id_2,
                                           'salario_diario': sal_int_diario,
                                           'fecha_inicio': p.date_from,
                                           'fecha_fin': p.date_to,
                                           'fecha_aporte': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                                           'dias_aporte': p.dias_acumulados,
                                           'monto_acumulado': history.monto_acumulado + sal_int_diario*(p.dias_acumulados + p.dias_adicionales),
                                           'dias_acumulados': history.dias_acumuluados + history.dias_aporte + p.dias_adicionales,
                                           'dias_adicionales':(p.dias_adicionales if p.dias_adicionales else 0),
                                           'aporte_dias_adic': (sal_int_diario * p.dias_adicionales) if p.dias_adicionales else 0.0,
                                           'GPS_dias_adicionales': history.GPS_dias_adicionales + GPS_dias_adicionales,
                                           'monto_tri_ant': history.monto_incremento if history.monto_incremento else sal_int_diario*float(dias_str),
                                           'total_anticipos': history.total_anticipos,
                                           'anticipo':history.anticipo,
                                           'fecha_anticipo':history.fecha_anticipo,
                                           'anticipo_intereses':history.anticipo_intereses,
                                           'fecha_anticipo_intereses': history.fecha_anticipo_intereses,
                                           'interes_a_pagar': 0.0,
                                           'type_record':'fideicomiso',})
                history_new_values.update(fi_hist_obj.calcula_intereses(p.employee_id.id, p.date_from, p.date_to, history, sal_int_diario, payslip_values
                                                                ))
                history_id = fi_hist_obj.create(history_new_values)
                fi_hist_obj.write({'history_id':history_id})
                #CTUALIZA LOS VALORES DE LAS PRESTACIONES SOCIALES EN EL CONTRATO DEL EMPLEADO


                contract_values.update({'monto_acumulado': history_new_values['monto_acumulado'],
                                        'fecha_ult_actualizacion': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                                        'anticipo_value': history_new_values['monto_acumulado'] * 0.75,
                                        'intereses_acumulado_value': history_new_values['monto_total_intereses'],
                                        'interes_acumulado_check': False,
                                        'come_from': 'nomina'})
                contract_id.write(contract_values)
        elif psr.check_special_struct and tipo_nomina in psr.struct_id.code and self.anticipo_check1==True:
            # ANTICIPOS
            for p in payslip_ids:
                # ANTICIPO DE PRESTACIONES SOCIALES
                code_anticipo = config_obj._hr_get_parameter('hr.payroll.anticipo.prestaciones', False)
                # ANTICIPO DE INTERESES SOBRE PRESTACIONES SOCIALES
                code_intereses = config_obj._hr_get_parameter('hr.payroll.anticipo.prestaciones.intereses', False)
                values.update({
                    'code_anticipo':code_anticipo,
                    'code_intereses':code_intereses,
                    'cedula':p.employee_id.identification_id_2,
                    'fecha_inicio':p.date_from,
                    'fech_fin':p.date_to})
                #ld = p.line_ids
                for lds in p.line_ids:
                    if lds.code == code_anticipo:
                        monto_anticipo1 = fi_hist_obj.procesar_anticipo(lds, p.employee_id.id, values)
                    elif lds.code == code_intereses:
                        if monto_anticipo1 != 0:
                            fi_hist_obj.procesar_interes_anticipo(lds,p.employee_id, values, p.date_from, monto_anticipo1)
                        else:
                            raise Warning(
                                (u'Verifique si se encuentra activo el anticipo en el contrato del empleado .\n'
                                 u' Por favor intente de nuevo!'))
                #line_id = line_obj.search([('slip_id', '=', p.id), '|', ('code', '=', code_anticipo),('code', '=', code_intereses)])
                #if line_id:
                #    fi_hist_obj.procesar_anticipo(line_id, p.employee_id.id, values)

        res = super(hr_payslip_run, self).close_payslip_run()
        return res