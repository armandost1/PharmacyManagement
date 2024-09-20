from odoo import models, fields


class PharmacyMedicineCategory(models.Model):
    _name = 'pharmacy.medicine.category'
    _description = 'Pharmacy Medicine Category'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')