/**
 * GhostAccessGate — popup modal shown to visitors who are not logged into
 * aixenergy.io (Ghost) when they arrive at the Energy Innovation Terminal.
 *
 * Design intent:
 *  - Simple, clean, on-brand (dark terminal aesthetic)
 *  - Not a hard block: "Browse without signing in" dismisses it for the session
 *  - Primary path: free account creation at aixenergy.io
 *  - Secondary path: sign in if they already have an account
 *  - Auto-closes: the gate is never shown again once Ghost auth resolves to
 *    "authenticated" (the hook handles that by not passing open=true)
 */

import React, { useEffect, useRef } from 'react';
import { X, Zap, LogIn, ArrowUpRight, ShieldCheck } from 'lucide-react';
import { GHOST_SIGNIN_URL, GHOST_SIGNUP_URL } from '../config/ghostAuth';
import { handleGhostSignInClick } from '../lib/ghostSignIn';
import './GhostAccessGate.css';

export interface GhostAccessGateProps {
  /** Whether the gate is currently shown. */
  open: boolean;
  /** Called when the user dismisses the gate (browse without signing in). */
  onClose: () => void;
}

export function GhostAccessGate({ open, onClose }: GhostAccessGateProps) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  // Focus management & ESC key
  useEffect(() => {
    if (!open) return;
    // Small delay so the animation plays before we steal focus
    const t = window.setTimeout(() => closeButtonRef.current?.focus(), 80);
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => {
      window.clearTimeout(t);
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="gag-backdrop"
      role="presentation"
      onClick={onClose}
      aria-label="Close access gate"
    >
      <div
        ref={dialogRef}
        className="gag-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="gag-title"
        onClick={(e) => e.stopPropagation()}
      >
        {/* ── Header ─────────────────────────────────────────────────── */}
        <div className="gag-header">
          <div className="gag-logo-mark">
            <Zap size={18} className="gag-logo-icon" />
          </div>
          <div className="gag-header-text">
            <span className="gag-brand">AIxEnergy</span>
            <span className="gag-product">Energy Innovation Terminal</span>
          </div>
          <button
            ref={closeButtonRef}
            type="button"
            className="gag-close"
            onClick={onClose}
            aria-label="Dismiss and browse without signing in"
          >
            <X size={16} />
          </button>
        </div>

        {/* ── Body ───────────────────────────────────────────────────── */}
        <div className="gag-body">
          <div className="gag-shield-row">
            <ShieldCheck size={32} className="gag-shield-icon" />
          </div>

          <h2 id="gag-title" className="gag-title">
            Create a free account for full access
          </h2>

          <p className="gag-desc">
            The Energy Innovation Terminal tracks{' '}
            <strong>$104B+ in non-dilutive energy transition capital</strong>,
            5,700+ active solicitations, and 56,000+ award precedents across
            federal and state agencies.
          </p>

          <p className="gag-desc gag-desc--secondary">
            A free account on <strong>aixenergy.io</strong> unlocks the full
            terminal — AI advisory, opportunity matching, recipient dossiers,
            and market intelligence — at no cost.
          </p>

          {/* ── CTAs ─────────────────────────────────────────────────── */}
          <div className="gag-actions">
            <a
              href={GHOST_SIGNUP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="gag-btn gag-btn--primary"
            >
              <Zap size={15} />
              Create Free Account
              <ArrowUpRight size={14} className="gag-btn-arrow" />
            </a>

            <a
              href={GHOST_SIGNIN_URL}
              className="gag-btn gag-btn--secondary"
              onClick={(e) => handleGhostSignInClick(e, GHOST_SIGNIN_URL)}
            >
              <LogIn size={15} />
              Sign In
            </a>
          </div>

          {/* ── Dismiss ──────────────────────────────────────────────── */}
          <button
            type="button"
            className="gag-dismiss"
            onClick={onClose}
          >
            Browse without signing in
          </button>
        </div>

        {/* ── Footer ─────────────────────────────────────────────────── */}
        <div className="gag-footer">
          <span>Free accounts · No credit card required · U.S. Energy Innovation Database by Clean Energy Research, LLC</span>
        </div>
      </div>
    </div>
  );
}
