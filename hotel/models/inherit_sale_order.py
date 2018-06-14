# -*- coding: utf-8 -*-
# Copyright 2017  Alexandre Díaz
# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    partner_id = fields.Many2one(track_visibility='onchange')
