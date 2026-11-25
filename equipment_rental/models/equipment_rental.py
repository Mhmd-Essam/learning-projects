from odoo import models, fields, api
from odoo.exceptions import UserError


class EquipmentRental(models.Model):
    _name = "equipment.rental"
    _description = "Equipment Rental"

    author = fields.Many2one(
        "res.users", string="Author", default=lambda self: self.env.user, readonly=True
    )
    customer_name = fields.Char(string="Customer Name", required=True)
    customer_contact = fields.Char(string="Customer Contact", required=True)
    equipment_id = fields.Many2one("equipment.item", string="Equipment", required=True)
    rental_from = fields.Datetime(string="Rental Start", required=True)
    rental_to = fields.Datetime(string="Expected Return", required=True)
    actual_return_date = fields.Datetime(string="Actual Return Date")
    status = fields.Selection(
        [("ongoing", "Ongoing"), ("completed", "Completed")],
        string="Status",
        default="ongoing",
    )
    rental_duration = fields.Integer(
        string="Rental Duration", compute="_compute_rental_duration", store=True
    )
    is_return_date_invalid = fields.Boolean(compute="_compute_is_return_date_invalid")
    is_return_date_valid = fields.Boolean(compute="_compute_is_return_date_valid")

    def create(self, vals_list):
        for vals in vals_list:
            equipment = self.env["equipment.item"].browse(vals.get("equipment_id"))
            if equipment.status == "rented":
                raise UserError("This equipment is already rented.")
            equipment.status = "rented"
        return super(EquipmentRental, self).create(vals_list)

    def write(self, vals):
        if "equipment_id" in vals:
            new_equipment = self.env["equipment.item"].browse(vals.get("equipment_id"))
            if new_equipment.status == "rented":
                raise UserError("This equipment is already rented.")
            self.equipment_id.status = "available"
            new_equipment.status = "rented"
        return super(EquipmentRental, self).write(vals)

    def unlink(self):
        for rental in self:
            if rental.status == "ongoing":
                raise UserError("Cannot delete an ongoing rental.")
            rental.equipment_id.status = "available"
        return super(EquipmentRental, self).unlink()

    def return_equipment(self):
        for rental in self:
            if rental.status != "ongoing":
                raise UserError("Only ongoing rentals can be returned.")
            if fields.Datetime.now() < rental.rental_to:
                raise UserError(
                    "Cannot return equipment before the expected return date."
                )
            rental.status = "completed"
            rental.actual_return_date = fields.Datetime.now()
            rental.equipment_id.status = "available"

    @api.depends("rental_from", "actual_return_date")
    def _compute_rental_duration(self):
        for rental in self:
            if rental.actual_return_date and rental.rental_from:
                rental.rental_duration = (
                    rental.actual_return_date - rental.rental_from
                ).days
            else:
                rental.rental_duration = 0

    @api.depends("actual_return_date", "rental_to")
    def _compute_is_return_date_invalid(self):
        for record in self:
            record.is_return_date_invalid = bool(
                record.actual_return_date
                and record.rental_to
                and record.actual_return_date > record.rental_to
            )

    @api.depends("actual_return_date", "rental_to")
    def _compute_is_return_date_valid(self):
        for record in self:
            record.is_return_date_valid = bool(
                record.actual_return_date
                and record.rental_to
                and record.actual_return_date <= record.rental_to
            )

    @api.constrains("rental_from", "rental_to")
    def _check_rental_dates(self):
        for record in self:
            if record.rental_from and record.rental_to:
                if record.rental_from >= record.rental_to:
                    raise UserError(
                        "Rental start date must be before the expected return date."
                    )
