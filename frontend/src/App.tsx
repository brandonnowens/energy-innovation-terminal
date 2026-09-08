import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import { SplashScreen } from './components/SplashScreen';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { NyserdaProvider } from './context/NyserdaContext';
import { Loader2 } from 'lucide-react';

// Route-based dynamic lazy loading for performant initial bundle loading
const AnalyzeProject = lazy(() => import('./pages/AnalyzeProject'));
const Opportunities = lazy(() => import('./pages/Opportunities'));
const OpportunityDetail = lazy(() => import('./pages/OpportunityDetail'));
const Proposals = lazy(() => import('./pages/Proposals'));
const Programs = lazy(() => import('./pages/Programs'));
const Organizations = lazy(() => import('./pages/Organizations'));
const Awards = lazy(() => import('./pages/Awards'));
const Network = lazy(() => import('./pages/Network'));
const Sankey = lazy(() => import('./pages/Sankey'));
const Trends = lazy(() => import('./pages/Trends'));
const Updates = lazy(() => import('./pages/Updates'));
const System = lazy(() => import('./pages/System'));
const Strategy = lazy(() => import('./pages/Strategy'));
const Reports = lazy(() => import('./pages/Reports'));
const Results = lazy(() => import('./pages/Results'));
const VenturePatentsPage = lazy(() => import('./pages/VenturePatentsPage'));
const KeyContacts = lazy(() => import('./pages/KeyContacts'));
const TechReference = lazy(() => import('./pages/TechReference'));
const TechnologyHub = lazy(() => import('./pages/TechnologyHub'));
const RecipientDossier = lazy(() => import('./pages/RecipientDossier'));
const AgencyHub = lazy(() => import('./pages/AgencyHub'));
const Dockets = lazy(() => import('./pages/Dockets'));
const PolicyReference = lazy(() => import('./pages/PolicyReference'));
const Chat = lazy(() => import('./pages/Chat'));
const AdminEmailHub = lazy(() => import('./pages/AdminEmailHub'));
const ForecastingRadar = lazy(() => import('./pages/ForecastingRadar').then(m => ({ default: m.ForecastingRadar })));
const NotFound = lazy(() => import('./pages/NotFound'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes cache freshness
      gcTime: 15 * 60 * 1000,   // 15 minutes garbage collection retention
    },
  },
});

function PageLoadingFallback() {
  return (
    <div className="flex h-[60vh] w-full flex-col items-center justify-center gap-3 text-slate-500">
      <Loader2 className="h-7 w-7 animate-spin text-slate-500" />
      <span className="text-xs font-medium text-slate-500">Loading module...</span>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <NyserdaProvider>
            <SplashScreen />
            <BrowserRouter>
              <Suspense fallback={<PageLoadingFallback />}>
                <Routes>
                  <Route path="/" element={<Layout />}>
                    <Route index element={<AnalyzeProject />} />
                    <Route path="analyze" element={<AnalyzeProject />} />
                    <Route path="match" element={<AnalyzeProject />} />
                    <Route path="radar" element={<ForecastingRadar />} />
                    <Route path="forecasting" element={<ForecastingRadar />} />
                    <Route path="chat" element={<Chat />} />
                  <Route path="opportunities" element={<Opportunities />} />
                  <Route path="opportunities/:id" element={<OpportunityDetail />} />
                  {/* Programmatic SEO Hubs */}
                  <Route path="recipients/:id" element={<RecipientDossier />} />
                  <Route path="recipients/:id/:slug" element={<RecipientDossier />} />
                  <Route path="agencies/:id" element={<AgencyHub />} />
                  <Route path="tech-hub/:slug" element={<TechnologyHub />} />

                  {/* Primary Technology & Fuels Innovation Reference */}
                  <Route path="technologies" element={<TechReference />} />
                  <Route path="technologies/:id" element={<TechReference />} />
                  <Route path="tech-reference" element={<TechReference />} />
                  <Route path="tech-reference/:id" element={<TechReference />} />

                  {/* Policy, Codes & IRA Incentives Reference */}
                  <Route path="policies" element={<PolicyReference />} />
                  <Route path="policies/:id" element={<PolicyReference />} />
                  <Route path="policy-reference" element={<PolicyReference />} />
                  <Route path="policy-reference/:id" element={<PolicyReference />} />

                  <Route path="proposals" element={<Proposals />} />
                  <Route path="programs" element={<Programs />} />
                  <Route path="organizations" element={<Organizations />} />
                  <Route path="contacts" element={<KeyContacts />} />
                  <Route path="key-contacts" element={<KeyContacts />} />
                  <Route path="awards" element={<Awards />} />
                  <Route path="dockets" element={<Dockets />} />
                  <Route path="proceedings" element={<Dockets />} />
                  <Route path="regulatory-reference" element={<Dockets />} />
                  <Route path="venture-patents" element={<VenturePatentsPage />} />
                  <Route path="results" element={<Results />} />
                  <Route path="network" element={<Network />} />
                  <Route path="sankey" element={<Sankey />} />
                  <Route path="trends" element={<Trends />} />
                  <Route path="updates" element={<Updates />} />
                  <Route path="sources" element={<System />} />
                  {/* System Admin Email & Outreach Hub */}
                  <Route path="admin/email-hub" element={<AdminEmailHub />} />
                  <Route path="admin/outreach" element={<AdminEmailHub />} />
                  <Route path="admin" element={<AdminEmailHub />} />
                  {/* Hidden but preserved */}
                  <Route path="strategy" element={<Strategy />} />
                  <Route path="strategy/:id" element={<Strategy />} />
                  <Route path="reports" element={<Reports />} />
                  <Route path="reports/:id" element={<Reports />} />
                  {/* Catch-all Not Found Route */}
                  <Route path="*" element={<NotFound />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </NyserdaProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);
}

export default App;
