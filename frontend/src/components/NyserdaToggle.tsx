import React from 'react';
import { useNyserda } from '../context/NyserdaContext';

interface NyserdaToggleProps {
  variant?: 'header' | 'sidebar' | 'compact';
  className?: string;
}

/**
 * NYSERDA Toggle Component.
 * Currently hidden per user specification (NYSERDA is permanently included in scope).
 */
export function NyserdaToggle(_props: NyserdaToggleProps) {
  // Return null to hide the toggle button from all UI views while keeping scope included
  return null;
}
