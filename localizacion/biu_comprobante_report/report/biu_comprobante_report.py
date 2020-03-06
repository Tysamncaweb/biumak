from odoo import models, api, _, exceptions
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta, time
class ReportAccountPayment(models.AbstractModel):
    _name = 'report.biu_comprobante_report.template_comprobante_contable'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['account.move'].browse(docids)}
        res = dict()
        docs = []
        lines = []
        debe_total = haber_total = 0.00
        fecha_actual = datetime.strptime(str(date.today()), '%Y-%m-%d')
        fecha_actual = fecha_actual.strftime('%d/%m/%Y')
        if data['form'].state != 'posted':
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'Solo puede generar un Comprobante en estado "Validado"'))
        if data['form'].state == 'posted':
            fecha = datetime.strptime(data['form'].date, '%Y-%m-%d')
            fecha = fecha.strftime('%d/%m/%Y')

            for line in data['form'].line_ids:
                lines.append({
                    'cuenta': line.account_id.name,
                    'empresa': line.partner_id.name,
                    'descripcion': line.name,
                    'cuenta_analitica': line.analytic_account_id.name,
                    'etiquetas_analiticas': line.analytic_tag_ids.name,
                    'importe_moneda': self.separador_cifra(line.amount_currency),
                    'moneda': line.currency_id.name,
                    'debe': self.separador_cifra(line.debit),
                    'haber': self.separador_cifra(line.credit),
                    'fecha_vencimiento': line.date_maturity,
                })
                debe_total +=  line.debit
                haber_total += line.credit
            docs.append({
                'name': data['form'].name,
                'date': fecha,
                'diario': data['form'].journal_id.name,
                'referencia': data['form'].ref,
                'compañia': data['form'].company_id.name,
                'fecha_actual': fecha_actual,
                'debe_total': self.separador_cifra(debe_total),
                'haber_total': self.separador_cifra(haber_total),
            })

        return {
            'data': data['form'],
            'model': self.env['report.biu_comprobante_report.template_comprobante_contable'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'lines': lines,


        }

    def separador_cifra(self,valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return  monto