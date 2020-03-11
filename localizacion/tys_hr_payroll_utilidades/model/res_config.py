# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, exceptions

class human_resources_configuration(models.TransientModel):
    _name = 'periodo.utilidades'

    module_hr_utilidades_add_calculo = fields.Boolean('Salario a base de calculo',
                                                           help="""Verdadero: obtener el salario promedio durante el periodo seleccionado.\n"
                                                                 "Falso: obtener el salario del mes anterior.""")
    module_hr_utilidades_add_date_start = fields.Date('Inicio periodo de calculo',
                                                           help="Fecha de inicio del periodo para calcular el salario promediio")
    module_hr_utilidades_add_date_end = fields.Date('Fin periodo de calculo',
                                                         help="Fecha de finalizacion del periodo para calcular el salario promediio")


    def get_config_values(self):
        res = {}
        self._cr.execute("""select
	                    module_hr_utilidades_add_calculo,
	                    module_hr_utilidades_add_date_start,
	                    module_hr_utilidades_add_date_end
                        from periodo_utilidades ORDER BY write_date desc LIMIT 1""")
        res = self._cr.dictfetchall()
        return res
