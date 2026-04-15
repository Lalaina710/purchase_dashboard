# Modified by: odoo-backend agent — 2026-04-13 — Fix late_count perf, bc_month, timezone
from odoo import fields, http
from odoo.http import request
from datetime import timedelta, datetime
import pytz
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

        # Convert date_from/date_to to UTC boundaries (user timezone)
        _ftz = pytz.timezone(request.env.user.tz or 'Indian/Antananarivo')
        if date_from and len(date_from) == 10:
            _df_local = _ftz.localize(datetime.strptime(date_from, '%Y-%m-%d'))
            date_from = _df_local.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        if date_to and len(date_to) == 10:
            _dt_local = _ftz.localize(datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
            date_to = _dt_local.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
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

        # Commandes en retard (optimisé — un seul search_count)
        now = fields.Datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        late_count = PO.search_count(base_domain + [
            ('state', '=', 'purchase'),
            ('order_line.date_planned', '<', now_str),
        ])

        # Total BC Achat (mois en cours par défaut)
        today = fields.Datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        bc_date_domain = date_domain if date_domain else [('date_order', '>=', month_start)]
        bc_domain = base_domain + bc_date_domain + [
            ('state', 'in', ['purchase', 'done']),
        ]
        bc_groups = PO.read_group(bc_domain, fields=['amount_total:sum'], groupby=[])
        bc_month = bc_groups[0].get('amount_total', 0) if bc_groups else 0

        # Facturation Achat ce mois : payé et non payé
        Invoice = request.env['account.move']
        invoice_domain = [
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ]
        if date_from:
            invoice_domain.append(('invoice_date', '>=', date_from))
        else:
            invoice_domain.append(('invoice_date', '>=', today.replace(day=1).strftime('%Y-%m-%d')))
        if date_to:
            invoice_domain.append(('invoice_date', '<=', date_to))
        if responsible_id:
            invoice_domain.append(('invoice_user_id', '=', responsible_id))
        if partner_id:
            invoice_domain.append(('partner_id', '=', partner_id))
        purchase_invoices = Invoice.search_read(
            invoice_domain,
            fields=['amount_total', 'payment_state'],
        )
        purchase_paid = sum(inv['amount_total'] for inv in purchase_invoices if inv['payment_state'] in ('paid', 'in_payment'))
        purchase_unpaid = sum(inv['amount_total'] for inv in purchase_invoices if inv['payment_state'] not in ('paid', 'in_payment'))

        # Montant achats par jour (optimisé read_group)
        pnow = fields.Datetime.now()
        pchart_start = (pnow - timedelta(days=chart_days - 1)).strftime('%Y-%m-%d 00:00:00')
        pchart_domain = base_domain + [('state', '=', 'purchase'), ('date_approve', '>=', pchart_start)]
        pchart_groups = PO.read_group(pchart_domain, fields=['amount_total:sum', 'date_approve'], groupby=['date_approve:day'])
        user_tz = pytz.timezone(request.env.user.tz or 'Indian/Antananarivo')
        pchart_by_date = {}
        for g in pchart_groups:
            rng = g.get('__range', {}).get('date_approve:day', {})
            from_str = rng.get('from', '')
            if from_str:
                utc_dt = datetime.strptime(from_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
                dk = utc_dt.astimezone(user_tz).strftime('%Y-%m-%d')
                pchart_by_date[dk] = {'amount': round(g.get('amount_total', 0), 2), 'count': g.get('__count', 0)}
        daily_purchases = []
        for i in range(chart_days - 1, -1, -1):
            day = pnow.replace(tzinfo=pytz.utc).astimezone(user_tz) - timedelta(days=i)
            day_key = day.strftime('%Y-%m-%d')
            data = pchart_by_date.get(day_key, {})
            daily_purchases.append({
                'date': day.strftime('%d/%m'),
                'amount': data.get('amount', 0),
                'count': data.get('count', 0),
            })

        # Statistiques période récente
        date_n_ago = fields.Datetime.now() - timedelta(days=recent_days)
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

        # Devise de la société
        currency = request.env.company.currency_id
        currency_info = {
            'symbol': currency.symbol or '',
            'position': currency.position or 'after',
        }

        return {
            'currency': currency_info,
            'state_counts': state_counts,
            'late_count': late_count,
            'bc_month': round(bc_month, 2),
            'invoice_purchase': {
                'total': round(purchase_paid + purchase_unpaid, 2),
                'paid': round(purchase_paid, 2),
                'unpaid': round(purchase_unpaid, 2),
            },
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
