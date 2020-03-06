# coding: utf-8
###########################################################################

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'


    calculate_wh_itf= fields.Boolean(
            'Automatic ITF Withhold',
            help='When True, Supplier ITF Withholding will be check and '
                 'validate automatically', default=False)
    wh_porcentage = fields.Float('Percentage ITF', help="The percentage to apply to withold ")

    account_wh_itf_id = fields.Many2one('account.account', string="Account account ITF", help="This account will be used instead of the default "
                                                       "one as the payable account for the current partner")

    @api.onchange('calculate_wh_itf')
    def _onchange_check_itf(self):

        if not self.calculate_wh_itf:
            self.write({'wh_porcentage':0.0,
                        'account_wh_itf_id': 'False'})
        return
