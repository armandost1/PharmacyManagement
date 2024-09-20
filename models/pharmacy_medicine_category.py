from odoo import models, fields, api

class PharmacyMedicineCategory(models.Model):
    _name = 'pharmacy.medicine.category'
    _description = 'Pharmacy Medicine Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')

    def action_view_medicines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medicines',
            'view_mode': 'tree',
            'res_model': 'pharmacy.medicine',
            'domain': [('category_id', '=', self.id)],
            'context': dict(self.env.context),
        }