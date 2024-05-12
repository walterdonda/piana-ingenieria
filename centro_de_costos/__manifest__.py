# -*- coding: utf-8 -*-
{
    "name": "Centro de costos y proyectos ingeniería",
    "summary": """
        Módulo que permite agregar el concepto de centro de costos a odoo 
        """,
    "description": """
        Este módulo permite hacer el seguimiento de la facturación de c/u de los proyectos de la empresa.

        A cada proyecto se le asigna un centro de costo o una jerarquía del mismo. 
        Para esto se modifica el modelo de odoo cuenta analítica y se le agregan los siguientes campos:
        
        budget_project --> Presupuesto del proyecto
        
        margin_project --> Margen económico del proyecto
        
        outstanding_invoice_amount --> Monto pendiente a facturar en cada centro de costo
        
        Al final del proyecto el monto pendiente de facturar en el centro de costo debe ser 0.
    """,
    "author": "Walter Donda",
    "category": "Services/Ingenieria",
    "version": "1.0",
    # Este módulo depende de los siguientes módulos de odoo 15
    "depends": ["base", "account", "analytic", "account_analytic_parent","project","l10n_ar_afipws_fe"],
    # Se cargan los datos de acceso y los reportes nuevos
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/project.xml",
        "views/debit_note_afip.xml",
        "views/report_invoice_analysis.xml",
        "report/report.xml",
        "report/template_centro_de_costos.xml",
    ],
    # Datos demos
    "demo": [
        "demo/demo.xml",
    ],
}
