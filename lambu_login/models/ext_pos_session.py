# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons import web
from odoo.service import security
from odoo import models, fields, api, exceptions

import werkzeug
import werkzeug.utils
import datetime

class ExtPosSession(models.Model):
    _inherit = 'pos.session'

    # def _get_lambu_user(self):
    #     tk= request.session['session_token_lambu']
    #     if (not tk):
    #         tk= None
    #     return tk

    def _get_host_info(self):
        wsgienv = request.httprequest.environ
        remote_addr = wsgienv['REMOTE_ADDR']
        return remote_addr


    user_lambu_id = fields.Many2one('lambu.login.session', string='Usuario Lambu', required=True)
    # token_lambu_user = fields.Char(default= _get_lambu_user, string='Usuario Lambu', required=True)
    ip_pc = fields.Char(default= _get_host_info, string= 'Dirección IP' ,required=True)

    @api.model
    def create(self, values):
        cookies = http.request.httprequest.cookies 
        session_tk = cookies.get('session_token_lambu')

        if (session_tk):
            session = http.request.env['lambu.login.session'].search([('token', '=', session_tk)])[0]
            if (session):
                res = super(ExtPosSession, self).create(values)
                res.write({'user_lambu_id': session.user_id.id})
                return res
        
        raise exceptions.UserError('No ha iniciado sesion de cajero')

   
