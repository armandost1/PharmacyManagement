from odoo import models, api


class EmployeeMedicineSalesReport(models.AbstractModel):
    _name = 'report.pharmacy_management.report_employee_medicine_sales'
    _description = 'Employee Medicine Sales Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        domain = [
            ('sale_invoice_id.invoice_date', '>=', data['start_date']),
            ('sale_invoice_id.invoice_date', '<=', data['end_date']),
        ]

        if data.get('medicine_ids'):
            domain.append(('medicine_id', 'in', data['medicine_ids']))

        if data.get('employee_ids'):
            domain.append(('sale_invoice_id.employee_id', 'in', data['employee_ids']))

        invoice_lines = self.env['pharmacy.sale.invoice.line'].search(domain)

        # Group data by medicine and employee
        grouped_data = {}
        for line in invoice_lines:
            key = (line.medicine_id.name, line.sale_invoice_id.employee_id.name)
            if key not in grouped_data:
                grouped_data[key] = {
                    'price_unit': line.price_unit,
                    'total_qty': 0,
                    'total_amount': 0,
                }
            grouped_data[key]['total_qty'] += line.quantity
            grouped_data[key]['total_amount'] += line.subtotal

        report_data = []
        for (medicine, employee), data in grouped_data.items():
            report_data.append({
                'medicine': medicine,
                'employee': employee,
                'price_unit': data['price_unit'],
                'total_qty': data['total_qty'],
                'total_amount': data['total_amount'],
            })

        return {
            'docs': report_data,
        }