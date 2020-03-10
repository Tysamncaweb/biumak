# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons import web
from odoo.service import security

import werkzeug
import werkzeug.utils
import datetime



class LambuLogin(web.controllers.main.Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False, csrf=False)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            print(kw['login'])
            lambu_login = request.env['lambu.login.users'].search([('user_name', '=', kw['login'])])

            if (lambu_login): 
                lambu_login._check_credentials(kw['password'])
                luid= lambu_login.id #lambu user id
                uid = lambu_login.odoo_user.id #odoo user id
                request.session.uid = uid
                request.env['res.users'].browse(uid)._update_last_login()
                # request.env['res.users']._invalidate_session_cache()
                # request.session.session_token = security.compute_session_token(request.session, request.env)
                
                # create new session and store tokken session
                lambu_session= request.env['lambu.login.session'].sudo().create({ 'user_id': luid })
                request.session['session_token_lambu'] = lambu_session.token #store tokken
                print(request.session.sid)
                
                # Session Expired time
                request.session['session_last_activity'] = datetime.datetime.now()
                # print ("on init: %s" % request.session['session_last_activity'])

                # Redirect and set cookies
                response = werkzeug.utils.redirect( '/web?&#action=%s' % (uid))
                response.set_cookie('session_token_lambu', request.session['session_token_lambu'])

                return response
                # return http.local_redirect(self._login_redirect(uid), keep_hash=True)

        return super(LambuLogin, self).web_login(redirect, **kw)

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        if (request.session.session_token_lambu ):
            tk= request.session['session_token_lambu'] # get lambu tokken of actual session
            lambu_session = request.env['lambu.login.session'].search([('token', '=', tk)]) # Get actual session
            if (lambu_session):
                return lambu_session._close_session()

        else :
            request.session.logout(keep_db=True)
            response = werkzeug.utils.redirect(redirect, 303)
            response.set_cookie('session_token_lambu', '') # clear cookie session tokken
            return response
        