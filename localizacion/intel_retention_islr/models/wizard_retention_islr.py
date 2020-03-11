# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
from io import BytesIO
import xlwt, base64
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class RetentionISLR(models.Model):
    _name = 'account.retention.islr'
    _description = 'Open Retention ISLR'

    company = fields.Many2one('res.company', required=True)
    start_date = fields.Date(required=True, default=fields.Datetime.now)
    end_date = fields.Date(required=True, default=fields.Datetime.now)
    supplier = fields.Boolean(default=False)
    customer = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner')
    clientes = fields.Many2one('res.partner')
    concepto = fields.Boolean(default=True)
    todos = fields.Boolean(default=False)
    concept = fields.Many2many('islr.wh.concept')

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)


    @api.multi
    def generate_retention_islr_xls(self, data):
        hoy = date.today()
        format_new = "%d/%m/%Y"
        hoy_date = datetime.strftime(hoy, format_new)
        start_date = datetime.strftime(datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT), format_new)
        end_date = datetime.strftime(datetime.strptime(self.end_date, DEFAULT_SERVER_DATE_FORMAT), format_new)
        locale.setlocale(locale.LC_ALL, '')

        self.ensure_one()
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        writer = wb.add_sheet('Nombre de hoja')

        header_content_style = xlwt.easyxf("font: name Helvetica size 80 px, bold 1, height 200;")
        sub_header_style = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")
        sub_header_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;")
        line_content_style_totales = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right;")

        row = 1
        col = 0

        # writer.write_merge(row, row, 0, header_cols, "Información de contactos",)

        writer.write_merge(row, row, 3, 4, "RAZON SOCIAL:", sub_header_style_bold)
        writer.write_merge(row, row, 5, 6, str(self.company.name), sub_header_content_style)
        writer.write_merge(row, row, 11, 12, "Fecha de Impresión:", sub_header_style_bold)
        writer.write_merge(row, row, 13, 13, hoy_date, sub_header_content_style)
        row += 1

        writer.write_merge(row, row, 3, 3, "R.I.F:", sub_header_style_bold)
        writer.write_merge(row, row, 4, 5, str(self.company.vat), sub_header_content_style)
        writer.write_merge(row, row, 8, 8, "Teléfono", sub_header_style_bold)
        writer.write_merge(row, row, 9, 9, str(self.company.phone), sub_header_content_style)
        row += 1

        writer.write_merge(row, row, 3, 4, "Dirección Fiscal:", sub_header_style_bold)
        writer.write_merge(row, row, 5, 6, str(self.company.street), sub_header_content_style)
        row += 1

        writer.write_merge(row, row, 1, 2, "Fecha Desde:", sub_header_style_bold)
        writer.write_merge(row, row, 3, 3, start_date, sub_header_content_style)
        writer.write_merge(row, row, 5, 6, "Fecha Hasta:", sub_header_style_bold)
        writer.write_merge(row, row, 7, 7, end_date, sub_header_content_style)
        row += 1

        islr_concept = []
        retention_islr = []
        pnre = []
        unico = []
        repetido = []
        retention_islr_asc = []
        pnre_asc = []
        partner = []
        concept_id = []
        lista_nueva_partner = []
        suma_base = 0
        suma_imp_ret = 0
        suma_total_base = 0
        suma_total_imp_ret = 0
        if self.todos == True:
            concepts = self.env['islr.wh.concept'].search([('id', '!=', 0)])
            concept = []
            for i in concepts:
                concept.append(i.id)
        if self.supplier == True and self.customer == False:
            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=',self.company.id),
                                                              ('partner_id', '=', self.partner_id.id),
                                                              ('type', '=', 'in_invoice'),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', self.start_date),
                                                              ('date_ret', '<=', self.end_date)])

        if self.supplier == False and self.customer == True:
            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', self.company.id),
                                                              ('partner_id', '=', self.clientes.id),
                                                              ('type', '=', 'out_invoice'),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', self.start_date),
                                                              ('date_ret', '<=', self.end_date)])

        if self.supplier == False and self.customer == False:
            todo_supplier = self.env['res.partner'].search([('supplier', '=', True)])
            todo_customer = self.env['res.partner'].search([('customer', '=', True)])
            for y in todo_supplier:
                partner.append(y.id)
            for g in todo_customer:
                partner.append(g.id)

            for i in partner:
                if i not in lista_nueva_partner:
                    lista_nueva_partner.append(i)
            type = ['out_invoice', 'in_invoice']

            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', self.company.id),
                                                              ('partner_id', 'in', lista_nueva_partner),
                                                              ('type', 'in', type),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', self.start_date),
                                                              ('date_ret', '<=', self.end_date)])


        for a in islr_concept_id:
            islr_concept.append(a.id)

        islr_concept_line = self.env['islr.wh.doc.line'].search([('concept_id', '=', concept),
                                                                 ('islr_wh_doc_id', '=', islr_concept)])
        if islr_concept_line:
            for i in islr_concept_line:
                concept_id.append(i.concept_id.name)
            concept_id.sort()
        else:
            raise UserError('No hay retenciones en estado Hecho')

        var_concept = concept_id[0]
        for concept_line in islr_concept_line:
            if concept_line.invoice_id:
                if concept_line.invoice_id.partner_id.vat[0] in 'VvEe':
                    if concept_line.partner_id.country_id == self.company.country_id:
                        var = 'PNRE'
                        nature = True
                        residence = True
                    else:
                        var = 'PNNR'
                        nature = True
                        residence = False
                elif concept_line.invoice_id.partner_id.vat[0] in 'GgJj':
                    if concept_line.invoice_id.partner_id.country_id == self.company.country_id:
                        var = 'PJDO'
                        nature = False
                        residence = True
                    else:
                        var = 'PJND'
                        nature = False
                        residence = False

                concepts_people_type = self.env['islr.rates'].search([('concept_id', '=', concept_line.concept_id.id),
                                                                      ('nature', '=', nature),
                                                                      ('residence', '=', residence)])

                retention_islr.append({
                    'concept': concept_line.concept_id.name,
                    'people_type': var,
                    'date': concept_line.invoice_id.date_invoice,
                    'invoice': concept_line.invoice_id.number,
                    'rif': concept_line.invoice_id.partner_id.vat,
                    'proveedor': concept_line.invoice_id.partner_id.name,
                    'amount': concept_line.base_amount,
                    'amount_ret': concept_line.amount,
                    'retention_islr': int(concept_line.retencion_islr),
                    'currency_id': concept_line.invoice_id.currency_id,
                })
                retention_islr_asc = sorted(retention_islr, key=lambda k: k['concept'])

                pnre.append({
                    'code': concepts_people_type.code,
                    'name': concept_line.concept_id.name,
                    'var': var,
                    'porcentaje': str(int(concept_line.retencion_islr)) + '%',
                    'porcentaje_islr': int(concept_line.retencion_islr),
                    'amount': concept_line.base_amount,
                    'amount_ret': concept_line.amount,
                })
                pnre_asc = sorted(pnre, key=lambda k: k['code'])
        for vars in pnre_asc:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('name') == vars2.get('name') and vars.get('var') == vars2.get('var') and vars.get(
                            'porcentaje') == vars2.get('porcentaje') and vars.get('code') == vars2.get('code')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)

        for uni in unico:
            for rep in repetido:
                if (uni['name'] == rep['name']) and (uni['var'] == rep['var']) and (
                        uni['porcentaje'] == rep['porcentaje']) and (uni['code'] == rep['code']):
                    uni.update({'amount': rep.get('amount') + uni.get('amount'),
                                'amount_ret': rep.get('amount_ret') + uni.get('amount_ret')})

        for type in unico:
            if var_concept != type['name']:
                if suma_total_base != 0:
                    row += 2
                    writer.write_merge(row, row, 2, 3, "Total General", sub_header_style)
                    writer.write_merge(row, row, 4, 9, type['name'], sub_header_style)
                    writer.write_merge(row, row, 10, 11, locale.format_string("%.2f", suma_total_base, grouping=True), line_content_style_totales)
                    writer.write_merge(row, row, 12, 13, locale.format_string("%.2f", suma_total_imp_ret, grouping=True), line_content_style_totales)

                    suma_total_base += type['amount']
                    suma_total_imp_ret += type['amount_ret']
                    suma_total_base = 0
                    suma_total_imp_ret = 0

            if (type['var'] == 'PNRE') or (type['var'] == 'PNNR') or (type['var'] == 'PJDO') or (type['var'] == 'PJND'):
                row += 2
                writer.row(row).height = 300
                writer.write_merge(row, row, 1, 1, "COD.", header_content_style)
                writer.write_merge(row, row, 2, 2, type['code'], header_content_style)
                writer.write_merge(row, row, 3, 10, type['name'], header_content_style)
                writer.write_merge(row, row, 11, 11, type['var'], header_content_style)
                writer.write_merge(row, row, 12, 12, type['porcentaje'], header_content_style)

                row += 2
                writer.write_merge(row, row, 1, 1, "Fecha", sub_header_style)
                writer.write_merge(row, row, 2, 3, "Rif", sub_header_style)
                writer.write_merge(row, row, 4, 7, "Nombre del Proveedor", sub_header_style)
                writer.write_merge(row, row, 8, 9, "Factura", sub_header_style)
                writer.write_merge(row, row, 10, 11, "Importe Base", sub_header_style)
                writer.write_merge(row, row, 12, 13, "Imp. Retenido", sub_header_style)

                for islr in retention_islr_asc:
                    if (type['porcentaje_islr'] == islr['retention_islr']) and (type['name'] == islr['concept']) and (
                            type['var'] == islr['people_type']):
                        row += 1
                        writer.write_merge(row, row, 1, 1, islr['date'], sub_header_content_style)
                        writer.write_merge(row, row, 2, 3, islr['rif'], sub_header_content_style)
                        writer.write_merge(row, row, 4, 7, islr['proveedor'], sub_header_content_style)
                        writer.write_merge(row, row, 8, 9, islr['invoice'], sub_header_content_style)
                        writer.write_merge(row, row, 10, 11, locale.format_string("%.2f", islr['amount'], grouping=True), line_content_style)
                        writer.write_merge(row, row, 12, 13, locale.format_string("%.2f", islr['amount_ret'], grouping=True), line_content_style)

                        suma_base += islr['amount']
                        suma_imp_ret += islr['amount_ret']
            row += 2
            writer.write_merge(row, row, 7, 8, "Total Retención", sub_header_style)
            writer.write_merge(row, row, 9, 9, type['code'], sub_header_style)
            writer.write_merge(row, row, 10, 11, locale.format_string("%.2f", suma_base, grouping=True), line_content_style_totales)
            writer.write_merge(row, row, 12, 13, locale.format_string("%.2f", suma_imp_ret, grouping=True), line_content_style_totales)
            suma_base = 0
            suma_imp_ret = 0

            suma_total_base += type['amount']
            suma_total_imp_ret += type['amount_ret']

            var_concept = type['name']
        row += 2
        writer.write_merge(row, row, 2, 3, "Total General", sub_header_style)
        writer.write_merge(row, row, 4, 9, type['name'], sub_header_style)
        writer.write_merge(row, row, 10, 11, locale.format_string("%.2f", suma_total_base, grouping=True), line_content_style_totales)
        writer.write_merge(row, row, 12, 13, locale.format_string("%.2f", suma_total_imp_ret, grouping=True), line_content_style_totales)

        suma_total_base = 0
        suma_total_imp_ret = 0

        col = 1

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'Detalle_De_Ret_de_ISLR.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.retention.islr',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def generate_retention_islr_pdf(self, data):
        b = []
        name = []
        for a in self.concept:
            b.append(a.id)
            name.append(a.name)
        data = {
            'ids': self.ids,
            'model': 'report.intel_retention_islr.report_retention_islr1',
            'form': {
                'date_start': self.start_date,
                'date_stop': self.end_date,
                'company': self.company.id,
                'supplier': self.supplier,
                'partner_id': self.partner_id.id,
                'customer': self.customer,
                'clientes': self.clientes.id,
                'concept': b,
                'concept_name': name,
                'todos': self.todos,
            },
            'context': self._context
        }
        return self.env.ref('intel_retention_islr.action_report_retention_islr').report_action(self, data=data, config=False)


