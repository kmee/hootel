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
from cStringIO import StringIO
import datetime
from datetime import datetime, date, time
import xlsxwriter
import base64
from odoo import api, fields, models, _
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class KellysWizard(models.TransientModel):
    _name = 'kellys'

    @api.model
    def _get_default_date_start(self):
        return datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

    date_start = fields.Date("Kellys Date Report",
                             default=_get_default_date_start)

    @api.multi
    def check_report(self):
        rooms = self.env['hotel.reservation'].search(
            ['&', '&', ('checkin', '<=', self.date_start),
             ('checkout', '>=', self.date_start),
             ('state', '<>', 'cancelled'),
             ],)
        return self.env['report'].get_action(rooms, 'report.kellys')
