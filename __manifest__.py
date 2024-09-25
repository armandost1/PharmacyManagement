{
    'name': 'pharmacy_management',
    'version': '1.0',
    'summary': 'Summery',
    'description': 'Pharmacy Management System',
    'category': 'Pharmacy',
    'author': 'Author',
    'website': 'Website',
    'depends': ['base', 'mail'],
    'data': [
        'data/invoice_sequence.xml',
        'views/menu.xml',
        'views/pharmacy_medicine_views.xml',
        'views/pharmacy_employee_views.xml',
        'views/pharmacy_selling_invoice_views.xml',
        'views/pharmacy_medicine_category_views.xml',
        'views/pharmacy_supplier_views.xml',
        'views/pharmacy_buying_invoice_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}