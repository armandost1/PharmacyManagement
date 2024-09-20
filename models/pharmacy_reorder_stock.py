from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RestockOrder(models.Model):
    _name = 'pharmacy.restock.order'
    _description = 'Restock Order'

    medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True, help="Select the medicine for restocking.")
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier', required=True, help="Supplier of the selected medicine.")
    quantity = fields.Integer(string='Quantity to Order', required=True, help="Quantity of medicine to order.")
    order_date = fields.Date(string='Order Date', default=fields.Date.today, help="Date when the order is placed.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', help="Current status of the restock order.")

    @api.onchange('medicine_id')
    def _onchange_medicine(self):
        """Automatically set the supplier based on the selected medicine."""
        if self.medicine_id:
            self.supplier_id = self.medicine_id.supplier_id

    @api.constrains('quantity')
    def _check_quantity(self):
        """Ensure the quantity is a positive number."""
        if any(record.quantity <= 0 for record in self):
            raise ValidationError("Quantity must be positive.")

    @api.constrains('order_date')
    def _check_order_date(self):
        """Ensure the order date is not in the future."""
        if any(record.order_date > fields.Date.today() for record in self):
            raise ValidationError("Order date cannot be in the future.")

    def action_send(self):
        """Change the state of the order to 'sent'."""
        self._check_order_state('draft', 'sent')

    def action_receive(self):
        """Update the state to 'received' and adjust the medicine quantity."""
        self._check_order_state('sent', 'received')
        for order in self:
            medicine = order.medicine_id
            medicine.quantity += order.quantity
            # Optionally, create a stock movement record or log the restock

    def _check_order_state(self, current_state, next_state):
        """Check the state and update it if valid."""
        for order in self:
            if order.state == current_state:
                order.state = next_state
            else:
                raise ValidationError(f"Order can only be {next_state} from the {current_state} state.")