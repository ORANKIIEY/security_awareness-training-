import { Circle, CircleAlert, CircleCheck, CircleX, Info, TriangleAlert } from 'lucide-react';

export function PageHeader({ eyebrow, title, children }) {
  return (
    <header className="page-head">
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      <h1>{title}</h1>
      {children && <p>{children}</p>}
    </header>
  );
}

export function ErrorNotice({ message }) {
  if (!message) return null;
  return (
    <div className="notice tone-bad" role="alert">
      <CircleAlert size={17} />
      <p>{message}</p>
    </div>
  );
}

const STATUS_ICONS = {
  good: CircleCheck,
  warn: TriangleAlert,
  bad: CircleX,
  info: Info,
  muted: Circle,
};

export function StatusIcon({ tone, size = 17 }) {
  const Icon = STATUS_ICONS[tone] || Info;
  return <Icon size={size} className={`tone-${tone}`} aria-hidden="true" />;
}

export function Tag({ tone = 'muted', children }) {
  return <span className={`tag tone-${tone}`}>{children}</span>;
}
