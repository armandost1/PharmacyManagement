from odoo import models, fields, api
from odoo.exceptions import UserError


class Employee(models.Model):
    _name = 'pharmacy.employee'
    _description = 'Employee'

    name = fields.Char(string='Name', required=True)
    position = fields.Char(string='Position', default='Seller')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    image = fields.Image(string='Image')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise UserError("The email must contain '@'.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone:
                if not record.phone.isdigit():
                    raise UserError("The phone number must contain only digits.")
                if len(record.phone) > 15:
                    raise UserError("The phone number must contain up to 15 digits.")