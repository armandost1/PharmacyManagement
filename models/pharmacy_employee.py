from datetime import timedelta, datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError


class Employee(models.Model):
    _name = 'pharmacy.employee'
    _description = 'Employee'

    name = fields.Char(string='Name', required=True)
    position = fields.Selection([
        ('manager', 'Manager'),
        ('seller', 'Seller'),
    ], string='Position')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    salary = fields.Float(string='Salary', required=True)
    user_id = fields.Many2one('res.users', string='User')
    current_shift = fields.Char(string='Working Shift', compute='_compute_current_shift')
    shift_ids = fields.One2many('pharmacy.shift', 'employee_id', string='Shifts')
    registration_date = fields.Date(string='Registration Date', required=True)
    points = fields.Integer(string='Points', default=0)
    image = fields.Image(string='Image')
    original_salary = fields.Float(string='Original Salary', required=True)
    last_salary_raise_date = fields.Date(string='Last Salary Raise Date')
    last_salary_increase_awarded = fields.Boolean(default=False)

    salary_increase_amount = 50
    salary_increase_threshold = 30

    def _award_salary_increase(self):
        for employee in self:
            if employee.points >= self.salary_increase_threshold:

                if not employee.last_salary_increase_awarded:
                    employee.salary += self.salary_increase_amount
                    employee.last_salary_raise_date = date.today()
                    employee.last_salary_increase_awarded = True

    @api.model
    def reset_monthly_data(self):
        today = date.today()
        for employee in self.search([]):
            if employee.last_salary_raise_date and (
                employee.last_salary_raise_date.month != today.month or
                employee.last_salary_raise_date.year != today.year
            ):
                employee.points = 0
                employee.salary = employee.original_salary
                employee.last_salary_increase_awarded = False

    @api.depends('salary')
    def _compute_original_salary(self):
        for employee in self:
            employee.original_salary = employee.salary

    @api.depends('shift_ids.start_time', 'shift_ids.end_time')
    def _compute_current_shift(self):
        for employee in self:
            shift = self.env['pharmacy.shift'].search([
                ('employee_id', '=', employee.id)
            ], limit=1)
            if shift:
                employee.current_shift = f"{shift.shift_type.capitalize()}"
            else:
                employee.current_shift = "No shift assigned"

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise UserError("The email must contain '@'.")

    @api.constrains('phone')
    def _check_phone(self):
        for number in self:
            if number.phone:
                if not number.phone.isdigit():
                    raise UserError("The phone number must contain only digits.")
                if len(number.phone) > 15:
                    raise UserError("The phone number must contain up to 15 digits.")


class EmployeeSalaryRaise(models.Model):
    _inherit = 'pharmacy.employee'

    @api.model
    def _raise_employee_salaries(self):
        today = datetime.today().date()
        employees_to_raise = self.search([])
        for employee in employees_to_raise:
            if employee.registration_date:
                registration_time = fields.Date.from_string(employee.registration_date)
                if today >= registration_time + timedelta(days=90):
                    employee.salary += 100
                    employee.original_salary = employee.salary
                    employee.registration_date = today
