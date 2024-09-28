from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleInvoice(models.Model):
    _name = 'pharmacy.sale.invoice'
    _description = 'Sale Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    employee_id = fields.Many2one('pharmacy.employee', string='Employee', required=True,
                                  compute='_compute_employee_shift', store=True)
    client_id = fields.Many2one('pharmacy.client', string='Client', required=True)
    invoice_date = fields.Datetime(string='Invoice Date', default=fields.Datetime.now())
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    sale_invoice_line_ids = fields.One2many('pharmacy.sale.invoice.line', 'sale_invoice_id',
                                            string='Sale Invoice Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('paid', 'Paid')
    ], string='Status', default='draft', required=True)
    shift_id = fields.Many2one('pharmacy.shift', string='Shift')

    @api.depends('invoice_date')
    def _compute_employee_shift(self):
        for record in self:
            shift = self.env['pharmacy.shift'].search([
                ('start_time', '<=', record.invoice_date),
                ('end_time', '>=', record.invoice_date),
            ], limit=1)
            record.employee_id = shift.employee_id if shift else False

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

        self.write({'state': 'done'})

    def action_paid(self):
        if self.state != 'done':
            raise UserError("Only done invoices can be marked as paid.")
        self.write({'state': 'paid'})

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('pharmacy.sale.invoice')
        values['code'] = code

        invoice_date = values.get('invoice_date', fields.Datetime.now())
        shift = self.env['pharmacy.shift'].search([
            ('start_time', '<=', invoice_date),
            ('end_time', '>=', invoice_date),
        ], limit=1)
        if shift:
            values['employee_id'] = shift.employee_id.id

        return super(SaleInvoice, self).create(values)

    def write(self, values):
        for record in self:
            if record.state == 'paid':
                raise UserError("This invoice cannot be edited once it is paid.")

            if 'client_id' in values:
                new_client_id = values['client_id']
                new_client = self.env['pharmacy.client'].browse(new_client_id)

                for line in record.sale_invoice_line_ids:
                    if line.medicine_id in new_client.allergy_ids:
                        raise UserError(
                            f"The new client {new_client.full_name} is allergic to {line.medicine_id.name}"
                        )
        return super(SaleInvoice, self).write(values)


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

