import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, LoaderCircle, RotateCcw, ShieldAlert, ShieldCheck } from 'lucide-react';
import { getJSON } from '../api';
import { loadAnswers, saveAnswers } from '../progress';
import { PageHeader, ErrorNotice, StatusIcon } from './ui';
import TrainingTabs from './TrainingTabs';

const LINK_PATTERN = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|(https?:\/\/[^\s)]+)/g;

function shuffle(items) {
  const shuffled = [...items];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

function MailBody({ text, onHoverLink, onClickLink }) {
  const parts = [];
  let last = 0;
  for (const match of text.matchAll(LINK_PATTERN)) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    const label = match[1] ?? match[3];
    const href = match[2] ?? match[3];
    parts.push(
      <button
        key={match.index}
        type="button"
        className="mail-link"
        onMouseEnter={() => onHoverLink(href)}
        onMouseLeave={() => onHoverLink(null)}
        onFocus={() => onHoverLink(href)}
        onBlur={() => onHoverLink(null)}
        onClick={onClickLink}
      >
        {label}
      </button>,
    );
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return <div className="mail-body">{parts}</div>;
}

export default function ScenariosQuiz() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [answers, setAnswers] = useState(loadAnswers);
  const [hoverUrl, setHoverUrl] = useState(null);
  const [clickNote, setClickNote] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getJSON('/api/scenarios')
      .then((data) => {
        const ordered = shuffle(data);
        setScenarios(ordered);
        const saved = loadAnswers();
        const firstOpen = ordered.find((s) => !saved[s.id]) ?? ordered[0];
        setSelectedId(firstOpen?.id ?? null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const select = (id) => {
    setSelectedId(id);
    setHoverUrl(null);
    setClickNote(false);
  };

  const scenario = scenarios.find((s) => s.id === selectedId);
  const answer = scenario ? answers[scenario.id] : null;
  const index = scenarios.findIndex((s) => s.id === selectedId);

  const stats = useMemo(() => {
    const done = scenarios.filter((s) => answers[s.id]);
    return { answered: done.length, correct: done.filter((s) => answers[s.id].correct).length };
  }, [scenarios, answers]);

  const choose = (choice) => {
    const correct = (choice === 'phish') === scenario.is_phishing;
    const next = { ...answers, [scenario.id]: { choice, correct } };
    setAnswers(next);
    saveAnswers(next);
  };

  const reset = () => {
    setAnswers({});
    saveAnswers({});
    select(scenarios[0]?.id ?? null);
  };

  const startNewRound = () => {
    let nextScenarios = shuffle(scenarios);
    if (nextScenarios.length > 1 && nextScenarios.every((s, i) => s.id === scenarios[i].id)) {
      nextScenarios = [...nextScenarios.slice(1), nextScenarios[0]];
    }
    setScenarios(nextScenarios);
    setAnswers({});
    saveAnswers({});
    select(nextScenarios[0]?.id ?? null);
  };

  const goNext = () => {
    const nextUnanswered = scenarios.slice(index + 1).find((s) => !answers[s.id]) ?? scenarios.find((s) => !answers[s.id]);
    const fallback = scenarios[(index + 1) % scenarios.length];
    select((nextUnanswered ?? fallback).id);
  };

  if (loading) {
    return (
      <div className="page">
        <div className="empty">
          <LoaderCircle size={18} className="spin" style={{ verticalAlign: -4, marginRight: 8 }} />
          Loading training emails…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <PageHeader eyebrow="Learn" title="Phishing training" />
        <ErrorNotice message={error} />
      </div>
    );
  }

  const allDone = scenarios.length > 0 && stats.answered === scenarios.length;

  return (
    <div className="page" style={{ maxWidth: 1080 }}>
      <PageHeader eyebrow="Learn" title="Phishing training">
        Read each email as if it landed in your inbox. Hover over links to see where they really go, then decide whether
        you'd trust it.
      </PageHeader>
      <TrainingTabs active="training" />

      <div className="training">
        <div>
          <div className="row-between" style={{ marginBottom: 10 }}>
            <span className="small">
              <strong>{stats.correct}</strong> <span className="muted">correct of {stats.answered} answered</span>
            </span>
            {stats.answered > 0 && (
              <button type="button" className="btn btn-ghost small" onClick={reset} style={{ padding: '4px 8px' }}>
                <RotateCcw size={14} /> Reset
              </button>
            )}
          </div>
          <ul className="scenario-list">
            {scenarios.map((s, i) => {
              const a = answers[s.id];
              return (
                <li key={s.id}>
                  <button
                    type="button"
                    className="scenario-btn"
                    aria-current={s.id === selectedId ? 'true' : undefined}
                    onClick={() => select(s.id)}
                  >
                    <StatusIcon tone={a ? (a.correct ? 'good' : 'bad') : 'muted'} size={15} />
                    <span>
                      <span style={{ display: 'block', fontWeight: 600 }}>Email {i + 1}</span>
                      <span className="muted">{a ? s.title : s.sender.split('<')[0].trim()}</span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {scenario && (
          <div>
            <article className="mail">
              <div className="mail-head">
                <div className="mail-subject">{scenario.subject}</div>
                <div>
                  <span className="k">From</span>
                  <span className="mono" style={{ fontSize: '0.82rem' }}>
                    {scenario.sender}
                  </span>
                </div>
                <div>
                  <span className="k">To</span>
                  <span className="muted">you@acme.com</span>
                </div>
              </div>
              <MailBody text={scenario.content} onHoverLink={setHoverUrl} onClickLink={() => setClickNote(true)} />
              <div className="mail-status" aria-live="polite">
                {hoverUrl
                  ? hoverUrl
                  : clickNote
                    ? 'Links are disabled in practice emails. Hover over them to see the real destination.'
                    : ' '}
              </div>
            </article>

            {!answer ? (
              <>
                <p className="small muted" style={{ marginTop: 16 }}>
                  Would you trust this email?
                </p>
                <div className="quiz-actions" style={{ marginTop: 8 }}>
                  <button type="button" className="btn btn-secondary" onClick={() => choose('legit')}>
                    <ShieldCheck size={17} /> Looks legitimate
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={() => choose('phish')}>
                    <ShieldAlert size={17} /> It's phishing
                  </button>
                </div>
              </>
            ) : (
              <section className="panel feedback">
                <div className={`feedback-head tone-${answer.correct ? 'good' : 'bad'}`}>
                  <StatusIcon tone={answer.correct ? 'good' : 'bad'} size={20} />
                  {answer.correct ? 'Correct' : 'Not quite'}
                  <span className="muted small" style={{ fontWeight: 400 }}>
                    This email is {scenario.is_phishing ? 'phishing' : 'legitimate'} ({scenario.category.toLowerCase()}).
                  </span>
                </div>

                <hr className="divider" />

                <h3 className="panel-title" style={{ marginBottom: 8 }}>
                  {scenario.is_phishing ? 'What gave it away' : 'Why it can be trusted'}
                </h3>
                <ul className="findings">
                  {(scenario.is_phishing ? scenario.red_flags : scenario.safe_signals).map((f) => (
                    <li key={f.title}>
                      <StatusIcon tone={scenario.is_phishing ? 'bad' : 'good'} />
                      <div>
                        <h4>{f.title}</h4>
                        <p>{f.explanation}</p>
                      </div>
                    </li>
                  ))}
                </ul>

                <div className="notice tone-info">
                  <StatusIcon tone="info" />
                  <p>{scenario.psychology_note}</p>
                </div>

                <div className="row-between" style={{ marginTop: 18 }}>
                  <span className="muted small">
                    {allDone ? `Finished: ${stats.correct} of ${scenarios.length} correct.` : `${scenarios.length - stats.answered} left`}
                  </span>
                  {allDone ? (
                    <button type="button" className="btn btn-secondary" onClick={startNewRound}>
                      <RotateCcw size={15} /> Try another round
                    </button>
                  ) : (
                    <button type="button" className="btn btn-primary" onClick={goNext}>
                      Next email <ArrowRight size={15} />
                    </button>
                  )}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
