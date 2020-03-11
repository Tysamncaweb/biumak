# coding: utf-8
##############################################################################
#
# Copyright (c) 2016 Tecnología y Servicios AMN C.A. (http://tysamnca.com/) All Rights Reserved.
# <contacto@tysamnca.com>
# <Teléfono: +58(212) 237.77.53>
# Caracas, Venezuela.
#
# Colaborador: <<nombre colaborador>> <e-mail del colaborador>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'Nóminas de Prestaciones Sociales',
    'version': '1.0',
    'category': 'Recursos Humanos',
    'summary': 'Permite procesar nóminas para prestaciones sociales y registra un histórico de todas los procesos asociado con el cálculo de prestaciones socuales',
    'description': """
NÓMINAS DE PRESTACIONES SOCIALES

Permite:
     * Generar nóminas de prestaciones sociales\n
     * LLevar un registro hisrórico de:\n
         ** Prestaciones generadas\n
         ** Intereses sobre prestaciones\n
         ** Carga de valores iniciales para todos los empleados\n
    """,

    'author': 'TYSAMNCA',
    'website': 'https://tysamnca.com',
    'depends': ['hr_payroll',
                'hr',
                'hr_config_parameter',
                'hr_special_struct',
                'tys_hr_special_payroll',
                'hr_contract'],
    'data': ['views/hr_historico_fideicomiso_view.xml',
             'views/hr_payroll_fideicomiso_view.xml',
             'views/hr_payroll_fideicomiso_intereses_view.xml',
             # 'data/hr_payroll_fideicomiso_data.xml',
             'views/hr_contract_view.xml',
             'views/hr_wizard_primeracarga.xml'
        ],
    #'demo': [],
    #'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: