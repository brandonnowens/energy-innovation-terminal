/**
 * GhostAuthProbe — invisible iframe that loads the Ghost auth-bridge page.
 *
 * The bridge page reads the visitor's Ghost member session cookie and sends
 * back a {type: "aixenergy-ghost-token", token: "<jwt>"} postMessage to this
 * frame's parent (the terminal app).  useGhostAuth listens for that message
 * and transitions the visitor to "authenticated" status.
 *
 * The iframe is zero-size and never visible.  It is only mounted when auth
 * is enabled and the visitor has not yet been confirmed as a member.
 */

import { useMemo } from 'react';
import { GHOST_AUTH_ENABLED, ghostTerminalAuthEmbedUrl } from '../config/ghostAuth';
import './GhostAuthProbe.css';

interface GhostAuthProbeProps {
  /** Should the probe be actively mounted? Pass false to suppress entirely. */
  active: boolean;
  /**
   * Increment this to force the iframe to reload (e.g. after focus returns
   * to the window following a sign-in attempt).
   */
  refreshKey?: number;
}

export function GhostAuthProbe({ active, refreshKey = 0 }: GhostAuthProbeProps) {
  // Recompute the src whenever refreshKey changes so the browser reloads the
  // bridge page and re-attempts the session probe.
  const src = useMemo(
    () => ghostTerminalAuthEmbedUrl(),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [refreshKey],
  );

  if (!GHOST_AUTH_ENABLED || !active) return null;

  return (
    <iframe
      className="ghost-auth-probe"
      title="Ghost member authentication probe"
      src={src}
      tabIndex={-1}
      aria-hidden="true"
      referrerPolicy="strict-origin-when-cross-origin"
    />
  );
}
