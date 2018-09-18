# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Jose Luis Algara Toledo <osotranquilo@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
from datetime import datetime, date, time
from odoo import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class KellysWizard(models.TransientModel):
    _name = 'kellys'

    @api.model
    def _get_default_habitaciones(self):
        return self.calculalimpiar(datetime.now())

    date_start = fields.Date("Fecha del listado", default=datetime.now())
    habitaciones = fields.Many2many('kellysrooms', string="Limpieza:",
                                    default=_get_default_habitaciones)

    @api.multi
    def calculate_report(self):
        self.habitaciones = self.calculalimpiar(
            datetime.strptime(self.date_start, "%Y-%m-%d"))
        return

    @api.multi
    def calculalimpiar(self, fechalimpieza=datetime.now()):
        dates = datetime.strftime(fechalimpieza, "%Y-%m-%d")
        grids = self.env['hotel.room'].search([], order='hcal_sequence ASC')
        grids2 = self.env['kellysrooms']
        listid = []
        for x in grids:
            rooms = self.env['hotel.reservation'].search(
                ['&', '&', ('checkin', '<=', dates),
                 ('checkout', '>=', dates),
                 ('state', '<>', 'cancelled'),
                 ('product_id', '=', x.product_id.id)
                 ],)
            tipos = False
            if len(rooms) != 0:
                if len(rooms) == 2:
                    tipos = 1
                else:
                    if rooms[0].checkin[:10] == dates:
                        tipos = 2
                    elif rooms[0].checkout[:10] == dates:
                        tipos = 1
                    else:
                        tipos = 3
            if tipos is not False:
                listid.append(grids2.create(
                    {'habitacion': rooms[0].product_id.name,
                     'habitacionid': rooms[0].product_id.id,
                     'tipo': tipos,
                     'notas': '',
                     'checkin': rooms[0].checkin[:10],
                     'checkout': rooms[0].checkout[:10],
                     # 'kelly': 5,
                     'clean_date': fechalimpieza
                     }).id)
        return self.env['kellysrooms'].search([('id', 'in', listid)])

    @api.multi
    def check_report(self):
        # Debug Stop -------------------
        # import wdb; wdb.set_trace()
        # Debug Stop -------------------
        rooms = self.env['kellysrooms'].search([('id', 'in',
                                                 self.habitaciones.ids)])
        return self.env['report'].get_action(rooms, 'report.kellys')



class KellysRooms(models.TransientModel):
    _name = 'kellysrooms'

    habitacion = fields.Char('Habitacion')
    habitacionid = fields.Integer('Habitacion ID')
    tipo = fields.Selection([(1, 'Salida'), (2, 'Revisar'), (3, 'Cliente')],
                            string='Limpiar como')
    notas = fields.Char('Notas limpieza')
    checkin = fields.Char('Entrada')
    checkout = fields.Char('Salida')
    kelly = fields.Many2one('kellysnames', string='Asignado a:')
    clean_date = fields.Date('Clean Date')
