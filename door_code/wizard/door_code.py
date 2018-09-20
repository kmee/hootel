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
from datetime import datetime, date, time, timedelta
from odoo import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class HotReserv(models.Model):
    _inherit = 'hotel.reservation'

    door_code = fields.Char('Clean Type', compute='_compute_door_code')

    def _compute_door_code(self):
        # Compute door code
        return


class DoorCodeWizard(models.TransientModel):
    _name = 'door_code'

    @api.model
    def _get_default_date_start(self):
        return datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

    date_start = fields.Date("Inicio periodo",
                             default=_get_default_date_start)
    date_end = fields.Date("Fin del periodo",
                           default=_get_default_date_start)

    door_code = fields.Char('Codigo para la puerta')

    @api.multi
    def doorcode4(self, fecha):
        # Calculate de Door Code... need a date in String format "%Y-%m-%d"
        d = datetime.strptime(fecha, DEFAULT_SERVER_DATE_FORMAT)
        dia_semana = datetime.weekday(d)  # Dias a restar y ponerlo en lunes
        d = d - timedelta(days=dia_semana)
        dtxt = d.strftime('%s.%%06d') % d.microsecond
        return dtxt[4:8]

    @api.multi
    def check_code(self):
        # d = datetime.strptime(self.date_start,DEFAULT_SERVER_DATE_FORMAT)
        # d = datetime.now()
        # d.strftime('%s.%%06d') % d.microsecond
        codes = 'Codigo de entrada: ' + self.doorcode4(self.date_start)
        return self.write({
             'door_code': codes
             })

             # Debug Stop -------------------
             #import wdb; wdb.set_trace()
             # Debug Stop -------------------
