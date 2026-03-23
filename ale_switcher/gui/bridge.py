"""Python-JS bridge API exposed to pywebview frontend."""

from __future__ import annotations

import json
import traceback
import webbrowser
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..infrastructure.factory import ServiceFactory
from ..infrastructure.oauth import OAuthClient


class Api:
    """Bridge between JS frontend and Python services.

    Methods are auto-exposed to window.pywebview.api.* in the webview.
    All methods return JSON-serializable dicts/lists.
    Errors are returned as {"error": "message"} instead of raising.
    """

    def __init__(self, factory: ServiceFactory):
        self._factory = factory

    def get_accounts(self) -> List[Dict[str, Any]]:
        try:
            accounts = self._factory.get_account_service().list_accounts()
            return [self._account_to_dict(a) for a in accounts]
        except Exception as e:
            return {'error': str(e)}

    def get_usage(self, force: bool = False) -> List[Dict[str, Any]]:
        try:
            store = self._factory.get_store()
            accounts = store.list_accounts()
            results = []

            for account in accounts:
                usage_data = self._fetch_account_usage(account, force)
                results.append(usage_data)

            return results
        except Exception as e:
            return {'error': str(e)}

    def switch_account(self, identifier: str) -> Dict[str, Any]:
        try:
            switching = self._factory.get_switching_service()
            account = switching.switch_to(identifier)
            return {'success': True, 'account': self._account_to_dict(account)}
        except Exception as e:
            traceback.print_exc()
            return {'error': f'{type(e).__name__}: {e}'}

    def get_oauth_token(self, identifier: str) -> Dict[str, Any]:
        """Get OAuth token for account (for macOS env var mode)."""
        try:
            switching = self._factory.get_switching_service()
            account = switching.switch_to(identifier, token_only=True)
            creds = account.get_credentials()
            token = creds.get('claudeAiOauth', {}).get('accessToken', '')
            label = account.nickname or account.display_name or account.email
            return {
                'success': True,
                'account': self._account_to_dict(account),
                'token': token,
                'label': label,
            }
        except Exception as e:
            traceback.print_exc()
            return {'error': f'{type(e).__name__}: {e}'}

    def select_optimal(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            switching = self._factory.get_switching_service()
            decision = switching.select_optimal(dry_run=dry_run)
            return {
                'success': True,
                'account': self._account_to_dict(decision.account),
                'tier': decision.tier,
                'window': decision.window,
                'headroom': decision.headroom,
                'hours_to_reset': decision.hours_to_reset,
                'drain_rate': decision.drain_rate,
                'adjusted_drain': decision.adjusted_drain,
                'five_hour_utilization': decision.five_hour_utilization,
                'sonnet_usage': decision.sonnet_usage,
                'overall_usage': decision.overall_usage,
                'reused': decision.reused,
            }
        except Exception as e:
            return {'error': str(e)}

    def get_current_account(self) -> Dict[str, Any]:
        try:
            from ..constants import CREDENTIALS_PATH

            if not CREDENTIALS_PATH.exists():
                return {'error': 'No active credentials file'}

            creds_text = CREDENTIALS_PATH.read_text(encoding='utf-8')
            creds = json.loads(creds_text)
            token = creds.get('claudeAiOauth', {}).get('accessToken', '')

            accounts = self._factory.get_account_service().list_accounts()
            for acc in accounts:
                acc_creds = acc.get_credentials()
                acc_token = acc_creds.get('claudeAiOauth', {}).get('accessToken', '')
                if acc_token and acc_token == token:
                    return self._account_to_dict(acc)

                if acc.api_key and acc.api_key == token:
                    return self._account_to_dict(acc)

            # Auto-import: credentials file exists but no matching account registered
            if token:
                try:
                    account_service = self._factory.get_account_service()
                    account, _ = account_service.add_account(creds_text)
                    return self._account_to_dict(account)
                except Exception:
                    pass

            return {'error': 'Active account not found in registered accounts'}
        except Exception as e:
            return {'error': str(e)}

    def login_oauth(self, nickname: Optional[str] = None) -> Dict[str, Any]:
        try:
            client = OAuthClient()
            credentials = client.login(auto_open=True, use_dual_flow=True)

            creds_json = json.dumps(credentials)
            account_service = self._factory.get_account_service()
            account, is_new = account_service.add_account(creds_json, nickname=nickname)

            return {
                'success': True,
                'account': self._account_to_dict(account),
                'is_new': is_new,
            }
        except Exception as e:
            return {'error': str(e)}

    def get_sessions(self) -> List[Dict[str, Any]]:
        try:
            session_service = self._factory.get_session_service()
            session_service.maybe_cleanup()
            sessions = session_service.list_active()
            store = self._factory.get_store()

            results = []
            for s in sessions:
                account = store.get_account_by_uuid(s.account_uuid) if s.account_uuid else None
                results.append({
                    'session_id': s.session_id,
                    'pid': s.pid,
                    'cwd': s.cwd,
                    'created_at': s.created_at,
                    'account_email': account.email if account else None,
                    'account_nickname': account.nickname if account else None,
                })

            return results
        except Exception as e:
            return {'error': str(e)}

    def get_session_history(self, limit: int = 30) -> List[Dict[str, Any]]:
        try:
            store = self._factory.get_store()
            sessions = store.get_session_history(min_duration_seconds=5, limit=limit)

            results = []
            for s in sessions:
                account = store.get_account_by_uuid(s.account_uuid) if s.account_uuid else None
                results.append({
                    'session_id': s.session_id,
                    'pid': s.pid,
                    'cwd': s.cwd,
                    'created_at': s.created_at,
                    'ended_at': s.ended_at,
                    'duration_seconds': s.duration_seconds(),
                    'account_email': account.email if account else None,
                    'account_nickname': account.nickname if account else None,
                })

            return results
        except Exception as e:
            return {'error': str(e)}

    def force_refresh_account(self, identifier: str) -> Dict[str, Any]:
        try:
            store = self._factory.get_store()
            cred_store = self._factory.get_credential_store()
            account = store.get_account_by_identifier(identifier)

            if not account:
                return {'error': f'Account not found: {identifier}'}

            refreshed = cred_store.refresh_access_token(account.credentials_json, force=True)
            if refreshed != account.get_credentials():
                store.update_credentials(account.uuid, refreshed)

            return {'success': True, 'account': self._account_to_dict(account)}
        except Exception as e:
            return {'error': str(e)}

    def _fetch_account_usage(self, account, force: bool = False) -> Dict[str, Any]:
        try:
            result = self._account_to_dict(account)
        except Exception as e:
            return {'uuid': getattr(account, 'uuid', '?'), 'usage_error': f'dict error: {e}'}

        try:
            store = self._factory.get_store()

            if not force:
                cached = store.get_recent_usage(account.uuid)
                if cached:
                    result['usage'] = self._usage_to_dict(cached)
                    return result

            from ..infrastructure.api import ClaudeAPI

            cred_store = self._factory.get_credential_store()
            refreshed = cred_store.refresh_access_token(account.credentials_json)
            token = refreshed.get('claudeAiOauth', {}).get('accessToken')

            if token:
                usage_data = ClaudeAPI.get_usage(token)
                usage_data['_cache_source'] = 'live'
                usage_data['_cache_age_seconds'] = 0.0
                usage_data['_queried_at'] = datetime.now(timezone.utc).isoformat()

                usage_to_store = {k: v for k, v in usage_data.items() if not k.startswith('_')}
                store.save_usage(account.uuid, usage_to_store)

                from ..core.models import UsageSnapshot

                snapshot = UsageSnapshot.from_api_response(account.uuid, usage_data, source='live')
                result['usage'] = self._usage_to_dict(snapshot)
        except Exception as e:
            result['usage_error'] = str(e)

        return result

    @staticmethod
    def _account_to_dict(account) -> Dict[str, Any]:
        return {
            'uuid': account.uuid,
            'index': account.index_num,
            'email': account.email,
            'nickname': account.nickname,
            'display_name': account.display_name,
            'full_name': account.full_name,
            'has_claude_max': account.has_claude_max,
            'has_claude_pro': account.has_claude_pro,
            'org_uuid': account.org_uuid,
            'org_name': account.org_name,
            'org_type': account.org_type,
            'rate_limit_tier': account.rate_limit_tier,
        }

    @staticmethod
    def _usage_to_dict(snapshot) -> Dict[str, Any]:
        def window_dict(w):
            return {
                'utilization': w.utilization,
                'resets_at': w.resets_at,
                'hours_until_reset': w.hours_until_reset(),
            }

        return {
            'five_hour': window_dict(snapshot.five_hour),
            'seven_day': window_dict(snapshot.seven_day),
            'seven_day_opus': window_dict(snapshot.seven_day_opus),
            'seven_day_sonnet': window_dict(snapshot.seven_day_sonnet),
            'cache_source': snapshot.cache_source,
            'cache_age_seconds': snapshot.cache_age_seconds,
            'queried_at': snapshot.queried_at,
        }
