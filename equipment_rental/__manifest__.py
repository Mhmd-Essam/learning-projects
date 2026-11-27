{
    "name": "Equipment Rental",
    "version": "1.0",
    "summary": "Equipment rental management",
    "description": "Manage equipment inventory and rental operations",
    "author": "Mohamed",
    "category": "Inventory",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/equipment_rental_security_ir_rule.xml",
        "data/ir_sequence_data.xml",
        "views/equipment_item_view.xml",
        "views/equipment_rental_view.xml",
    ],
    "installable": True,
    "application": True,
}
