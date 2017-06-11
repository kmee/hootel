# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
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
from openerp import models, fields, api
from openerp.exceptions import except_orm, UserError, ValidationError


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    @api.depends('wrid', 'wchannel_id')
    def _is_from_channel(self):
        for record in self:
            record.wis_from_channel = record.wrid != 'none' \
                                        and record.wchannel_id != 'none'

    wrid = fields.Char("WuBook Reservation ID", default="none", readonly=True)
    wchannel_id = fields.Char("WuBook Channel ID", default='none',
                              readonly=True)
    wchannel_reservation_code = fields.Char("WuBook Channel Reservation Code",
                                            default='none', readonly=True)
    wis_from_channel = fields.Boolean('WuBooK Is From Channel',
                                      compute=_is_from_channel, store=False,
                                      readonly=True)

    wstatus = fields.Selection([
        ('0', 'No WuBook'),
        ('1', 'Confirmed'),
        ('2', 'Waiting'),
        ('3', 'Refused'),
        ('4', 'Accepted'),
        ('5', 'Cancelled'),
        ('6', 'Cancelled with penalty')], string='WuBook Status', default='0',
                                        readonly=True)
    wstatus_reason = fields.Char("WuBook Status Reason", readonly=True)

    @api.model
    def create(self, vals):
        if self._context.get('wubook_action', True):
            self.env['wubook'].update_availability(vals)
        res = super(HotelReservation, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if self._context.get('wubook_action', True):
            self.env['wubook'].update_availability({
                'product_id': self.product_id.id,
                'checkin': self.checkin,
                'checkout': self.checkout,
            })
        ret_vals = super(HotelReservation, self).write(vals)
        if self._context.get('wubook_action', True):
            self.env['wubook'].update_availability(vals)
        return ret_vals

    @api.multi
    def unlink(self):
        for record in self:
            if self.wchannel_id == '0':
                self.env['wubook'].cancel_reservation(record.id, 'Cancelled by admin')
        self.env['wubook'].update_availability({
            'product_id': self.product_id.id,
            'checkin': self.checkin,
            'checkout': self.checkout,
        })
        return super(HotelReservation, self).unlink()
