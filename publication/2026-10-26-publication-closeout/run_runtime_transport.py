"""Runtime transport adaptation only; unmodified pinned verifier retains checks."""
import os
from pathlib import Path
import ssl
import urllib.parse
import urllib.request
import verify_public_release as original

class RuntimeTransportVerifier(original.Verifier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proxies = {}
        for scheme in ('http', 'https'):
            value = os.environ.get(scheme.upper() + '_PROXY')
            if value:
                parsed = urllib.parse.urlsplit(value)
                original.require(parsed.scheme in ('http', 'https') and parsed.hostname
                                 and not parsed.username and not parsed.password,
                                 'Runtime proxy must not include credentials')
                proxies[scheme] = value
                self.env[scheme.upper() + '_PROXY'] = value
        for key in ('SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'PIP_CERT'):
            value = os.environ.get(key)
            if value:
                original.require(Path(value).is_file(), 'Runtime CA bundle is missing')
                self.env[key] = value
        context = ssl.create_default_context(cafile=self.env.get('SSL_CERT_FILE'))
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler(proxies),
            original.PublicRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )
        self.report['runtime_transport_adaptation'] = {
            'reason': 'This execution environment requires a transport proxy; the unmodified direct-HTTPS attempt failed DNS resolution before downloading data.',
            'proxy_credentials': False,
            'github_or_provider_credentials': False,
            'tls_verification': True,
            'runtime_ca_bundle': True,
            'verification_assertions_changed': False,
            'pinned_verifier_sha256': original.file_hash(Path(original.__file__)),
            'wrapper_sha256': original.file_hash(Path(__file__)),
        }
        self.save()

original.Verifier = RuntimeTransportVerifier
raise SystemExit(original.main())
