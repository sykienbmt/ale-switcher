/**
 * AleSwitcher GUI - Alpine.js application
 */
function app() {
  return {
    // State
    ready: false,
    loading: false,
    accounts: [],
    currentAccount: null,
    optimalResult: null,
    refreshInterval: null,
    searchQuery: '',
    switchingId: null,
    refreshingIds: new Set(),
    detailAccount: null,
    toast: { show: false, message: '', type: 'info' },

    // Computed: filtered accounts
    get filteredAccounts() {
      if (!this.searchQuery) return this.accounts;
      const q = this.searchQuery.toLowerCase();
      return this.accounts.filter(a =>
        (a.email && a.email.toLowerCase().includes(q)) ||
        (a.nickname && a.nickname.toLowerCase().includes(q))
      );
    },

    // Init
    async init() {
      await this.waitForBridge();
      this.ready = true;
      await this.refreshAll();
      this.refreshInterval = setInterval(() => this.refreshAll(), 60000);
    },

    async waitForBridge() {
      let attempts = 0;
      while ((!window.pywebview || !window.pywebview.api) && attempts < 100) {
        await new Promise(r => setTimeout(r, 100));
        attempts++;
      }
      if (!window.pywebview || !window.pywebview.api) {
        console.error('pywebview bridge not available');
      }
    },

    // Toast notifications
    showToast(message, type = 'info') {
      this.toast = { show: true, message, type };
      setTimeout(() => { this.toast.show = false; }, 4000);
    },

    // Data fetching
    async refreshAll() {
      if (this.loading) return;
      this.loading = true;
      try {
        await Promise.all([
          this.loadAccounts(),
          this.loadCurrentAccount(),
        ]);
      } finally {
        this.loading = false;
      }
    },

    async loadAccounts() {
      try {
        const data = await window.pywebview.api.get_usage(false);
        if (Array.isArray(data)) {
          this.accounts = data;
        } else if (data?.error) {
          console.warn('get_usage failed, falling back to get_accounts:', data.error);
          const fallback = await window.pywebview.api.get_accounts();
          if (Array.isArray(fallback)) this.accounts = fallback;
        }
      } catch (e) {
        console.error('Failed to load accounts:', e);
        try {
          const fallback = await window.pywebview.api.get_accounts();
          if (Array.isArray(fallback)) this.accounts = fallback;
        } catch (e2) {
          console.error('Fallback get_accounts also failed:', e2);
        }
      }
    },

    async loadCurrentAccount() {
      try {
        const data = await window.pywebview.api.get_current_account();
        if (!data.error) this.currentAccount = data;
      } catch (e) {
        console.error('Failed to load current account:', e);
      }
    },

    // Actions
    async switchTo(acc) {
      if (this.switchingId) return;
      this.switchingId = acc.uuid;
      try {
        const id = String(acc.index);
        const result = await window.pywebview.api.switch_account(id);
        if (result.error) {
          this.showToast('Switch failed: ' + result.error, 'error');
        } else {
          this.currentAccount = result.account;
          this.showToast('Switched to ' + (result.account.nickname || result.account.email), 'success');
          await this.loadAccounts();
        }
      } finally {
        setTimeout(() => { this.switchingId = null; }, 500);
      }
    },

    async switchOptimal() {
      if (this.loading) return;
      this.loading = true;
      this.optimalResult = null;
      try {
        const result = await window.pywebview.api.select_optimal(false);
        if (result.error) {
          this.optimalResult = 'Error: ' + result.error;
          this.showToast('Optimal switch failed', 'error');
        } else {
          const name = result.account.nickname || result.account.email;
          this.optimalResult = `Switched to ${name} (headroom: ${result.headroom?.toFixed(1)}%, drain: ${result.adjusted_drain?.toFixed(2)} %/h)`;
          this.currentAccount = result.account;
          this.showToast('Switched to ' + name, 'success');
          await this.loadAccounts();
        }
      } finally {
        this.loading = false;
      }
    },

    async loginOAuth() {
      if (this.loading) return;
      this.loading = true;
      try {
        const result = await window.pywebview.api.login_oauth(null);
        if (result.error) {
          this.showToast('Login failed: ' + result.error, 'error');
        } else {
          const action = result.is_new ? 'added' : 'updated';
          this.showToast(`Account ${action}: ${result.account.email}`, 'success');
        }
      } finally {
        // Must set loading=false BEFORE calling refreshAll() to avoid the guard
        this.loading = false;
      }
      await Promise.all([this.loadAccounts(), this.loadCurrentAccount()]);
    },

    async forceRefresh(acc) {
      const id = acc.uuid;
      this.refreshingIds = new Set([...this.refreshingIds, id]);
      try {
        const result = await window.pywebview.api.force_refresh_account(String(acc.index));
        if (result.error) {
          this.showToast('Refresh failed: ' + result.error, 'error');
        } else {
          this.showToast('Token refreshed for ' + (acc.nickname || acc.email), 'success');
          await this.loadAccounts();
        }
      } finally {
        const next = new Set(this.refreshingIds);
        next.delete(id);
        this.refreshingIds = next;
      }
    },

    showAccountDetails(acc) {
      this.detailAccount = acc;
    },

    // Helpers
    getUsageBars(acc) {
      if (!acc || !acc.usage) return [];
      const bars = [];
      const windows = [
        { key: 'five_hour', label: '5h Window' },
        { key: 'seven_day', label: '7d Window' },
        { key: 'seven_day_sonnet', label: 'Sonnet 7d' },
      ];

      for (const w of windows) {
        const data = acc.usage[w.key];
        if (!data) continue;
        const val = data.utilization != null ? Math.round(data.utilization) : 0;
        bars.push({
          label: w.label,
          value: val,
          colorClass: this.usageColorClass(val),
          barClass: this.usageBarClass(val),
        });
      }
      return bars;
    },

    usageColorClass(val) {
      if (val >= 90) return 'text-red-600';
      if (val >= 70) return 'text-amber-600';
      if (val >= 40) return 'text-yellow-600';
      return 'text-emerald-600';
    },

    usageBarClass(val) {
      if (val >= 90) return 'bg-gradient-to-r from-red-500 to-red-400';
      if (val >= 70) return 'bg-gradient-to-r from-amber-500 to-amber-400';
      if (val >= 40) return 'bg-gradient-to-r from-yellow-500 to-yellow-400';
      return 'bg-gradient-to-r from-emerald-500 to-emerald-400';
    },

    formatTime(iso) {
      if (!iso) return '-';
      try {
        const d = new Date(iso);
        const now = new Date();
        const diffMs = now - d;
        const diffMin = Math.floor(diffMs / 60000);
        if (diffMin < 1) return 'just now';
        if (diffMin < 60) return diffMin + 'm ago';
        const diffHr = Math.floor(diffMin / 60);
        if (diffHr < 24) return diffHr + 'h ago';
        return d.toLocaleDateString();
      } catch {
        return iso;
      }
    },
  };
}
