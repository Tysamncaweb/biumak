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
##############################################################################

from odoo import fields, models, api, exceptions
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, time, timedelta
import time
#import pytz
import os
import re

class ResCountryStates(models.Model):
    _inherit = "res.country.state"

    res_state_ve_id = fields.Char("Id uníco estados de Venezuela")


class res_country_city(models.Model):
    _name = "res.country.city"

    res_country_state_id = fields.Char("Estate")
    name = fields.Char("City")
    is_capital = fields.Boolean("Is capital")

class res_state_municipal(models.Model):
    _name = "res.state.municipal"

    ids_comp = fields.Char("id")
    res_country_state_id = fields.Char("Estate")
    name = fields.Char("Municipal")

class res_municipal_parish(models.Model):
    _name = "res.municipal.parish"

    res_state_municipal_id = fields.Char("Municipio")
    name = fields.Char("Parish")

