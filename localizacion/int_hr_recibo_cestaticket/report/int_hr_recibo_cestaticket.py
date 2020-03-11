from odoo import models, api, _, exceptions
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta, time
class ReportAccountPayment(models.AbstractModel):
    _name = 'report.int_hr_recibo_cestaticket.template_recibo_cestaticket'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip'].browse(docids)}
        res = dict()
        docs = []
        if len(data['form'].struct_id.rule_ids) == 1:
            if data['form'].struct_id.rule_ids.code == '7001':
                name = data['form'].employee_id.display_name
                fecha_ingreso = data['form'].employee_id.fecha_inicio
                fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d')
                fecha_ingreso = fecha_ingreso.strftime('%d/%m/%Y')
                cedula_letra = data['form'].employee_id.nationality
                cedula = data['form'].employee_id.identification_id_2
                rif = data['form'].employee_id.rif[3:11]
                rif2 = data['form'].employee_id.rif[-1]
                cargo = data['form'].employee_id.job_id.display_name
                banco = data['form'].employee_id.bank_account_id_emp_2.display_name
                cuenta = data['form'].employee_id.account_number_2
                responsable = data['form'].employee_id.coach_id.display_name
                date_from = data['form'].date_from
                date_to = data['form'].date_to
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                date_from = date_from.strftime('%d/%m/%Y')
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                date_to = date_to.strftime('%d/%m/%Y')

                fecha_actual0 = str(date.today())
                fecha_genera = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]
                n_dias = data['form'].worked_days_line_ids[0].number_of_days
                if n_dias > 30:
                    n_dias=30
                for a in data['form'].line_ids:
                    if a.code == '7001':
                        monto = a.total
                        salario = a.total/n_dias
                        salario = float("{0:.2f}".format(salario))
                monto = self.separador_cifra(monto)
                salario = self.separador_cifra(salario)
                docs.append({
                    'name': name.upper(),
                    'fecha_ingreso':fecha_ingreso,
                    'date_from':date_from,
                    'date_to':date_to,
                    'rif': rif,
                    'rif2':rif2,
                    'cedula_letra':cedula_letra,
                    'cedula': cedula,
                    'cargo': cargo,
                    'banco': banco,
                    'cuenta': cuenta,
                    'n_dias': int(n_dias),
                    'salario_diario': salario,
                    'monto':monto,
                    'fecha_genera' : fecha_genera,
                    'responsable': responsable

                })
            else:
                raise exceptions.except_orm(_('Advertencia!'), (u'La nómina actual no es de Cestaticket, no se puede generar dicho Recibo.'))
        else:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'La nómina actual no es de Cestaticket, no se puede generar dicho Recibo.'))
        return {
            'data': data['form'],
            'model': self.env['report.int_hr_recibo_cestaticket.template_recibo_cestaticket'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,


        }

    def separador_cifra(self,valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return  monto