# -*- coding: utf-8 -*-
{
    "name": "Centro de costos para hacer seguimiento de proyectos de ingeniería",
    "summary": """
        Módulo que permite agregar el concepto de centro de costos a odoo 
        """,
    "description": """
        Este módulo permite hacer el seguimiento de la facturación de c/u de los proyectos/departamentos de la empresa.
        A cada proyecto se le asigna un centro de costo o una jerarquía del mismo. 
        Para esto se modifica el modelo de odoo cuenta analítica y se le agregan los siguientes campos:
        budget_project --> Presupuesto del proyecto
        margin_project --> Margen económico del proyecto
        outstanding_invoice_amount --> Monto pendiente a facturar
        Al final del proyecto el monto pendiente de facturar debe ser 0, el monto pendiente de facturar es la resta entre
        el presupuesto (variable) y la diferencia resultante entre las facturas a cliente menos las facturas de proveedores (balance)
    """,
    "author": "Walter Donda",
    "category": "Services/Ingenieria",
    "version": "15.0",
    # any module necessary for this one to work correctly
    "depends": ["analytic"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
