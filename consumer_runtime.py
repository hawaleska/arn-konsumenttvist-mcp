"""Explicit ARN-only local integration; no secrets or legal text defaults."""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from cryptography import x509

from consumer_flow import ConsumerFlow, register_integrated_routes
from consumer_confirmation_gate import receipt_accepted
from disclosure_policy import policy_from_environment


def configure_consumer(server, *, license_database, base_url, plan_ids, paypal_environment=None):
    config_path = os.getenv('ARN_CONSUMER_CONFIG')
    if not config_path:
        return None
    try:
        config = json.loads(Path(config_path).read_text(encoding='utf-8'))
        if config.get('publication_approved') is not True:
            return None
        if paypal_environment not in {'live', 'sandbox'}:
            raise ValueError()
        root = Path(license_database).resolve().parent
        receipt_directory = Path(config['receipt_directory'])
        receipt_owner_uid = config['receipt_owner_uid']
        if (not receipt_directory.is_absolute() or type(receipt_owner_uid) is not int
                or receipt_owner_uid <= 0
                or os.name == 'posix' and receipt_owner_uid == os.geteuid()):
            raise ValueError()
        def verified_text(name):
            data = Path(config[name + '_file']).read_bytes()
            if hashlib.sha256(data).hexdigest() != config[name + '_sha256']:
                raise ValueError()
            return data.decode('utf-8')
        certificate = x509.load_pem_x509_certificate(Path(config['certificate_file']).read_bytes())
        secret_file = Path(config['secret_file'])
        if os.name == 'posix' and secret_file.stat().st_mode & 0o077:
            raise ValueError()
        secret = secret_file.read_bytes()
        def approval(user_id, subscription_id):
            with closing(sqlite3.connect(Path(license_database).resolve().as_uri() + '?mode=ro', uri=True)) as conn:
                row = conn.execute('SELECT approval_url FROM paypal_creation_intents '
                                   "WHERE user_id=? AND subscription_id=? AND state='registered'",
                                   (user_id, subscription_id)).fetchone()
                return row[0] if row else None
        from urllib.parse import urlsplit
        parsed = urlsplit(base_url)
        disclosure_policy=policy_from_environment(required=True)
        disclosure_policy.validate_available()
        flow = ConsumerFlow(approved=True, origin=parsed.scheme + '://' + parsed.netloc,
                            public_base_url=base_url, database=root/'consumer-data/requests.sqlite3',
                            certificate=certificate, certificate_sha256=config['certificate_sha256'],
                            secret=secret, terms=verified_text('terms'), privacy=verified_text('privacy'),
                            withdrawal_instructions=verified_text('withdrawal'),
                            plan_ids=plan_ids, lookup_approval=approval,
                            acceptance_reader=lambda reference: receipt_accepted(
                                receipt_directory, receipt_owner_uid, reference),
                            disclosure_policy=disclosure_policy,
                            paypal_host='www.paypal.com' if paypal_environment == 'live' else 'www.sandbox.paypal.com')
        register_integrated_routes(server, flow)
        return flow
    except Exception:
        raise RuntimeError('Consumer configuration could not be verified') from None
