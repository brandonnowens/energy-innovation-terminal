/**
 * Ghost sign-in click handler for the Energy Innovation Terminal.
 * Ported from the AIxEnergy Map app (S:\aixenergy-global-project-map\src\lib\ghostSignIn.ts).
 *
 * Opens the Ghost Portal sign-in page in a named tab. When that tab closes
 * (e.g. after the user signs in), fires a custom event so the terminal's
 * auth hook knows to re-probe for a valid Ghost session.
 */

import { TERMINAL_AUTH_REFRESH_EVENT, TERMINAL_GATE_DISMISSED_KEY } from '../config/ghostAuth';
import { clearGhostTokenHold } from './ghostSession';

function requestAuthRefresh(): void {
  window.dispatchEvent(new Event(TERMINAL_AUTH_REFRESH_EVENT));
}

/**
 * Handle a click on the "Sign In" link within the GhostAccessGate.
 * Opens Ghost Portal in a full named tab (not a constrained popup) so that
 * the one-time-code / magic-link email flow works cross-origin.
 * When the user closes that tab we fire an auth-refresh event so the hook
 * can re-probe and close the gate automatically.
 */
export function handleGhostSignInClick(
  event: { preventDefault: () => void },
  signinUrl: string,
): void {
  clearGhostTokenHold();
  // Clear the dismissed flag so the gate re-appears if sign-in is attempted.
  try {
    window.sessionStorage.removeItem(TERMINAL_GATE_DISMISSED_KEY);
  } catch {
    // ignore
  }

  const signinWindow = window.open(signinUrl, 'aixenergy-ghost-auth');
  if (!signinWindow) return;

  event.preventDefault();
  signinWindow.focus();

  // Poll until the tab closes, then trigger a refresh probe.
  const timer = window.setInterval(() => {
    if (signinWindow.closed) {
      window.clearInterval(timer);
      requestAuthRefresh();
    }
  }, 1000);
}
