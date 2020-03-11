# coding: utf-8

from odoo import fields, models, api, exceptions
#from openerp.osv import osv
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payroll_fideicomiso_intereses(models.Model):
    _name = 'hr.payroll.fideicomiso.intereses'
    _description = 'tambla de interese de fideicomiso'

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

    anio = fields.Integer('Anio tasa de interes')
    mes = fields.Selection(MESES,'Mes tasa de interes')
    tasa = fields.Float('Tasa Interes',digits=(3,2), help=u'Tasa de Interés activa')
    numero_gaceta  = fields.Char('Numero gaceta', size=7, help=u'Número de gaceta oficial donde se publicó la tasa de interés')
    fecha_gaceta = fields.Date('Fecha gaceta')
    activa_pasiva = fields.Float('Tasa activa', digits=(3,2), help='Promedio entre tasa activa y pasiva')

    @api.multi
    def get_tasa(self,fecha):
        tasa = 0.0
        fecha = datetime.strptime(fecha,DEFAULT_SERVER_DATE_FORMAT)
        interes_id = self.search([('anio','=',fecha.year),('mes','=',str(fecha.month))])
        for i in self.browse(interes_id.id):
            tasa = i.activa_pasiva

        return tasa
