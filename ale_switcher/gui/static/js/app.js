/**
 * AleSwitcher GUI - Alpine.js application
 */
function app() {
  return {
    // State
    page: 'dashboard',
    ready: false,
    loading: false,
    accounts: [],
    currentAccount: null,
    sessions: [],
    sessionHistory: [],
    optimalResult: null,
    refreshInterval: null,
    searchQuery: '',
    switchingId: null,
    refreshingIds: new Set(),
    detailAccount: null,
    showAddModal: false,
    addNickname: '',
    addingAccount: false,
    toast: { show: false, message: '', type: 'info' },

    // Navigation with icons
    navItems: [
      {
        id: 'dashboard', label: 'Dashboard',
        icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/></svg>',
      },
      {
        id: 'accounts', label: 'Accounts',
        icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z"/></svg>',
      },
      {
        id: 'sessions', label: 'Sessions',
        icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z"/></svg>',
      },
      {
        id: 'settings', label: 'Settings',
        icon: '<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
      },
    ],

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
          this.loadSessions(),
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

    async loadSessions() {
      try {
        if (window.pywebview.api.get_sessions) {
          const data = await window.pywebview.api.get_sessions();
          if (Array.isArray(data)) {
            this.sessions = data;
          } else if (data?.active) {
            this.sessions = data.active || [];
            this.sessionHistory = data.history || [];
          }
        }
      } catch (e) {
        console.error('Failed to load sessions:', e);
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
      this.loading = true;
      try {
        const result = await window.pywebview.api.login_oauth(null);
        if (result.error) {
          this.showToast('Login failed: ' + result.error, 'error');
        } else {
          const action = result.is_new ? 'added' : 'updated';
          this.showToast(`Account ${action}: ${result.account.email}`, 'success');
          await this.refreshAll();
        }
      } finally {
        this.loading = false;
      }
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

    formatDuration(seconds) {
      if (!seconds) return '-';
      if (seconds < 60) return seconds + 's';
      if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      return h + 'h ' + m + 'm';
    },
  };
}
