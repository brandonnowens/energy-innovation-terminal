import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from './AuthContext';

interface NyserdaContextType {
  includeNyserda: boolean;
  setIncludeNyserda: (val: boolean | ((prev: boolean) => boolean)) => void;
  toggleNyserda: () => void;
  isAdmin: boolean;
  isNyserda: (textOrObj?: any) => boolean;
  isNyserdaAgency: (textOrObj?: any) => boolean;
  filterNyserda: <T>(items: T[], getAgencyFn?: (item: T) => string | undefined | null) => T[];
}

const STORAGE_KEY = 'energy_terminal_include_nyserda';

const NyserdaContext = createContext<NyserdaContextType | undefined>(undefined);

export function isNyserdaAgency(val?: any): boolean {
  if (!val) return false;
  if (typeof val === 'string') {
    const s = val.toLowerCase().trim();
    return (
      s === 'nyserda' ||
      s.includes('nyserda') ||
      s.includes('new york state energy research and development authority')
    );
  }
  if (typeof val === 'object') {
    const checkFields = [
      val.agency,
      val.agency_code,
      val.agency_name,
      val.organization,
      val.organization_name,
      val.org_name,
      val.code,
      val.name,
      val.source_name,
      val.funded_agencies,
      val.funder_name,
      val.label,
      val.title,
    ];
    return checkFields.some(f => isNyserdaAgency(f));
  }
  return false;
}

export function NyserdaProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const isAdmin = Boolean(
    user && (
      user.role === 'admin' ||
      user.email?.toLowerCase() === 'bowens@aixenergy.io' ||
      user.full_name?.toLowerCase().includes('brandon owens')
    )
  );

  const [includeNyserda, setIncludeNyserdaState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== null) {
        return saved === 'true';
      }
    } catch {
      // ignore
    }
    return true; // Default ON
  });

  const setIncludeNyserda = useCallback((val: boolean | ((prev: boolean) => boolean)) => {
    setIncludeNyserdaState(prev => {
      const nextVal = typeof val === 'function' ? val(prev) : val;
      try {
        localStorage.setItem(STORAGE_KEY, String(nextVal));
      } catch {
        // ignore
      }
      return nextVal;
    });
  }, []);

  const toggleNyserda = useCallback(() => {
    setIncludeNyserda(prev => !prev);
  }, [setIncludeNyserda]);

  // Invalidate queries whenever includeNyserda changes so UI data re-fetches
  useEffect(() => {
    queryClient.invalidateQueries();
  }, [includeNyserda, queryClient]);

  // Sync state across multiple tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue !== null) {
        setIncludeNyserdaState(e.newValue === 'true');
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const filterNyserda = useCallback(<T,>(items: T[], getAgencyFn?: (item: T) => string | undefined | null): T[] => {
    if (!items || !Array.isArray(items)) return [];
    if (includeNyserda) return items;
    return items.filter(item => {
      if (getAgencyFn) {
        const agency = getAgencyFn(item);
        return !isNyserdaAgency(agency);
      }
      return !isNyserdaAgency(item);
    });
  }, [includeNyserda]);

  return (
    <NyserdaContext.Provider
      value={{
        includeNyserda,
        setIncludeNyserda,
        toggleNyserda,
        isAdmin,
        isNyserda: isNyserdaAgency,
        isNyserdaAgency,
        filterNyserda,
      }}
    >
      {children}
    </NyserdaContext.Provider>
  );
}

export function useNyserda() {
  const context = useContext(NyserdaContext);
  if (!context) {
    throw new Error('useNyserda must be used within a NyserdaProvider');
  }
  return context;
}
