import { useEffect, useRef, useState } from 'react';
import { ChevronRight, LoaderCircle, Search } from 'lucide-react';
import { postJSON } from '../api';
import { PageHeader, ErrorNotice, StatusIcon, Tag } from './ui';
import { TONE_BY_BADGE } from '../tones';

const SAMPLES = [
  {
    label: 'Fake IT password reset',
    subject: 'URGENT: Mandatory Password Verification Required',
    sender: 'Acme Support Desk <security-verify@acme-support-portal.top>',
    headers: '',
    body: 'Dear Employee,\n\nYour account password will expire in 2 hours due to unauthorized activity detected on your workstation.\n\nPlease click below immediately to verify your credentials and avoid account suspension:\n\nhttp://192.168.1.45/verify-account\n\nFailure to respond within 24 hours will result in immediate termination of IT system access.\n\nRegards,\nAcme IT Global Security',
  },
  {
    label: 'Spoofed PayPal notice',
    subject: 'Your account has been limited',
    sender: 'PayPal <service@paypa1-resolution.com>',
    headers: 'Reply-To: resolution-team@mail-desk.ru\nAuthentication-Results: mx.acme.com; spf=softfail; dkim=fail; dmarc=fail',
    body: 'Hello,\n\nWe noticed suspicious activity on your PayPal account and have temporarily limited it.\n\nTo restore full access, confirm your identity here:\n\n<a href="http://paypa1-resolution.com/secure/login">https://www.paypal.com/myaccount</a>\n\nIf you do not complete this within 24 hours your account will be permanently suspended.\n\nPayPal Security',
  },
  {
    label: 'Normal company email',
    subject: 'Quarterly town hall: schedule and agenda',
    sender: 'Internal Communications <communications@acme.com>',
    headers: '',
    body: 'Hi everyone,\n\nPlease join us this Thursday at 2:00 PM for our quarterly town hall.\n\nWe will review team achievements, Q3 results and preview next quarter\u2019s roadmap.\n\nThe agenda is on the intranet: https://intranet.acme.com/events/townhall\n\nBest regards,\nCorporate Communications',
  },
];

const SEVERITY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3 };
const SEVERITY_TONE = { Critical: 'bad', High: 'bad', Medium: 'warn', Low: 'info' };

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function Highlighted({ text, terms }) {
  if (!terms.length) return text;
  const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'gi');
  const lower = new Set(terms.map((t) => t.toLowerCase()));
  return text.split(pattern).map((part, i) => (lower.has(part.toLowerCase()) ? <mark key={i}>{part}</mark> : part));
}

