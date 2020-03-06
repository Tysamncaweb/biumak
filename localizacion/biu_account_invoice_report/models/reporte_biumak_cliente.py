from odoo import models, api, _, exceptions, fields
from odoo.exceptions import UserError, Warning
from datetime import datetime, date, timedelta

class tiposdepago(models.Model):
    _name = "tipo.pago"
    name = fields.Char(string="Tipo de pago")

class tiposdebanco(models.Model):
    _name = "tipo.debanco"
    name = fields.Char(string="Banco")

class reporte_invoice(models.Model):
    _inherit = 'account.invoice'

    pago_transfe = fields.Many2one('tipo.pago')
    tipo_banco = fields.Many2one('tipo.debanco')

    @api.multi
    def obtener_reporte(self,docids):
        update = {'id': self.id }
        docids.update(update)
        return self.env.ref('biu_account_invoice_report.action_reporte_biumak_cliente').report_action([], data=docids)
class ReportAccountPayment_biucliente(models.AbstractModel):
    _name = 'report.biu_account_invoice_report.template_cliente'

    @api.model
    def get_report_values(self, docids, data):
        if docids:
            data = {'form': self.env['account.invoice'].browse(docids)}
            var = data['form']
        else:
            var = self.env['account.invoice'].search([('id', '=', data['id'])])

        res = dict()
        docs = []
        info = []

        if var.date_document:
            fecha = var.date_document
        else:
            fecha = var.date_invoice
        fecha = datetime.strptime(fecha, '%Y-%m-%d')
        fecha = fecha.strftime('%d/%m/%Y')
        n_factura = var.number
        n_cliente = var.partner_id.num_cliente
        razon = var.partner_id.name
        rif = var.partner_id.vat
        direccion = var.partner_id.street
        telefono = var.partner_id.phone
        forma_pago = var.pago_transfe.name
        banco = var.tipo_banco.name
        cont = 0
        total = 0
        if var.refund_invoice_id:
            origen = 'REC'
        else:
            origen = 'FAC'
        nota_cred = var.name
        origin_number = var.origin
        info.append({
            'fecha':fecha,
            'n_factura': n_factura,
            'n_cliente': n_cliente,
            'razon': razon,
            'rif': rif,
            'direccion': direccion,
            'telefono': telefono,
            'forma_pago': forma_pago,
            'banco': banco
        })
        for lin in var.invoice_line_ids:
            a =  lin
            cont += 1
            #bus_lote = self.env['sale.order.line'].search([('name', '=', lin.name),('state','!=', 'draft')], order='create_date desc')

            #if bus_lote:
            #    numero_lote = bus_lote[0].num_lot
            #else:
            #    numero_lote = ''


            docs.append({
                'n': cont,
                'cod': lin.product_id.default_code,
                'cant': lin.quantity,
                'um': lin.uom_id.name,
                'descripcion': lin.product_id.product_tmpl_id.name,
                'lote': lin.nro_lote,
                'precio_unitario': self.formato_cifras(lin.price_unit),
                'precio_total': self.formato_cifras(lin.tasa_me),
            })
            total += lin.tasa_me
        #if docs:
        #    docs.append({
        #        'n': ' ',
        #        'cod': ' ',
        #        'cant': ' ',
        #        'um': ' ',
        #        'descripcion': ' ',
        #        'lote': ' ',
        #        'precio_unitario': ' ',
        #        'precio_total': ' ',
        #    })

        return {
            'data': var,
            'model': self.env['report.biu_account_invoice_report.template_cliente'],
            'lines': res,  # self.get_lines(data.get('form')),
            # date.partner_id
            'docs': docs,
            'infos': info,
            'total': self.formato_cifras(total),
            'cifra_total': self.numero_to_letras(total),
            'compañia': var.partner_id.company_id.name,
            'origin_check': origen,
            'nota_cred': nota_cred,
            'origin_number': origin_number,

        }

    def formato_cifras(self, valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return monto

    def numero_to_letras(self,numero):
        indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero) * 100))
        # print 'decimal : ',decimal
        contador = 0
        numero_letras = ""
        while entero > 0:
            a = entero % 1000
            if contador == 0:
                en_letras = self.convierte_cifra(a, 1).strip()
            else:
                en_letras = self.convierte_cifra(a, 0).strip()
            if a == 0:
                numero_letras = en_letras + " " + numero_letras
            elif a == 1:
                if contador in (1, 3):
                    numero_letras = indicador[contador][0] + " " + numero_letras
                else:
                    numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras
        return numero_letras

    def convierte_cifra(self,numero, sw):
        lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                         "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        lista_decena = ["", (
        "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        centena = int(numero / 100)
        decena = int((numero - (centena * 100)) / 10)
        unidad = int(numero - (centena * 100 + decena * 10))
        # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

        texto_centena = ""
        texto_decena = ""
        texto_unidad = ""

        # Validad las centenas
        texto_centena = lista_centana[centena]
        if centena == 1:
            if (decena + unidad) != 0:
                texto_centena = texto_centena[1]
            else:
                texto_centena = texto_centena[0]

        # Valida las decenas
        texto_decena = lista_decena[decena]
        if decena == 1:
            texto_decena = texto_decena[unidad]
        elif decena > 1:
            if unidad != 0:
                texto_decena = texto_decena[1]
            else:
                texto_decena = texto_decena[0]
        # Validar las unidades
        # print "texto_unidad: ",texto_unidad
        if decena != 1:
            texto_unidad = lista_unidad[unidad]
            if unidad == 1:
                texto_unidad = texto_unidad[sw]

        return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)