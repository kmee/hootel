# -*- coding: utf8 -*-
# --------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# ---------------------------------------------------------------------------
from openerp import models, fields, api, _


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    product_id = fields.Many2one(track_visibility='onchange')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        reservs = self.env['hotel.reservation'].search([
            ('order_line_id', 'in', self.ids)
        ])
        services = self.env['hotel.service.line'].search([
            ('service_line_id', 'in', self.ids)
        ])
        if reservs or services:
            for line in reservs:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.order_line_id.tax_id.compute_all(price, line.order_line_id.order_id.currency_id, line.order_line_id.product_uom_qty, product=line.order_line_id.product_id, partner=line.order_line_id.order_id.partner_shipping_id)
                line.order_line_id.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            for line in services:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.service_line_id.tax_id.compute_all(price, line.service_line_id.order_id.currency_id, line.service_line_id.product_uom_qty, product=line.service_line_id.product_id, partner=line.service_line_id.order_id.partner_shipping_id)
                line.service_line_id.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
        else:
            super(SaleOrderLine, self)._compute_amount()
