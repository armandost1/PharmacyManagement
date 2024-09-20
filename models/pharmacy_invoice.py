from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Invoice(models.Model):
    _name = 'pharmacy.invoice'
    _description = 'Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    employee_id = fields.Many2one('pharmacy.employee', string='Employee')
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    invoice_line_ids = fields.One2many('pharmacy.invoice.line', 'invoice_id', string='Invoice Lines')
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Payment Status', default='unpaid')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True)

    @api.depends('invoice_line_ids.subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(line.subtotal for line in record.invoice_line_ids)

    @api.constrains('invoice_line_ids')
    def _check_invoice_lines(self):
        for record in self:
            if not record.invoice_line_ids:
                raise ValidationError("An invoice must have at least one invoice line.")


    def action_draft(self):
        self.write({'state': 'confirmed'})
        for record in self:
            record.payment_status = 'unpaid'

    def action_pay(self):
        self.write({'state': 'paid'})
        for record in self:
            record.payment_status = 'paid'

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        for record in self:
            record.payment_status = 'cancelled'

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('pharmacy.invoice')
        values['code'] = code
        res = super(Invoice, self).create(values)
        return res

    def write(self, values):
        res = super(Invoice, self).write(values)
        return res


class InvoiceLine(models.Model):
    _name = 'pharmacy.invoice.line'
    _description = 'Invoice Line'

    invoice_id = fields.Many2one('pharmacy.invoice', string='Invoice', ondelete='cascade')
    medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
    quantity = fields.Integer(string='Quantity', required=True)
    price_unit = fields.Float(string='Unit Price', related='medicine_id.price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.constrains('quantity', 'price_unit')
    def _check_positive_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be positive.")
            if line.price_unit <= 0:
                raise ValidationError("Unit Price must be positive.")


