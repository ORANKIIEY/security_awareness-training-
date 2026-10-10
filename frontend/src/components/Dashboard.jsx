import { useEffect, useState } from 'react';
import { KeyRound, Mail, Globe, GraduationCap, ArrowRight } from 'lucide-react';
import { getJSON } from '../api';
import { loadAnswers } from '../progress';

const TOOLS = [
  {
    id: 'password',
    icon: KeyRound,
    name: 'Password check',
    desc: 'How long it would take to crack, and whether it has already leaked.',
  },
  {
    id: 'email',
    icon: Mail,
    name: 'Email check',
    desc: 'Paste a suspicious email to see spoofed senders, fake links and pressure tactics.',
  },
  {
    id: 'website',
    icon: Globe,
    name: 'Website check',
    desc: "Look up a site's certificate, HTTPS setup and security headers.",
  },
];

export default function Dashboard({ navigate }) {
  const [answers] = useState(loadAnswers);
  const [total, setTotal] = useState(null);

  useEffect(() => {
    getJSON('/api/scenarios')
      .then((data) => setTotal(data.length))
      .catch(() => setTotal(null));
  }, []);

  const answered = Object.keys(answers).length;
  const correct = Object.values(answers).filter((a) => a.correct).length;
  const finished = total !== null && answered >= total;

  return (
    <div className="page">
      <header className="page-head home-hero">
        <h1>Check before you click.</h1>
        <p>
          Most breaches start with a reused password, a convincing email or a fake login page. These tools help
          you spot all three, and the training teaches you to notice them without a tool.
        </p>
      </header>

      <section className="training-cta">
        <div className="training-cta-icon">
          <GraduationCap size={22} />
        </div>
        <div className="training-cta-body">
          <div className="eyebrow">Training</div>
          <h2>Can you spot the phishing email?</h2>
          <p>
            Work through {total ?? 'a set of'} realistic emails. Decide whether each one is safe or phishing, then see
            exactly what gave it away. Takes about five minutes.
          </p>
          {answered > 0 && (
            <p className="training-cta-progress">
              <strong>
                {correct}/{answered}
              </strong>{' '}
              correct{total ? ` · ${answered} of ${total} answered` : ''}
            </p>
          )}
        </div>
        <div className="training-cta-actions">
          <button type="button" className="btn btn-primary" onClick={() => navigate('training')}>
            {answered === 0 ? 'Start training' : finished ? 'Review answers' : 'Continue training'}
            <ArrowRight size={16} />
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('quiz')}>
            Take the quiz
          </button>
        </div>
      </section>

      <h2 className="section-title">Check something</h2>
      <ul className="tool-list">
        {TOOLS.map(({ id, icon: Icon, name, desc }) => (
          <li key={id}>
            <a className="tool-link" href={`#/${id}`}>
              <span className="tool-icon">
                <Icon size={18} />
              </span>
              <span>
                <span className="tool-name" style={{ display: 'block' }}>
                  {name}
                </span>
                <span className="tool-desc">{desc}</span>
              </span>
              <ArrowRight size={18} className="tool-arrow" />
            </a>
          </li>
        ))}
      </ul>

      <section className="panel" style={{ marginTop: 36 }}>
        <h2 className="panel-title">Habits that stop most attacks</h2>
        <ol className="tips">
          <li>
            <span>
              <strong>Use a password manager</strong> so every account gets its own long, random password.
            </span>
          </li>
          <li>
            <span>
              <strong>Turn on two-factor authentication</strong> for email, banking and work accounts first.
            </span>
          </li>
          <li>
            <span>
              <strong>Go to the site yourself.</strong> If an email asks you to log in, type the address instead of
              clicking the link.
            </span>
          </li>
          <li>
            <span>
              <strong>Verify money requests by phone</strong>, using a number you already have, not one in the email.
            </span>
          </li>
        </ol>
      </section>
    </div>
  );
}
