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
from openerp.exceptions import ValidationError
from openerp import models, fields, api, _

class SendConfirmMailWizard(models.TransientModel):
    _name = 'hotel.wizard.send.confirm.mail'

    @api.multi
    def send_confirm_mail(self):
        folios = self.env['hotel.folio'].browse(
            self._context.get('active_ids', []))
        if len(folios) > 1:
            raise ValidationError("Can't send more than one mail at the same time")
        return folios[0].send_reservation_mail()
