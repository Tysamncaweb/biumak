# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ProfesorRecord(models.Model):
    _name = "data.test"
    name=fields.Char(string='Mi Nombre',required=True)
    lname=fields.Char(string='Mi Apellidos') 
    edad=fields.Char('Edad')    
    genero = fields.Selection([('h', 'Hombre'), ('m', 'Mujer'), ('o', 'Otro')], string='Género')
    nacionalidad = fields.Many2one('res.country', string='Nacionalidad')

