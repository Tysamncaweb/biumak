from odoo import models, fields, api
from odoo.exceptions import UserError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.exceptions import ValidationError
import urllib
from odoo import http



class report_replacement_petty_cash(models.Model):
    _name = "report.tys_account_petty_cash.report_replacement_petty_cash"
    _description = "Report Reposicion Caja Chica"

    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['replacement.petty.cash'].browse(docids)}
        res = dict()
        docs = []
        facturas_ids = []
        debe = 0
        haber = 0

        format_new = "%d/%m/%Y"

        fecha_actual0 = str(date.today())
        fecha_actual = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]


        replacement = self.env['replacement.petty.cash']
        replacement_number = replacement.search([('id', '=', docids)])

        saldo_transitoria = self.env['account.move.line'].search([('account_id', '=', replacement_number.transitoria.id)])
        for transitoria in saldo_transitoria:
            debe += transitoria.debit
            haber += transitoria.credit
        saldo_trans1 = debe - haber
        saldo_trans = round(saldo_trans1,2)

        code = replacement_number.code.name
        disponible_petty_cash = replacement_number.apertura - replacement_number.amount_total

        responsible = replacement_number.responsable
        number = replacement_number.name

        disponible = str(replacement_number.disponible).split('.')
        disponible = ",".join(disponible)

        liq_pendiente = saldo_trans - replacement_number.amount_total


        self.env.cr.execute(
            "SELECT invoice_petty_cash_id FROM invoice_petty_cash_replacement_petty_cash_rel WHERE replacement_petty_cash_id=%s",
            (replacement_number.id,))
        var1 = self.env.cr.fetchall()

        for a in var1:
            id = a[0]
            facturas_ids.append(id)

        for factura in facturas_ids:
            invoice_petty_cash = self.env['invoice.petty.cash'].search([('id', '=', factura)])

            if invoice_petty_cash.type_petty_cash == 'invoice':
                type_document = 'FACTURA'
            if invoice_petty_cash.type_petty_cash == 'document':
                type_document = 'DOCUMENTO'
            if invoice_petty_cash.type_petty_cash == 'nota':
                type_document = 'NOTA_ENTREGA'


            docs.append({
                'date_invoice': datetime.strftime(datetime.strptime(invoice_petty_cash.date_petty_cash, DEFAULT_SERVER_DATE_FORMAT), format_new),
                'responsible': invoice_petty_cash.petty_cash_partner.name,
                'rif': invoice_petty_cash.petty_cash_partner.vat,
                'type_document': type_document,
                'nro_document': invoice_petty_cash.name,
                'concepto': invoice_petty_cash.razon_gasto,
                'cta_analitica': invoice_petty_cash.cuenta_analitica.name,
                'et_analitica': invoice_petty_cash.etiqueta_analitica.name,
                'amount_exento': invoice_petty_cash.amount_exento,
                'amount_gravable': invoice_petty_cash.amount_gravable,
                'iva': invoice_petty_cash.iva,
                'amount_total': invoice_petty_cash.amount_total,
            })


        return {
            'data': data['form'],
            'model': self.env['report.tys_account_petty_cash.report_replacement_petty_cash'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'code': code,
            'fecha_actual': fecha_actual,
            'number': number,
            'total_exento': replacement_number.amount_exento,
            'total_gravable': replacement_number.amount_gravable,
            'total_iva': replacement_number.amount_tax,
            'total': replacement_number.amount_total,
            'apertura': replacement_number.apertura,
            'disponible': disponible_petty_cash,
            'consumido': replacement_number.consumido,
            'responsible': responsible,
            'liq_pendiente': liq_pendiente,
            'saldo_trans': saldo_trans,
            #'number': number,
        }



