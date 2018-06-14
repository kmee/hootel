# -*- coding: utf-8 -*-
# Copyright 2017  Alexandre Díaz
# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class HotelRoomType(models.Model):

    _name = "hotel.room.type"
    _description = "Room Type"

    cat_id = fields.Many2one('product.category', 'category', required=True,
                             delegate=True, index=True, ondelete='cascade')
    code_type = fields.Char('Code', required=True)

    _sql_constraints = [('code_type_unique', 'unique(code_type)',
                         'code must be unique!')]

    @api.multi
    def unlink(self):
        self.cat_id.unlink()
        return super(HotelRoomType, self).unlink()
