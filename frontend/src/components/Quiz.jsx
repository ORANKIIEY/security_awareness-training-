import { useEffect, useState } from 'react';
import { ArrowRight, LoaderCircle, RotateCcw } from 'lucide-react';
import { getJSON } from '../api';
import { PageHeader, ErrorNotice, StatusIcon } from './ui';
import TrainingTabs from './TrainingTabs';

const BEST_KEY = 'spotcheck.quiz.best';
const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];
const QUESTION_COUNT = 10;

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function buildAttempt(questions) {
  return shuffle(questions).map((q) => ({
    ...q,
    choices: shuffle(q.options.map((text, i) => ({ text, correct: i === q.answer }))),
  }));
}

function loadBest() {
  try {
    return JSON.parse(localStorage.getItem(BEST_KEY));
  } catch {
    return null;
  }
}

function saveBest(best) {
  try {
    localStorage.setItem(BEST_KEY, JSON.stringify(best));
  } catch {
    // Storage unavailable; best score just won't persist.
  }
}

export default function Quiz() {
  const [attempt, setAttempt] = useState([]);
  const [phase, setPhase] = useState('intro');
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [results, setResults] = useState([]);
  const [best, setBest] = useState(loadBest);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const current = attempt[index];
  const answered = selected !== null;
  const isLast = index === attempt.length - 1;

  const start = async () => {
    setLoading(true);
    setError('');
    try {
      const questions = await getJSON(`/api/quiz?count=${QUESTION_COUNT}`);
      setAttempt(buildAttempt(questions));
      setIndex(0);
      setSelected(null);
      setResults([]);
      setPhase('question');
      window.scrollTo(0, 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const pick = (choiceIndex) => {
    if (answered) return;
    setSelected(choiceIndex);
    const choice = current.choices[choiceIndex];
    setResults((r) => [...r, { question: current, chosen: choice.text, correct: choice.correct }]);
  };

  const next = () => {
    if (!isLast) {
      setIndex((i) => i + 1);
      setSelected(null);
      return;
    }
    const score = results.filter((r) => r.correct).length;
    if (!best || score / results.length > best.score / best.total) {
      const record = { score, total: results.length };
      setBest(record);
      saveBest(record);
    }
    setPhase('results');
  };

  useEffect(() => {
    if (phase !== 'question') return;
    const onKey = (e) => {
      if (e.target.closest?.('input, textarea')) return;
      const n = Number(e.key);
      if (!answered && n >= 1 && n <= (current?.choices.length ?? 0)) pick(n - 1);
      else if (answered && e.key === 'Enter') next();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  const header = (
    <>
      <PageHeader eyebrow="Learn" title="Security quiz">
        Test what you know about passwords, phishing and safe browsing. Each answer comes with a short explanation.
      </PageHeader>
      <TrainingTabs active="quiz" />
    </>
  );

  if (phase === 'intro') {
    return (
      <div className="page">
        {header}
        <section className="panel quiz-intro">
          <h2>{QUESTION_COUNT} questions, new every time</h2>
          <p className="muted">
            Questions are generated fresh for each attempt, with different brands, links, passwords and attachments,
            so you can't just memorise the answers. Covers passwords, phishing, websites and everyday habits.
          </p>
          {best && (
            <p className="small" style={{ marginTop: 10 }}>
              Your best score: <strong>{best.score}/{best.total}</strong>
            </p>
          )}
          <button type="button" className="btn btn-primary" style={{ marginTop: 18 }} onClick={start} disabled={loading}>
            {loading ? <LoaderCircle size={16} className="spin" /> : null}
            {loading ? 'Generating questions…' : best ? 'Take a new quiz' : 'Start quiz'}
            {!loading && <ArrowRight size={16} />}
          </button>
          <ErrorNotice message={error} />
        </section>
      </div>
    );
  }

  if (phase === 'results') {
    const score = results.filter((r) => r.correct).length;
    const pct = Math.round((score / results.length) * 100);
    const missed = results.filter((r) => !r.correct);
    const byTopic = Object.entries(
      results.reduce((acc, r) => {
        const t = (acc[r.question.topic] ??= { right: 0, total: 0 });
        t.total += 1;
        if (r.correct) t.right += 1;
        return acc;
      }, {}),
    );
    const tone = pct >= 80 ? 'good' : pct >= 50 ? 'warn' : 'bad';
    const verdict =
      pct === 100
        ? 'Perfect score.'
        : pct >= 80
          ? 'Great work. You know how to spot most attacks.'
          : pct >= 50
            ? 'Not bad. Review the questions you missed below.'
            : 'Worth another go. The explanations below cover what you missed.';

    return (
      <div className="page">
        {header}
        <section className="panel">
          <div className="verdict">
            <div className={`verdict-score tone-${tone}`}>
              {score}
              <small>/{results.length}</small>
            </div>
            <div>
              <div className="verdict-label">{verdict}</div>
              <p className="muted small">
                {pct}% correct{best ? ` · best ${best.score}/${best.total}` : ''}
              </p>
            </div>
          </div>
          <dl className="facts">
            {byTopic.map(([topic, t]) => (
              <div className="fact" key={topic}>
                <dt>{topic}</dt>
                <dd className={t.right === t.total ? 'tone-good' : undefined}>
                  {t.right}/{t.total}
                </dd>
              </div>
            ))}
          </dl>
          <div className="row" style={{ marginTop: 18 }}>
            <button type="button" className="btn btn-primary" onClick={start} disabled={loading}>
              {loading ? <LoaderCircle size={15} className="spin" /> : <RotateCcw size={15} />} New quiz
            </button>
            <a className="btn btn-secondary" href="#/training" style={{ textDecoration: 'none' }}>
              Practise with real emails
            </a>
          </div>
          <ErrorNotice message={error} />
        </section>

        {missed.length > 0 && (
          <section className="panel">
            <h2 className="panel-title">Questions you missed</h2>
            <ul className="findings">
              {missed.map((r) => (
                <li key={r.question.id}>
                  <StatusIcon tone="bad" />
                  <div>
                    <h4>{r.question.question}</h4>
                    <p>
                      You answered: <span className="tone-bad">{r.chosen}</span>
                    </p>
                    <p>
                      Correct answer: <span className="tone-good">{r.question.options[r.question.answer]}</span>
                    </p>
                    <p className="muted">{r.question.explanation}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    );
  }

  const progress = ((index + (answered ? 1 : 0)) / attempt.length) * 100;
  const chosenCorrect = answered && current.choices[selected].correct;

  return (
    <div className="page">
      {header}
      <section className="panel">
        <div className="row-between small">
          <span className="muted">
            Question {index + 1} of {attempt.length}
          </span>
          <span className="tag tone-muted">{current.topic}</span>
        </div>
        <div className="bar" style={{ marginTop: 10 }}>
          <span style={{ width: `${progress}%`, background: 'var(--accent)' }} />
        </div>

        <h2 className="quiz-question">{current.question}</h2>

        <div className="quiz-options" role="radiogroup" aria-label="Answers">
          {current.choices.map((choice, i) => {
            let state = '';
            if (answered) {
              if (choice.correct) state = 'is-correct';
              else if (i === selected) state = 'is-wrong';
              else state = 'is-dim';
            }
            return (
              <button
                key={choice.text}
                type="button"
                role="radio"
                aria-checked={i === selected}
                className={`quiz-option ${state}`}
                onClick={() => pick(i)}
                disabled={answered}
              >
                <span className="quiz-letter">{LETTERS[i]}</span>
                <span>{choice.text}</span>
                {answered && choice.correct && <StatusIcon tone="good" />}
                {answered && i === selected && !choice.correct && <StatusIcon tone="bad" />}
              </button>
            );
          })}
        </div>

        {answered && (
          <div className={`notice tone-${chosenCorrect ? 'good' : 'bad'}`} role="status">
            <StatusIcon tone={chosenCorrect ? 'good' : 'bad'} />
            <div>
              <strong>{chosenCorrect ? 'Correct' : 'Not quite'}</strong>
              <p>{current.explanation}</p>
            </div>
          </div>
        )}

        <div className="row-between" style={{ marginTop: 18 }}>
          <span className="muted small">
            {answered ? 'Press Enter to continue' : 'Pick an answer, or press 1 to 4'}
          </span>
          <button type="button" className="btn btn-primary" onClick={next} disabled={!answered}>
            {isLast ? 'See results' : 'Next question'} <ArrowRight size={15} />
          </button>
        </div>
      </section>
    </div>
  );
}
