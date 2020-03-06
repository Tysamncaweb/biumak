from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, Warning


class DarrellUser(models.Model):
    _inherit = 'res.users'

    pos_config_id = fields.Many2many('pos.config')