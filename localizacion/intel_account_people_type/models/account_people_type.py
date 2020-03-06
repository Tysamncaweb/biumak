# -*- coding: utf-8 -*-
import locale
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat

class ResPartner(models.Model):
    _inherit = 'res.partner'

    people_type = fields.Selection([
        ('pnre', 'PNRE    Persona Natural Residente'),
        ('pnnr', 'PNNR    Persona Natural No Residente'),
        ('pjdo', 'PJDO    Persona Jurídica Domiciliada'),
        ('pjnd', 'PJND    Persona Jurídica No Domiciliada')
    ], 'Tipo de Persona', required=True)

