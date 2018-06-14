# -*- coding: utf-8 -*-
# Copyright 2017  Alexandre Díaz
# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
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
