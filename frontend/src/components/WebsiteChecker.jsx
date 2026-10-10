import { useEffect, useRef, useState } from 'react';
import { LoaderCircle, Search } from 'lucide-react';
import { postJSON } from '../api';
import { PageHeader, ErrorNotice, StatusIcon } from './ui';
import { TONE_BY_BADGE } from '../tones';

const SAMPLES = [
  { label: 'github.com', url: 'github.com' },
  { label: 'Expired certificate', url: 'expired.badssl.com' },
  { label: 'HTTP only', url: 'http://http.badssl.com' },
];

const STATUS_TONE = { PASS: 'good', WARN: 'warn', FAIL: 'bad', INFO: 'muted' };

export default function WebsiteChecker() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const resultsRef = useRef(null);

  useEffect(() => {
    if (result) resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [result]);

  const check = async (target) => {
    const value = (target ?? url).trim();
    if (!value || loading) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      setResult(await postJSON('/api/website/check', { url: value }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const tone = result ? TONE_BY_BADGE[result.badge_color] : 'muted';
  const ssl = result?.ssl_info;
  const failures = result ? result.security_checks.filter((c) => c.status === 'FAIL').length : 0;
  const warnings = result ? result.security_checks.filter((c) => c.status === 'WARN').length : 0;

  return (
    <div className="page">
      <PageHeader eyebrow="Check something" title="Website check">
        Enter a website to inspect its certificate, whether it forces HTTPS, and which browser security protections it
        turns on. A good grade means the site is set up carefully, not that its owner can be trusted.
      </PageHeader>

      <section className="panel">
        <form
          className="inline-form"
          onSubmit={(e) => {
            e.preventDefault();
            check();
          }}
        >
          <input
            className="input"
            placeholder="example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            aria-label="Website address"
            autoComplete="url"
            spellCheck={false}
            inputMode="url"
          />
          <button type="submit" className="btn btn-primary" disabled={!url.trim() || loading}>
            {loading ? <LoaderCircle size={16} className="spin" /> : <Search size={16} />}
            {loading ? 'Checking…' : 'Check site'}
          </button>
        </form>

        <div className="chips" style={{ marginTop: 14 }}>
          <span className="chips-label">Try:</span>
          {SAMPLES.map((s) => (
            <button
              key={s.url}
              type="button"
              className="chip"
              disabled={loading}
              onClick={() => {
                setUrl(s.url);
                check(s.url);
              }}
            >
              {s.label}
            </button>
          ))}
        </div>

        <ErrorNotice message={error} />
      </section>

      {loading && (
        <div className="empty">
          <LoaderCircle size={18} className="spin" style={{ verticalAlign: -4, marginRight: 8 }} />
          Connecting to the site and reading its certificate. This can take a few seconds.
        </div>
      )}

      {result && (
        <>
          <section className="panel" style={{ marginTop: 16, scrollMarginTop: 16 }} ref={resultsRef}>
            <div className="verdict">
              <div className={`grade tone-${tone}`}>{result.grade}</div>
              <div style={{ minWidth: 0 }}>
                <div className="verdict-label" style={{ overflowWrap: 'anywhere' }}>
                  {result.hostname}
                </div>
                <p className="muted small">
                  {result.grade === '?'
                    ? "The site didn't respond, so this check is incomplete."
                    : failures + warnings === 0
                      ? 'Every check passed.'
                      : [failures && `${failures} failed`, warnings && `${warnings} warning${warnings > 1 ? 's' : ''}`]
                          .filter(Boolean)
                          .join(', ') + ` · score ${result.score}/100`}
                </p>
              </div>
            </div>

            <dl className="facts">
              <div className="fact">
                <dt>Final address</dt>
                <dd className="mono">{result.final_url}</dd>
              </div>
              <div className="fact">
                <dt>IP address</dt>
                <dd className="mono">{result.ip_addresses?.[0] ?? 'Unknown'}</dd>
              </div>
              {result.header_info?.server && (
                <div className="fact">
                  <dt>Server</dt>
                  <dd>{result.header_info.server}</dd>
                </div>
              )}
            </dl>
          </section>

          <div className="split">
            <section className="panel">
              <h2 className="panel-title">Checks</h2>
              <ul className="findings">
                {result.security_checks.map((c) => (
                  <li key={c.name}>
                    <StatusIcon tone={STATUS_TONE[c.status]} />
                    <div>
                      <h4>{c.name}</h4>
                      <p>{c.detail}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            <div>
              <section className="panel">
                <h2 className="panel-title">Certificate</h2>
                {ssl?.valid ? (
                  <dl className="facts" style={{ marginTop: 0 }}>
                    <div className="fact">
                      <dt>Issued by</dt>
                      <dd>{ssl.issuer}</dd>
                    </div>
                    <div className="fact">
                      <dt>Expires</dt>
                      <dd className={ssl.days_remaining < 30 ? 'tone-warn' : undefined}>
                        {ssl.valid_until} ({ssl.days_remaining} days)
                      </dd>
                    </div>
                    <div className="fact">
                      <dt>Protocol</dt>
                      <dd>{ssl.version}</dd>
                    </div>
                    <div className="fact">
                      <dt>Covers</dt>
                      <dd>
                        {ssl.san_sample.slice(0, 3).join(', ')}
                        {ssl.san_count > 3 ? ` +${ssl.san_count - 3} more` : ''}
                      </dd>
                    </div>
                  </dl>
                ) : (
                  <div className="notice tone-bad" style={{ marginTop: 0 }}>
                    <StatusIcon tone="bad" />
                    <div>
                      <strong>No trusted certificate</strong>
                      <p>{ssl?.error || 'The site could not be reached over HTTPS.'}</p>
                    </div>
                  </div>
                )}
              </section>

              {result.risk_factors.length > 0 && (
                <section className="panel">
                  <h2 className="panel-title">Why this matters</h2>
                  <ul className="bullets">
                    {result.risk_factors.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                </section>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
