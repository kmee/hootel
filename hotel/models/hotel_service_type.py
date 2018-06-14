# -*- coding: utf-8 -*-
# Copyright 2017  Alexandre Díaz
# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class HotelServiceType(models.Model):

    _name = "hotel.service.type"
    _description = "Service Type"

    ser_id = fields.Many2one('product.category', 'category', required=True,
                             delegate=True, index=True, ondelete='cascade')

    @api.multi
    def unlink(self):
        self.ser_id.unlink()
        return super(HotelServiceType, self).unlink()
