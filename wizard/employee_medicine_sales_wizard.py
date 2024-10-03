from odoo import models, fields, api

class EmployeeMedicineSalesWizard(models.TransientModel):
    _name = 'employee.medicine.sales.wizard'
    _description = 'Employee Medicine Sales Wizard'

    medicine_ids = fields.Many2many('pharmacy.medicine', string="Medicines")
    employee_ids = fields.Many2many('pharmacy.employee', string="Employees")
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def print_report(self):
        data = {
            'medicine_ids': self.medicine_ids.ids,
            'employee_ids': self.employee_ids.ids,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('pharmacy_management.action_employee_medicine_sales_report').report_action(self, data=data)