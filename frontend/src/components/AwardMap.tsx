import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as maptilersdk from '@maptiler/sdk';
import '@maptiler/sdk/dist/maptiler-sdk.css';
import {
  Layers, MapPin, DollarSign, Compass, Maximize2, RotateCcw,
  Sparkles, Download, Eye, EyeOff, Radio, Circle, Globe,
  ZoomIn, ZoomOut, Flame, Filter, ChevronRight, ChevronDown, ChevronUp, BarChart2,
  Building2, ExternalLink, Sliders, Box, HelpCircle, Info
} from 'lucide-react';
import { AwardMapMarker, AwardMapSummary } from '../api/client';
import { OrgLogo } from './OrgLogo';
import { AwardDossierDrawer } from './AwardDossierDrawer';
import { AwardMapNYTExport } from './AwardMapNYTExport';

// MapTiler API Key
maptilersdk.config.apiKey = 'SHVkNkVhetk6rqMgmb1q';

interface AwardMapProps {
  markers: AwardMapMarker[];
  summary?: AwardMapSummary | null;
  isLoading?: boolean;
  activeFiltersDesc?: string;
  onSelectState?: (stateCode: string) => void;
  onRadiusChange?: (lat: number | null, lng: number | null, miles: number | null) => void;
}

// Color palettes for different categorical modes
const AGENCY_COLORS: Record<string, string> = {
  'DOE': '#4F46E5',
  'DOE-EERE': '#4338CA',
  'DOE-SC': '#6366F1',
  'DOE-OCED': '#3730A3',
  'NSF': '#059669',
  'ARPA-E': '#D97706',
  'EPA': '#0284C7',
  'NYSERDA': '#7C3AED',
  'Gates Foundation': '#0D9488',
  'DOD': '#DC2626',
  'NASA': '#2563EB',
  'USDA': '#65A30D',
  'DOT': '#EA580C',
  'MassCEC': '#0891B2',
  'CEC': '#059669',
  'Con Edison': '#E11D48',
  'National Grid': '#2563EB',
  'NYSEG': '#16A34A',
  'Central Hudson': '#D97706',
  'NYPA': '#4F46E5',
};

const TECH_COLORS: Record<string, string> = {
  'Grid Modernization & Smart Grid': '#4F46E5',
  'Energy Storage': '#059669',
  'Electric Vehicles & Clean Transit': '#D97706',
  'Solar PV': '#EAB308',
  'Building Envelope & Efficiency': '#0284C7',
  'Energy Efficiency': '#0D9488',
  'Bioenergy & Biogas': '#16A34A',
  'Electric Vehicles': '#EA580C',
  'Power Electronics & Inverters': '#7C3AED',
  'AI/ML': '#EC4899',
  'Hydrogen': '#06B6D4',
  'Wind': '#38BDF8',
  'Nuclear': '#8B5CF6',
  'Carbon Management': '#64748B',
};

const SECTOR_COLORS: Record<string, string> = {
  'Electric Grid & Utility': '#4F46E5',
  'Defense & National Security': '#DC2626',
  'Education': '#059669',
  'Industry & Manufacturing': '#D97706',
  'Buildings': '#0284C7',
  'Transportation': '#EA580C',
  'Utility/Grid': '#6366F1',
  'Commercial': '#0D9488',
  'Government & Municipal': '#7C3AED',
};

const FUEL_COLORS: Record<string, string> = {
  'Electricity': '#4F46E5',
  'Storage & Chemical': '#059669',
  'Nuclear': '#8B5CF6',
  'Solar': '#EAB308',
  'Wind': '#0284C7',
  'Hydrogen': '#06B6D4',
  'Biomass & Biogas': '#16A34A',
  'Geothermal': '#EA580C',
};

const STAGE_COLORS: Record<string, string> = {
  'Applied R&D & Innovation': '#4F46E5',
  'Fundamental R&D': '#059669',
  'Workforce Development': '#D97706',
  'Pilot & Demonstration': '#0284C7',
  'Deployment & Infrastructure': '#7C3AED',
  'Commercialization & Scale': '#0D9488',
  'Technical Assistance': '#EA580C',
};

const TYPE_COLORS: Record<string, string> = {
  'university': '#059669',
  'company': '#4F46E5',
  'lab': '#7C3AED',
  'nonprofit': '#0D9488',
  'government': '#DC2626',
  'utility': '#EA580C',
};

const BRACKET_COLORS: Record<string, string> = {
  'Under $250K': '#94A3B8',
  '$250K - $1M': '#38BDF8',
  '$1M - $5M': '#4F46E5',
  '$5M - $20M': '#8B5CF6',
  '$20M+': '#059669',
};

const VINTAGE_COLORS: Record<string, string> = {
  '2024 - 2026': '#059669',
  '2021 - 2023': '#4F46E5',
  '2018 - 2020': '#D97706',
  'Historic (<2018)': '#64748B',
};

export type ColorByMode = 'agency' | 'technology' | 'sector' | 'fuel' | 'stage' | 'type' | 'bracket' | 'vintage';
export type SizeByMode = 'funding' | 'uniform' | 'cost_share';
export type OutlineMode = 'white' | 'dark' | 'glow' | 'match' | 'none';

const COLOR_BY_OPTIONS: { id: ColorByMode; label: string; icon: string }[] = [
  { id: 'agency', label: 'Organization', icon: '🏛️' },
  { id: 'technology', label: 'Technology', icon: '⚡' },
  { id: 'sector', label: 'Sector', icon: '🏭' },
  { id: 'fuel', label: 'Clean Fuel', icon: '🌱' },
  { id: 'stage', label: 'Stage', icon: '📈' },
  { id: 'type', label: 'Entity Type', icon: '👥' },
  { id: 'bracket', label: 'Capital Bracket', icon: '💰' },
  { id: 'vintage', label: 'Award Vintage', icon: '📅' },
];

const SIZE_BY_OPTIONS: { id: SizeByMode; label: string; desc: string }[] = [
  { id: 'funding', label: 'Funding Amount', desc: 'Proportional to capital' },
  { id: 'uniform', label: 'Uniform Size', desc: 'Constant pin radius' },
  { id: 'cost_share', label: 'Cost Share', desc: 'Match investment' },
];

