from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleInvoice(models.Model):
    _name = 'pharmacy.sale.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    employee_id = fields.Many2one('pharmacy.employee', string='Employee', required=True)
    client_id = fields.Many2one('pharmacy.client', string='Client', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    sale_invoice_line_ids = fields.One2many('pharmacy.sale.invoice.line', 'sale_invoice_id',
                                             string='Sale Invoice Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid')
    ], string='Status', default='draft', required=True)

    @api.depends('sale_invoice_line_ids.subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(line.subtotal for line in record.sale_invoice_line_ids)

    @api.constrains('sale_invoice_line_ids')
    def _check_invoice_lines(self):
        for record in self:
            if not record.sale_invoice_line_ids:
                raise UserError("A sale invoice must have at least one invoice line.")

    def action_done(self):
        if self.state != 'draft':
            raise UserError("Only draft invoices can be marked as done.")

        for line in self.sale_invoice_line_ids:
            medicine = line.medicine_id
            if medicine.quantity < line.quantity:
                raise UserError(f"Not enough stock for {medicine.name}. Available: {medicine.quantity}.")
            medicine.quantity -= line.quantity
            medicine.write({'quantity': medicine.quantity})
            self.message_post(
                body=f'{line.quantity} units of {medicine.name} sold by {self.employee_id.name}.'
            )

        self.write({'state': 'done'})

    def action_paid(self):
        if self.state != 'done':
            raise UserError("Only done invoices can be marked as paid.")
        self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('pharmacy.sale.invoice')
        values['code'] = code
        return super(SaleInvoice, self).create(values)


class SaleInvoiceLine(models.Model):
    _name = 'pharmacy.sale.invoice.line'
    _description = 'Sale Invoice Line'

    sale_invoice_id = fields.Many2one('pharmacy.sale.invoice', string='Sale Invoice', ondelete='cascade')
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

    @api.constrains('medicine_id')
    def _check_allergies(self):
        for line in self:
            client = line.sale_invoice_id.client_id
            if line.medicine_id in client.allergy_ids:
                raise UserError(
                    f"The client {client.full_name} is allergic to {line.medicine_id.name}")

    @api.model
    def create(self, values):
        invoice_id = values.get('sale_invoice_id')
        medicine_id = values.get('medicine_id')
        existing_line = self.search([('sale_invoice_id', '=', invoice_id),
                                     ('medicine_id', '=', medicine_id)], limit=1)
        if existing_line:
            raise UserError("Each invoice line should have different medicines")

        medicine = self.env['pharmacy.medicine'].browse(medicine_id)
        if medicine.quantity < values['quantity']:
            raise UserError(f"Not enough stock for {medicine.name}. Available quantity is {medicine.quantity}.")
        return super(SaleInvoiceLine, self).create(values)