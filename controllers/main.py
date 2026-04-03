from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from werkzeug.exceptions import Forbidden


class PurchaseDashboardController(http.Controller):

    @http.route('/purchase_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        if not request.env.user.has_group('purchase_dashboard.group_purchase_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard achat")
        PO = request.env['purchase.order']

        # Récupérer les paramètres dynamiques (filtres du frontend)
        filters = kwargs.get('filters', {})
        chart_days = filters.get('chart_days', 7)
        recent_days = filters.get('recent_days', 30)
        active_order_limit = filters.get('active_order_limit', 50)
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        responsible_id = filters.get('responsible_id')
        partner_id = filters.get('partner_id')

        # Construire le domaine de base à partir des filtres
        base_domain = []
        if responsible_id:
            base_domain.append(('user_id', '=', responsible_id))
        if partner_id:
            base_domain.append(('partner_id', '=', partner_id))

        # Domaine temporel pour les filtres date
        date_domain = []
        if date_from:
            date_domain.append(('date_order', '>=', date_from))
        if date_to:
            date_domain.append(('date_order', '<=', date_to))

        # Compteurs par état
        states = ['draft', 'sent', 'to approve', 'purchase', 'done', 'cancel']
        state_counts = {}
        for state in states:
            domain = base_domain + date_domain + [('state', '=', state)]
            state_counts[state] = PO.search_count(domain)

        # Commandes en retard (confirmées, date_planned passée, réception incomplète)
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        late_orders = PO.search(base_domain + [
            ('state', '=', 'purchase'),
        ])
        late_count = 0
        for order in late_orders:
            for line in order.order_line:
                if line.date_planned and line.date_planned < datetime.now() and line.qty_received < line.product_qty:
                    late_count += 1
                    break

        # Dépenses ce mois (montant total des commandes confirmées du mois en cours)
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        month_orders = PO.search_read(
            base_domain + [
                ('state', '=', 'purchase'),
                ('date_approve', '>=', month_start),
            ],
            fields=['amount_total'],
        )
        month_total = sum(o['amount_total'] for o in month_orders)

        # Montant achats par jour (N derniers jours - commandes confirmées par date_approve)
        daily_purchases = []
        for i in range(chart_days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            day_end = day.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            domain = base_domain + [
                ('state', '=', 'purchase'),
                ('date_approve', '>=', day_start),
                ('date_approve', '<=', day_end),
            ]
            orders = PO.search_read(domain, fields=['amount_total'])
            amount = sum(o['amount_total'] for o in orders)
            daily_purchases.append({
                'date': day.strftime('%d/%m'),
                'amount': round(amount, 2),
                'count': len(orders),
            })

        # Statistiques période récente
        date_n_ago = datetime.now() - timedelta(days=recent_days)
        recent_orders = PO.search_read(
            base_domain + [
                ('state', '=', 'purchase'),
                ('date_approve', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['amount_total'],
        )
        recent_total_count = len(recent_orders)
        recent_total_amount = sum(o['amount_total'] for o in recent_orders)

        # Commandes actives
        active_domain = base_domain + [
            ('state', 'in', ['draft', 'sent', 'to approve', 'purchase']),
        ]
        if date_from:
            active_domain.append(('date_order', '>=', date_from))
        if date_to:
            active_domain.append(('date_order', '<=', date_to))

        active_orders = PO.search_read(
            active_domain,
            fields=[
                'name', 'partner_id', 'amount_total',
                'state', 'date_order', 'date_planned',
                'user_id', 'receipt_status',
            ],
            order='date_order desc',
            limit=active_order_limit,
        )

        # Top 10 fournisseurs (période récente, commandes confirmées)
        top_suppliers_data = PO.read_group(
            base_domain + [
                ('state', '=', 'purchase'),
                ('date_approve', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['partner_id', 'amount_total:sum'],
            groupby=['partner_id'],
            orderby='amount_total desc',
            limit=10,
        )
        top_suppliers = []
        for s in top_suppliers_data:
            if s['partner_id']:
                top_suppliers.append({
                    'id': s['partner_id'][0],
                    'name': s['partner_id'][1],
                    'amount': round(s['amount_total'], 2),
                    'count': s['partner_id_count'],
                })

        # Config pour le frontend
        config = request.env['purchase.dashboard.config'].get_config()

        return {
            'state_counts': state_counts,
            'late_count': late_count,
            'month_total': round(month_total, 2),
            'daily_purchases': daily_purchases,
            'active_orders': active_orders,
            'recent_total_count': recent_total_count,
            'recent_total_amount': round(recent_total_amount, 2),
            'top_suppliers': top_suppliers,
            'config': config,
        }

    @http.route('/purchase_dashboard/filters_data', type='json', auth='user')
    def get_filters_data(self):
        """Retourne les données pour les listes déroulantes des filtres."""
        if not request.env.user.has_group('purchase_dashboard.group_purchase_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard achat")
        # Acheteurs/responsables ayant des commandes
        users = request.env['purchase.order'].read_group(
            [('user_id', '!=', False)],
            fields=['user_id'],
            groupby=['user_id'],
        )
        responsible_list = [
            {'id': u['user_id'][0], 'name': u['user_id'][1]}
            for u in users if u['user_id']
        ]

        # Fournisseurs
        partners = request.env['purchase.order'].read_group(
            [],
            fields=['partner_id'],
            groupby=['partner_id'],
            limit=200,
        )
        partner_list = [
            {'id': p['partner_id'][0], 'name': p['partner_id'][1]}
            for p in partners if p['partner_id']
        ]

        return {
            'responsibles': responsible_list,
            'partners': partner_list,
        }
