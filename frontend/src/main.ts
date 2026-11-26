import './style.css';
import { FoundationRuntime } from './runtime';

const host = document.querySelector<HTMLElement>('#viewport')!;
const runtime = new FoundationRuntime(host, message => {
  const error = document.querySelector<HTMLElement>('#error')!;
  error.hidden = false; error.textContent = message;
});
runtime.start();
// Local diagnostics only; no credentials, networking, gameplay or admin operations.
Object.assign(window, { foundation: runtime });
window.addEventListener('pagehide', () => runtime.dispose(), { once: true });
if (import.meta.hot) import.meta.hot.dispose(() => runtime.dispose());
