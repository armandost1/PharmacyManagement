from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Medicine(models.Model):
    _name = 'pharmacy.medicine'
    _description = 'Medicine'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price', required=True)
    quantity = fields.Integer(string='Quantity in Stock', default=50, required=True)
    expiry_date = fields.Date(string='Expiry Date')
    category_id = fields.Many2one('pharmacy.medicine.category', string='Category', required=True)
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier')
    reorder_level = fields.Integer(string='Reorder Level', default=30)

    @api.constrains('price', 'quantity', 'reorder_level')
    def _check_positive_values(self):
        for record in self:
            if record.price <= 0:
                raise UserError("Price must be a positive number.")
            if record.quantity < 0:
                raise UserError("Quantity cannot be negative.")
            if record.reorder_level <= 0:
                raise UserError("Reorder level must be a positive number.")
    def check_reorder(self):
        for medicine in self:
            _logger.info(
                f"Checking reorder for {medicine.name}: Current Quantity = {medicine.quantity}, Reorder Level = {medicine.reorder_level}")

            if medicine.quantity < medicine.reorder_level:
                if not medicine.supplier_id:
                    raise UserError(f"Cannot restock '{medicine.name}' because no supplier is assigned.")
                restock_amount = 40
                medicine.quantity += restock_amount
                _logger.info(
                    f"Restocked '{medicine.name}' by {restock_amount} units. New Quantity = {medicine.quantity}")

        return True