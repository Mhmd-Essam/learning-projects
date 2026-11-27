from odoo import models, fields, api
from odoo.exceptions import UserError


class EquipmentItem(models.Model):
    _name = "equipment.item"
    _description = "Equipment Item"

    name = fields.Char(string="Equipment Name", required=True)
    status = fields.Selection(
        [("available", "Available"), ("rented", "Rented")],
        string="Status",
        default="available",
    )
    type = fields.Selection(
        [("electrical", "Electrical"), ("mechanical", "Mechanical")],
        string="Type",
        required=True,
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    equipment_parcode = fields.Char(
        string="Equipment Barcode",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: "New",
        
    )
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name = vals.get("name")
            company_id = vals.get("company_id")
            if vals.get("equipment_parcode", "New") == "New":
                vals["equipment_parcode"] = self.env["ir.sequence"].next_by_code("equipment.item") or "New"
            existing_equipment = self.env["equipment.item"].search(
                [("name", "=", name), ("company_id", "=", company_id)]
            )
            if existing_equipment:
                raise UserError(
                    "Equipment with the same name already exists in this company."
                )

        return super(EquipmentItem, self).create(vals_list)

    def unlink(self):
        for record in self:
            if record.status == "rented":
                existing_equipment = self.env["equipment.rental"].search(
                    [("equipment_id", "=", record.id), ("status", "=", "ongoing")]
                )
                if existing_equipment:
                    raise UserError(
                        "Cannot delete equipment that is currently rented."
                    )
        return super(EquipmentItem, self).unlink()

    def write(self, vals):
        for record in self:
            if "name" in vals:
                new_name = vals["name"]
                company_id = record.company_id.id
                company = self.env["res.company"].browse(company_id)
                existing_equipment = self.env["equipment.item"].search(
                    [
                        ("name", "=", new_name),
                        ("company_id", "=", company_id),
                        ("id", "!=", record.id),
                    ]
                )
                if existing_equipment:
                    raise UserError(
                        f"Equipment with the same name already exists in {company.name}."
                    )
        return super(EquipmentItem, self).write(vals)
