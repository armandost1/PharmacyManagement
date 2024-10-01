from odoo import models, api


class PharmacySaleInvoiceReport(models.AbstractModel):
    _name = 'report.pharmacy_management.report_invoice'
    _description = 'Pharmacy Sale Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = [
            ('sale_invoice_id.invoice_date', '>=', data['start_date']),
            ('sale_invoice_id.invoice_date', '<=', data['end_date']),
        ]

        if not data.get('medicine_ids'):
            medicine_summary_name = 'All Medicines'
        else:
            domain.append(('medicine_id', 'in', data['medicine_ids']))
            medicines = self.env['pharmacy.medicine'].browse(data['medicine_ids']).mapped('name')
            medicine_summary_name = f'Medicines: {", ".join(medicines)}'

        invoice_lines = self.env['pharmacy.sale.invoice.line'].search(domain)

        # Group data by medicine
        grouped_data = {}
        for line in invoice_lines:
            medicine_name = line.medicine_id.name
            if medicine_name not in grouped_data:
                grouped_data[medicine_name] = {
                    'qty': 0,
                    'total': 0,
                }
            grouped_data[medicine_name]['qty'] += line.quantity
            grouped_data[medicine_name]['total'] += line.subtotal

        report_data = []
        for medicine, data in grouped_data.items():
            report_data.append({
                'medicine': medicine,
                'qty': data['qty'],
                'total': data['total'],
            })

        return {
            'docs': report_data,
            'r_name': medicine_summary_name,
        }