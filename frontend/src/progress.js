const KEY = 'spotcheck.training.v1';

export function loadAnswers() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {};
  } catch {
    return {};
  }
}

export function saveAnswers(answers) {
  try {
    localStorage.setItem(KEY, JSON.stringify(answers));
  } catch {
    // Storage may be unavailable (private mode); progress just won't persist.
  }
}
