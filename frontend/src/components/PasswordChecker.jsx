import { useEffect, useRef, useState } from 'react';
import { Eye, EyeOff, Copy, Check, RefreshCw, LoaderCircle, Lock } from 'lucide-react';
import { postJSON } from '../api';
import { PageHeader, ErrorNotice, StatusIcon, Tag } from './ui';
import { TONE_BY_BADGE } from '../tones';

const CHARSETS = [
  'abcdefghijkmnopqrstuvwxyz',
  'ABCDEFGHJKLMNPQRSTUVWXYZ',
  '23456789',
  '!@#$%^&*-_=+?',
];

function randomIndex(max) {
  // Rejection sampling avoids modulo bias.
  const limit = Math.floor(0x100000000 / max) * max;
  const buf = new Uint32Array(1);
  do {
    crypto.getRandomValues(buf);
  } while (buf[0] >= limit);
  return buf[0] % max;
}

function generatePassword(length = 20) {
  const all = CHARSETS.join('');
  const chars = CHARSETS.map((set) => set[randomIndex(set.length)]);
  while (chars.length < length) chars.push(all[randomIndex(all.length)]);
  for (let i = chars.length - 1; i > 0; i--) {
    const j = randomIndex(i + 1);
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.join('');
}

const TONE_COLORS = { good: 'var(--good)', info: 'var(--info)', warn: 'var(--warn)', bad: 'var(--bad)' };

export default function PasswordChecker() {
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const inputRef = useRef(null);

  const updatePassword = (value) => {
    setPassword(value);
    setCopied(false);
    setLoading(Boolean(value));
    if (!value) {
      setResult(null);
      setError('');
    }
  };

  useEffect(() => {
    if (!password) return;

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const data = await postJSON('/api/password/check', { password }, { signal: controller.signal });
        setResult(data);
        setError('');
      } catch (err) {
        if (err.name === 'AbortError') return;
        setError(err.message);
        setResult(null);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 350);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [password]);

  const handleGenerate = () => {
    updatePassword(generatePassword());
    setVisible(true);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(password);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      inputRef.current?.select();
    }
  };

  const tone = result ? TONE_BY_BADGE[result.badge_color] : 'muted';
  const filled = result ? Math.max(1, Math.ceil(result.score / 20)) : 0;
  const breach = result?.breach_status;

  return (
    <div className="page">
      <PageHeader eyebrow="Check something" title="Password check">
        See roughly how long a password would survive a cracking attempt, and whether it already appears in known data
        breaches.
      </PageHeader>

      <section className="panel">
        <label className="field-label" htmlFor="pw">
          Password
        </label>
        <div className="input-wrap">
          <input
            id="pw"
            ref={inputRef}
            type={visible ? 'text' : 'password'}
            className="input mono"
            placeholder="Type or paste a password"
            value={password}
            onChange={(e) => updatePassword(e.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
          <div className="input-actions">
            {password && (
              <button type="button" className="icon-btn" onClick={handleCopy} aria-label="Copy password" title="Copy">
                {copied ? <Check size={16} className="tone-good" /> : <Copy size={16} />}
              </button>
            )}
            <button
              type="button"
              className="icon-btn"
              onClick={() => setVisible((v) => !v)}
              aria-label={visible ? 'Hide password' : 'Show password'}
              title={visible ? 'Hide' : 'Show'}
            >
              {visible ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div className="row-between" style={{ marginTop: 12 }}>
          <p className="muted small" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <Lock size={13} /> Only a partial hash is sent to the breach database, never the password itself.
          </p>
          <button type="button" className="btn btn-secondary" onClick={handleGenerate}>
            <RefreshCw size={15} /> Generate a strong one
          </button>
        </div>

        <ErrorNotice message={error} />
      </section>

      {!password && !result && (
        <div className="empty">Results appear here as you type.</div>
      )}

      {result && (
        <div style={{ opacity: loading ? 0.6 : 1, transition: 'opacity 0.15s' }}>
          <section className="panel" style={{ marginTop: 16 }}>
            <div className="row-between">
              <div>
                <div className="muted small">Strength</div>
                <div className="verdict-label" style={{ color: TONE_COLORS[tone] }}>
                  {result.rating}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="muted small">Time to crack</div>
                <div className="verdict-label">{result.crack_time}</div>
              </div>
            </div>
            <div className="meter" aria-label={`Strength score ${result.score} out of 100`}>
              {[0, 1, 2, 3, 4].map((i) => (
                <span key={i} style={i < filled ? { background: TONE_COLORS[tone] } : undefined} />
              ))}
            </div>
            <dl className="facts">
              <div className="fact">
                <dt>Score</dt>
                <dd>{result.score} / 100</dd>
              </div>
              <div className="fact">
                <dt>Length</dt>
                <dd>{result.password_length} characters</dd>
              </div>
              <div className="fact">
                <dt>Entropy</dt>
                <dd>{result.entropy_bits} bits</dd>
              </div>
            </dl>
            <p className="muted small" style={{ marginTop: 10 }}>
              Crack time assumes an offline attack at 100 billion guesses per second. Common words and patterns fall much
              faster.
            </p>

            {breach && (
              <div className={`notice tone-${breach.is_breached ? 'bad' : breach.checked ? 'good' : 'warn'}`}>
                <StatusIcon tone={breach.is_breached ? 'bad' : breach.checked ? 'good' : 'warn'} />
                <div>
                  <strong>
                    {breach.is_breached
                      ? breach.count
                        ? `Seen ${breach.count.toLocaleString()} times in data breaches`
                        : 'This is a well-known leaked password'
                      : breach.checked
                        ? 'Not found in known breaches'
                        : "Couldn't check breach database"}
                  </strong>
                  <p>
                    {breach.is_breached
                      ? 'Attackers try these first. Don\u2019t use it for any account.'
                      : breach.checked
                        ? 'Checked against Have I Been Pwned. That doesn\u2019t guarantee it\u2019s safe, only that it hasn\u2019t leaked publicly.'
                        : 'Have I Been Pwned is unreachable right now, so only the strength rules above were applied.'}
                  </p>
                </div>
              </div>
            )}
          </section>

          <div className="split">
            <section className="panel">
              <h2 className="panel-title">Requirements</h2>
              <ul className="checklist">
                <CheckItem pass={result.checks.sufficient_length} label="At least 12 characters" />
                <CheckItem pass={result.checks.has_lowercase} label="Lowercase letters" />
                <CheckItem pass={result.checks.has_uppercase} label="Uppercase letters" />
                <CheckItem pass={result.checks.has_digits} label="Numbers" />
                <CheckItem pass={result.checks.has_symbols} label="Symbols" />
              </ul>
            </section>

            <section className="panel">
              <h2 className="panel-title">
                What to improve
                {result.warnings.length > 0 && <Tag tone="bad">{result.warnings.length} issue{result.warnings.length > 1 ? 's' : ''}</Tag>}
              </h2>
              {result.warnings.length === 0 && result.suggestions.length === 0 ? (
                <p className="muted small">Nothing to fix. Store it in a password manager and don't reuse it.</p>
              ) : (
                <ul className="bullets">
                  {result.warnings.map((w) => (
                    <li key={w} className="tone-bad">
                      {w}
                    </li>
                  ))}
                  {result.suggestions.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </div>
      )}

      {loading && !result && (
        <div className="empty">
          <LoaderCircle size={18} className="spin" style={{ verticalAlign: -4, marginRight: 8 }} />
          Checking…
        </div>
      )}
    </div>
  );
}

function CheckItem({ pass, label }) {
  return (
    <li className={pass ? '' : 'off'}>
      <StatusIcon tone={pass ? 'good' : 'muted'} size={16} />
      {label}
    </li>
  );
}
