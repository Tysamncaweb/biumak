# coding: utf-8

import base64
import time
from xml.etree.ElementTree import Element, SubElement, tostring

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.addons import decimal_precision as dp

ISLR_XML_WH_LINE_TYPES = [('invoice', 'Invoice'), ('employee', 'Employee')]


class IslrXmlWhDoc(models.Model):
    _name = "islr.xml.wh.doc"
    _description = 'Generate XML'

    @api.depends('xml_ids')
    def _get_amount_total(self):
        """ Return withhold total amount
        """
        self.amount_total_ret = 0.0
        for line in self.xml_ids:
            self.amount_total_ret += line.wh
        #return amount_ret

    @api.depends('xml_ids')
    def _get_amount_total_base(self):
        """ Return base total amount
        """
        self.amount_total_base = 0.0
        # for xml in self.browse():
        #   res[xml.id] = 0.0
        for line in self.xml_ids:
            self.amount_total_base += line.base
        #return amount_base

    @api.model
    def _get_company(self):
        user = self.env['res.users'].browse()
        return user.company_id.id


    name = fields.Char(
            string='Description', size=128, required=True, select=True,
            default='Income Withholding ' + time.strftime('%m/%Y'),
            help="Description about statement of income withholding")
    company_id = fields.Many2one(
            'res.company', string='Company', required=True,
            default=lambda s: s._get_company(),
            help="Company")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('generated', 'Generated'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], string='State', readonly=True, default='draft',
            help="Voucher state")
    amount_total_ret = fields.Float(
            compute='_get_amount_total', method=True, digits=(16, 2), readonly=True,
            string='Income Withholding Amount Total',
            help="Amount Total of withholding")
    amount_total_base= fields.Float(
            compute='_get_amount_total_base', method=True, digits=(16, 2), readonly=True,
            string='Without Tax Amount Total', help="Total without taxes")
    xml_ids = fields.One2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold invoice line id')
    invoice_xml_ids = fields.One2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold invoice line id',
            domain=[('type', '=', 'invoice')])
    employee_xml_ids = fields.One2many(
            'islr.xml.wh.line', 'islr_xml_wh_doc', 'XML Document Lines',
            readonly=True, states={'draft': [('readonly', False)]},
            help='XML withhold employee line id',
            domain=[('type', '=', 'employee')])
    user_id = fields.Many2one(
            'res.users', string='User', readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda s: s._uid,
            help='User Creating Document')
        #rsosa: ID 95
    xml_filename = fields.Char('Nombre Archivo XML')
    xml_binary = fields.Binary('Archivo XML')
    # period_id = fields.Many2one(
    #        'account.period', string='Period', required=True,
    #       default=lambda s: s.period_return(),
    #      help="Period when the accounts entries were done")
    date_start = fields.Date("Fecha Inicio", required=True,
        states={'draft': [('readonly', False)]},
        help="Begin date of period")
    date_end = fields.Date("fecha Fin", required=True,
        states={'draft': [('readonly', False)]},
        help="Begin date of period")

    @api.multi
    def copy(self, default=None):
        """ Initialized id by duplicating
        """
        if default is None:
            default = {}
        default = default.copy()
        default.update({
            'xml_ids': [],
            'invoice_xml_ids': [],
            'employee_xml_ids': [],
        })

        return super(IslrXmlWhDoc, self).copy(default)

    @api.multi
    def get_period(self):

        split_date = self.date_end.split('-')

        return str(split_date[0]) + str(split_date[1])

    def period_return(self):
        """ Return current period
        """
        '''
        period_obj = self.pool.get('account.period')
        fecha = time.strftime('%m/%Y')
        period_id = period_obj.search([('code', '=', fecha)])
        if period_id:
            return period_id[0]
        else:
            return False

    def search_period(self, period_id, ids):
        """ Return islr lines associated with the period_id
        @param period_id: period associated with returned islr lines
        """
        if self._context is None:
            context = {}
        res = {'value': {}}
        if period_id:
            islr_line = self.pool.get('islr.xml.wh.line')
            islr_line_ids = islr_line.search(
                 [('period_id', '=', period_id)])
            if islr_line_ids:
                res['value'].update({'xml_ids': islr_line_ids})
                return res
        '''

    @api.multi
    def name_get(self):
        """ Return id and name of all records
        """
        context = self._context or {}
        if not len(self.ids):
            return []

        res = [(r['id'], r['name']) for r in self.read(
             ['name'])]
        return res

    @api.multi
    def action_anular1(self):
        """ Return the document to draft status
        """
        #context = self._context or {}
        return self.write({'state': 'draft'})

    @api.multi
    def action_confirm1(self):
        """ Passes the document to state confirmed
        """
        # to set date_ret if don't exists
        #obj_ixwl = self.env['islr.xml.wh.line']
        #self.invoice_xml_ids = obj_ixwl.search([('date_ret','>=',self.date_start),
        #                             ('date_ret','<=',self.date_end)])

        #for item in self.browse(self.ids):
        #    for ixwl in item.xml_ids:
        #        if not ixwl.date_ret and ixwl.islr_wh_doc_inv_id:
        #            obj_ixwl.write(
        #                 [ixwl.id],
        #                {'date_ret':
        #                    ixwl.islr_wh_doc_inv_id.islr_wh_doc_id.date_ret})
        #            ixwl.write({'date_ret':
        #                    ixwl.islr_wh_doc_inv_id.islr_wh_doc_id.date_ret})
        return self.write({'state': 'confirmed'})

    @api.multi
    def action_generate_line_xml(self):
        """ Passes the document to state confirmed
        """
        # to set date_ret if don't exists
        obj_ixwl = self.env['islr.xml.wh.line']
        self.invoice_xml_ids = obj_ixwl.search([('date_ret', '>=', self.date_start),
                                                ('date_ret', '<=', self.date_end)])
        return True

    @api.multi
    def action_done1(self):
        """ Passes the document to state done
        """
        #context = self._context or {}
        root = self._xml()
        self._write_attachment(root)
        self.write({'state': 'done'})
        return True

    @api.multi
    def _write_attachment(self, root):
        """ Codify the xml, to save it in the database and be able to
        see it in the client as an attachment
        @param root: data of the document in xml
        """
        fecha = time.strftime('%Y_%m_%d_%H%M%S')
        name = 'ISLR_' + fecha + '.' + 'xml'
