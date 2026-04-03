{
    'name': 'Tableau de bord Achats',
    'version': '18.0.2.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Dashboard Achats dynamique avec KPI, filtres et configuration',
    'description': 'Tableau de bord interactif pour le suivi des achats avec filtres dynamiques, rafraîchissement auto et configuration.',
    'author': 'SOPROMER',
    'depends': ['purchase'],
    'data': [
        'security/purchase_dashboard_groups.xml',
        'security/ir.model.access.csv',
        'views/purchase_dashboard_config_views.xml',
        'views/purchase_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_dashboard/static/src/css/purchase_dashboard.css',
            'purchase_dashboard/static/src/xml/purchase_dashboard.xml',
            'purchase_dashboard/static/src/js/purchase_dashboard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
