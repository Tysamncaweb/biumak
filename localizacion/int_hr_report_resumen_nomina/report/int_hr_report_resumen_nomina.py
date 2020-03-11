from odoo import models, api, _, exceptions
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.int_hr_report_resumen_nomina.template_resumen_nomina'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip.run'].browse(docids)}
        res = dict()
        docs = []
        payslip = self.env['hr.payslip']
        payslip_run = payslip.search([('payslip_run_id', '=', docids)])
        total_monto = 0
        final_total = 0
        config_obj = self.env['hr.config.parameter']
        code_liq = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.liquidacion', True)
        code_cest = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.cestaticket', True)
        code_prest = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones', True)
        code_util = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.utilidades', True)
        code_vac = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.vacaciones', True)

        if not payslip_run:
            raise UserError(_("Por favor verifique si tiene Nóminas Individuales"))


        for slip in payslip_run:

            if slip.state == 'draft':
                raise exceptions.except_orm(_('Advertencia!'), (
                    "No se puede imprimir un reporte que no se encuentre en estado Realizado"))

            if slip.struct_id.code == code_cest:
                raise exceptions.except_orm(_('Advertencia!'),
                                            (
                                                u'La nómina actual es de Cestaticket, no se puede generar dicho Resumen de Nómina.'))
            if slip.struct_id.code == code_prest:
                raise exceptions.except_orm(_('Advertencia!'),
                                            (
                                                u'La nómina actual es Prestaciones Sociales, no se puede generar dicho Resumen de Nómina.'))
            if slip.struct_id.code == code_util:
                raise exceptions.except_orm(_('Advertencia!'),
                                            (
                                                u'La nómina actual es de Utilidades, no se puede generar dicho Resumen de Nómina.'))
            if slip.struct_id.code == code_vac:
                raise exceptions.except_orm(_('Advertencia!'),
                                            (
                                                u'La nómina actual es de Vacaciones, no se puede generar dicho Resumen de Nómina.'))

            cedula_employee = str(slip.employee_id.nationality) + '-' + str(slip.employee_id.identification_id_2)
            fecha_actual0 = str(date.today())
            fecha_actual = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]
            date_start = str(slip.date_from)
            fecha_start = date_start[8:10] + "/" + date_start[5:7] + "/" + date_start[0:4]
            date_end = str(slip.date_to)
            fecha_end = date_end[8:10] + "/" + date_end[5:7] + "/" + date_end[0:4]

            for a in slip.line_ids:
                if a.category_id.code == 'NET':
                    totalD_net = a.total
                    net_conv = '{0:,.2f}'.format(totalD_net).replace(',', 'X').replace('.', ',').replace('X', '.')

                    docs.append({
                        'prueba':' ',
                        'iniciales': (slip.employee_id.firstname + ' ' + slip.employee_id.lastname),
                        'nro_cuenta': slip.employee_id.account_number_2,
                        'cedula_i': cedula_employee,
                        'cargo': slip.employee_id.job_id.name,
                        'total': net_conv,
                        'struct_id': slip.employee_id.contract_id.struct_id.name,
                        'banco': slip.employee_id.bank_account_id_emp_2.name,


                    })
                    if totalD_net != 0:
                        total_monto += totalD_net
                        final_total = '{0:,.2f}'.format(total_monto).replace(',', 'X').replace('.', ',').replace('X', '.')
                    else:
                        final_total = 0


        return {
                    'data': data['form'],
                    'model': self.env['report.int_hr_report_resumen_nomina.template_resumen_nomina'],
                    'lines': res,  # self.get_lines(data.get('form')),
                    # date.partner_id
                    'docs': docs,
                    'final_monto': final_total,
                    'date_start': fecha_start,
                    'date_end': fecha_end,
                    'date_actual': fecha_actual,


                }
