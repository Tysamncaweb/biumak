# -*- coding: utf-8 -*-
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo import models, fields, api
from passlib.context import CryptContext
from hashlib import sha256
import datetime
import werkzeug
import werkzeug.utils
import contextlib
import passlib.context
import uuid
import socket



class LambuResUsers(models.Model):
    _inherit = 'res.users'

    # relations
    lambu_user = fields.One2many(
        'lambu.login.users', 'odoo_user', string='Usuario Lambu')


DEFAULT_CRYPT_CONTEXT = passlib.context.CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'plaintext'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['plaintext'],
)


class LambuLoginUser(models.Model):
    _name = 'lambu.login.users'
    _table = 'lambu_login_users'
    _description = 'Lambu users'
    _sql_constraints = [
        ('user_name_key', 'UNIQUE (user_name)',
         'You can not have two users with the same login !')
    ]

    user_name = fields.Char('Usuario', required=True)
    password = fields.Char('Contraseña', compute='_compute_password',
                           inverse='_set_password', copy=False, store=True)
    active = fields.Boolean('Activo', default=True)

    # relations
    odoo_user = fields.Many2one('res.users', string='Usuario_Odoo', required=True, domain=[
                                ('active', '=', True)])  # Role
    employee_id = fields.Many2one(
        'hr.employee', string='Empleado', required=True)
    session_id = fields.One2many('lambu.login.session', 'user_id', 'Sesiones')

    def init(self):
        cr = self.env.cr
        # allow setting plaintext passwords via SQL and have them
        # automatically encrypted at startup: look for passwords which don't
        # match the "extended" MCF and pass those through passlib.
        # Alternative: iterate on *all* passwords and use CryptContext.identify
        cr.execute("""
        SELECT id, password FROM lambu_login_users
        WHERE password IS NOT NULL
          AND password !~ '^\$[^$]+\$[^$]+\$.'
        """)
        if self.env.cr.rowcount:
            Users = self.sudo()
            for uid, pw in cr.fetchall():
                Users.browse(uid).password = pw

    def _set_password(self):
        ctx = self._crypt_context()
        for user in self:
            self._set_encrypted_password(user.id, ctx.encrypt(user.password))

    def _crypt_context(self):
        """ Passlib CryptContext instance used to encrypt and verify
        passwords. Can be overridden if technical, legal or political matters
        require different kdfs than the provided default.

        Requires a CryptContext as deprecation and upgrade notices are used
        internally
        """
        return DEFAULT_CRYPT_CONTEXT

    def _set_encrypted_password(self, uid, pw):
        assert self._crypt_context().identify(pw) != 'plaintext'

        self.env.cr.execute(
            'UPDATE lambu_login_users SET password=%s WHERE id=%s',
            (pw, uid)
        )
        self.invalidate_cache(['password'], [uid])

    def _check_credentials(self, password):
        """ Validates the current user's password.

        Override this method to plug additional authentication methods.

        Overrides should:

        * call `super` to delegate to parents for credentials-checking
        * catch AccessDenied and perform their own checking
        * (re)raise AccessDenied if the credentials are still invalid
          according to their own validation method

        When trying to check for credentials validity, call _check_credentials
        instead.
        """
        """ Override this method to plug additional authentication methods"""
        assert password
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM lambu_login_users WHERE id=%s",
            [self.id]
        )
        [hashed] = self.env.cr.fetchone()
        valid, replacement = self._crypt_context()\
            .verify_and_update(password, hashed)
        if replacement is not None:
            self._set_encrypted_password(self.env.user.id, replacement)
        if not valid:
            raise AccessDenied()

    def _compute_password(self):
        for user in self:
            user.password = ''


class LambuLoginSession(models.Model):
    _name = 'lambu.login.session'  # model name
    _description = 'Lambu sessions'

    def _default_token(self):
        return uuid.uuid4().hex

    def _get_host_info(self):
        # hostname = socket.gethostname()
        # remote_addr = socket.gethostbyname(hostname)
        wsgienv = request.httprequest.environ
        remote_addr = wsgienv['REMOTE_ADDR']
        return remote_addr

    token = fields.Char(default=_default_token, required=True)
    ip_pc = fields.Char(default= _get_host_info, string= 'Dirección IP' ,required=True)
    date_close = fields.Datetime(default= None, string= 'Fecha de cierre de sesion')

    #relations
    user_id = fields.Many2one('lambu.login.users', string='Usuario', required=True)
    user_name = fields.Char(related="user_id.user_name", store=False)

    def _close_session(self, redirect='/web'):
        if (request.session.session_token_lambu ):
            tk= request.session['session_token_lambu'] # get lambu tokken of actual session
            lambu_session = request.env['lambu.login.session'].search([('token', '=', tk)]) # Get actual session
            if (lambu_session):
                close_moment= datetime.datetime.now() # fecha y hora de cierre
                lambu_session.sudo().write({'date_close': close_moment}) #se actualiza la fecha de cierre de la session
                request.session['session_token_lambu']= None # clear session tokken
                request.session['session_last_activity']= None
            # else: #What happens?
        
        request.session.logout(keep_db=True)
        response = werkzeug.utils.redirect(redirect, 303)
        response.set_cookie('session_token_lambu', '') # clear cookie session tokken
        return response

class LambuActivitySession(models.AbstractModel):
    _inherit= 'ir.http'

    @classmethod
    def _authenticate(cls, auth_method='user'):
        super(LambuActivitySession, cls)._authenticate(auth_method)
        _expired_time= 15 # expired session time (2hours)
        ignore_url= ['longpolling/poll']
        ignore = False

        for url in ignore_url:
            if url in request.httprequest.url:
                ignore= True
                print("Ignore URL:: " + request.httprequest.url)
        
        if (request.session.session_token_lambu and request.session.session_last_activity and not ignore): # check cookies
            tk= request.session['session_token_lambu'] # get lambu tokken
            lambu_session = request.env['lambu.login.session'].search([('token', '=', tk)]) # Get actual session

            if (lambu_session): # if find actual session
                last_activity= request.session['session_last_activity'] # last activity
                # print ("on check: %s" % last_activity)
                actual_moment= datetime.datetime.now()  # get actual moment
                inactivity_time= (actual_moment - last_activity).total_seconds() / 60 # compute inactivity time
                
                if (inactivity_time < _expired_time): # if has not expierd session
                    request.session['session_last_activity'] = datetime.datetime.now() # update last activity
                    # print ("%s" % request.session['session_last_activity'])
                else :
                    return lambu_session._close_session() # close session
            
