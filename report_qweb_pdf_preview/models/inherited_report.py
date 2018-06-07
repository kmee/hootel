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
from openerp import models, fields, api


class Report(models.Model):
    _inherit = 'report'

    @api.noguess
    def get_action(self, docids, report_name, data=None):
        res = super(Report, self).get_action(docids, report_name, data=data)
        context = self.env.context
        if docids:
            if isinstance(docids, models.Model):
                active_ids = docids.ids
            elif isinstance(docids, int):
                active_ids = [docids]
            elif isinstance(docids, list):
                active_ids = docids
            context = dict(self.env.context, active_ids=active_ids)

        report = self.env['ir.actions.report.xml'].with_context(context).search([('report_name', '=', report_name)], limit=1)
        if not report:
            raise UserError(_("Bad Report Reference") + _("This report is not loaded into the database: %s.") % report_name)
        if report.report_type == 'qweb-pdf' and report.pdfjs_enabled:
            res.update({
                'report_type': 'qweb-pdfjs',
                'pdfjs': {
                    'print_dpi': report.pdfjs_print_dpi,
                    'auto_print': report.pdfjs_auto_print,
                }
            })
        return res
