from odoo import api, fields, models
from odoo.exceptions import UserError


class Employee(models.Model):
    _name = 'pharmacy.employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee'

    name = fields.Char(string='Name', required=True, tracking=True)
    position = fields.Selection([
        ('manager', 'Manager'),
        ('seller', 'Seller'),
    ], string='Position')
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    image = fields.Image(string='Image')
    salary = fields.Float(string='Salary', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='User')
    current_shift = fields.Char(string='Working Shift', compute='_compute_current_shift')
    shift_ids = fields.One2many('pharmacy.shift', 'employee_id', string='Shifts')


    def name_get(self):
        res = []
        for employee in self:
            try:
                # Check if the current user is an admin
                if not self.env.user.has_group('base.group_system'):
                    raise UserError("You don't have access to see this record.")

                res.append((employee.id, employee.name))
            except UserError as e:
                # Append the error message instead of the employee's name
                res.append((employee.id, str(e)))
        return res

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

