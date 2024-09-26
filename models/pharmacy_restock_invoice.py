from odoo import models, fields, api
from odoo.exceptions import UserError


class RestockInvoice(models.Model):
    _name = 'pharmacy.restock.invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Restock Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('done', 'Done'),
                                                        ('paid', 'Paid')], default='draft')
    restock_invoice_line_ids = fields.One2many('pharmacy.restock.invoice.line',
                                              'restock_invoice_id', string='Restock Invoice Lines')

    @api.depends('restock_invoice_line_ids.subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(line.subtotal for line in record.restock_invoice_line_ids)

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].next_by_code('pharmacy.restock.invoice')
        return super(RestockInvoice, self).create(values)

    def action_done(self):
        for invoice_line in self.restock_invoice_line_ids:
            invoice_line.medicine_id.quantity += invoice_line.quantity
            self.message_post(
                body=f'{invoice_line.quantity} units of {invoice_line.medicine_id.name}'
                     f' bought from {self.supplier_id.name}.'
            )
        self.state = 'done'

    def action_paid(self):
        self.state = 'paid'


class RestockInvoiceLine(models.Model):
    _name = 'pharmacy.restock.invoice.line'
    _description = 'Restock Invoice Line'

    restock_invoice_id = fields.Many2one('pharmacy.restock.invoice',
                                          string='Restock Invoice', ondelete='cascade')
    medicine_id = fields.Many2one('pharmacy.medicine', string='Medicine', required=True)
    quantity = fields.Integer(string='Quantity', required=True)
    price_unit = fields.Float(string='Unit Price', related='medicine_id.price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.model
    def create(self, values):
        invoice_id = values.get('restock_invoice_id')
        medicine_id = values.get('medicine_id')
        existing_line = self.search([('restock_invoice_id', '=', invoice_id),
                                      ('medicine_id', '=', medicine_id)], limit=1)
        if existing_line:
            raise UserError("Each invoice line should have different medicines")
        return super(RestockInvoiceLine, self).create(values)