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
from cStringIO import StringIO
import datetime
from datetime import datetime, date, time
import xlsxwriter
import base64
from odoo import api, fields, models, _
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class CallCenterReportWizard(models.TransientModel):
    _name = 'call.center.report.wizard'

    @api.model
    def _get_default_date_start(self):
        return datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.model
    def _get_default_date_end(self):
        return datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)

    date_start = fields.Date("Start Date", default=_get_default_date_start)
    date_end = fields.Date("End Date", default=_get_default_date_end)
    xls_filename = fields.Char()
    xls_binary = fields.Binary()

    @api.model
    def _export(self):
        file_data = StringIO()
        workbook = xlsxwriter.Workbook(file_data, {
            'strings_to_numbers': True,
            'default_date_format': 'dd/mm/yyyy'
        })

        company_id = self.env.user.company_id
        workbook.set_properties({
            'title': 'Exported data from ' + company_id.name,
            'subject': 'Payments Data from Odoo of ' + company_id.name,
            'author': 'Odoo',
            'manager': u'Call Center',
            'company': company_id.name,
            'category': 'Hoja de Calculo',
            'keywords': 'payments, odoo, data, ' + company_id.name,
            'comments': 'Created with Python in Odoo and XlsxWriter'})
        workbook.use_zip64()

        xls_cell_format_date = workbook.add_format({
            'num_format': 'dd/mm/yyyy'
        })
        xls_cell_format_money = workbook.add_format({
            'num_format': '#,##0.00'
        })
        xls_cell_format_header = workbook.add_format({
            'bg_color': '#CCCCCC'
        })

        worksheet = workbook.add_worksheet(_('Call Center Report'))

        worksheet.write('A1', _('Ficha'), xls_cell_format_header)
        worksheet.write('B1', _('Fecha de Pedido'), xls_cell_format_header)
        worksheet.write('C1', _('Checkin'), xls_cell_format_header)
        worksheet.write('D1', _('Checkout'), xls_cell_format_header)
        worksheet.write('E1', _('Producto'), xls_cell_format_header)
        worksheet.write('F1', _('Creado por'), xls_cell_format_header)
        worksheet.write('G1', _('Total'), xls_cell_format_header)

        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 13)

        reservations_obj = self.env['hotel.reservation']
        reservations = reservations_obj.search([
            ('checkout', '>=', self.date_start),
            ('checkout', '<=', self.date_end),
            ('state','=','done'),
            ('channel_type','=','call'),
            ('folio_id.invoices_amount','<',1),
        ])
        offset = 1
        total_reservation_amount = 0.0
        for k_res, v_res in enumerate(reservations):
            worksheet.write(k_res+offset, 0, v_res.folio_id.name)
            worksheet.write(k_res+offset, 1, v_res.folio_id.date_order,
                            xls_cell_format_date)
            worksheet.write(k_res+offset, 2, v_res.checkin,
                            xls_cell_format_date)
            worksheet.write(k_res+offset, 3, v_res.checkout,
                            xls_cell_format_date)
            worksheet.write(k_res+offset, 4, v_res.product_id.name)
            worksheet.write(k_res+offset, 5, v_res.create_uid.name)
            worksheet.write(k_res+offset, 6, v_res.price_total,
                            xls_cell_format_money)
            total_reservation_amount += v_res.price_total

        folio_ids = reservations.mapped('folio_id.id')
        folios = self.env['hotel.folio'].browse(folio_ids)
        services = self.env['hotel.service.line'].browse()
        for folio in folios:
            services += folio.service_lines.filtered(lambda r:
                r.channel_type == 'call' and r.folio_id.invoices_amount < 1)
        offset += len(reservations)
        total_service_amount = k_line = 0.0
        for k_service, v_service in enumerate(services):
            worksheet.write(k_service+offset, 0, v_service.folio_id.name)
            worksheet.write(k_service+offset, 1, v_service.folio_id.date_order,
                            xls_cell_format_date)
            worksheet.write(k_service+offset, 2, '')
            worksheet.write(k_service+offset, 3, '')
            worksheet.write(k_service+offset, 4, v_service.product_id.name)
            worksheet.write(k_service+offset, 5, v_service .create_uid.name)
            worksheet.write(k_service+offset, 6, v_service.price_total,
                            xls_cell_format_money)
            total_service_amount += v_service.price_total
        offset += len(services)
        if total_reservation_amount == 0 and total_service_amount == 0:
            raise UserError(_('No Hay reservas de Call Center'))
        line = offset
        if k_line:
            line = k_line + offset
        if total_reservation_amount > 0:
            line += 1
            worksheet.write(line, 4, _('TOTAL RESERVAS'))
            worksheet.write(line, 5, total_reservation_amount,
                            xls_cell_format_money)
        if total_service_amount > 0:
            line += 1
            worksheet.write(line, 4, _('TOTAL SERVICIOS'))
            worksheet.write(line, 5, total_service_amount,
                            xls_cell_format_money)
        line += 1
        worksheet.write(line, 4, _('TOTAL'))
        worksheet.write(
            line,
            5,
            total_reservation_amount + total_service_amount,
            xls_cell_format_money)

        workbook.close()
        file_data.seek(0)
        tnow = fields.Datetime.now().replace(' ', '_')
        return {
            'xls_filename': 'call_%s.xlsx' %self.env.user.company_id.property_name,
            'xls_binary': base64.encodestring(file_data.read()),
        }

    @api.multi
    def export(self):
        self.write(self._export())
        return {
            "type": "ir.actions.do_nothing",
        }
