import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, User, MembershipManifest } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  authModalOpen: boolean;
  authModalTab: 'login' | 'register' | 'forgot';
  membershipModalOpen: boolean;
  accountModalOpen: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string, organizationName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateProfile: (data: { full_name?: string; organization_name?: string }) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  openAuthModal: (tab?: 'login' | 'register' | 'forgot') => void;
  closeAuthModal: () => void;
  openMembershipModal: () => void;
  closeMembershipModal: () => void;
  openAccountModal: () => void;
  closeAccountModal: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register' | 'forgot'>('login');
  const [membershipModalOpen, setMembershipModalOpen] = useState(false);
  const [accountModalOpen, setAccountModalOpen] = useState(false);

  const refreshUser = async () => {
    const currentToken = localStorage.getItem('auth_token');
    if (!currentToken) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const res = await api.getMe();
      setUser(res.user);
    } catch (err) {
      console.warn('Session expired or invalid, logging out.', err);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, [token]);

  // Sync token changes across multiple tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token') {
        setToken(e.newValue);
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    localStorage.setItem('auth_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    setAuthModalOpen(false);
  };

  const register = async (email: string, password: string, fullName?: string, organizationName?: string) => {
    const res = await api.register({
      email,
      password,
      full_name: fullName,
      organization_name: organizationName,
    });
    localStorage.setItem('auth_token', res.access_token);
    setToken(res.access_token);
    setUser(res.user);
    setAuthModalOpen(false);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const updateProfile = async (data: { full_name?: string; organization_name?: string }) => {
    const res = await api.updateProfile(data);
    setUser(res.user);
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    await api.changePassword({ current_password: currentPassword, new_password: newPassword });
  };

  const openAuthModal = (tab: 'login' | 'register' | 'forgot' = 'login') => {
    setAuthModalTab(tab);
    setAuthModalOpen(true);
  };

  const closeAuthModal = () => setAuthModalOpen(false);
  const openMembershipModal = () => setMembershipModalOpen(true);
  const closeMembershipModal = () => setMembershipModalOpen(false);
  const openAccountModal = () => setAccountModalOpen(true);
  const closeAccountModal = () => setAccountModalOpen(false);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        authModalOpen,
        authModalTab,
        membershipModalOpen,
        accountModalOpen,
        login,
        register,
        logout,
        refreshUser,
        updateProfile,
        changePassword,
        openAuthModal,
        closeAuthModal,
        openMembershipModal,
        closeMembershipModal,
        openAccountModal,
        closeAccountModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
