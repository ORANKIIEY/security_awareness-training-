const TABS = [
  { id: 'training', label: 'Spot the phish' },
  { id: 'quiz', label: 'Knowledge quiz' },
];

export default function TrainingTabs({ active }) {
  return (
    <nav className="tabs" aria-label="Training sections">
      {TABS.map((t) => (
        <a key={t.id} href={`#/${t.id}`} className="tab" aria-current={active === t.id ? 'page' : undefined}>
          {t.label}
        </a>
      ))}
    </nav>
  );
}