const OUTLINE_OPTIONS: { id: OutlineMode; label: string; swatch: string }[] = [
  { id: 'white', label: 'White Halo', swatch: '#FFFFFF' },
  { id: 'dark', label: 'Dark Slate', swatch: '#0F172A' },
  { id: 'glow', label: 'Neon Glow', swatch: '#38BDF8' },
  { id: 'match', label: 'Match Color', swatch: '#4F46E5' },
  { id: 'none', label: 'None', swatch: 'transparent' },
];

const MAP_STYLES = [
  { id: 'dataviz-light', label: 'Dataviz Light', icon: '☀️', style: maptilersdk.MapStyle.DATAVIZ.LIGHT },
  { id: 'dataviz-dark', label: 'Dataviz Dark', icon: '🌙', style: maptilersdk.MapStyle.DATAVIZ.DARK },
  { id: 'backdrop', label: 'Classic Editorial', icon: '📰', style: maptilersdk.MapStyle.BACKDROP.LIGHT },
  { id: 'outdoor', label: 'Outdoor Topo', icon: '🏔️', style: maptilersdk.MapStyle.OUTDOOR },
  { id: 'satellite', label: 'Satellite Hybrid', icon: '🛰️', style: maptilersdk.MapStyle.SATELLITE },
  { id: 'streets', label: 'Streets Nav', icon: '🗺️', style: maptilersdk.MapStyle.STREETS },
];

const PROJECTIONS = [
  { id: 'albers', label: 'Albers USA', desc: 'Equal Area' },
  { id: 'globe', label: '3D Globe', desc: 'Interactive Sphere' },
  { id: 'mercator', label: 'Mercator', desc: 'Standard Web' },
  { id: 'equalEarth', label: 'Equal Earth', desc: 'Preserves Area' },
];

const REGION_PRESETS = [
  { id: 'us', label: 'National US', center: [-98.35, 39.5] as [number, number], zoom: 3.8, pitch: 0, bearing: 0 },
  { id: 'ny', label: 'New York Innovation', center: [-75.5, 42.8] as [number, number], zoom: 6.8, pitch: 35, bearing: -10 },
  { id: 'ca', label: 'Silicon Valley / West', center: [-121.5, 37.5] as [number, number], zoom: 7.0, pitch: 40, bearing: 15 },
  { id: 'tx', label: 'Texas Energy Corridor', center: [-96.5, 30.5] as [number, number], zoom: 6.5, pitch: 30, bearing: 0 },
  { id: 'ne', label: 'Boston / Northeast', center: [-71.5, 42.5] as [number, number], zoom: 7.5, pitch: 35, bearing: -15 },
  { id: 'mw', label: 'Midwest Clean Belt', center: [-86.5, 41.5] as [number, number], zoom: 6.5, pitch: 20, bearing: 0 },
  { id: 'co', label: 'Colorado / NREL Hub', center: [-105.2, 39.8] as [number, number], zoom: 7.5, pitch: 45, bearing: 20 },
  { id: 'se', label: 'Oak Ridge / Southeast', center: [-84.3, 35.9] as [number, number], zoom: 7.0, pitch: 35, bearing: 10 },
];

