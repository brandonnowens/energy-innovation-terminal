import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Video, Maximize2, Minimize2, PhoneOff,
  Sparkles, ShieldCheck, RefreshCw, ChevronDown, Check,
  MessageSquare, Volume2, Play, Clock,
  FileText, ArrowRight, AlertCircle, User, Building2,
  Trophy, BookUser, BookOpen, ExternalLink, Search,
  TrendingUp, BarChart3, Mic, MicOff, Zap, CheckCircle2, Layers
} from 'lucide-react';
import DailyIframe, { DailyCall } from '@daily-co/daily-js';
import {
  api,
  TavusConversationResponse,
  ChatCitationsMetadata,
  TavusTechBreakdownItem,
  TavusSyncIntelligenceResponse
} from '../api/client';
import { UserRole } from '../pages/Chat';

interface RoleOption {
  id: UserRole;
  title: string;
  badge: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  description: string;
  spokenStarters: string[];
}

interface TavusVideoConversationProps {
  userRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  roles: RoleOption[];
  onSwitchToChat: () => void;
  onBackToHub?: () => void;
}

export default function TavusVideoConversation({
  userRole,
  onRoleChange,
  roles,
  onSwitchToChat,
  onBackToHub,
}: TavusVideoConversationProps) {
  const [isInitializing, setIsInitializing] = useState(false);
  const [activeConversation, setActiveConversation] = useState<TavusConversationResponse | null>(null);
  const [ragCitations, setRagCitations] = useState<ChatCitationsMetadata | null>(null);
  const [detectedTopic, setDetectedTopic] = useState<string>('US Clean Energy Innovation & Capital Intelligence');
  const [activeQuery, setActiveQuery] = useState<string>('');
  const [executiveGist, setExecutiveGist] = useState<string>('');
  const [keyEntities, setKeyEntities] = useState<string[]>([]);
  const [secondsUntilNextSync, setSecondsUntilNextSync] = useState<number>(30);
  const [liveTopicSearch, setLiveTopicSearch] = useState<string>('');
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [isListeningMic, setIsListeningMic] = useState<boolean>(false);
  const [liveSpokenText, setLiveSpokenText] = useState<string>('');
  const [callDuration, setCallDuration] = useState(0);
  const [callEnded, setCallEnded] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [notes, setNotes] = useState('');
  const [isReviewingNotes, setIsReviewingNotes] = useState(false);
  const [sidecarTab, setSidecarTab] = useState<'citations' | 'questions' | 'notes'>('citations');
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);

  const videoContainerRef = useRef<HTMLDivElement>(null);
  const dailyCallRef = useRef<DailyCall | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const activeConvIdRef = useRef<string | null>(null);
  const recentTranscriptBufferRef = useRef<string[]>([]);
  const cumulativeTranscriptRef = useRef<string[]>([]);

  const currentRoleConfig = roles.find(r => r.id === userRole) || roles[0];

  // 30-Second Cumulative Conversation Synthesizer & Cadence Engine
  const performPeriodicSynthesis = async (forcedQuery?: string) => {
    const recentBufferText = forcedQuery || recentTranscriptBufferRef.current.join(' ').trim();
    if (!recentBufferText && !cumulativeTranscriptRef.current.length && !forcedQuery) {
      return;
    }

    setIsSyncing(true);
    try {
      const res = await api.synthesizeAndSyncTavusSession({
        recent_transcript_buffer: recentBufferText || cumulativeTranscriptRef.current.slice(-4).join(' '),
        cumulative_transcript: cumulativeTranscriptRef.current.join(' '),
        user_role: userRole,
        conversation_id: activeConvIdRef.current || undefined
      });

      if (res.executive_gist) setExecutiveGist(res.executive_gist);
      if (res.detected_topic) setDetectedTopic(res.detected_topic);
      if (res.key_entities) setKeyEntities(res.key_entities);
      if (res.citations) setRagCitations(res.citations);
      setActiveQuery(res.search_query || forcedQuery || '');
      setSidecarTab('citations');

      // Clear recent buffer after synthesis cycle
      recentTranscriptBufferRef.current = [];
      setSecondsUntilNextSync(30);
    } catch (e) {
      console.warn('Periodic synthesis error:', e);
    } finally {
      setIsSyncing(false);
    }
  };

  // Helper to record dialogue from user or advisor
  const recordSpokenUtterance = (text: string, speaker: 'user' | 'advisor' = 'user') => {
    const clean = text.trim();
    if (!clean || clean.length < 3) return;
    setLiveSpokenText(clean);
    recentTranscriptBufferRef.current.push(`[${speaker.toUpperCase()}]: ${clean}`);
    cumulativeTranscriptRef.current.push(`[${speaker.toUpperCase()}]: ${clean}`);

    // If panel is on blank slate, immediately trigger the first synthesis so user sees initial grounding
    if (!ragCitations && cumulativeTranscriptRef.current.length === 1) {
      performPeriodicSynthesis(clean);
    }
  };

  // 30-Second Cadence Heartbeat Timer
  useEffect(() => {
    if (!activeConversation || callEnded) return;

    const interval = setInterval(() => {
      setSecondsUntilNextSync(prev => {
        if (prev <= 1) {
          if (recentTranscriptBufferRef.current.length > 0) {
            performPeriodicSynthesis();
          }
          return 30;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [activeConversation, callEnded, userRole, ragCitations]);

  // Continuous Fast Browser Speech Recognition for Live Conversation Synchronization
  useEffect(() => {
    if (!activeConversation || callEnded) {
      setIsListeningMic(false);
      return;
    }

    const SpeechRecClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecClass) return;

    let recognition: any = null;

    try {
      recognition = new SpeechRecClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListeningMic(true);
      };

      recognition.onresult = (event: any) => {
        const lastIndex = event.results.length - 1;
        const result = event.results[lastIndex];
        const transcript = result[0]?.transcript?.trim();
        if (transcript && transcript.length > 3) {
          recordSpokenUtterance(transcript, 'user');
        }
      };

      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          console.debug('Speech recognition status:', event.error);
        }
      };

      recognition.onend = () => {
        if (activeConvIdRef.current && !callEnded) {
          try { recognition.start(); } catch (_) {}
        } else {
          setIsListeningMic(false);
        }
      };

      recognition.start();
    } catch (err) {
      console.debug('SpeechRecognition setup note:', err);
    }

    return () => {
      if (recognition) {
        try { recognition.stop(); } catch (_) {}
      }
      setIsListeningMic(false);
    };
  }, [activeConversation, callEnded]);

  // WebRTC PostMessage Listener for Daily.co / Tavus transcripts
  useEffect(() => {
    const handleDailyMessage = (e: MessageEvent) => {
      if (!e.data) return;
      const msg = typeof e.data === 'string' ? (() => { try { return JSON.parse(e.data); } catch { return null; } })() : e.data;
      if (!msg) return;

      const potentialText = msg.text || msg.transcript || msg.data?.text || msg.data?.transcript;
      if (typeof potentialText === 'string' && potentialText.trim().length > 4) {
        recordSpokenUtterance(potentialText, 'advisor');
      }
    };

    window.addEventListener('message', handleDailyMessage);
    return () => window.removeEventListener('message', handleDailyMessage);
  }, [userRole]);

  // Auto-launch video session immediately on mount
  useEffect(() => {
    handleStartCall();
  }, [userRole]);

  // Cleanup on component unmount to instantly end session and stop token billing
  useEffect(() => {
    return () => {
      if (activeConvIdRef.current) {
        api.endTavusConversation(activeConvIdRef.current).catch(() => {});
      }
    };
  }, []);

  // Call duration timer
  useEffect(() => {
    if (activeConversation && !callEnded) {
      activeConvIdRef.current = activeConversation.conversation_id;
      setCallDuration(0);
      timerRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1);
      }, 1000);
    } else {
      activeConvIdRef.current = null;
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [activeConversation, callEnded]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartCall = async () => {
    setIsInitializing(true);
    setErrorMessage(null);
    setCallEnded(false);

    try {
      const response = await api.createTavusConversation({
        user_role: userRole,
        replica_id: 'read903b2a48', // Brandon Owens April 14 2026 (Phoenix-4 CVI)
        persona_id: 'p8c4fc7f28ac', // Energy Innovation Terminal PAL (Ultra Low-Latency & Low-Token)
        conversation_name: `Energy Innovation Terminal Video Advisory - ${currentRoleConfig.badge}`
      });

      activeConvIdRef.current = response.conversation_id;
      setActiveConversation(response);
      setRagCitations(null);
      setDetectedTopic('');
      setExecutiveGist('');
      setKeyEntities([]);
      setActiveQuery('');
      setLiveSpokenText('');
      recentTranscriptBufferRef.current = [];
      cumulativeTranscriptRef.current = [];
      setSecondsUntilNextSync(30);

      // Pre-flight camera & microphone permissions for cross-browser reliability
      if (typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
          stream.getTracks().forEach(t => t.stop());
        } catch (_) {
          try {
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioStream.getTracks().forEach(t => t.stop());
          } catch (_) {}
        }
      }

      // Mount Daily.co WebRTC Frame with Event Listeners
      setTimeout(async () => {
        if (videoContainerRef.current && response.conversation_url) {
          try {
            if (dailyCallRef.current) {
              await dailyCallRef.current.destroy();
              dailyCallRef.current = null;
            }

            videoContainerRef.current.innerHTML = '';

            const callFrame = DailyIframe.createFrame(videoContainerRef.current, {
              iframeStyle: {
                width: '100%',
                height: '100%',
                border: '0',
                backgroundColor: '#000000',
              },
              showLeaveButton: false,
              showFullscreenButton: false,
              subscribeToTracksAutomatically: true,
            });

            // Explicitly ensure the iframe element has permissive allow attributes for all browsers
            const iframeEl = videoContainerRef.current.querySelector('iframe');
            if (iframeEl) {
              iframeEl.setAttribute(
                'allow',
                'camera *; microphone *; autoplay *; display-capture *; fullscreen *; speaker-selection *'
              );
              iframeEl.setAttribute('allowUserMedia', 'true');
            }

            callFrame.on('app-message', (evt: any) => {
              const data = evt?.data;
              if (data) {
                const text = data.text || data.transcript || (typeof data === 'string' ? data : null);
                if (text && text.trim().length > 3) {
                  recordSpokenUtterance(text, 'advisor');
                }
              }
            });

            callFrame.on('transcription-message', (evt: any) => {
              const text = evt?.text;
              if (text && text.trim().length > 3) {
                recordSpokenUtterance(text, 'advisor');
              }
            });

            callFrame.on('left-meeting', () => {
              handleEndCall();
            });

            dailyCallRef.current = callFrame;
            await callFrame.join({
              url: response.conversation_url,
              subscribeToTracksAutomatically: true,
            });
          } catch (dErr) {
            console.warn('Daily.js frame initialization note:', dErr);
          }
        }
      }, 100);
    } catch (err: any) {
      console.error('Failed to create Tavus conversation:', err);
      setErrorMessage(err.message || 'Failed to initialize Tavus video conversation. Please verify server connection.');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleReviewNotes = async () => {
    if (!notes.trim()) return;
    setIsReviewingNotes(true);
    try {
      const res = await api.reviewTavusSession({
        transcript_or_notes: notes,
        user_role: userRole
      });
      if (res.citations) {
        setRagCitations(res.citations);
      }
      setSidecarTab('citations');
    } catch (e) {
      console.warn('Failed to review notes and link to database:', e);
    } finally {
      setIsReviewingNotes(false);
    }
  };

  const handleEndCall = async () => {
    if (activeConversation?.conversation_id) {
      try {
        await api.endTavusConversation(activeConversation.conversation_id);
      } catch (e) {
        console.warn('Error ending Tavus call:', e);
      }
    }
    if (dailyCallRef.current) {
      try {
        await dailyCallRef.current.leave();
        await dailyCallRef.current.destroy();
      } catch (_) {}
      dailyCallRef.current = null;
    }
    activeConvIdRef.current = null;
    setCallEnded(true);
    setActiveConversation(null);
  };

  const toggleFullscreen = () => {
    if (!videoContainerRef.current) return;

    if (!document.fullscreenElement) {
      videoContainerRef.current.requestFullscreen().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen().then(() => setIsFullscreen(false)).catch(() => {});
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-slate-900 text-slate-100 relative overflow-hidden">
      {/* Top Header Bar inside Video View */}
      <div className="h-13 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-4 flex items-center justify-between shrink-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-semibold text-[12px]">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <Video size={13} className="text-cyan-400" />
            <span>Advisor · Video Session</span>
            <span className="text-[10px] text-cyan-400/70 font-mono">· Brandon Owens</span>
          </div>

          {/* Active Role Selector Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsRoleDropdownOpen(!isRoleDropdownOpen)}
              disabled={isInitializing}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[12px] font-medium transition-colors cursor-pointer ${
                isInitializing
                  ? 'bg-slate-800/50 border-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-800 hover:bg-slate-700/80 border-slate-700 text-slate-200'
              }`}
            >
              <currentRoleConfig.icon size={13} className="text-cyan-400" />
              <span>Perspective: <strong className="font-semibold text-white">{currentRoleConfig.badge}</strong></span>
              {!isInitializing && <ChevronDown size={12} className="text-slate-400 ml-0.5" />}
            </button>

            {isRoleDropdownOpen && !isInitializing && (
              <div className="absolute left-0 mt-1 w-80 bg-slate-800 rounded-xl shadow-2xl border border-slate-700 p-1.5 z-30 animate-in fade-in-50 duration-100 max-h-96 overflow-y-auto">
                <div className="px-2.5 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Switch Operational Perspective
                </div>
                {roles.map(r => (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => {
                      onRoleChange(r.id);
                      setIsRoleDropdownOpen(false);
                    }}
                    className={`w-full text-left p-2 rounded-lg flex items-start gap-2.5 text-[12px] transition-colors cursor-pointer ${
                      userRole === r.id ? 'bg-cyan-500/20 text-cyan-200 font-semibold border border-cyan-500/30' : 'hover:bg-slate-700/60 text-slate-300'
                    }`}
                  >
                    <r.icon size={14} className={`shrink-0 mt-0.5 ${userRole === r.id ? 'text-cyan-400' : 'text-slate-400'}`} />
                    <div>
                      <div className="flex items-center justify-between">
                        <span>{r.title}</span>
                        {userRole === r.id && <Check size={12} className="text-cyan-400" />}
                      </div>
                      <div className="text-[10.5px] text-slate-400 font-normal leading-tight mt-0.5">
                        {r.description}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onBackToHub && (
            <button
              type="button"
              onClick={onBackToHub}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[12px] font-medium transition-colors cursor-pointer"
            >
              <span>Advisor Hub</span>
            </button>
          )}

          {/* Switch to Text Chat */}
          <button
            type="button"
            onClick={onSwitchToChat}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[12px] font-medium transition-colors cursor-pointer"
          >
            <MessageSquare size={13} className="text-cyan-400" />
            <span>Switch to Chat</span>
          </button>
        </div>
      </div>

      {/* Main Content Area: Connecting Screen vs Active Call vs Post Call */}
      <div className="flex-1 flex overflow-hidden">
        {/* DIRECT CONNECTING SCREEN (NO WAITING ROOM) */}
        {!activeConversation && !callEnded && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center">
            <div className="max-w-xl w-full text-center space-y-6">
              {/* Radar Connection Pulse */}
              <div className="relative inline-flex items-center justify-center">
                <div className="w-24 h-24 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center animate-pulse">
                  <div className="w-16 h-16 rounded-full bg-cyan-500/20 border border-cyan-400/50 flex items-center justify-center">
                    <User size={32} className="text-cyan-400" />
                  </div>
                </div>
                <RefreshCw size={24} className="text-cyan-400 animate-spin absolute -top-1 -right-1" />
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-white">
                  Connecting Live Video Session...
                </h2>
                <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
                  Launching real-time conversational video room with <strong className="text-cyan-300 font-semibold">Brandon Owens (April 14 2026)</strong>.
                </p>
              </div>

              {/* Active Perspectives & Brain */}
              <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700 text-xs text-slate-200">
                  <currentRoleConfig.icon size={13} className="text-cyan-400" />
                  <span>Adopting: <strong className="text-white">{currentRoleConfig.badge}</strong></span>
                </div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700 text-xs text-slate-200">
                  <Sparkles size={13} className="text-emerald-400" />
                  <span>Knowledge Brain: <strong className="text-white">US Energy Innovation Database by Brandon N. Owens (56,413 Awards · $104.16B)</strong></span>
                </div>
              </div>

              {/* Error Banner if any */}
              {errorMessage && (
                <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-3 text-left">
                  <div className="flex items-center gap-2">
                    <AlertCircle size={16} className="shrink-0 text-rose-400" />
                    <span>{errorMessage}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      type="button"
                      onClick={handleStartCall}
                      className="px-3 py-1.5 rounded-lg bg-rose-500 text-white text-xs font-semibold hover:bg-rose-600 transition-colors cursor-pointer"
                    >
                      Retry Connection
                    </button>
                    <button
                      type="button"
                      onClick={onSwitchToChat}
                      className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 text-xs hover:bg-slate-800 transition-colors cursor-pointer"
                    >
                      Switch to Advisory Chat
                    </button>
                  </div>
                </div>
              )}

              {/* Privacy Notice */}
              <div className="flex items-center justify-center gap-4 text-[11px] text-slate-500 pt-2">
                <span className="flex items-center gap-1">
                  <ShieldCheck size={12} className="text-emerald-400" />
                  <span>Enterprise WebRTC Encrypted</span>
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <Sparkles size={12} className="text-cyan-400" />
                  <span>Sub-second Neural Streaming</span>
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ACTIVE LIVE VIDEO CALL */}
        {activeConversation && !callEnded && (
          <div className="flex-1 flex flex-col md:flex-row h-full overflow-hidden">
            {/* Left: Video Frame Container Managed by Daily.js */}
            <div className="flex-1 flex flex-col bg-black relative overflow-hidden">
              <div
                ref={videoContainerRef}
                className="w-full h-full flex-1"
              />

              {/* Floating Bottom In-Call Bar */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md border border-slate-700 px-4 py-2.5 rounded-2xl shadow-2xl flex items-center gap-3.5 z-30">
                {/* Live Timer Pill */}
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-[11.5px] font-mono text-cyan-300">
                  <Clock size={12} className="text-cyan-400" />
                  <span>{formatTimer(callDuration)}</span>
                </div>

                {/* Role Pill */}
                <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 text-[11.5px] text-slate-300 font-medium">
                  <currentRoleConfig.icon size={12} className="text-cyan-400" />
                  <span>{currentRoleConfig.badge}</span>
                </div>

                {/* Live Mic Voice Sync Indicator */}
                {isListeningMic && (
                  <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/80 border border-emerald-500/40 text-[11px] text-emerald-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    <Mic size={11} className="text-emerald-400" />
                    <span>Voice Intel Active</span>
                  </div>
                )}

                {/* Fullscreen Toggle */}
                <button
                  type="button"
                  onClick={toggleFullscreen}
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
                  title="Toggle Fullscreen"
                >
                  {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>

                {/* End Call Button */}
                <button
                  type="button"
                  onClick={handleEndCall}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shadow-lg shadow-rose-600/30 transition-all cursor-pointer"
                >
                  <PhoneOff size={14} />
                  <span>End Session</span>
                </button>
              </div>
            </div>

            {/* Right: In-Call Real-Time Synchronized Intelligence Panel */}
            <div className="w-full md:w-84 lg:w-96 bg-slate-900 border-t md:border-t-0 md:border-l border-slate-800 flex flex-col shrink-0 overflow-hidden">
              {/* Header & Real-time Topic Banner */}
              <div className="p-3 border-b border-slate-800 space-y-2.5 shrink-0 bg-slate-950/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-200">
                    <Sparkles size={13} className="text-cyan-400" />
                    <span>Real-Time Intelligence</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {isSyncing ? (
                      <span className="text-[10px] font-mono text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30 flex items-center gap-1">
                        <RefreshCw size={10} className="animate-spin text-cyan-400" />
                        <span>Synthesizing...</span>
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => performPeriodicSynthesis()}
                        className="text-[10px] font-mono text-slate-300 bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded border border-slate-700 flex items-center gap-1 cursor-pointer transition-colors"
                        title="Click to synthesize and sync database now"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span>Syncs in {secondsUntilNextSync}s</span>
                        <span className="text-cyan-400 font-bold ml-0.5">· Sync Now</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Live Topic Search Bar */}
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    if (liveTopicSearch) {
                      performPeriodicSynthesis(liveTopicSearch);
                    }
                  }}
                  className="relative"
                >
                  <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={liveTopicSearch}
                    onChange={e => setLiveTopicSearch(e.target.value)}
                    placeholder="Search database or focus topic..."
                    className="w-full pl-7 pr-14 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-[11.5px] text-slate-200 placeholder:text-slate-500 focus:outline-hidden focus:border-cyan-500"
                  />
                  <button
                    type="submit"
                    disabled={isSyncing}
                    className="absolute right-1 top-1/2 -translate-y-1/2 px-2 py-0.8 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px] font-bold cursor-pointer disabled:opacity-50"
                  >
                    Sync
                  </button>
                </form>

                {/* Tab Switcher */}
                <div className="grid grid-cols-3 gap-1 bg-slate-800/80 p-1 rounded-xl text-[11px] font-medium">
                  <button
                    type="button"
                    onClick={() => setSidecarTab('citations')}
                    className={`py-1 rounded-lg transition-all cursor-pointer ${
                      sidecarTab === 'citations'
                        ? 'bg-cyan-500 text-slate-950 font-bold shadow-xs'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Intelligence ({ragCitations ? (ragCitations.opportunities.length + ragCitations.awards.length) : '0'})
                  </button>
                  <button
                    type="button"
                    onClick={() => setSidecarTab('questions')}
                    className={`py-1 rounded-lg transition-all cursor-pointer ${
                      sidecarTab === 'questions'
                        ? 'bg-cyan-500 text-slate-950 font-bold shadow-xs'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Questions
                  </button>
                  <button
                    type="button"
                    onClick={() => setSidecarTab('notes')}
                    className={`py-1 rounded-lg transition-all cursor-pointer ${
                      sidecarTab === 'notes'
                        ? 'bg-cyan-500 text-slate-950 font-bold shadow-xs'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Notes
                  </button>
                </div>
              </div>

              {/* Tab Content Body */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3 text-xs">
                {/* TAB 1: SYNCHRONIZED INTELLIGENCE & CITATIONS */}
                {sidecarTab === 'citations' && (
                  <div className="space-y-3">
                    {/* Clean Blank Slate State before discussion starts */}
                    {(!ragCitations || (ragCitations.opportunities.length === 0 && ragCitations.awards.length === 0)) ? (
                      <div className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/50 text-center space-y-3.5 my-auto">
                        <div className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 text-cyan-400 flex items-center justify-center mx-auto shadow-inner">
                          <Mic size={20} className="animate-pulse" />
                        </div>
                        <div className="space-y-1">
                          <div className="font-bold text-white text-[13.5px]">
                            Live Database Grounding
                          </div>
                          <p className="text-[12px] text-slate-400 leading-relaxed max-w-xs mx-auto">
                            The intelligence panel dynamically synthesizes conversation every 30 seconds, pulling relevant funding opportunities, past awards, and verified institutions from the database.
                          </p>
                        </div>
                        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-700/80 text-[10.5px] font-mono text-cyan-300">
                          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                          <span>Listening to dialogue...</span>
                        </div>
                      </div>
                    ) : (
                      /* Active Grounded Database Records */
                      <>
                        {/* Executive Discussion Gist & Focus Card */}
                        <div className="p-3 rounded-xl bg-gradient-to-br from-slate-800/90 via-slate-800/60 to-cyan-950/30 border border-slate-700/80 shadow-xs space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[9.5px] font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                              <Sparkles size={11} className="text-cyan-400" />
                              <span>Discussion Gist &amp; Focus:</span>
                            </span>
                            <span className="text-[9px] font-mono text-slate-400 bg-slate-900/80 px-1.5 py-0.5 rounded border border-slate-700/50">
                              30s AI Sync
                            </span>
                          </div>

                          <div className="space-y-1">
                            <div className="font-semibold text-white text-[12px] leading-snug">
                              {detectedTopic || 'Clean Energy Discussion'}
                            </div>
                            {executiveGist && (
                              <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-900/40 p-2 rounded-lg border border-slate-800/80">
                                {executiveGist}
                              </p>
                            )}
                          </div>

                          {keyEntities && keyEntities.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-0.5">
                              {keyEntities.map((ent, idx) => (
                                <span
                                  key={idx}
                                  className="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-700/40 text-cyan-300"
                                >
                                  {ent}
                                </span>
                              ))}
                            </div>
                          )}

                          {liveSpokenText && (
                            <div className="text-[10px] text-slate-400 italic line-clamp-1 pt-0.5 flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                              <span className="truncate">&ldquo;{liveSpokenText}&rdquo;</span>
                            </div>
                          )}
                        </div>

                        {/* MATCHING SOLICITATIONS & OPPORTUNITIES */}
                        {ragCitations.opportunities && ragCitations.opportunities.length > 0 && (
                          <div className="space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1">
                                <FileText size={11} />
                                <span>Matching Solicitations ({ragCitations.opportunities.length}):</span>
                              </span>
                              <Link to="/opportunities" target="_blank" className="text-[10px] text-cyan-400 hover:underline">
                                Directory &rarr;
                              </Link>
                            </div>
                            <div className="space-y-1">
                              {ragCitations.opportunities.slice(0, 5).map(o => (
                                <Link
                                  key={o.id}
                                  to={o.url}
                                  target="_blank"
                                  className="flex items-center justify-between p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 hover:border-cyan-500/50 hover:bg-slate-800 transition-all text-slate-200 group"
                                >
                                  <div className="truncate pr-2">
                                    <span className="font-semibold text-white group-hover:text-cyan-300">{o.agency} · {o.solicitation_number}</span>
                                    <span className="text-slate-400 text-[10.5px] ml-1.5 truncate block">{o.name}</span>
                                  </div>
                                  <div className="flex items-center gap-1.5 shrink-0">
                                    {o.total_funding ? (
                                      <span className="font-mono text-[10px] text-emerald-300 font-bold bg-emerald-500/20 px-1.5 py-0.5 rounded border border-emerald-500/30">
                                        ${(o.total_funding / 1e6).toFixed(1)}M
                                      </span>
                                    ) : null}
                                    <ExternalLink size={11} className="text-slate-500 group-hover:text-cyan-400" />
                                  </div>
                                </Link>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* MATCHING HISTORICAL AWARDS */}
                        {ragCitations.awards && ragCitations.awards.length > 0 && (
                          <div className="space-y-1.5 pt-1 border-t border-slate-800">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                                <Trophy size={11} />
                                <span>Historical Awards &amp; Comps ({ragCitations.awards.length}):</span>
                              </span>
                              <Link to="/awards" target="_blank" className="text-[10px] text-emerald-400 hover:underline">
                                All Awards &rarr;
                              </Link>
                            </div>
                            <div className="space-y-1">
                              {ragCitations.awards.slice(0, 5).map(awd => (
                                <Link
                                  key={awd.id}
                                  to={awd.url}
                                  target="_blank"
                                  className="flex items-center justify-between p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 hover:border-emerald-500/50 hover:bg-slate-800 transition-all text-slate-200 group"
                                >
                                  <div className="truncate pr-2">
                                    <span className="font-semibold text-white group-hover:text-emerald-300 truncate block">
                                      {awd.project_title || 'Clean Energy Demonstration'}
                                    </span>
                                    <span className="text-slate-400 text-[10.5px] truncate block">
                                      {awd.recipient_name} {awd.year ? `(${awd.year})` : ''}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-1.5 shrink-0">
                                    {awd.award_amount ? (
                                      <span className="font-mono text-[10px] text-emerald-300 font-bold bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-800/40">
                                        ${(awd.award_amount / 1e6).toFixed(1)}M
                                      </span>
                                    ) : null}
                                    <ExternalLink size={11} className="text-slate-500 group-hover:text-emerald-400" />
                                  </div>
                                </Link>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* VERIFIED ORGANIZATIONS */}
                        {ragCitations.organizations && ragCitations.organizations.length > 0 && (
                          <div className="space-y-1.5 pt-1 border-t border-slate-800">
                            <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider block">
                              Verified Recipient Entities ({ragCitations.organizations.length}):
                            </span>
                            <div className="space-y-1">
                              {ragCitations.organizations.slice(0, 4).map(org => (
                                <div key={org.id} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 text-[11px]">
                                  <span className="truncate text-slate-200 font-medium">
                                    {org.name} <span className="text-slate-500">({org.state || 'US'})</span>
                                  </span>
                                  <span className="font-mono font-bold text-cyan-300 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/40 text-[10px] shrink-0 ml-1.5">
                                    {org.total_funding ? `$${(org.total_funding / 1e6).toFixed(1)}M` : `${org.awards_count || 1} awards`}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {/* TAB 2: SPOKEN QUESTIONS */}
                {sidecarTab === 'questions' && (
                  <div className="space-y-2">
                    <span className="text-[10.5px] font-bold text-slate-400 uppercase tracking-wider block">
                      Recommended Questions to Ask Aloud:
                    </span>
                    <div className="space-y-1.5">
                      {currentRoleConfig.spokenStarters?.map((q, idx) => (
                        <div
                          key={idx}
                          onClick={() => performPeriodicSynthesis(q)}
                          className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-[11.5px] text-slate-300 hover:border-cyan-500/50 hover:bg-slate-800 transition-colors cursor-pointer"
                        >
                          <span className="text-cyan-400 font-bold mr-1.5">&rarr;</span>
                          <span>{q}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* TAB 3: NOTES & DATABASE SCAN */}
                {sidecarTab === 'notes' && (
                  <div className="space-y-3 flex flex-col h-full">
                    <div className="space-y-1.5">
                      <span className="text-[10.5px] font-bold text-slate-400 uppercase tracking-wider block">
                        Live Advisory Notes:
                      </span>
                      <textarea
                        value={notes}
                        onChange={e => setNotes(e.target.value)}
                        placeholder="Type session takeaways or grant numbers discussed aloud..."
                        className="w-full h-36 p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-[12px] text-slate-200 placeholder:text-slate-500 focus:outline-hidden focus:border-cyan-500 resize-none"
                      />
                    </div>

                    <button
                      type="button"
                      onClick={handleReviewNotes}
                      disabled={isReviewingNotes || !notes.trim()}
                      className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-semibold text-xs transition-colors cursor-pointer"
                    >
                      {isReviewingNotes ? (
                        <>
                          <RefreshCw size={13} className="animate-spin" />
                          <span>Scanning &amp; Linking Database...</span>
                        </>
                      ) : (
                        <>
                          <Search size={13} />
                          <span>Scan Notes &amp; Link to Database</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Sidecar Footer */}
              <div className="p-3 border-t border-slate-800 bg-slate-950/40 shrink-0">
                <button
                  type="button"
                  onClick={onSwitchToChat}
                  className="w-full inline-flex items-center justify-center gap-1.5 p-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-medium transition-colors cursor-pointer"
                >
                  <FileText size={13} className="text-cyan-400" />
                  <span>Generate Full Monograph in Chat</span>
                  <ArrowRight size={12} className="text-slate-400" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* POST-CALL DEBRIEF WITH FULL SYNCHRONIZED INTELLIGENCE */}
        {callEnded && (
          <div className="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center">
            <div className="max-w-lg w-full bg-slate-800 rounded-2xl border border-slate-700 p-6 text-center space-y-5 shadow-2xl">
              <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
                <Check size={24} />
              </div>

              <div className="space-y-1">
                <h3 className="text-xl font-bold text-white">Video Advisory Concluded</h3>
                <p className="text-xs text-slate-400">
                  Session duration: <strong className="text-cyan-400 font-mono">{formatTimer(callDuration)}</strong> · Perspective: <strong className="text-slate-200">{currentRoleConfig.badge}</strong>
                </p>
              </div>

              {/* Executive Summary in Debrief */}
              {executiveGist && (
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-700 text-left space-y-2 text-xs">
                  <span className="font-semibold text-slate-300 text-[10.5px] uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles size={13} className="text-cyan-400" />
                    <span>Executive Session Gist:</span>
                  </span>
                  <p className="text-slate-200 leading-relaxed text-[11.5px]">
                    {executiveGist}
                  </p>
                </div>
              )}

              {/* Grounded Citations Summary */}
              {ragCitations && (
                <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-700 text-left space-y-2 text-xs">
                  <span className="font-semibold text-slate-400 text-[10px] uppercase flex items-center gap-1">
                    <ShieldCheck size={12} className="text-emerald-400" />
                    <span>Grounded Database Cross-References ({ragCitations.opportunities.length + (ragCitations.organizations?.length || 0)} Entities Verified):</span>
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {ragCitations.opportunities.slice(0, 3).map(o => (
                      <Link
                        key={o.id}
                        to={o.url}
                        target="_blank"
                        className="px-2 py-0.5 rounded-md bg-cyan-950 border border-cyan-800/60 text-cyan-300 hover:bg-cyan-900 text-[11px] font-mono"
                      >
                        {o.solicitation_number}
                      </Link>
                    ))}
                    {ragCitations.organizations?.slice(0, 3).map(org => (
                      <span key={org.id} className="px-2 py-0.5 rounded-md bg-blue-950 border border-blue-800/60 text-blue-300 text-[11px]">
                        {org.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {notes && (
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-700 text-left text-xs space-y-1">
                  <span className="font-semibold text-slate-400 text-[10px] uppercase">Your Session Notes:</span>
                  <p className="text-slate-300 whitespace-pre-wrap">{notes}</p>
                </div>
              )}

              <div className="space-y-2 pt-2">
                <button
                  type="button"
                  onClick={onSwitchToChat}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-xs shadow-md cursor-pointer"
                >
                  <MessageSquare size={14} />
                  <span>Continue in Advisory Chat</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setCallEnded(false);
                    setActiveConversation(null);
                    handleStartCall();
                  }}
                  className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium cursor-pointer"
                >
                  <RefreshCw size={14} />
                  <span>Start New Video Session</span>
                </button>

                {onBackToHub && (
                  <button
                    type="button"
                    onClick={onBackToHub}
                    className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl border border-slate-700 hover:bg-slate-700/50 text-slate-400 hover:text-white text-xs font-medium cursor-pointer transition-colors"
                  >
                    <span>Return to Advisor Hub</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
