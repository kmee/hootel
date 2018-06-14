# -*- coding: utf-8 -*-
# Copyright 2017  Alexandre Díaz
# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class HotelRoomAmenitiesType(models.Model):

    _name = 'hotel.room.amenities.type'
    _description = 'amenities Type'

    cat_id = fields.Many2one('product.category', 'category', required=True,
                             delegate=True, ondelete='cascade')

    @api.multi
    def unlink(self):
        self.cat_id.unlink()
        return super(HotelRoomAmenitiesType, self).unlink()
