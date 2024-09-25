from odoo import api, fields, models


class BuyingInvoice(models.Model):
    _name = 'pharmacy.buying.invoice'
    _description = 'Buying Invoice'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, default='New')
    supplier_id = fields.Many2one('pharmacy.supplier', string='Supplier', required=True)
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today)
    amount_total = fields.Float(string='Total Amount', compute='_compute_amount_total', store=True)
    state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('done', 'Done'),
                                                        ('paid', 'Paid')], default='draft')
    buying_invoice_line_ids = fields.One2many('pharmacy.buying.invoice.line',
                                              'buying_invoice_id', string='Buying Invoice Lines')

    @api.depends('buying_invoice_line_ids.subtotal')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(line.subtotal for line in record.buying_invoice_line_ids)

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].next_by_code('pharmacy.buying.invoice')
        return super(BuyingInvoice, self).create(values)

    def action_done(self):
        for invoice_line in self.buying_invoice_line_ids:
            invoice_line.medicine_id.quantity += invoice_line.quantity
        self.state = 'done'

    def action_paid(self):
        self.state = 'paid'


class BuyingInvoiceLine(models.Model):
    _name = 'pharmacy.buying.invoice.line'
    _description = 'Buying Invoice Line'

    buying_invoice_id = fields.Many2one('pharmacy.buying.invoice',
                                        string='Buying Invoice', ondelete='cascade')
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
        return super(BuyingInvoiceLine, self).create(values)
