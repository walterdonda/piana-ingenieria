from odoo import models, fields, api


class UpdateIndex(models.Model):

    _name = "update.index"
    _description = "Índice de actualización"
    type = fields.Selection(
        [
            ("idc", "Índice de la construcción"),
            ("ipc", "Índice de precios al consumidor"),
        ],
        string="Nombre de índice",
    )

    period = fields.Selection(
        [
            ("january", "Enero"),
            ("february", "Febrero"),
            ("march", "Marzo"),
            ("april", "Abril"),
            ("may", "Mayo"),
            ("june", "Junio"),
            ("july", "Julio"),
            ("august", "Agosto"),
            ("september", "Septiembre"),
            ("october", "Octubre"),
            ("november", "Noviembre"),
            ("december", "Diciembre"),
        ],
        string="Periodo",
    )
    year = fields.Integer(string="Año", related="period.year")
    period_year = fields.Char(
        string="Período y año", compute="_compute_period_year", store=True, unique=True
    )
    interest_rate = fields.Float(string="Tasa de interés")
    centro_costos_ids = fields.Many2many(
        "account.analytic.account", string="centro_costos"
    )

    @api.depends("period", "year")
    def _compute_period_year(self):
        for record in self:
            record.period_year = f"{record.period} {record.year}"

    @api.constrains("period", "year")
    def _check_unique_period(self):
        for record in self:
            if self.search([("period_year", "=", record.period_year)]):
                raise ValueError("El período y año ya existen.")
