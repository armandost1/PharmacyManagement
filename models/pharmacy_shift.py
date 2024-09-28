from odoo import models, fields, api
from odoo.exceptions import UserError


class PharmacyShift(models.Model):
    _name = 'pharmacy.shift'
    _description = 'Employee Shift'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('pharmacy.employee', string='Employee', required=True)
    shift_type = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night'),
    ], string='Shift Type', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    creation_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)

    @api.constrains('start_time', 'end_time')
    def _check_time_consistency(self):
        for record in self:
            if record.start_time >= record.end_time:
                raise UserError("End Time must be after Start Time.")

    @api.constrains('employee_id', 'start_time', 'end_time')
    def _check_overlapping_shifts(self):
        for record in self:
            overlapping_shifts = self.env['pharmacy.shift'].search([
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ])
            if overlapping_shifts:
                raise UserError("The employee is already assigned to another shift during this time period.")

    @api.model
    def update_shift_dates(self):
        current_datetime = fields.Datetime.now()
        shifts = self.search([])

        for shift in shifts:
            new_start_time = fields.Datetime.combine(current_datetime.date(), shift.start_time.time())
            new_end_time = fields.Datetime.combine(current_datetime.date(), shift.end_time.time())
            shift.write({
                'start_time': new_start_time,
                'end_time': new_end_time,
            })