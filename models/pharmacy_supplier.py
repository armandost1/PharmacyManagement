from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Supplier(models.Model):
    _name = 'pharmacy.supplier'
    _description = 'Supplier'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    company_name = fields.Char(string='Company Name')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Invalid email address format.")

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                raise ValidationError("Phone number should contain only digits.")
