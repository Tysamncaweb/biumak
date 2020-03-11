# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    Change: jeduardo **  12/05/2016 **  hr_contract **  Modified
#    Comments: Creacion de campos adicionales para el modulo de contratos
#
# ##############################################################################################################################################################################

from odoo import fields, models, api
from odoo import osv
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'


    utilidades_fraccionadas_check = fields.Boolean('check utilidades fraccionadas')
    utilidades_fraccionadas_value = fields.Float('value utilidades fraccionadas')
    vacaciones_fraccionadas_check = fields.Boolean('Vacaciones fraccionadas')
    vacaciones_fraccionadas_value = fields.Float('Vacaciones Fraccionadas')
    bono_vac_fraccionado_check = fields.Boolean('check bono vac fraccionado')
    bono_vac_fraccionado_value = fields.Float('value bono vac fraccionado')
    indemnizacion_check = fields.Boolean('Indemnizacion check')
    indemnizacion_value = fields.Float('Indemnizacion value')



hr_contract()
