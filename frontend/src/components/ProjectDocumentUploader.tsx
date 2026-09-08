import React, { useState, useRef, useCallback } from 'react';
import {
  Upload, FileText, FileSpreadsheet, Presentation, CheckCircle2,
  AlertCircle, Loader2, Sparkles, X, Trash2, ArrowRight, ShieldCheck,
  Check, RefreshCw, FileCode
} from 'lucide-react';
import clsx from 'clsx';
import {
  api,
  ExtractedProjectProfile,
  DocumentExtractionResponse,
} from '../api/client';

interface ProjectDocumentUploaderProps {
  onProfileExtracted: (profile: ExtractedProjectProfile) => void;
  onDirectMatch?: (extractedData: any) => void;
  isAnalyzingParent?: boolean;
}

const SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.csv', '.txt', '.md', '.rtf'];
const ACCEPT_STRING = SUPPORTED_EXTENSIONS.join(',');

function getFileIcon(filename: string) {
  const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'));
  if (ext === '.pdf') {
    return <FileText className="text-red-500 shrink-0" size={16} />;
  }
  if (['.docx', '.doc'].includes(ext)) {
    return <FileText className="text-blue-500 shrink-0" size={16} />;
  }
  if (['.pptx', '.ppt'].includes(ext)) {
    return <Presentation className="text-amber-500 shrink-0" size={16} />;
  }
  if (['.xlsx', '.xls', '.csv'].includes(ext)) {
    return <FileSpreadsheet className="text-emerald-500 shrink-0" size={16} />;
  }
  return <FileCode className="text-slate-400 shrink-0" size={16} />;
}