#         self.env('ir.attachment').create(cr, uid, {
#             'name': name,
#             'datas': base64.encodestring(root),
#             'datas_fname': name,
#             'res_model': 'islr.xml.wh.doc',
#             'res_id': ids[0],
#         }, context=context
#         )
#         cr.commit()
        #rsosa: ID 95
        self.write({
            'xml_filename': name,
            'xml_binary': base64.encodebytes(root)
                                  })
        #self.log( self.ids[0], _("File XML %s generated.") % name)

    def indent(self, elem, level=0):
        """ Return indented text
        @param level: number of spaces for indentation
        @param elem: text to indentig
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def import_xml_employee(self):
        ids = isinstance(self.ids, (int)) and [self.ids] or self.ids
        xml_brw = self.browse(ids)[0]
        #period = time.strptime(xml_brw.period_id.date_stop, '%Y-%m-%d')
        return {'name': _('Import XML employee'),
                'type': 'ir.actions.act_window',
                'res_model': 'employee.income.wh',
                'view_type': 'form',
                'view_id': False,
                'view_mode': 'form',
                'nodestroy': True,
                'target': 'new',
                'domain': "",
                'context': {
                    #'default_period_id': xml_brw.period_id.id,
                    #'islr_xml_wh_doc_id': xml_brw.id,
                    #'period_code': "%0004d%02d" % (
                    #    period.tm_year, period.tm_mon),
                    'company_vat': xml_brw.company_id.partner_id.vat[0:]}}

    def _xml(self):
        """ Transform this document to XML format
        """
        rp_obj = self.env['res.partner']
        inv_obj = self.env['account.invoice']
        root = ''
        for ixwd_id in self.ids:
            wh_brw = self.browse(ixwd_id)

            #period = time.strptime(wh_brw.period_id.date_stop, '%Y-%m-%d')
            period = self.get_period()
            #period2 = "%0004d%02d" % (period.tm_year, period.tm_mon)

            local_ids = [int(i.id) for i in wh_brw.xml_ids]
            if local_ids:
                sql = '''
                SELECT partner_vat,control_number, porcent_rete,
                    concept_code,invoice_number,
                    SUM(COALESCE(base,0)) as base, account_invoice_id, date_ret
                FROM islr_xml_wh_line
                WHERE id in (%s)
                GROUP BY partner_vat, control_number, porcent_rete, concept_code,
                    invoice_number,account_invoice_id, date_ret''' % "," .join(map(str,local_ids))
                self.env.cr.execute(sql)
                xml_lines = self.env.cr.fetchall()
            else:
                xml_lines = []
            company_vat = rp_obj._find_accounting_partner(wh_brw.company_id.partner_id).vat[0:]
            company_vat = company_vat.replace("-","")
            company_vat1 = wh_brw.company_id.partner_id.vat
            company_vat1 = company_vat1.replace("-","")
            root = Element("RelacionRetencionesISLR")
            #root.attrib['RifAgente'] = rp_obj._find_accounting_partner(wh_brw.company_id.partner_id).vat[0:] if wh_brw.company_id.partner_id.vat else ''
            x1 = "RifAgente"
            x2 = "Periodo"
            root.attrib[x1] = company_vat if company_vat1 else ''
            root.attrib[x2] = period



            for line in xml_lines:
                partner_vat, control_number, porcent_rete, concept_code, \
                    invoice_number, base, inv_id, date_ret = line
                control_number = control_number.replace("-","")
                invoice_number = invoice_number.replace("-","")
                detalle = SubElement(root, "DetalleRetencion")
                SubElement(detalle, "RifRetenido").text = partner_vat

                SubElement(detalle, "NumeroFactura").text = invoice_number
                SubElement(detalle, "NumeroControl").text = control_number

                #SubElement(detalle, "NumeroFactura").text = ''.join(
                #    i for i in invoice_number if i.isdigit())[:] or '0'
                #SubElement(detalle, "NumeroControl").text = ''.join(
                #    i for i in control_number if i.isdigit())[:] or 'NA'
                if date_ret:
                    date_ret = time.strptime(date_ret, '%Y-%m-%d')
                    SubElement(detalle, "FechaOperacion").text = time.strftime(
                        '%d/%m/%Y', date_ret)
                # This peace of code will be left for backward compatibility
                # TODO: Delete on V8 onwards
                elif inv_id and inv_obj.browse(inv_id).islr_wh_doc_id:
                    date_ret = time.strptime(inv_obj.browse(
                         inv_id).islr_wh_doc_id.date_ret, '%Y-%m-%d')
                    SubElement(detalle, "FechaOperacion").text = time.strftime(
                        '%d/%m/%Y', date_ret)
                SubElement(detalle, "CodigoConcepto").text = concept_code
                SubElement(detalle, "MontoOperacion").text = str(base)
                SubElement(detalle, "PorcentajeRetencion").text = str(
                    porcent_rete)
        #self.indent(root)
        return tostring(root, encoding="ISO-8859-1")

IslrXmlWhDoc()


class IslrXmlWhLine(models.Model):
    _name = "islr.xml.wh.line"
    _description = 'Generate XML Lines'


    concept_id = fields.Many2one(
            'islr.wh.concept', string='Withholding Concept',
            help="Withholding concept associated with this rate",
            required=True, ondelete='cascade')
    #period_id = fields.Many2one(
    #        'account.period', 'Period', required=False,
    #        help="Period when the journal entries were done")
    partner_vat = fields.Char(
            'VAT', size=10, required=True, help="Partner VAT")
    invoice_number = fields.Char(
            'Invoice Number', size=20, required=True,
            default='0',
            help="Number of invoice")
    control_number = fields.Char(
            'Control Number', size=20, required=True,
            default='NA',
            help="Reference")
    concept_code = fields.Char(
            'Concept Code', size=10, required=True, help="Concept code")
    base = fields.Float(
            'Base Amount', required=True,
            help="Amount where a withholding is going to be computed from",
            digits=dp.get_precision('Withhold ISLR'))
    raw_base_ut = fields.Float(
            'UT Amount', digits=dp.get_precision('Withhold ISLR'),
            help="UT Amount")
    raw_tax_ut= fields.Float(
            'UT Withheld Tax',
            digits=dp.get_precision('Withhold ISLR'),
            help="UT Withheld Tax")
    porcent_rete = fields.Float(
            'Withholding Rate', required=True, help="Withholding Rate",
            digits=dp.get_precision('Withhold ISLR'))
    wh = fields.Float(
            'Withheld Amount', required=True,
            help="Withheld amount to partner",
            digits=dp.get_precision('Withhold ISLR'))
    rate_id = fields.Many2one(
            'islr.rates', 'Person Type',
            domain="[('concept_id','=',concept_id)]", required=False,
            help="Person type")
    islr_wh_doc_line_id = fields.Many2one(
            'islr.wh.doc.line', 'Income Withholding Document',
            ondelete='cascade', help="Income Withholding Document")
    account_invoice_line_id = fields.Many2one(
            'account.invoice.line', 'Invoice Line',
            help="Invoice line to Withhold")
    account_invoice_id = fields.Many2one(
            'account.invoice', 'Invoice', help="Invoice to Withhold")
    islr_xml_wh_doc = fields.Many2one(
            'islr.xml.wh.doc', 'ISLR XML Document', help="Income tax XML Doc")
    partner_id = fields.Many2one(
            'res.partner', 'Partner', required=True,
            help="Partner object of withholding")
    sustract = fields.Float(
            'Subtrahend', help="Subtrahend",
            digits=dp.get_precision('Withhold ISLR'))
    islr_wh_doc_inv_id = fields.Many2one(
            'islr.wh.doc.invoices', 'Withheld Invoice',
            help="Withheld Invoices")
    date_ret = fields.Date('Operation Date')
    type = fields.Selection(
            ISLR_XML_WH_LINE_TYPES,
            string='Type', required=True, readonly=False,
            default='invoice')
    _rec_name = 'partner_id'

    def onchange_partner_vat(self, partner_id):
        """ Changing the partner, the partner_vat field is updated.
        """
        context = self._context or {}
        rp_obj = self.env['res.partner']
        acc_part_brw = rp_obj._find_accounting_partner(rp_obj.browse(
             partner_id))
        return {'value': {'partner_vat': acc_part_brw.vat[2:]}}

    def onchange_code_perc(self,rate_id):
        """ Changing the rate of the islr, the porcent_rete and concept_code fields
        is updated.
        """
        context = self._context or {}
        rate_brw = self.env['islr.rates'].browse(rate_id)
        return {'value': {'porcent_rete': rate_brw.wh_perc,
                          'concept_code': rate_brw.code}}


IslrXmlWhLine()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    wh_xml_id = fields.Many2one('islr.xml.wh.line',string='XML Id',default=0,help="XML withhold line id")


AccountInvoiceLine()
