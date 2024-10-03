from odoo import api, fields, models
from odoo.exceptions import UserError

class Medicine(models.Model):
    _name = 'pharmacy.medicine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Medicine'

    name = fields.Char(string='Name', required=True, tracking=True)
    price = fields.Float(string='Price', required=True,
                         tracking=True)
    quantity = fields.Integer(string='Quantity in Stock', default=0, required=True, tracking=True)
    category_id = fields.Many2one('pharmacy.medicine.category', string='Category', required=True,
                                  tracking=True)
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier', tracking=True)
    image = fields.Image(string='Image')
    allergy_ids = fields.Many2many('pharmacy.client', string='Clients Allergic to This Medicine')

    @api.constrains('price', 'quantity')
    def _check_positive_values(self):
        for record in self:
            if record.price <= 0:
                raise UserError("Price must be a positive number.")
            if record.quantity < 0:
                raise UserError("Quantity cannot be negative.")
