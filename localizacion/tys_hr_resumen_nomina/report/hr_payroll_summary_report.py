from odoo import models, api, _, exceptions, fields
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class ReportAccountPayment(models.AbstractModel):
    _name = 'report.tys_hr_resumen_nomina.template_hr_payroll_summary_report'



    @api.model
    def get_report_values(self, docids, data=None):
        if not docids:
            raise UserError(_("You need select a data to print."))
        data = {'form': self.env['hr.payslip'].browse(docids)}
        res = dict()
        docs = []
        contract = self.env['hr.contract']
        payslip = self.env['hr.payslip']
        docs2 = []
        var2 = 0
        cont = 0
        config_obj = self.env['hr.config.parameter']
        code_liq = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.liquidacion', True)
        code_cest = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.cestaticket', True)
        totalD_net = totalD_ded = totalD_asig = 0
        varsal = cant_sueldo = 0
        payslip = self.env['hr.payslip'].search([('id', '=', docids)])
        code_prest = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.prestaciones', True)
        code_util = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.utilidades', True)
        code_vac = config_obj._hr_get_parameter('hr.payroll.codigos.nomina.vacaciones', True)
        if payslip.state == 'draft':
            raise exceptions.except_orm(_('Advertencia!'), (
                "No se puede imprimir un reporte que no se encuentre en estado Realizado"))

        if payslip.struct_id.code == code_cest:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'La nómina actual es de Cestaticket, no se puede generar dicho Recibo de pago.'))

        if payslip.structure.code == code_liq:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (u'La nómina actual es de Liquidación, no se puede generar dicho Recibo de pago.'))

        if payslip.struct_id.code == code_prest:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (
                                            u'La nómina actual es Prestaciones Sociales, no se puede generar dicho Resumen de Nómina.'))
        if payslip.struct_id.code == code_util:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (
                                            u'La nómina actual es de Utilidades, no se puede generar dicho Resumen de Nómina.'))
        if payslip.struct_id.code == code_vac:
            raise exceptions.except_orm(_('Advertencia!'),
                                        (
                                            u'La nómina actual es de Vacaciones, no se puede generar dicho Resumen de Nómina.'))



        for slip in payslip:
            cont2 = 0
            fecha_actual0 = str(date.today())
            fecha_actual = fecha_actual0[8:10] + "/" + fecha_actual0[5:7] + "/" + fecha_actual0[0:4]
            date_start = str(slip.date_from)
            fecha_start = date_start[8:10] + "/" + date_start[5:7] + "/" + date_start[0:4]
            date_end = str(slip.date_to)
            fecha_end = date_end[8:10] + "/" + date_end[5:7] + "/" + date_end[0:4]


            if not slip.line_ids:
                raise exceptions.except_orm(_('Advertencia!'),("Por favor verifique si tiene cargado los conceptos de la Estructura Salarial "))
            unidad = 0
            for a in slip.line_ids:

                cant_sueldo = ' '

                if a.category_id.code == 'BASIC':
                    totalD_asig = a.total
                if a.category_id.code == 'GROSS':
                    totalD_ded = a.total
                if a.category_id.code == 'NET':
                    totalD_net = a.total

                if a.category_id.code == 'ALW':
                    cont += 1
                    cont2 += 1

                    if a.amount_python_compute:
                        if (a.amount_python_compute.find("worked_days.WORK100.number_of_days") != -1):
                            dias = cant_sueldo= int(slip.worked_days_line_ids[0].number_of_days)
                            varsal = a.total
                            if dias > 30:
                                dias = 30
                            varsal = a.total
                            unidad = a.total/dias

                        if varsal != 0 and dias != 0:
                            if a.amount_python_compute.find("night_bonus") != -1:
                               cant_sueldo = float((a.total/(((varsal/dias)/8)*1.8)))

                               min = str(cant_sueldo).split('.')[1]
                               hors = str(cant_sueldo).split('.')[0]
                               cambio2 = '0.' + min
                               cambio3 = float(cambio2)*60
                               redondear = round(cambio3)
                               total_min = '0.' + str(redondear)
                               horas_min = int(hors)+ float(total_min)
                               cant_sueldo = '{0:,.2f}'.format(float(horas_min)).replace('.', ',')

                            if a.amount_python_compute.find("diurnal_extra_hours") != -1:
                               cant_sueldo = float((a.total/(((varsal/dias)/8)*1.5)))

                               min = str(cant_sueldo).split('.')[1]
                               hors = str(cant_sueldo).split('.')[0]
                               cambio2 = '0.' + min
                               cambio3 = float(cambio2)*60
                               redondear = round(cambio3)
                               total_min = '0.' + str(redondear)
                               horas_min = int(hors)+ float(total_min)
                               cant_sueldo = '{0:,.2f}'.format(float(horas_min)).replace('.', ',')


                            if  a.amount_python_compute.find("holidays_value") != -1:
                                cant_sueldo = int(round((a.total)/((varsal/dias)*1.5)))

                            if  a.amount_python_compute.find("contract.sundays_value+contract.saturdays_value") != -1:
                                cant_sueldo = int(round((a.total)/((varsal/dias)*1.5)))

                            if a.amount_python_compute.find("days_of_salary_pending_value") != -1:
                                cant_sueldo = int(round((a.total) / (varsal / dias)))

                    total_asg_conv = '{0:,.2f}'.format(a.total).replace(',', 'X').replace('.', ',').replace('X', '.')
                    if unidad != 0:
                        unidad_conv = '{0:,.2f}'.format(unidad).replace(',', 'X').replace('.', ',').replace('X', '.')
                    else:
                        unidad_conv = ' '
                    docs2.append({
                        'descripcion': a.name,
                        'total_alw': total_asg_conv,
                        'total_ded' : ' ',
                        'code': a.code,
                        'cant_sueldo': cant_sueldo,
                    })

                elif a.category_id.code == 'DED':
                    cont += 1
                    cont2 += 1

                    if a.amount_python_compute:
                        if varsal != 0 and dias != 0:
                            if a.amount_python_compute.find("ausencias_ded_value") != -1:
                                cant_sueldo = int(round((a.total) / (varsal/dias)))

                            if a.amount_python_compute.find("unpaid_permit_days_value") != -1:
                                cant_sueldo = int(round((a.total) / (varsal/dias)))

                            if a.amount_python_compute.find("hours_not_worked") != -1:
                               cant_sueldo = float((a.total/((varsal/dias)/8)))
                               min = str(cant_sueldo).split('.')[1]
                               hors = str(cant_sueldo).split('.')[0]
                               cambio2 = '0.' + min
                               cambio3 = float(cambio2) * 60
                               redondear = round(cambio3)
                               total_min = '0.' + str(redondear)
                               horas_min = int(hors) + float(total_min)
                               cant_sueldo = '{0:,.2f}'.format(float(horas_min)).replace('.', ',')


                    total_ded_conv = '{0:,.2f}'.format(a.total).replace(',', 'X').replace('.', ',').replace('X', '.')
                    docs2.append({
                        'descripcion': a.name,
                        'total_alw': ' ',
                        'total_ded': total_ded_conv,
                        'code': a.code,
                        'cant_sueldo': cant_sueldo,

                    })
            if not slip.struct_id:
                totalD_net = 0

            asig_conv =    '{0:,.2f}'.format(totalD_asig).replace(',', 'X').replace('.', ',').replace('X', '.')
            ded_conv =   '{0:,.2f}'.format(totalD_ded).replace(',', 'X').replace('.', ',').replace('X', '.')
            net_conv =   '{0:,.2f}'.format(totalD_net).replace(',', 'X').replace('.', ',').replace('X', '.')
            mensual_suel = unidad * 30
            sueldo_lis = '{0:,.2f}'.format(mensual_suel).replace(',', 'X').replace('.', ',').replace('X', '.')

            docs.append({
                'ci': slip.employee_id.identification_id_2,
                'employee': slip.employee_id.firstname + ' '+ slip.employee_id.lastname,
                'f_ing': slip.employee_id.fecha_inicio,
                'wage': sueldo_lis,
                'cargo': slip.contract_id.job_id.name,
                'correo': slip.employee_id.personal_email,
                'concepto': slip.contract_id.struct_id.name,
                'sal_diario': unidad_conv,
                'date_start': fecha_start,
                'date_end': fecha_end,
                'date_actual': fecha_actual,
                'var1': cont -1,
                'var2': var2,
                'asig_total' : asig_conv,
                'ded_total' :  ded_conv,
                'net_total' : net_conv,
                'department': slip.employee_id.department_id.name,
                'total_depart' : totalD_net,
            })
            var2 = var2 + cont2



        return {
            'data': data['form'],
            'model': self.env['report.tys_hr_resumen_nomina.template_hr_payroll_summary_report'],
            'lines': res,
            'docs': docs,
            'docs2': docs2,
        }