function getFileBadge(filename: string) {
  const ext = filename.toLowerCase().slice(filename.lastIndexOf('.')).replace('.', '').toUpperCase();
  const colorMap: Record<string, string> = {
    PDF: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-500/30',
    DOCX: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-500/30',
    DOC: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-500/30',
    PPTX: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/30',
    PPT: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/30',
    XLSX: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30',
    CSV: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30',
    TXT: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
    MD: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700',
  };
  return (
    <span className={clsx('text-[9.5px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase', colorMap[ext] || 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-300')}>
      {ext || 'DOC'}
    </span>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ProjectDocumentUploader({
  onProfileExtracted,
  isAnalyzingParent = false,
}: ProjectDocumentUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressStep, setProgressStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [extractionResult, setExtractionResult] = useState<DocumentExtractionResponse | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;
    setError(null);

    const newFiles: File[] = [];
    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
      if (SUPPORTED_EXTENSIONS.includes(ext)) {
        if (!files.some(f => f.name === file.name && f.size === file.size)) {
          newFiles.push(file);
        }
      } else {
        setError(`File "${file.name}" has an unsupported format. Supported: PDF, DOCX, PPTX, XLSX, TXT, CSV`);
      }
    }

    if (newFiles.length > 0) {
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  }, [files]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    if (files.length <= 1) {
      setExtractionResult(null);
    }
  };

  const clearAll = () => {
    setFiles([]);
    setExtractionResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const executeExtraction = async () => {
    if (files.length === 0) return;
    setIsProcessing(true);
    setError(null);

    try {
      setProgressStep(`Extracting text from ${files.length} document${files.length > 1 ? 's' : ''}...`);
      await new Promise(r => setTimeout(r, 300));

      setProgressStep('Extracting project scope, TRL, budget, location & taxonomy with OpenAI...');

      const response = await api.uploadAndExtractProjectDocs(files);

      setExtractionResult(response);
      onProfileExtracted(response.extracted_profile);
      setProgressStep('Extraction complete!');
    } catch (err: any) {
      setError(err.message || 'Failed to analyze project documents');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-white/5">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-300 dark:border-indigo-500/30">
              <Upload size={12} className="text-indigo-600 dark:text-indigo-400" />
              <span>Document Extraction Engine</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-600">|</span>
            <span className="text-[11px] font-mono font-bold text-slate-500 dark:text-slate-400">
              PDF · DOCX · PPTX · XLSX · CSV · TXT
            </span>
          </div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mt-1.5 flex items-center gap-2">
            Upload Project Documents for Instant Auto-Characterization
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
            Upload technical proposals, pitch decks, TEA sheets, or executive summaries. OpenAI interprets the text, sets matching parameters, and surfaces target funding organizations.
          </p>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={clsx(
          'relative border-2 border-dashed rounded-xl p-6 transition-all text-center cursor-pointer flex flex-col items-center justify-center gap-2 group',
          isDragging
            ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20'
            : 'border-slate-300 dark:border-white/10 bg-slate-50/60 dark:bg-black/20 hover:border-indigo-400 hover:bg-slate-50 dark:hover:bg-white/[0.03]'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ACCEPT_STRING}
          onChange={e => handleFileSelect(e.target.files)}
          className="hidden"
        />

        <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center group-hover:scale-105 transition-transform">
          <Upload size={20} />
        </div>

        <div className="space-y-0.5">
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200">
            Drag &amp; drop project documents here, or <span className="text-indigo-600 dark:text-indigo-400 underline underline-offset-2">browse files</span>
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400">
            Supports multi-file upload (.pdf, .docx, .doc, .pptx, .xlsx, .csv, .txt)
          </div>
        </div>
      </div>

      {/* Selected Files Queue */}
      {files.length > 0 && (
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider text-[11px]">
              Uploaded Documents ({files.length} {files.length === 1 ? 'file' : 'files'} · {formatBytes(files.reduce((s, f) => s + f.size, 0))})
            </span>
            <button
              type="button"
              onClick={clearAll}
              className="text-slate-400 hover:text-rose-500 text-[11px] font-semibold transition-colors flex items-center gap-1 cursor-pointer"
            >
              <Trash2 size={11} />
              <span>Clear files</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
            {files.map((file, idx) => (
              <div
                key={`${file.name}-${idx}`}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 text-xs group"
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  {getFileIcon(file.name)}
                  <div className="min-w-0 flex-1">
                    <div className="font-semibold text-slate-800 dark:text-slate-200 truncate" title={file.name}>
                      {file.name}
                    </div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5 font-mono">
                      {getFileBadge(file.name)}
                      <span>{formatBytes(file.size)}</span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                  className="p-1 rounded-md text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-colors ml-2 cursor-pointer shrink-0"
                  title="Remove file"
                >
                  <X size={13} />
                </button>
              </div>
            ))}
          </div>

          {/* Action Trigger Button */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <Sparkles size={13} className="text-indigo-600 dark:text-indigo-400 shrink-0" />
              <span>LLM extracts project parameters and auto-fills matching settings below.</span>
            </div>

            <button
              type="button"
              onClick={executeExtraction}
              disabled={isProcessing || isAnalyzingParent}
              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold h-9 px-5 rounded-xl shadow-2xs hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer shrink-0"
            >
              {isProcessing ? (
                <>
                  <Loader2 size={13} className="animate-spin text-white" />
                  <span>Extracting Parameters...</span>
                </>
              ) : (
                <>
                  <Sparkles size={13} />
                  <span>Interpret &amp; Set Matching Parameters</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Progress / Status Message */}
      {isProcessing && (
        <div className="p-3.5 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200/80 dark:border-indigo-500/30 text-indigo-900 dark:text-indigo-200 text-xs flex items-center gap-2.5 animate-in fade-in duration-200">
          <Loader2 size={14} className="animate-spin text-indigo-600 dark:text-indigo-400 shrink-0" />
          <div className="font-mono text-xs">{progressStep || 'Processing documents with OpenAI...'}</div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-200 text-xs flex items-start gap-2 animate-in fade-in duration-200">
          <AlertCircle size={14} className="text-rose-500 shrink-0 mt-0.5" />
          <div>{error}</div>
        </div>
      )}

      {/* Extracted Insights Summary Card */}
      {extractionResult && (
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/10 space-y-3 animate-in fade-in slide-in-from-top-1 duration-200">
          <div className="flex items-start justify-between gap-3 pb-2.5 border-b border-slate-200/60 dark:border-white/5">
            <div>
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30 text-[10px] font-bold flex items-center gap-1">
                  <CheckCircle2 size={11} /> Project Interpreted
                </span>
                <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 font-semibold">
                  {extractionResult.total_files} Documents · {extractionResult.total_words.toLocaleString()} Words
                </span>
              </div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
                {extractionResult.extracted_profile.project_title}
              </h4>
            </div>

            <button
              type="button"
              onClick={executeExtraction}
              className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-semibold flex items-center gap-1 transition-colors cursor-pointer shrink-0"
              title="Re-run extraction"
            >
              <RefreshCw size={11} />
              <span>Re-extract</span>
            </button>
          </div>

          {/* Quick parameter pills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
            <div className="p-2 rounded-lg bg-white dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/5">
              <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">TRL Stage</div>
              <div className="font-bold text-indigo-600 dark:text-indigo-400 font-mono mt-0.5">TRL {extractionResult.extracted_profile.estimated_trl}</div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{extractionResult.extracted_profile.trl_rationale}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/5">
              <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">Budget / CapEx</div>
              <div className="font-bold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">
                ${(extractionResult.extracted_profile.estimated_cost / 1_000_000).toFixed(1)}M
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{extractionResult.extracted_profile.cost_rationale}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/5">
              <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">Location</div>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5 truncate">
                {extractionResult.extracted_profile.location}
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">Applicant: {extractionResult.extracted_profile.applicant_type}</div>
            </div>
            <div className="p-2 rounded-lg bg-white dark:bg-white/[0.03] border border-slate-200/80 dark:border-white/5">
              <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">Primary Sector</div>
              <div className="font-bold text-slate-900 dark:text-white mt-0.5 truncate">
                {extractionResult.extracted_profile.technology_areas.slice(0, 2).join(', ')}
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                {extractionResult.extracted_profile.sectors?.[0] || 'Clean Energy'}
              </div>
            </div>
          </div>

          <div className="flex items-center text-xs pt-0.5 text-emerald-700 dark:text-emerald-300 font-medium">
            <Check size={13} className="text-emerald-600 dark:text-emerald-400 mr-1.5 shrink-0" />
            <span>Matching parameters configured below. Click &ldquo;Match Opportunities&rdquo; to execute multi-agency matching.</span>
          </div>
        </div>
      )}
    </div>
  );
}
