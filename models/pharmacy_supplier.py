from odoo import models, fields, api
from odoo.exceptions import UserError

class Supplier(models.Model):
    _name = 'pharmacy.supplier'
    _description = 'Supplier'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email', required=True)
    address = fields.Text(string='Address')
    company_name = fields.Char(string='Company Name', required=True )
    image = fields.Image(string='Image')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise UserError("Invalid email address format.")

    @api.constrains('phone')
    def _check_phone(self):
        for number in self:
            if number.phone:
                if not number.phone.isdigit():
                    raise UserError("The phone number must contain only digits.")
                if len(number.phone) > 15:
                    raise UserError("The phone number must contain up to 15 digits.")
