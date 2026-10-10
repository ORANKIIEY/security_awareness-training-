import { House, KeyRound, Mail, Globe, GraduationCap, ListChecks, ShieldCheck } from 'lucide-react';

const TOOLS = [
  { id: 'password', label: 'Password check', icon: KeyRound },
  { id: 'email', label: 'Email check', icon: Mail },
  { id: 'website', label: 'Website check', icon: Globe },
];

const STATUS_TEXT = {
  checking: 'Connecting to server…',
  online: 'Server connected',
  offline: 'Server offline',
};

export default function Navbar({ route, navigate, apiStatus }) {
  const item = ({ id, label, icon: Icon }) => (
    <a
      key={id}
      href={id === 'home' ? '#/' : `#/${id}`}
      className="nav-item"
      aria-current={route === id ? 'page' : undefined}
      title={label}
    >
      <Icon size={17} />
      <span>{label}</span>
    </a>
  );

  return (
    <aside className="sidebar">
      <button type="button" className="brand" onClick={() => navigate('home')}>
        <span className="brand-mark">
          <ShieldCheck size={16} />
        </span>
        <span>
          <span className="brand-name">Spotcheck</span>
          <span className="brand-sub">Security awareness toolkit</span>
        </span>
      </button>

      <nav className="nav" aria-label="Main">
        {item({ id: 'home', label: 'Home', icon: House })}
        <div className="nav-label">Check something</div>
        {TOOLS.map(item)}
        <div className="nav-label">Learn</div>
        {item({ id: 'training', label: 'Training', icon: GraduationCap })}
        {item({ id: 'quiz', label: 'Quiz', icon: ListChecks })}
      </nav>

      <div className="sidebar-foot">
        <span className={`status-dot ${apiStatus}`} />
        {STATUS_TEXT[apiStatus]}
      </div>
    </aside>
  );
}
