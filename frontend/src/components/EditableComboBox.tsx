import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, X, Search, Sliders } from 'lucide-react';

export interface ComboBoxOption {
  value: string;
  label?: string;
  group?: string;
  description?: string;
}

export interface EditableComboBoxProps {
  value: string;
  onChange: (value: string) => void;
  options: Array<string | ComboBoxOption>;
  placeholder?: string;
  label?: string;
  subLabel?: string;
  badge?: string;
  multiline?: boolean;
  rows?: number;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  allowCustom?: boolean;
  onSelectOption?: (option: string) => void;
}

export const EditableComboBox: React.FC<EditableComboBoxProps> = ({
  value,
  onChange,
  options,
  placeholder = 'Type or select an option...',
  label,
  subLabel,
  badge,
  multiline = false,
  rows = 3,
  className = '',
  disabled = false,
  required = false,
  error,
  allowCustom = true,
  onSelectOption
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Normalize options to structured format
  const normalizedOptions: ComboBoxOption[] = options.map(opt => {
    if (typeof opt === 'string') {
      return { value: opt, label: opt };
    }
    return {
      value: opt.value,
      label: opt.label || opt.value,
      group: opt.group,
      description: opt.description
    };
  });

  // Filter options based on search term
  const filteredOptions = normalizedOptions.filter(opt => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    const matchesLabel = opt.label?.toLowerCase().includes(term);
    const matchesValue = opt.value.toLowerCase().includes(term);
    const matchesDesc = opt.description?.toLowerCase().includes(term);
    const matchesGroup = opt.group?.toLowerCase().includes(term);
    return matchesLabel || matchesValue || matchesDesc || matchesGroup;
  });

  // Group options if group is present
  const groupedOptions: Record<string, ComboBoxOption[]> = {};
  filteredOptions.forEach(opt => {
    const groupKey = opt.group || 'Suggestions';
    if (!groupedOptions[groupKey]) {
      groupedOptions[groupKey] = [];
    }
    groupedOptions[groupKey].push(opt);
  });

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (selectedVal: string) => {
    onChange(selectedVal);
    if (onSelectOption) {
      onSelectOption(selectedVal);
    }
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange('');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <div ref={containerRef} className={`relative space-y-1.5 ${className}`}>
      {(label || badge) && (
        <div className="flex items-center justify-between">
          <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1.5">
            <span>{label}</span>
            {required && <span className="text-rose-500">*</span>}
          </label>
          {badge && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
              <Sliders size={10} />
              {badge}
            </span>
          )}
        </div>
      )}

      {subLabel && (
        <p className="text-[11px] text-slate-500 leading-tight">{subLabel}</p>
      )}

      {/* Input container */}
      <div className="relative group">
        {multiline ? (
          <textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            rows={rows}
            value={value}
            disabled={disabled}
            onChange={e => onChange(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className={`w-full text-xs rounded-lg border p-2.5 pr-14 font-medium text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition ${
              error
                ? 'border-rose-300 bg-rose-50/30'
                : 'border-slate-200 bg-slate-50/50 hover:bg-white focus:bg-white'
            } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
          />
        ) : (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type="text"
            value={value}
            disabled={disabled}
            onChange={e => onChange(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className={`w-full text-xs rounded-lg border p-2.5 pr-14 font-medium text-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none transition ${
              error
                ? 'border-rose-300 bg-rose-50/30'
                : 'border-slate-200 bg-slate-50/50 hover:bg-white focus:bg-white'
            } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
          />
        )}

        {/* Action icons (Clear + Chevron) */}
        <div className="absolute right-2 top-2.5 flex items-center gap-1 text-slate-400">
          {value && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:text-slate-600 rounded transition"
              title="Clear input"
            >
              <X size={13} />
            </button>
          )}
          <button
            type="button"
            disabled={disabled}
            onClick={() => setIsOpen(!isOpen)}
            className={`p-1 hover:text-slate-600 rounded transition ${isOpen ? 'rotate-180 text-indigo-600' : ''}`}
            title="Toggle suggestions"
          >
            <ChevronDown size={14} />
          </button>
        </div>
      </div>

      {error && (
        <p className="text-[11px] text-rose-600 font-medium">{error}</p>
      )}

      {/* Floating Suggestions Dropdown */}
      {isOpen && !disabled && (
        <div className="absolute z-50 left-0 right-0 mt-1 bg-white rounded-xl border border-slate-200 shadow-xl max-h-72 overflow-y-auto divide-y divide-slate-100 animate-in fade-in zoom-in-95 duration-100">
          {/* Quick Filter Bar when more than 5 options */}
          {normalizedOptions.length > 5 && (
            <div className="p-2 bg-slate-50/80 sticky top-0 backdrop-blur-xs border-b border-slate-100">
              <div className="relative">
                <Search size={12} className="absolute left-2.5 top-2 text-slate-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  placeholder="Filter suggestions..."
                  className="w-full text-[11px] pl-7 pr-2.5 py-1 rounded-md border border-slate-200 bg-white focus:outline-indigo-500 text-slate-700"
                  onClick={e => e.stopPropagation()}
                />
              </div>
            </div>
          )}

          {/* Grouped Options List */}
          {Object.keys(groupedOptions).length === 0 ? (
            <div className="p-3 text-center text-xs text-slate-400">
              No matching suggestions. You can type your custom entry above.
            </div>
          ) : (
            Object.entries(groupedOptions).map(([groupName, items]) => (
              <div key={groupName} className="py-1">
                {Object.keys(groupedOptions).length > 1 && (
                  <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-50/50">
                    {groupName}
                  </div>
                )}
                {items.map(opt => {
                  const isSelected = value === opt.value;
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => handleSelect(opt.value)}
                      className={`w-full text-left px-3 py-2 text-xs flex items-start justify-between gap-2 hover:bg-indigo-50/70 transition cursor-pointer ${
                        isSelected ? 'bg-indigo-50 font-semibold text-indigo-900' : 'text-slate-700'
                      }`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="truncate">{opt.label}</span>
                          {isSelected && <Check size={13} className="text-indigo-600 shrink-0" />}
                        </div>
                        {opt.description && (
                          <p className="text-[10px] text-slate-500 leading-tight mt-0.5 line-clamp-2">
                            {opt.description}
                          </p>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
