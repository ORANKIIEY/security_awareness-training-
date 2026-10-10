import { useEffect, useState } from 'react';
import { TriangleAlert } from 'lucide-react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import PasswordChecker from './components/PasswordChecker';
import PhishingChecker from './components/PhishingChecker';
import WebsiteChecker from './components/WebsiteChecker';
import ScenariosQuiz from './components/ScenariosQuiz';
import Quiz from './components/Quiz';

const PAGES = {
  home: Dashboard,
  password: PasswordChecker,
  email: PhishingChecker,
  website: WebsiteChecker,
  training: ScenariosQuiz,
  quiz: Quiz,
};

function readRoute() {
  const route = window.location.hash.replace(/^#\/?/, '');
  return route in PAGES ? route : 'home';
}

export default function App() {
  const [route, setRoute] = useState(readRoute);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    const onHashChange = () => {
      setRoute(readRoute());
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (!cancelled) setApiStatus(res.ok ? 'online' : 'offline');
      } catch {
        if (!cancelled) setApiStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const navigate = (id) => {
    window.location.hash = id === 'home' ? '/' : `/${id}`;
  };

  const Page = PAGES[route];

  return (
    <div className="shell">
      <Navbar route={route} navigate={navigate} apiStatus={apiStatus} />
      <main className="main">
        {apiStatus === 'offline' && (
          <div className="offline-banner" role="status">
            <TriangleAlert size={17} style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              The analysis server isn't responding, so checks won't work yet. Start it with{' '}
              <code>python main.py</code> inside the <code>backend</code> folder.
            </div>
          </div>
        )}
        <Page navigate={navigate} />
      </main>
    </div>
  );
}
