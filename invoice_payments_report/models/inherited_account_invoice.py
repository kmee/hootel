# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 Alexandre Díaz <dev@redneboa.es>
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
import json
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('payments_widget', 'amount_total')
    def _compute_balance_due(self):
        for record in self:
            json_payments = record.payments_widget and json.loads(record.payments_widget) or False
            if json_payments:
                payments_amount_total = 0.0
                for payment in json_payments['content']:
                    payments_amount_total += payment['amount']
                record.balance_due = record.amount_total - payments_amount_total
            else:
                record.balance_due = record.amount_total

    balance_due = fields.Float('Balance Due', compute="_compute_balance_due")