function fmt(value?: number | null): string {
  if (!value) return '$0';
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value.toLocaleString()}`;
}

export const AwardMap: React.FC<AwardMapProps> = ({
  markers,
  summary,
  isLoading = false,
  activeFiltersDesc,
  onSelectState,
  onRadiusChange,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<maptilersdk.Map | null>(null);
  const hoverPopup = useRef<maptilersdk.Popup | null>(null);

  // UI State: Default to individual data points (clusters off) and legend open
  const [currentStyleId, setCurrentStyleId] = useState<string>('dataviz-light');
  const [currentProjection, setCurrentProjection] = useState<string>('albers');
  const [colorBy, setColorBy] = useState<ColorByMode>('agency');
  const [sizeBy, setSizeBy] = useState<SizeByMode>('funding');
  const [outlineMode, setOutlineMode] = useState<OutlineMode>('white');
  const [outlineWidth, setOutlineWidth] = useState<number>(1.6);
  const [legendTab, setLegendTab] = useState<'color' | 'size' | 'outline' | 'layers'>('color');
  
  const [enableTerrain, setEnableTerrain] = useState<boolean>(false);
  const [enableClusters, setEnableClusters] = useState<boolean>(true);
  const [enableHeatmap, setEnableHeatmap] = useState<boolean>(false);
  const [bubbleScale, setBubbleScale] = useState<number>(1.0);
  const [vintageFilter, setVintageFilter] = useState<'all' | '2024' | '2025' | '2026'>('all');
  const [isLegendOpen, setIsLegendOpen] = useState<boolean>(true);
  const [isLegendCollapsed, setIsLegendCollapsed] = useState<boolean>(false);
  
  // Radius tool state
  const [radiusMode, setRadiusMode] = useState<boolean>(false);
  const [radiusMiles, setRadiusMiles] = useState<number>(50);
  const [radiusCenter, setRadiusCenter] = useState<[number, number] | null>(null);

  // Slide-over Dossier & Executive Export Modals
  const [selectedAward, setSelectedAward] = useState<AwardMapMarker | null>(null);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);

  // Filter markers based on vintage quick-filter
  const filteredMarkers = useMemo(() => {
    if (vintageFilter === 'all') return markers;
    const targetYear = parseInt(vintageFilter);
    return markers.filter((m) => m.year === targetYear);
  }, [markers, vintageFilter]);

  // Active color palette
  const activeColorPalette = useMemo(() => {
    switch (colorBy) {
      case 'agency': return AGENCY_COLORS;
      case 'technology': return TECH_COLORS;
      case 'sector': return SECTOR_COLORS;
      case 'fuel': return FUEL_COLORS;
      case 'stage': return STAGE_COLORS;
      case 'type': return TYPE_COLORS;
      case 'bracket': return BRACKET_COLORS;
      case 'vintage': return VINTAGE_COLORS;
      default: return AGENCY_COLORS;
    }
  }, [colorBy]);

  const getMarkerCategory = (m: AwardMapMarker): string => {
    if (colorBy === 'technology') {
      const t = m.technologies?.[0] || m.primary_technology;
      return t || 'Energy Innovation';
    }
    if (colorBy === 'sector') {
      const s = m.sectors?.[0] || m.primary_sector;
      return s || 'Electric Grid & Utility';
    }
    if (colorBy === 'fuel') {
      const f = m.fuels?.[0] || m.primary_fuel;
      return f || 'Electricity';
    }
    if (colorBy === 'stage') {
      const st = m.stages?.[0] || m.stage;
      return st || 'Applied R&D & Innovation';
    }

    if (colorBy === 'type') {
      return (m.type || 'company').toLowerCase();
    }
    if (colorBy === 'bracket') {
      const amt = Number(m.amount) || 0;
      if (amt < 250000) return 'Under $250K';
      if (amt < 1000000) return '$250K - $1M';
      if (amt < 5000000) return '$1M - $5M';
      if (amt < 20000000) return '$5M - $20M';
      return '$20M+';
    }
    if (colorBy === 'vintage') {
      const y = Number(m.year) || 2020;
      if (y >= 2024) return '2024 - 2026';
      if (y >= 2021) return '2021 - 2023';
      if (y >= 2018) return '2018 - 2020';
      return 'Historic (<2018)';
    }
    return m.agency || 'Federal';
  };

  // Compute breakdown of categories in the current active marker set
  const legendBreakdown = useMemo(() => {
    const counts: Record<string, { count: number; funding: number }> = {};
    let totalFunding = 0;

    for (let i = 0; i < filteredMarkers.length; i++) {
      const m = filteredMarkers[i];
      const key = getMarkerCategory(m);
      const amt = Number(m.amount) || 0;
      if (!counts[key]) {
        counts[key] = { count: 0, funding: 0 };
      }
      counts[key].count += 1;
      counts[key].funding += amt;
      totalFunding += amt;
    }

    const items = Object.entries(counts)
      .sort((a, b) => b[1].count - a[1].count)
      .map(([name, data]) => ({
        name,
        count: data.count,
        funding: data.funding,
        color: activeColorPalette[name] || '#6366F1',
      }));

    return {
      items,
      totalCount: filteredMarkers.length,
      totalFunding,
    };
  }, [filteredMarkers, colorBy, activeColorPalette]);

  // Convert markers to GeoJSON FeatureCollection
  const geojsonData = useMemo(() => {
    const features: GeoJSON.Feature[] = [];

    for (let i = 0; i < filteredMarkers.length; i++) {
      const m = filteredMarkers[i];
      const lng = Number(m.lng);
      const lat = Number(m.lat);

      if (isNaN(lng) || isNaN(lat)) continue;

      const colorKey = getMarkerCategory(m);
      const pointColor = activeColorPalette[colorKey] || '#6366F1';
      const amt = Number(m.amount) || 0;

      let radius = 6.0 * bubbleScale;
      if (sizeBy === 'funding') {
        radius = Math.max(3.0, Math.min(24.0, Math.sqrt(Math.max(0, amt) / 40000) * 3.2 * bubbleScale));
      } else if (sizeBy === 'uniform') {
        radius = 5.5 * bubbleScale;
      } else if (sizeBy === 'cost_share') {
        const val = Math.max(0, amt * 0.25);
        radius = Math.max(3.0, Math.min(22.0, Math.sqrt(val / 30000) * 3.0 * bubbleScale));
      }

      if (isNaN(radius) || radius <= 0) radius = 5.0 * bubbleScale;

      let outlineColor = '#FFFFFF';
      if (outlineMode === 'dark') outlineColor = '#0F172A';
      else if (outlineMode === 'glow') outlineColor = '#38BDF8';
      else if (outlineMode === 'match') outlineColor = pointColor;
      else if (outlineMode === 'none') outlineColor = '#00000000';

      features.push({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [lng, lat],
        },
        properties: {
          id: m.id,
          name: m.name || '',
          title: m.title || '',
          amount: amt,
          amount_fmt: fmt(amt),
          agency: m.agency || 'Federal',
          year: m.year || '',
          type: m.type || 'organization',
          city: m.city || '',
          state: m.state || '',
          pi: m.pi || '',
          primary_tech: m.technologies?.[0] || m.primary_technology || 'Clean Tech',
          primary_sector: m.sectors?.[0] || m.primary_sector || 'Electric Grid',
          color: pointColor,
          outline_color: outlineColor,
          radius: radius,
        },
      });
    }

    return {
      type: 'FeatureCollection' as const,
      features,
    };
  }, [filteredMarkers, colorBy, sizeBy, outlineMode, activeColorPalette, bubbleScale]);

  // Dynamic references to ensure map event callbacks always access fresh state
  const geojsonDataRef = useRef(geojsonData);
  geojsonDataRef.current = geojsonData;

  const markersRef = useRef(markers);
  markersRef.current = markers;

  const enableClustersRef = useRef(enableClusters);
  enableClustersRef.current = enableClusters;

  const enableHeatmapRef = useRef(enableHeatmap);
  enableHeatmapRef.current = enableHeatmap;

  const outlineModeRef = useRef(outlineMode);
  outlineModeRef.current = outlineMode;

  const outlineWidthRef = useRef(outlineWidth);
  outlineWidthRef.current = outlineWidth;

  const radiusCenterRef = useRef(radiusCenter);
  radiusCenterRef.current = radiusCenter;

  const radiusMilesRef = useRef(radiusMiles);
  radiusMilesRef.current = radiusMiles;

  const radiusModeRef = useRef(radiusMode);
  radiusModeRef.current = radiusMode;

  // Hover Tooltip Handlers
  const handlePointMouseEnter = (e: any) => {
    const map = mapInstance.current;
    if (!map) return;
    map.getCanvas().style.cursor = 'pointer';
    if (!e.features?.[0]) return;
    const f = e.features[0];
    const props = f.properties;
    const coords = (f.geometry as any).coordinates.slice();

    const html = `
      <div style="font-family: system-ui, -apple-system, sans-serif; padding: 4px; max-width: 240px;">
        <div style="font-weight: 700; font-size: 13px; color: #0f172a; line-height: 1.2;">${props.name}</div>
        ${props.title ? `<div style="font-size: 11px; color: #475569; margin-top: 3px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${props.title}</div>` : ''}
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px; padding-top: 4px; border-top: 1px solid #e2e8f0; font-size: 11px;">
          <span style="font-weight: 800; color: #059669;">${props.amount_fmt}</span>
          <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600; color: #334155;">${props.agency}</span>
        </div>
        <div style="font-size: 10px; color: #64748b; margin-top: 4px;">
          ${[props.city, props.state].filter(Boolean).join(', ')} · ${props.primary_tech}
        </div>
      </div>
    `;

    hoverPopup.current?.setLngLat(coords).setHTML(html).addTo(map);
  };

  const handlePointMouseLeave = () => {
    const map = mapInstance.current;
    if (!map) return;
    map.getCanvas().style.cursor = '';
    hoverPopup.current?.remove();
  };

  const handlePointClick = (e: any) => {
    if (radiusModeRef.current) return;
    if (!e.features?.[0]) return;
    const markerId = e.features[0].properties?.id;
    const targetMarker = markersRef.current.find((m) => m.id === markerId);
    if (targetMarker) {
      setSelectedAward(targetMarker);
    }
  };

  const handleClusterClick = (e: any) => {
    const map = mapInstance.current;
    if (!map) return;
    const features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
    const clusterId = features[0]?.properties?.cluster_id;
    const source: any = map.getSource('awards-source');
    if (source && clusterId !== undefined) {
      source.getClusterExpansionZoom(clusterId, (err: any, zoom: number) => {
        if (err) return;
        const coords = (features[0].geometry as any).coordinates;
        map.easeTo({ center: coords, zoom: zoom + 0.5, duration: 600 });
      });
    }
  };

  // Draw Radius polygon on map
  const drawRadiusCircle = (map: maptilersdk.Map, center: [number, number], miles: number) => {
    if (!map || !map.isStyleLoaded()) return;
    const points = 64;
    const km = miles * 1.60934;
    const coords: [number, number][] = [];
    const distanceX = km / (111.32 * Math.cos((center[1] * Math.PI) / 180));
    const distanceY = km / 110.574;

    for (let i = 0; i < points; i++) {
      const theta = (i / points) * (2 * Math.PI);
      const x = distanceX * Math.cos(theta);
      const y = distanceY * Math.sin(theta);
      coords.push([center[0] + x, center[1] + y]);
    }
    coords.push(coords[0]);

    const polygonGeojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [coords],
          },
          properties: {},
        },
      ],
    };

    try {
      const src: any = map.getSource('radius-source');
      if (src && typeof src.setData === 'function') {
        src.setData(polygonGeojson);
      } else {
        if (map.getSource('radius-source')) map.removeSource('radius-source');
        map.addSource('radius-source', {
          type: 'geojson',
          data: polygonGeojson,
        });

        if (!map.getLayer('radius-polygon-layer')) {
          map.addLayer({
            id: 'radius-polygon-layer',
            type: 'fill',
            source: 'radius-source',
            paint: {
              'fill-color': '#4F46E5',
              'fill-opacity': 0.15,
            },
          });
        }

        if (!map.getLayer('radius-line-layer')) {
          map.addLayer({
            id: 'radius-line-layer',
            type: 'line',
            source: 'radius-source',
            paint: {
              'line-color': '#4F46E5',
              'line-width': 2,
              'line-dasharray': [2, 2],
            },
          });
        }
      }
    } catch (err) {
      console.warn('Radius draw error:', err);
    }
  };

  // Setup / Re-setup data sources & layers (always reads fresh data from refs)
  const setupLayers = (map: maptilersdk.Map) => {
    if (!map) return;
    if (!map.isStyleLoaded()) {
      map.once('styledata', () => setupLayers(map));
      return;
    }

    try {
      // Remove existing layers & sources if present
      ['award-heat', 'clusters', 'cluster-count', 'unclustered-point', 'unclustered-halo', 'radius-polygon-layer', 'radius-line-layer'].forEach((layerId) => {
        if (map.getLayer(layerId)) {
          try { map.removeLayer(layerId); } catch (_) {}
        }
      });
      if (map.getSource('awards-source')) {
        try { map.removeSource('awards-source'); } catch (_) {}
      }
      if (map.getSource('radius-source')) {
        try { map.removeSource('radius-source'); } catch (_) {}
      }

      const currentGeojson = geojsonDataRef.current;
      const currentClusters = enableClustersRef.current;
      const currentHeatmap = enableHeatmapRef.current;
      const currentOutlineMode = outlineModeRef.current;
      const currentOutlineWidth = outlineWidthRef.current;

      // Add GeoJSON source with clustering option
      map.addSource('awards-source', {
        type: 'geojson',
        data: currentGeojson,
        cluster: currentClusters,
        clusterMaxZoom: 14,
        clusterRadius: 45,
      });

      // 1. Heatmap Layer
      if (currentHeatmap) {
        map.addLayer({
          id: 'award-heat',
          type: 'heatmap',
          source: 'awards-source',
          maxzoom: 12,
          paint: {
            'heatmap-weight': ['interpolate', ['linear'], ['get', 'amount'], 0, 0.2, 5000000, 1, 50000000, 3],
            'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 9, 3],
            'heatmap-color': [
              'interpolate', ['linear'], ['heatmap-density'],
              0, 'rgba(33,102,172,0)',
              0.2, 'rgb(103,169,207)',
              0.4, 'rgb(209,229,240)',
              0.6, 'rgb(253,219,199)',
              0.8, 'rgb(239,138,98)',
              1, 'rgb(178,24,43)'
            ],
            'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 6, 9, 25],
            'heatmap-opacity': 0.8,
          },
        });
      }

      // 2. Clusters Layer
      if (currentClusters) {
        map.addLayer({
          id: 'clusters',
          type: 'circle',
          source: 'awards-source',
          filter: ['has', 'point_count'],
          paint: {
            'circle-color': [
              'step', ['get', 'point_count'],
              '#6366F1', 10,
              '#4F46E5', 50,
              '#4338CA', 200,
              '#3730A3', 500,
              '#312E81'
            ],
            'circle-radius': [
              'step', ['get', 'point_count'],
              16, 10,
              20, 50,
              26, 200,
              32, 500,
              38
            ],
            'circle-stroke-width': 2.5,
            'circle-stroke-color': '#FFFFFF',
            'circle-opacity': 0.88,
          },
        });

        map.addLayer({
          id: 'cluster-count',
          type: 'symbol',
          source: 'awards-source',
          filter: ['has', 'point_count'],
          layout: {
            'text-field': '{point_count_abbreviated}',
            'text-font': ['Noto Sans Bold'],
            'text-size': 12,
          },
          paint: {
            'text-color': '#FFFFFF',
          },
        });

        // Click on cluster to zoom in
        map.off('click', 'clusters', handleClusterClick);
        map.on('click', 'clusters', handleClusterClick);
      }

      // 3. Individual Data Points Layer (Always Visible & Highly Contrasting)
      map.addLayer({
        id: 'unclustered-point',
        type: 'circle',
        source: 'awards-source',
        filter: currentClusters ? ['!', ['has', 'point_count']] : ['all'],
        paint: {
          'circle-color': ['coalesce', ['get', 'color'], '#6366F1'],
          'circle-radius': [
            'interpolate', ['linear'], ['zoom'],
            3, ['*', ['coalesce', ['get', 'radius'], 5], 0.65],
            6, ['coalesce', ['get', 'radius'], 5],
            10, ['*', ['coalesce', ['get', 'radius'], 5], 1.35],
            15, ['*', ['coalesce', ['get', 'radius'], 5], 1.9]
          ],
          'circle-stroke-width': currentOutlineMode === 'none' ? 0 : currentOutlineWidth,
          'circle-stroke-color': ['coalesce', ['get', 'outline_color'], '#FFFFFF'],
          'circle-opacity': 0.88,
        },
      });

      // Attach hover and click handlers
      map.off('mouseenter', 'unclustered-point', handlePointMouseEnter);
      map.off('mouseleave', 'unclustered-point', handlePointMouseLeave);
      map.off('click', 'unclustered-point', handlePointClick);

      map.on('mouseenter', 'unclustered-point', handlePointMouseEnter);
      map.on('mouseleave', 'unclustered-point', handlePointMouseLeave);
      map.on('click', 'unclustered-point', handlePointClick);

      // If radius filter was active, redraw it
      if (radiusCenterRef.current && radiusMilesRef.current) {
        drawRadiusCircle(map, radiusCenterRef.current, radiusMilesRef.current);
      }
    } catch (err) {
      console.warn('setupLayers error, retrying on styledata:', err);
      map.once('styledata', () => setupLayers(map));
    }
  };

  // 1. Initialize MapTiler Map
  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return;

    const initialStyleObj = MAP_STYLES.find(s => s.id === currentStyleId) || MAP_STYLES[0];
    const map = new maptilersdk.Map({
      container: mapContainer.current,
      style: initialStyleObj.style as any,
      center: [-98.35, 39.5],
      zoom: 3.8,
      projection: currentProjection as any,
      preserveDrawingBuffer: true,
      hash: false,
    } as any);

    // Add Navigation & Scale Controls
    map.addControl(new maptilersdk.NavigationControl({ visualizePitch: true }), 'top-right');
    map.addControl(new maptilersdk.ScaleControl({ unit: 'imperial' }), 'bottom-left');
    map.addControl(new maptilersdk.FullscreenControl(), 'top-right');

    hoverPopup.current = new maptilersdk.Popup({
      closeButton: false,
      closeOnClick: false,
      offset: 12,
      className: 'award-map-hover-popup',
    });

    map.on('load', () => {
      mapInstance.current = map;
      setupLayers(map);
    });

    // Style.load & styledata fires whenever map.setStyle completes loading new style
    map.on('style.load', () => {
      setupLayers(map);
    });

    map.on('styledata', () => {
      if (map.isStyleLoaded() && !map.getSource('awards-source')) {
        setupLayers(map);
      }
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // 2. Update GeoJSON data when markers, colorBy, sizeBy, bubbleScale, or outline change
  useEffect(() => {
    const map = mapInstance.current;
    if (!map || !map.isStyleLoaded()) return;

    const source: any = map.getSource('awards-source');
    if (source && typeof source.setData === 'function') {
      try {
        source.setData(geojsonData);
      } catch (err) {
        console.warn('Error setting GeoJSON data on map, recreating layers:', err);
        setupLayers(map);
      }
    } else {
      setupLayers(map);
    }
  }, [geojsonData]);

  // Re-run setupLayers whenever cluster, heatmap, or outlineMode/width change
  useEffect(() => {
    const map = mapInstance.current;
    if (!map || !map.isStyleLoaded()) return;
    setupLayers(map);
  }, [enableClusters, enableHeatmap, outlineMode, outlineWidth]);

  // Map Click Handler for Radius Filter Mode
  useEffect(() => {
    const map = mapInstance.current;
    if (!map) return;

    const handleMapClick = (e: any) => {
      if (!radiusModeRef.current) return;
      const { lng, lat } = e.lngLat;
      const newCenter: [number, number] = [lng, lat];
      setRadiusCenter(newCenter);
      drawRadiusCircle(map, newCenter, radiusMilesRef.current);
      onRadiusChange?.(lat, lng, radiusMilesRef.current);
    };

    map.on('click', handleMapClick);
    return () => {
      map.off('click', handleMapClick);
    };
  }, [radiusMode, onRadiusChange]);

  // 3. Handle Style Change (Guaranteed point preservation)
  const handleStyleChange = (styleObj: (typeof MAP_STYLES)[0]) => {
    setCurrentStyleId(styleObj.id);
    const map = mapInstance.current;
    if (!map) return;

    map.setStyle(styleObj.style as any);

    const reapply = () => {
      setupLayers(map);
      if (enableTerrain) {
        try {
          map.setTerrain({ source: 'maptiler_terrain', exaggeration: 1.5 });
        } catch (e) {
          console.warn('Terrain error on style change:', e);
        }
      }
    };

    map.once('style.load', reapply);
    map.once('styledata', () => {
      if (map.isStyleLoaded() && !map.getSource('awards-source')) {
        reapply();
      }
    });
    map.once('idle', () => {
      if (!map.getSource('awards-source')) {
        reapply();
      }
    });
  };

  // 4. Handle Projection Change
  const handleProjectionChange = (proj: string) => {
    setCurrentProjection(proj);
    const map = mapInstance.current;
    if (map) {
      map.setProjection(proj as any);
    }
  };

  // 5. Handle 3D Terrain Toggle
  const handleTerrainToggle = () => {
    const map = mapInstance.current;
    if (!map) return;
    const nextTerrain = !enableTerrain;
    setEnableTerrain(nextTerrain);

    if (nextTerrain) {
      map.setTerrain({ source: 'maptiler_terrain', exaggeration: 1.5 });
      map.easeTo({ pitch: 45, duration: 800 });
    } else {
      map.setTerrain(null);
      map.easeTo({ pitch: 0, duration: 600 });
    }
  };

  // 6. Fly to Region
  const handleFlyToRegion = (region: (typeof REGION_PRESETS)[0]) => {
    const map = mapInstance.current;
    if (!map) return;
    map.flyTo({
      center: region.center,
      zoom: region.zoom,
      pitch: region.pitch,
      bearing: region.bearing,
      essential: true,
      duration: 1200,
    });
  };

  // Clear radius filter
  const handleClearRadius = () => {
    setRadiusMode(false);
    setRadiusCenter(null);
    onRadiusChange?.(null, null, null);
    const map = mapInstance.current;
    if (map && map.getSource('radius-source')) {
      const src: any = map.getSource('radius-source');
      src.setData({ type: 'FeatureCollection', features: [] });
    }
  };

  return (
    <div className="relative w-full h-[780px] rounded-2xl overflow-hidden border border-slate-200/80 shadow-lg bg-slate-950 select-none">
      {/* Map Canvas Container */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 z-40 bg-slate-900/30 backdrop-blur-xs flex items-center justify-center">
          <div className="bg-white/95 px-4 py-3 rounded-xl shadow-xl border border-slate-200 flex items-center gap-3">
            <div className="w-4 h-4 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin" />
            <span className="text-xs font-semibold text-slate-800">Updating awardee geodata...</span>
          </div>
        </div>
      )}

      {/* === TOP-LEFT: Executive KPI Summary Pill === */}
      <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 max-w-sm pointer-events-none">
        <div className="bg-white/95 backdrop-blur-md rounded-xl border border-slate-200/80 shadow-lg p-3 pointer-events-auto flex items-center justify-between gap-4">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Mapped Capital</div>
            <div className="text-lg font-extrabold text-slate-900 leading-none mt-0.5">
              {fmt(summary?.total_funding)}
            </div>
          </div>
          <div className="h-7 w-px bg-slate-200" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Individual Points</div>
            <div className="text-base font-bold text-indigo-600 leading-none mt-0.5">
              {markers.length.toLocaleString()} <span className="text-[10px] font-medium text-slate-500">awardees</span>
            </div>
          </div>
          <div className="h-7 w-px bg-slate-200" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recipients</div>
            <div className="text-base font-bold text-slate-700 leading-none mt-0.5">
              {summary?.unique_recipients?.toLocaleString() || markers.length}
            </div>
          </div>
        </div>
      </div>

      {/* === TOP-RIGHT: Style, Projections, 3D Terrain, Legend Toggle & NYT Export === */}
      <div className="absolute top-4 right-14 z-20 flex items-center gap-2 pointer-events-auto flex-wrap justify-end">
        {/* Prominent Marker Size Slider in Top Bar */}
        <div className="bg-white/95 backdrop-blur-md rounded-xl border border-slate-200/80 shadow-md px-3 py-1.5 flex items-center gap-2 text-xs font-semibold text-slate-700">
          <span className="text-[11px] font-bold text-slate-500 flex items-center gap-1 shrink-0">
            <span>Marker Size:</span>
            <span className="font-mono text-indigo-600 font-extrabold">{bubbleScale.toFixed(1)}x</span>
          </span>
          <input
            type="range"
            min={0.3}
            max={3.0}
            step={0.1}
            value={bubbleScale}
            onChange={(e) => setBubbleScale(parseFloat(e.target.value))}
            className="w-20 sm:w-28 accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg appearance-none"
            title={`Adjust Marker Size (${bubbleScale.toFixed(1)}x)`}
          />
          <div className="flex items-center gap-0.5 pl-1 border-l border-slate-200">
            {([
              { label: 'S', val: 0.6 },
              { label: 'M', val: 1.0 },
              { label: 'L', val: 1.6 },
              { label: 'XL', val: 2.2 },
            ]).map((p) => (
              <button
                key={p.label}
                onClick={() => setBubbleScale(p.val)}
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold transition-all ${
                  Math.abs(bubbleScale - p.val) < 0.15
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-500 hover:bg-slate-100'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Legend Quick Toggle */}
        <button
          onClick={() => setIsLegendOpen(!isLegendOpen)}
          className={`px-3 py-1.5 rounded-xl border shadow-md backdrop-blur-md transition-all flex items-center gap-1.5 text-xs font-bold ${
            isLegendOpen
              ? 'bg-indigo-600 text-white border-indigo-700 shadow-indigo-100'
              : 'bg-white/95 text-slate-700 border-slate-200/80 hover:bg-slate-50'
          }`}
          title="Toggle interactive map legend"
        >
          <Layers size={14} />
          <span>Map Legend</span>
        </button>

        {/* Vintage Wave Timeline Quick-Filter Pill */}
        <div className="flex items-center bg-white/95 backdrop-blur-md rounded-xl border border-slate-200/80 shadow-md p-0.5">
          {[
            { id: 'all', label: 'All Vintages', icon: '🌐' },
            { id: '2024', label: '2024 Infra ($39.8B)', icon: '🏛️' },
            { id: '2025', label: '2025 Scale ($12.95B)', icon: '⚡' },
            { id: '2026', label: '2026 Utility ($1.08B)', icon: '🔌' },
          ].map((v) => (
            <button
              key={v.id}
              onClick={() => setVintageFilter(v.id as any)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 cursor-pointer ${
                vintageFilter === v.id
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
              title={`Filter to ${v.label}`}
            >
              <span>{v.icon}</span>
              <span className="hidden lg:inline">{v.label}</span>
            </button>
          ))}
        </div>

        {/* Map Styles Selector */}
        <div className="flex items-center bg-white/95 backdrop-blur-md rounded-xl border border-slate-200/80 shadow-md p-0.5">
          {MAP_STYLES.map((st) => (
            <button
              key={st.id}
              onClick={() => handleStyleChange(st)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1 ${
                currentStyleId === st.id
                  ? 'bg-slate-900 text-white shadow-xs font-semibold'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
              title={st.label}
            >
              <span>{st.icon}</span>
              <span className="hidden xl:inline">{st.label}</span>
            </button>
          ))}
        </div>

        {/* Projection Switcher */}
        <select
          value={currentProjection}
          onChange={(e) => handleProjectionChange(e.target.value)}
          className="bg-white/95 backdrop-blur-md rounded-xl border border-slate-200/80 shadow-md px-2.5 py-1.5 text-xs font-semibold text-slate-700 outline-none cursor-pointer hover:bg-slate-50 transition-colors"
        >
          {PROJECTIONS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>

        {/* 3D Terrain Elevation Toggle */}
        <button
          onClick={handleTerrainToggle}
          className={`p-2 rounded-xl border shadow-md backdrop-blur-md transition-all flex items-center gap-1.5 text-xs font-semibold ${
            enableTerrain
              ? 'bg-amber-500 text-white border-amber-600 shadow-amber-200'
              : 'bg-white/95 text-slate-700 border-slate-200/80 hover:bg-slate-50'
          }`}
          title="Toggle 3D Terrain Elevation Mesh"
        >
          <Box size={14} />
          <span className="hidden sm:inline">3D</span>
        </button>

        {/* Executive GIS Wall Map Export Button */}
        <button
          onClick={() => setIsExportOpen(true)}
          className="px-3 py-1.5 rounded-xl border border-indigo-600 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md transition-all flex items-center gap-1.5 cursor-pointer"
          title="Export high-resolution Executive Publication GIS wall map"
        >
          <Download size={14} />
          <span>Executive Export</span>
        </button>
      </div>

      {/* === PROMINENT FLOATING MAP LEGEND STUDIO (Left / Upper-Left) === */}
      {isLegendOpen && (
        <div className="absolute top-20 left-4 z-30 bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/90 shadow-2xl p-3.5 w-80 max-w-[calc(100vw-2rem)] pointer-events-auto transition-all animate-in fade-in duration-200">
          {/* Legend Header */}
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5 mb-2.5">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                <Layers size={13} />
              </div>
              <div>
                <h4 className="text-xs font-extrabold text-slate-900 tracking-tight leading-none">Map Legend</h4>
                <div className="text-[10px] text-slate-500 font-medium mt-0.5">
                  Color by: <span className="font-bold text-indigo-600 capitalize">{colorBy}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsLegendCollapsed(!isLegendCollapsed)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                title={isLegendCollapsed ? "Expand legend" : "Collapse legend"}
              >
                {isLegendCollapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
              </button>
            </div>
          </div>

          {!isLegendCollapsed && (
            <div className="space-y-2.5">
              {/* Studio Tabs Navigation */}
              <div className="grid grid-cols-4 gap-1 p-0.5 bg-slate-100 rounded-lg">
                {[
                  { id: 'color' as const, label: 'Color', icon: '🎨' },
                  { id: 'size' as const, label: 'Size', icon: '📏' },
                  { id: 'outline' as const, label: 'Outline', icon: '⭕' },
                  { id: 'layers' as const, label: 'Layers', icon: '⚙️' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setLegendTab(tab.id)}
                    className={`py-1 text-[10px] font-bold rounded-md transition-all flex items-center justify-center gap-1 ${
                      legendTab === tab.id
                        ? 'bg-white text-indigo-700 shadow-xs'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* TAB 1: COLOR THEME & PALETTE */}
              {legendTab === 'color' && (
                <div className="space-y-2.5 animate-in fade-in duration-150">
                  <div>
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Color Dimension</div>
                    <div className="grid grid-cols-4 gap-1">
                      {COLOR_BY_OPTIONS.map((btn) => (
                        <button
                          key={btn.id}
                          onClick={() => setColorBy(btn.id)}
                          className={`px-1 py-1 rounded-md text-[9px] font-semibold transition-all truncate text-center ${
                            colorBy === btn.id
                              ? 'bg-indigo-600 text-white shadow-xs'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                          title={btn.label}
                        >
                          {btn.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center justify-between">
                      <span>Categories ({legendBreakdown.items.length})</span>
                      <span className="font-mono text-[9px] text-slate-500">{markers.length.toLocaleString()} points</span>
                    </div>
                    <div className="space-y-1 max-h-44 overflow-y-auto pr-1">
                      {legendBreakdown.items.slice(0, 12).map((cat) => (
                        <div
                          key={cat.name}
                          className="flex items-center justify-between text-[11px] py-0.5 px-1 rounded hover:bg-slate-50 transition-colors group"
                        >
                          <div className="flex items-center gap-1.5 truncate pr-2">
                            <div
                              className="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs border border-white"
                              style={{ backgroundColor: cat.color }}
                            />
                            <span className="text-slate-700 font-medium truncate group-hover:text-slate-900">{cat.name}</span>
                          </div>
                          <div className="flex items-center gap-1 shrink-0 text-[10px]">
                            <span className="font-mono font-bold text-slate-700">{cat.count}</span>
                            <span className="text-slate-300">·</span>
                            <span className="font-semibold text-emerald-600">{fmt(cat.funding)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: MARKER SIZE & SCALING */}
              {legendTab === 'size' && (
                <div className="space-y-2.5 animate-in fade-in duration-150">
                  <div>
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Size Dimension</div>
                    <div className="grid grid-cols-3 gap-1">
                      {SIZE_BY_OPTIONS.map((s) => (
                        <button
                          key={s.id}
                          onClick={() => setSizeBy(s.id)}
                          className={`p-1.5 rounded-md text-[10px] font-semibold transition-all text-center ${
                            sizeBy === s.id
                              ? 'bg-indigo-600 text-white shadow-xs'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          <div>{s.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Benchmark Size Key */}
                  <div className="p-2 bg-slate-50 rounded-xl border border-slate-100">
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Radius Scale Key</div>
                    <div className="flex items-center justify-around text-[10px] text-slate-600">
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-2 h-2 rounded-full bg-indigo-500" />
                        <span className="text-[9px]">&lt; $250K</span>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-3.5 h-3.5 rounded-full bg-indigo-600 border border-white" />
                        <span className="text-[9px]">$1M - $5M</span>
                      </div>
                      <div className="flex flex-col items-center gap-1">
                        <div className="w-5 h-5 rounded-full bg-indigo-700 border border-white shadow-xs" />
                        <span className="text-[9px]">$10M - $50M+</span>
                      </div>
                    </div>
                  </div>

                  {/* Slider with Presets */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] text-slate-600 font-medium">
                      <span>Radius Multiplier</span>
                      <span className="font-mono text-indigo-600 font-bold">{bubbleScale.toFixed(1)}x</span>
                    </div>
                    <input
                      type="range"
                      min={0.3}
                      max={3.0}
                      step={0.1}
                      value={bubbleScale}
                      onChange={(e) => setBubbleScale(parseFloat(e.target.value))}
                      className="w-full accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg appearance-none"
                    />
                    <div className="grid grid-cols-4 gap-1 pt-0.5">
                      {[
                        { label: 'Small (0.6x)', val: 0.6 },
                        { label: 'Med (1.0x)', val: 1.0 },
                        { label: 'Large (1.6x)', val: 1.6 },
                        { label: 'XL (2.2x)', val: 2.2 },
                      ].map((preset) => (
                        <button
                          key={preset.label}
                          onClick={() => setBubbleScale(preset.val)}
                          className={`py-1 rounded text-[9px] font-bold text-center transition-all ${
                            Math.abs(bubbleScale - preset.val) < 0.15
                              ? 'bg-indigo-600 text-white shadow-xs'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          {preset.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}


              {/* TAB 3: OUTLINE & HALO STYLING */}

              {legendTab === 'outline' && (
                <div className="space-y-2.5 animate-in fade-in duration-150">
                  <div>
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Outline / Halo Style</div>
                    <div className="grid grid-cols-3 gap-1">
                      {OUTLINE_OPTIONS.map((o) => (
                        <button
                          key={o.id}
                          onClick={() => setOutlineMode(o.id)}
                          className={`p-1.5 rounded-md text-[10px] font-semibold transition-all flex items-center justify-center gap-1.5 ${
                            outlineMode === o.id
                              ? 'bg-indigo-600 text-white shadow-xs'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          <div
                            className="w-2.5 h-2.5 rounded-full border border-slate-300"
                            style={{ backgroundColor: o.swatch }}
                          />
                          <span>{o.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Stroke Width Selector */}
                  <div>
                    <div className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Stroke Width</div>
                    <div className="grid grid-cols-4 gap-1">
                      {[1.0, 1.8, 2.8, 4.0].map((w) => (
                        <button
                          key={w}
                          onClick={() => setOutlineWidth(w)}
                          className={`py-1 rounded text-[10px] font-bold transition-all ${
                            outlineWidth === w
                              ? 'bg-slate-900 text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          {w}px
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: LAYERS & DISPLAY MODES */}
              {legendTab === 'layers' && (
                <div className="space-y-2 animate-in fade-in duration-150">
                  <div className="grid grid-cols-2 gap-1.5">
                    <button
                      onClick={() => setEnableClusters(!enableClusters)}
                      className={`py-1.5 px-2 rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-1 ${
                        !enableClusters
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : 'bg-indigo-50 text-indigo-800 border border-indigo-200'
                      }`}
                      title="Toggle point clustering"
                    >
                      <Circle size={10} className={!enableClusters ? 'text-emerald-600 fill-emerald-600' : ''} />
                      <span>{enableClusters ? 'Grouped Clusters' : 'Individual Points'}</span>
                    </button>

                    <button
                      onClick={() => setEnableHeatmap(!enableHeatmap)}
                      className={`py-1.5 px-2 rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-1 ${
                        enableHeatmap
                          ? 'bg-amber-500 text-white shadow-xs'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                      title="Toggle capital density heatmap"
                    >
                      <Flame size={10} />
                      <span>Heatmap {enableHeatmap ? 'ON' : 'OFF'}</span>
                    </button>
                  </div>

                  <div className="p-2 bg-slate-50 rounded-lg text-[10px] text-slate-600 space-y-1">
                    <div className="flex justify-between">
                      <span>Mapped Points:</span>
                      <span className="font-mono font-bold text-slate-800">{markers.length.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Capital:</span>
                      <span className="font-mono font-bold text-emerald-700">{fmt(summary?.total_funding)}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Quick Marker Size Slider directly in Legend Studio Footer */}
              <div className="pt-2 mt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                <div className="flex items-center gap-1 text-[10px] font-bold text-slate-600 shrink-0">
                  <span>Marker Size:</span>
                  <span className="font-mono text-indigo-600 font-extrabold">{bubbleScale.toFixed(1)}x</span>
                </div>
                <input
                  type="range"
                  min={0.3}
                  max={3.0}
                  step={0.1}
                  value={bubbleScale}
                  onChange={(e) => setBubbleScale(parseFloat(e.target.value))}
                  className="flex-1 accent-indigo-600 cursor-pointer h-1.5 bg-slate-200 rounded-lg appearance-none max-w-[130px]"
                />
                <button
                  onClick={() => setBubbleScale(1.0)}
                  className="text-[9px] font-semibold text-slate-400 hover:text-indigo-600 hover:underline shrink-0"
                >
                  Reset
                </button>
              </div>
            </div>
          )}
        </div>
      )}


      {/* === BOTTOM-RIGHT: Regional Navigation Hubs & Proximity Tool === */}
      <div className="absolute bottom-4 right-4 z-20 bg-white/95 backdrop-blur-md rounded-2xl border border-slate-200/80 shadow-xl p-2.5 pointer-events-auto flex flex-col gap-1 max-w-[210px]">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1.5 mb-0.5 flex items-center justify-between">
          <span>Innovation Hubs</span>
          <Compass size={11} className="text-indigo-500" />
        </div>
        <div className="grid grid-cols-2 gap-1">
          {REGION_PRESETS.map((reg) => (
            <button
              key={reg.id}
              onClick={() => handleFlyToRegion(reg)}
              className="px-2 py-1 rounded-lg text-left text-[11px] font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors truncate"
            >
              {reg.label}
            </button>
          ))}
        </div>

        {/* Proximity / Radius Filter Tool */}
        <div className="mt-1 pt-1.5 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={() => {
              if (radiusMode) handleClearRadius();
              else setRadiusMode(true);
            }}
            className={`w-full py-1 px-2 rounded-lg text-[10px] font-bold uppercase transition-all flex items-center justify-center gap-1 ${
              radiusMode
                ? 'bg-amber-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            <MapPin size={10} />
            <span>{radiusMode ? `Radius: ${radiusMiles}mi (Click map)` : 'Proximity Filter'}</span>
          </button>
        </div>
      </div>

      {/* Award Dossier Slide-Over Drawer */}
      <AwardDossierDrawer
        award={selectedAward}
        onClose={() => setSelectedAward(null)}
        onSelectRelatedAward={(relatedId) => {
          const target = markers.find((m) => m.id === relatedId);
          if (target) setSelectedAward(target);
        }}
      />

      {/* Executive Style GIS Wall Map Export Modal */}
      <AwardMapNYTExport
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        getMapCanvas={() => mapInstance.current?.getCanvas() || null}
        markers={markers}
        summary={summary}
        activeFiltersDesc={activeFiltersDesc}
        colorByMode={colorBy}
        colorPalette={activeColorPalette}
      />
    </div>
  );
};
