from odoo import models, fields


class Employee(models.Model):
    _name = 'pharmacy.employee'
    _description = 'Employee'

    name = fields.Char(string='Name', required=True)
    position = fields.Char(string='Position')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')