function UrlWithHost({ url }) {
  const match = url.match(/^(https?:\/\/)?([^/:?#]+)(.*)$/i);
  if (!match) return url;
  return (
    <>
      {match[1]}
      <b>{match[2]}</b>
      {match[3]}
    </>
  );
}

export default function PhishingChecker() {
  const [sender, setSender] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [headers, setHeaders] = useState('');
  const [showHeaders, setShowHeaders] = useState(false);
  const [result, setResult] = useState(null);
  const [analyzed, setAnalyzed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const resultsRef = useRef(null);

  useEffect(() => {
    if (result) resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [result]);

  const canSubmit = (body.trim() || subject.trim()) && !loading;

  const analyze = async (e) => {
    e?.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError('');
    try {
      const data = await postJSON('/api/phishing/check', { email_body: body, subject, sender, headers });
      setResult(data);
      setAnalyzed({ subject, body });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (s) => {
    setSender(s.sender);
    setSubject(s.subject);
    setBody(s.body);
    setHeaders(s.headers);
    setShowHeaders(Boolean(s.headers));
    setResult(null);
    setError('');
  };

  const clear = () => {
    loadSample({ sender: '', subject: '', body: '', headers: '' });
  };

  const tone = result ? TONE_BY_BADGE[result.badge_color] : 'muted';
  const flags = result ? [...result.red_flags].sort((a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity]) : [];

  return (
    <div className="page">
      <PageHeader eyebrow="Check something" title="Email check">
        Paste an email you're unsure about. It's checked for impersonated senders, links that lead somewhere other than
        they claim, risky attachments and pressure tactics.
      </PageHeader>

      <form className="panel" onSubmit={analyze}>
        <div className="chips" style={{ marginBottom: 18 }}>
          <span className="chips-label">Try an example:</span>
          {SAMPLES.map((s) => (
            <button key={s.label} type="button" className="chip" onClick={() => loadSample(s)}>
              {s.label}
            </button>
          ))}
        </div>

        <div className="split" style={{ marginTop: 0 }}>
          <label className="field">
            <span className="field-label">From</span>
            <input
              className="input"
              placeholder="Name <address@example.com>"
              value={sender}
              onChange={(e) => setSender(e.target.value)}
            />
          </label>
          <label className="field" style={{ marginTop: 0 }}>
            <span className="field-label">Subject</span>
            <input className="input" value={subject} onChange={(e) => setSubject(e.target.value)} />
          </label>
        </div>

        <label className="field" style={{ marginTop: 14 }}>
          <span className="field-label">Message</span>
          <textarea
            className="textarea"
            rows={8}
            placeholder="Paste the email text here. HTML is fine, links inside it will be inspected."
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </label>

        <details className="more" open={showHeaders} onToggle={(e) => setShowHeaders(e.currentTarget.open)}>
          <summary>
            <ChevronRight size={15} /> Raw headers <span className="field-hint">(optional, enables SPF/DKIM/Reply-To checks)</span>
          </summary>
          <div>
            <textarea
              className="textarea mono"
              placeholder={'Reply-To: ...\nAuthentication-Results: spf=pass; dkim=pass; dmarc=pass'}
              value={headers}
              onChange={(e) => setHeaders(e.target.value)}
            />
          </div>
        </details>

        <div className="row" style={{ justifyContent: 'flex-end', marginTop: 18 }}>
          {(sender || subject || body || headers) && (
            <button type="button" className="btn btn-ghost" onClick={clear}>
              Clear
            </button>
          )}
          <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
            {loading ? <LoaderCircle size={16} className="spin" /> : <Search size={16} />}
            {loading ? 'Checking…' : 'Check email'}
          </button>
        </div>

        <ErrorNotice message={error} />
      </form>

      {result && (
        <>
          <section className="panel" style={{ marginTop: 16, scrollMarginTop: 16 }} ref={resultsRef}>
            <div className="verdict">
              <div className={`verdict-score tone-${tone}`}>
                {result.score}
                <small>/100</small>
              </div>
              <div>
                <div className={`verdict-label tone-${tone}`}>{result.risk_level}</div>
                <p className="muted small">
                  {result.red_flags_count === 0
                    ? 'No warning signs found.'
                    : `${result.red_flags_count} warning sign${result.red_flags_count > 1 ? 's' : ''} found.`}{' '}
                  Higher scores mean more phishing indicators.
                </p>
              </div>
            </div>
            <div className="bar">
              <span style={{ width: `${Math.max(2, result.score)}%`, background: `var(--${tone})` }} />
            </div>
          </section>

          <div className="split">
            <section className="panel">
              <h2 className="panel-title">Warning signs</h2>
              {flags.length === 0 ? (
                <p className="muted small">Nothing suspicious was detected.</p>
              ) : (
                <ul className="findings">
                  {flags.map((f, i) => (
                    <li key={i}>
                      <StatusIcon tone={SEVERITY_TONE[f.severity]} />
                      <div>
                        <h4>
                          {f.category} <Tag tone={SEVERITY_TONE[f.severity]}>{f.severity}</Tag>
                        </h4>
                        <p>{f.detail}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <div>
              <section className="panel">
                <h2 className="panel-title">What to do</h2>
                <ul className="bullets">
                  {result.recommendations.map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
              </section>

              <section className="panel">
                <h2 className="panel-title">
                  Links found <span className="muted small">{result.detected_urls.length}</span>
                </h2>
                {result.detected_urls.length === 0 ? (
                  <p className="muted small">No links in the message.</p>
                ) : (
                  <ul className="url-list">
                    {result.detected_urls.map((u) => (
                      <li key={u}>
                        <UrlWithHost url={u} />
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>
          </div>

          {analyzed && result.highlighted_keywords.length > 0 && (
            <section className="panel" style={{ marginTop: 16 }}>
              <h2 className="panel-title">Pressure phrases in the message</h2>
              <div className="preview">
                {analyzed.subject && (
                  <>
                    <strong>
                      <Highlighted text={analyzed.subject} terms={result.highlighted_keywords} />
                    </strong>
                    {'\n\n'}
                  </>
                )}
                <Highlighted text={analyzed.body} terms={result.highlighted_keywords} />
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
