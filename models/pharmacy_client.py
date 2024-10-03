from odoo import models, fields, api
from odoo.exceptions import UserError


class Client(models.Model):
    _name = 'pharmacy.client'
    _description = 'Client'
    _rec_name = 'full_name'

    full_name = fields.Char(string='Full Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    allergy_ids = fields.Many2many('pharmacy.medicine', string='Allergies')

    @api.constrains('phone')
    def _check_phone(self):
        for number in self:
            if number.phone:
                if not number.phone.isdigit():
                    raise UserError("The phone number must contain only digits.")
                if len(number.phone) > 15:
                    raise UserError("The phone number must contain up to 15 digits.")
