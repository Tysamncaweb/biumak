# coding: utf-8
from odoo import fields, models, api, exceptions, _
#from openerp.osv import osv
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class primera_carga_historico(models.TransientModel):
    _name = 'primera.carga.historico'


    empleado = fields.Many2one('hr.employee', 'Empleado')
    fecha_ini = fields.Date('Fecha Inicio')
    fecha_fin =  fields.Date('Fecha fin')
    #ACUMULADO DE PRESTACIONES SOCIALES
    neto_acumulado = fields.Float('Monto acumulado Prestaciones Sociales')
    dias_acumulados = fields.Integer('Dias Acumulado Prestaciones Sociales')
    dias_adicionales = fields.Integer('dias adicionales prestaciones Sociales')
    acumulado_dias_adic = fields.Float('Acumulado de los dias adicionales')
    #ANTICIPO DE PRESTACIONES SOCIALES
    total_anticipo = fields.Float('Total anticipos')
    ultimo_anticipo = fields.Float('ultimo anticipo')
    fecha_ult_ant = fields.Date('Fecha del Ultimo Anticipo')
    #ACUMULADO DE INTERESES DE PRESTACIONES SOCIALES
    total_int_acu = fields.Float('Intereses Acumulados')
    interes_pagado= fields.Float('Intereses Pagados')
    fecha_ult_interes = fields.Date('Fehca Intereses Pagados')



    @api.multi
    def carga_data(self):

        contract_obj = self.env['hr.contract']
        values = {self.neto_acumulado: 'Antiguedad Neto Acumulado de las GPS', self.dias_acumulados: ' Días Acumulados de las GPS',
                 }


        for a,b in values.items():
            if a == 0:
                raise exceptions.except_orm(_('Advertencia'), _('Por Favor Recuerde que para el campo %s se le debe registrar un valor')%(b))
        history_values = {}
        cedula = self.empleado.identification_id_2
        monto = acumulado = 0.0
        hoy = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        contract_id = contract_obj.search([('employee_id', '=', self.empleado.id)])
        fi_hist_obj = self.env['hr.historico.fideicomiso']
        carga_values = {}

        history_values.update({'employee_id': self.empleado.id,
                               'cedula_identidad': cedula,
                               'salario_diario': 0.0,
                               'type_record': 'inicial',
                               'fecha_inicio': self.fecha_ini,
                               'fecha_fin': self.fecha_fin,
                               'monto_tri_ant': 0.0,
                               'monto_incremento': 0.0,
                               'fecha_aporte': hoy,
                               'dias_aporte': 0,
                               'monto_acumulado': self.neto_acumulado + self.acumulado_dias_adic - self.total_anticipo,
                               'dias_acumuluados': self.dias_acumulados + self.dias_adicionales ,
                               'dias_adicionales': self.dias_adicionales,
                               'aporte_dias_adic': 0.0,
                               'GPS_dias_adicionales': self.acumulado_dias_adic,
                               'total_anticipos': self.total_anticipo,
                               'anticipo': self.ultimo_anticipo,
                               'fecha_anticipo': self.fecha_ult_ant,
                               'tasa': 0.0,
                               'monto_intereses': 0.0,
                               'interes_a_pagar': 0.0,
                               'monto_total_intereses': self.total_int_acu,
                               'anticipo_intereses': self.interes_pagado,
                               'fecha_anticipo_intereses': self.fecha_ult_interes,
                               })

        history_id = fi_hist_obj.create(history_values)
        fi_hist_obj.write({'history_id': history_id})
        carga_values.update(
            {'monto_acumulado': (self.neto_acumulado +  self.acumulado_dias_adic), 'fecha_ult_actualizacion': hoy, 'anticipo_check':False,
             'anticipo_value': self.neto_acumulado*0.75, 'interes_acumulado_check':False, 'interes_acumulado_value': self.total_int_acu,
             })
        contract_id.write(carga_values)
