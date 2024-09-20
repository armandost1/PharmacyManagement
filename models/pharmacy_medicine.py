from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Medicine(models.Model):
    _name = 'pharmacy.medicine'
    _description = 'Medicine'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True)
    quantity = fields.Integer(string='Quantity in Stock', required=True)
    expiry_date = fields.Date(string='Expiry Date')
    category_id = fields.Many2one('pharmacy.medicine.category', string='Category')
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier')
    reorder_level = fields.Integer(string='Reorder Level', default=50)

    @api.constrains('price', 'quantity', 'reorder_level')
    def _check_positive_values(self):
        """
        Ensure that price, quantity, and reorder level are positive.
        """
        for record in self:
            if record.price <= 0:
                raise ValidationError("Price must be a positive number.")
            if record.quantity < 0:
                raise ValidationError("Quantity cannot be negative.")
            if record.reorder_level <= 0:
                raise ValidationError("Reorder level must be a positive number.")

    def check_reorder(self):
        """
        Check if the quantity of medicine is below the reorder level and create a restock order if necessary.
        """
        for medicine in self:
            if medicine.quantity < medicine.reorder_level:
                if not medicine.supplier_id:
                    raise ValidationError(
                        f"Cannot create a restock order for '{medicine.name}' because no supplier is assigned."
                    )

                existing_order = self.env['pharmacy.restock.order'].search([
                    ('medicine_id', '=', medicine.id),
                    ('state', 'not in', ['received', 'cancelled'])
                ], limit=1)

                if not existing_order:
                    self.env['pharmacy.restock.order'].create({
                        'medicine_id': medicine.id,
                        'quantity': medicine.reorder_level * 2,  # Example quantity for reorder
                        'supplier_id': medicine.supplier_id.id,
                    })