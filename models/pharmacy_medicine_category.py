from odoo import models, fields, api


class PharmacyMedicineCategory(models.Model):
    _name = 'pharmacy.medicine.category'
    _description = 'Pharmacy Medicine Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    total_quantity = fields.Integer(string='Total Quantity', compute='_compute_total_quantity', store=True)
    medicine_ids = fields.One2many('pharmacy.medicine', 'category_id', string='Medicines')

    def action_view_medicines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medicines',
            'view_mode': 'tree',
            'res_model': 'pharmacy.medicine',
            'domain': [('category_id', '=', self.id)],
            'context': dict(self.env.context),
        }

    @api.depends('medicine_ids.quantity')
    def _compute_total_quantity(self):
        for category in self:
            total = sum(medicine.quantity for medicine in
                        self.env['pharmacy.medicine'].search([('category_id', '=', category.id)]))
            category.total_quantity = total

    def _update_quantity(self):
        for category in self:
            category.total_quantity = sum(medicine.quantity for medicine in category.medicine_ids)
