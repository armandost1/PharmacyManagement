from odoo import models, fields, api


class SaleInvoiceWizard(models.TransientModel):
    _name = 'sale.invoice.wizard'
    _description = 'Sale Invoice wizard'

    medicine_ids = fields.Many2many('pharmacy.medicine', string="Medicines")
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def print_report(self):
        data = {
            'medicine_ids': self.medicine_ids.ids,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('pharmacy_management.action_report_invoice').report_action(self, data=data)

