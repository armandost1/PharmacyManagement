from odoo import models, fields, api
from odoo.exceptions import UserError


class SellingInvoice(models.Model):
    _name = 'pharmacy.selling.invoice'
    _description = 'Selling Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    employee_id = fields.Many2one('pharmacy.employee', string='Employee', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    selling_invoice_line_ids = fields.One2many('pharmacy.selling.invoice.line', 'selling_invoice_id',
                                               string='Selling Invoice Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid')
    ], string='Status', default='draft', required=True)

    @api.depends('selling_invoice_line_ids.subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(line.subtotal for line in record.selling_invoice_line_ids)

    @api.constrains('selling_invoice_line_ids')
    def _check_invoice_lines(self):
        for record in self:
            if not record.selling_invoice_line_ids:
                raise UserError("A selling invoice must have at least one invoice line.")

    def action_done(self):
        """
        Move the invoice to the done state and reduce the stock.
        """
        if self.state != 'draft':
            raise UserError("Only draft invoices can be marked as done.")

        # Adjust medicine stock only when invoice is marked as done
        for line in self.selling_invoice_line_ids:
            medicine = line.medicine_id
            if medicine.quantity < line.quantity:
                raise UserError(f"Not enough stock for {medicine.name}. Available: {medicine.quantity}.")
            medicine.quantity -= line.quantity
            medicine.write({'quantity': medicine.quantity})

        self.write({'state': 'done'})

    def action_paid(self):
        """
        Move the invoice to the paid state.
        """
        if self.state != 'done':
            raise UserError("Only done invoices can be marked as paid.")
        self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('pharmacy.selling.invoice')
        values['code'] = code
        return super(SellingInvoice, self).create(values)


class SellingInvoiceLine(models.Model):
    _name = 'pharmacy.selling.invoice.line'
    _description = 'Selling Invoice Line'

    selling_invoice_id = fields.Many2one('pharmacy.selling.invoice', string='Selling Invoice', ondelete='cascade')
    medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
    quantity = fields.Integer(string='Quantity', required=True)
    price_unit = fields.Float(string='Unit Price', related='medicine_id.price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.constrains('quantity')
    def _check_positive_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise UserError("Quantity must be positive.")

    @api.model
    def create(self, values):
        medicine = self.env['pharmacy.medicine'].browse(values['medicine_id'])
        if medicine.quantity < values['quantity']:
            raise UserError(f"Not enough stock for {medicine.name}. Available quantity is {medicine.quantity}.")
        return super(SellingInvoiceLine, self).create(values)