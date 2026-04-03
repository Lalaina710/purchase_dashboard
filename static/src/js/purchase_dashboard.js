/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class PurchaseDashboard extends Component {
    static template = "purchase_dashboard.PurchaseDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {},
            // Filtres dynamiques
            filters: {
                chart_days: 7,
                recent_days: 30,
                active_order_limit: 50,
                date_from: '',
                date_to: '',
                responsible_id: 0,
                partner_id: 0,
            },
            // Données des listes déroulantes
            responsibles: [],
            partners: [],
            // Panneau filtres visible/masqué
            showFilters: false,
            // Auto-refresh
            autoRefreshInterval: 0,
            // Dernière mise à jour
            lastUpdate: '',
        });
        this._refreshTimer = null;

        onWillStart(async () => {
            await this.loadFiltersData();
            await this.loadConfig();
            await this.loadData();
        });

        onMounted(() => {
            this._startAutoRefresh();
        });

        onWillUnmount(() => {
            this._stopAutoRefresh();
        });
    }

    async loadConfig() {
        try {
            const config = await this.orm.call(
                'purchase.dashboard.config', 'get_config', []
            );
            this.state.filters.chart_days = config.chart_days;
            this.state.filters.recent_days = config.recent_days;
            this.state.filters.active_order_limit = config.active_order_limit;
            this.state.autoRefreshInterval = config.auto_refresh_interval;
        } catch (e) {
            console.warn("Config non disponible, valeurs par défaut utilisées");
        }
    }

    async loadFiltersData() {
        try {
            const data = await rpc("/purchase_dashboard/filters_data", {});
            this.state.responsibles = data.responsibles || [];
            this.state.partners = data.partners || [];
        } catch (e) {
            console.warn("Impossible de charger les filtres:", e);
        }
    }

    async loadData() {
        this.state.loading = true;
        try {
            const filters = { ...this.state.filters };
            // Nettoyer les filtres vides
            if (!filters.responsible_id) delete filters.responsible_id;
            if (!filters.partner_id) delete filters.partner_id;
            if (!filters.date_from) delete filters.date_from;
            if (!filters.date_to) delete filters.date_to;

            this.state.data = await rpc("/purchase_dashboard/data", { filters });
            this.state.lastUpdate = new Date().toLocaleTimeString("fr-FR");
        } catch (e) {
            console.error("Purchase Dashboard error:", e);
            this.state.data = {
                state_counts: {},
                late_count: 0,
                month_total: 0,
                daily_purchases: [],
                active_orders: [],
                recent_total_count: 0,
                recent_total_amount: 0,
                top_suppliers: [],
            };
        }
        this.state.loading = false;
    }

    // --- Gestion des filtres ---

    toggleFilters() {
        this.state.showFilters = !this.state.showFilters;
    }

    onFilterChange(field, ev) {
        const value = ev.target.value;
        if (['chart_days', 'recent_days', 'active_order_limit',
             'responsible_id', 'partner_id'].includes(field)) {
            this.state.filters[field] = parseInt(value) || 0;
        } else {
            this.state.filters[field] = value;
        }
    }

    applyFilters() {
        this.loadData();
    }

    resetFilters() {
        this.state.filters = {
            chart_days: 7,
            recent_days: 30,
            active_order_limit: 50,
            date_from: '',
            date_to: '',
            responsible_id: 0,
            partner_id: 0,
        };
        this.loadData();
    }

    // --- Auto-refresh ---

    onRefreshIntervalChange(ev) {
        this.state.autoRefreshInterval = parseInt(ev.target.value) || 0;
        this._startAutoRefresh();
    }

    _startAutoRefresh() {
        this._stopAutoRefresh();
        const interval = this.state.autoRefreshInterval;
        if (interval > 0) {
            this._refreshTimer = setInterval(() => this.loadData(), interval * 1000);
        }
    }

    _stopAutoRefresh() {
        if (this._refreshTimer) {
            clearInterval(this._refreshTimer);
            this._refreshTimer = null;
        }
    }

    // --- Formatage et helpers ---

    formatAmount(amount) {
        if (!amount && amount !== 0) return "0,00";
        const formatted = Number(amount).toLocaleString("fr-FR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
        const cur = this.state.data.currency || {};
        const symbol = cur.symbol || '';
        if (!symbol) return formatted;
        if (cur.position === 'before') {
            return symbol + ' ' + formatted;
        }
        return formatted + ' ' + symbol;
    }

    formatQty(qty) {
        if (!qty) return "0";
        return Math.round(qty).toLocaleString("fr-FR");
    }

    getBarHeight(amount) {
        const maxAmount = Math.max(
            ...this.state.data.daily_purchases.map((d) => d.amount),
            1
        );
        return Math.max((amount / maxAmount) * 150, 4);
    }

    getStateLabel(state) {
        const labels = {
            draft: "Brouillon",
            sent: "Envoyée",
            "to approve": "A approuver",
            purchase: "Confirmée",
            done: "Verrouillée",
            cancel: "Annulée",
        };
        return labels[state] || state;
    }

    getStateBadgeClass(state) {
        const classes = {
            draft: "draft",
            sent: "sent",
            "to approve": "to_approve",
            purchase: "purchase",
            done: "done",
            cancel: "cancel",
        };
        return classes[state] || "draft";
    }

    getReceiptLabel(order) {
        const status = order.receipt_status;
        if (status === 'full') return "Complet";
        if (status === 'partial') return "Partiel";
        if (status === 'pending') return "En attente";
        return "N/A";
    }

    getReceiptClass(order) {
        const status = order.receipt_status;
        if (status === 'full') return "receipt-full";
        if (status === 'partial') return "receipt-partial";
        if (status === 'pending') return "receipt-pending";
        return "receipt-na";
    }

    hasActiveFilters() {
        const f = this.state.filters;
        return f.date_from || f.date_to || f.responsible_id || f.partner_id
            || f.chart_days !== 7 || f.recent_days !== 30;
    }

    openOrders(state) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: `Achats - ${this.getStateLabel(state)}`,
            res_model: "purchase.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "=", state]],
            target: "current",
        });
    }

    openLateOrders() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Commandes en retard",
            res_model: "purchase.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["state", "=", "purchase"],
            ],
            target: "current",
        });
    }

    openOrder(orderId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "purchase.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openSupplier(partnerId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Commandes fournisseur",
            res_model: "purchase.order",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["partner_id", "=", partnerId],
                ["state", "=", "purchase"],
            ],
            target: "current",
        });
    }
}

registry.category("actions").add("purchase_dashboard.PurchaseDashboard", PurchaseDashboard);