class ReportRetentionISLR(models.AbstractModel):
    _name = 'report.intel_retention_islr.report_retention_islr1'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        end_date = data['form']['date_stop']
        company_id = data['form']['company']
        supplier = data['form']['supplier']
        partner_id = data['form']['partner_id']
        customer = data['form']['customer']
        clientes = data['form']['clientes']
        concept = data['form']['concept']
        concept_name = data['form']['concept_name']
        todos = data['form']['todos']
        today = date.today()

        islr_concept = []
        retention_islr = []
        pnre = []
        unico = []
        repetido = []
        retention_islr_asc = []
        pnre_asc = []
        concept_id = []
        partner = []
        lista_nueva_partner = []
        if todos == True:
            concepts = self.env['islr.wh.concept'].search([('id', '!=', 0)])
            concept = []
            for i in concepts:
                concept.append(i.id)

        company = self.env['res.company'].search([('id', '=', company_id)])

        if supplier == True and customer == False:
            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', company_id),
                                                              ('partner_id', '=', partner_id),
                                                              ('type', '=', 'in_invoice'),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', date_start),
                                                              ('date_ret', '<=', end_date)])

        if supplier == False and customer == True:
            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', company_id),
                                                              ('partner_id', '=', clientes),
                                                              ('type', '=', 'out_invoice'),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', date_start),
                                                              ('date_ret', '<=', end_date)])

        if supplier == True and customer == True:
            type = ['out_invoice', 'in_invoice']
            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', company_id),
                                                              ('partner_id', 'in', [clientes, partner_id]),
                                                              ('type', '=', type),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', date_start),
                                                              ('date_ret', '<=', end_date)])

        if supplier == False and customer == False:
            todo_supplier = self.env['res.partner'].search([('supplier', '=', True)])
            todo_customer = self.env['res.partner'].search([('customer', '=', True)])
            for y in todo_supplier:
                partner.append(y.id)
            for g in todo_customer:
                partner.append(g.id)

            for i in partner:
                if i not in lista_nueva_partner:
                    lista_nueva_partner.append(i)
            type = ['out_invoice', 'in_invoice']

            islr_concept_id = self.env['islr.wh.doc'].search([('company_id', '=', company_id),
                                                              ('partner_id', 'in', lista_nueva_partner),
                                                              ('type', 'in', type),
                                                              ('state', '=', 'done'),
                                                              ('date_ret', '>=', date_start),
                                                              ('date_ret', '<=', end_date)])



        for a in islr_concept_id:
            islr_concept.append(a.id)

        islr_concept_line = self.env['islr.wh.doc.line'].search([('concept_id', '=', concept),
                                                                 ('islr_wh_doc_id', '=', islr_concept)])

        if islr_concept_line:
            for i in islr_concept_line:
                concept_id.append(i.concept_id.name)
            concept_id.sort()
        else:
            raise UserError('No hay retenciones en estado Hecho')

        '''concepts_people_type = self.env['islr.rates'].search([('concept_id', '=', concept)])
        for concept_line in concepts_people_type:

            pnre.append({
                'name': concept_line.concept_id.name,
                'residence': concept_line.residence,
                'nature': concept_line.nature,
                'porcentaconcept_linee': concept_line.wh_perc,
            })'''


        for concept_line in islr_concept_line:
            if concept_line.invoice_id:
                if concept_line.invoice_id.partner_id.vat[0] in 'VvEe':
                    if concept_line.partner_id.country_id == company.country_id:
                        var = 'PNRE'
                        nature = True
                        residence = True
                    else:
                        var = 'PNNR'
                        nature = True
                        residence = False
                elif concept_line.invoice_id.partner_id.vat[0] in 'GgJj':
                    if concept_line.invoice_id.partner_id.country_id == company.country_id:
                        var = 'PJDO'
                        nature = False
                        residence = True
                    else:
                        var = 'PJND'
                        nature = False
                        residence = False
                concepts_people_type = self.env['islr.rates'].search([('concept_id', '=', concept_line.concept_id.id),
                                                                      ('nature', '=', nature),
                                                                      ('residence', '=', residence)])

                retention_islr.append({
                    'concept': concept_line.concept_id.name,
                    'people_type': var,
                    'date': concept_line.invoice_id.date_invoice,
                    'type': concept_line.invoice_id.type,
                    'invoice': concept_line.invoice_id.number,
                    'number': concept_line.invoice_id.supplier_invoice_number,
                    'rif': concept_line.invoice_id.partner_id.vat,
                    'proveedor': concept_line.invoice_id.partner_id.name,
                    'amount': concept_line.base_amount,
                    'amount_ret': concept_line.amount,
                    'retention_islr': concept_line.retencion_islr,
                    'currency_id': concept_line.invoice_id.currency_id,
                })
                retention_islr_asc = sorted(retention_islr, key=lambda k: k['concept'])

                pnre.append({
                    'code': concepts_people_type.code,
                    'name': concept_line.concept_id.name,
                    'var': var,
                    'porcentaje': concept_line.retencion_islr,
                    'amount': concept_line.base_amount,
                    'amount_ret': concept_line.amount,
                })
                pnre_asc = sorted(pnre, key=lambda k: k['code'])
        for vars in pnre_asc:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('name') == vars2.get('name') and vars.get('var') == vars2.get('var')  and vars.get('porcentaje') == vars2.get('porcentaje') and vars.get('code') == vars2.get('code')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)

        for uni in unico:
            for rep in repetido:
                if (uni['name'] == rep['name']) and (uni['var'] == rep['var']) and (uni['porcentaje'] == rep['porcentaje']) and (uni['code'] == rep['code']):
                    uni.update({'amount': rep.get('amount') + uni.get('amount'),
                                'amount_ret': rep.get('amount_ret') + uni.get('amount_ret')})



        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'end_date': end_date,
            'start_date': date_start,
            'today': today,
            'company': company,
            'rif': company.vat,
            'pnre': unico,
            'concept_name': concept_name,
            'var_concept': concept_id,
            'retention_islr': retention_islr_asc,
            }