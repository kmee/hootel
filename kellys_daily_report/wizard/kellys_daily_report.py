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
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

# Global variable to compute clean types
date_start_g = datetime.now()


class HotReserv(models.Model):
    _inherit = 'hotel.reservation'

    clean_type = fields.Char('Clean Type', compute='_compute_clean_type')

    def _compute_clean_type(self):
        # Compute if is a room to by cleaned
        global date_start_g
        for res in self:
            if datetime.strptime(res.checkout[0:10],
                                 "%Y-%m-%d") == datetime.strptime(date_start_g,
                                                                  "%Y-%m-%d"):
                res.clean_type = 'exit'
            else:
                res.clean_type = 'client'


class KellysWizard(models.TransientModel):
    _name = 'kellys'

    @api.model
    def _get_default_date_start(self):
        return datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

    date_start = fields.Date("Kellys Date Report",
                             default=_get_default_date_start)

    @api.multi
    def check_report(self):
        global date_start_g
        date_start_g = self.date_start
        # data = {}
        # data['form'] = self.read(['date_start'])[0]
        rooms = self.env['hotel.reservation'].search(
            ['&', '&', ('checkin', '<=', self.date_start),
             ('checkout', '>=', self.date_start),
             ('state', '<>', 'cancelled'),
             ],)
        return self.env['report'].get_action(rooms, 'report.kellys')
