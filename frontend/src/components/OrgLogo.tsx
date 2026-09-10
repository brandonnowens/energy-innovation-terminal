import React, { useState } from 'react';

export interface OrgBrand {
  name: string;
  abbr: string;           // Short display abbreviation
  color: string;          // Primary brand color (hex)
  bgColor: string;        // Background color for badges
  textColor: string;      // Text color on bg
  fullName: string;       // Full organization name
  domain?: string;        // Official website domain
}

// Official brand colors sourced from organizational style guides
export const ORG_BRANDS: Record<string, OrgBrand> = {
  'NYSERDA': {
    name: 'State Energy Authority (NY)', abbr: 'NY', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF',
    fullName: 'State Clean Energy Research & Development Authority',
    domain: 'nyserda.ny.gov',
  },
  'DOE': {
    name: 'DOE', abbr: 'DOE', color: '#003A5C', bgColor: '#003A5C', textColor: '#FFFFFF',
    fullName: 'U.S. Department of Energy',
    domain: 'energy.gov',
  },
  'NSF': {
    name: 'NSF', abbr: 'NSF', color: '#2B6CB0', bgColor: '#2B6CB0', textColor: '#FFFFFF',
    fullName: 'National Science Foundation',
    domain: 'nsf.gov',
  },
  'ARPA-E': {
    name: 'ARPA-E', abbr: 'AE', color: '#C53030', bgColor: '#C53030', textColor: '#FFFFFF',
    fullName: 'Advanced Research Projects Agency–Energy',
    domain: 'arpa-e.energy.gov',
  },
  'EPA': {
    name: 'EPA', abbr: 'EPA', color: '#0077B6', bgColor: '#0077B6', textColor: '#FFFFFF',
    fullName: 'U.S. Environmental Protection Agency',
    domain: 'epa.gov',
  },
  'DOD': {
    name: 'DOD', abbr: 'DOD', color: '#1A365D', bgColor: '#1A365D', textColor: '#FFFFFF',
    fullName: 'U.S. Department of Defense',
    domain: 'defense.gov',
  },
  'NASA': {
    name: 'NASA', abbr: 'NASA', color: '#0B3D91', bgColor: '#0B3D91', textColor: '#FC3D21',
    fullName: 'National Aeronautics and Space Administration',
    domain: 'nasa.gov',
  },
  'USDA': {
    name: 'USDA', abbr: 'USDA', color: '#2D6A4F', bgColor: '#2D6A4F', textColor: '#FFFFFF',
    fullName: 'U.S. Department of Agriculture',
    domain: 'usda.gov',
  },
  'DOT': {
    name: 'DOT', abbr: 'DOT', color: '#005EA2', bgColor: '#005EA2', textColor: '#FFFFFF',
    fullName: 'U.S. Department of Transportation',
    domain: 'transportation.gov',
  },
  'DOC': {
    name: 'DOC', abbr: 'DOC', color: '#003366', bgColor: '#003366', textColor: '#FFFFFF',
    fullName: 'U.S. Department of Commerce',
    domain: 'commerce.gov',
  },
  'Gates Foundation': {
    name: 'Gates Foundation', abbr: 'GF', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'Bill & Melinda Gates Foundation',
    domain: 'gatesfoundation.org',
  },
  'CEC': {
    name: 'CEC', abbr: 'CEC', color: '#B45309', bgColor: '#B45309', textColor: '#FFFFFF',
    fullName: 'California Energy Commission',
    domain: 'energy.ca.gov',
  },
  'MassCEC': {
    name: 'MassCEC', abbr: 'MA', color: '#1D4ED8', bgColor: '#1D4ED8', textColor: '#FFFFFF',
    fullName: 'Massachusetts Energy Innovation Center',
    domain: 'masscec.com',
  },
  'NJEDA': {
    name: 'NJEDA', abbr: 'NJ', color: '#B91C1C', bgColor: '#B91C1C', textColor: '#FFFFFF',
    fullName: 'New Jersey Economic Development Authority',
    domain: 'njeda.gov',
  },
  'Efficiency Maine': {
    name: 'Efficiency Maine', abbr: 'ME', color: '#15803D', bgColor: '#15803D', textColor: '#FFFFFF',
    fullName: 'Efficiency Maine Trust',
    domain: 'efficiencymaine.com',
  },
  'Colorado CEO': {
    name: 'Colorado CEO', abbr: 'CO', color: '#7C3AED', bgColor: '#7C3AED', textColor: '#FFFFFF',
    fullName: 'Colorado Energy Office',
    domain: 'energyoffice.colorado.gov',
  },
  'MN Commerce': {
    name: 'MN Commerce', abbr: 'MN', color: '#0369A1', bgColor: '#0369A1', textColor: '#FFFFFF',
    fullName: 'Minnesota Department of Commerce',
    domain: 'mn.gov',
  },
  'WA Commerce': {
    name: 'WA Commerce', abbr: 'WA', color: '#047857', bgColor: '#047857', textColor: '#FFFFFF',
    fullName: 'Washington State Department of Commerce',
    domain: 'commerce.wa.gov',
  },
  'IL DCEO': {
    name: 'IL DCEO', abbr: 'IL', color: '#DC2626', bgColor: '#DC2626', textColor: '#FFFFFF',
    fullName: 'Illinois Department of Commerce & Economic Opportunity',
    domain: 'illinois.gov',
  },
  'MD MEA': {
    name: 'MD MEA', abbr: 'MD', color: '#B91C1C', bgColor: '#B91C1C', textColor: '#F59E0B',
    fullName: 'Maryland Energy Administration',
    domain: 'energy.maryland.gov',
  },
  'NM EMNRD': {
    name: 'NM EMNRD', abbr: 'NM', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'New Mexico Energy, Minerals and Natural Resources Dept.',
    domain: 'emnrd.nm.gov',
  },
  'TX SECO': {
    name: 'TX SECO', abbr: 'TX', color: '#1E40AF', bgColor: '#1E40AF', textColor: '#FFFFFF',
    fullName: 'Texas State Energy Conservation Office',
    domain: 'comptroller.texas.gov',
  },
  'WI OEI': {
    name: 'WI OEI', abbr: 'WI', color: '#B91C1C', bgColor: '#B91C1C', textColor: '#FFFFFF',
    fullName: 'Wisconsin Office of Energy Innovation',
    domain: 'oei.wi.gov',
  },
  'Con Edison': {
    name: 'Con Edison', abbr: 'CE', color: '#0066B3', bgColor: '#0066B3', textColor: '#FFFFFF',
    fullName: 'Consolidated Edison, Inc.',
    domain: 'coned.com',
  },
  'Orange & Rockland': {
    name: 'Orange & Rockland', abbr: 'O&R', color: '#F47B20', bgColor: '#F47B20', textColor: '#FFFFFF',
    fullName: 'Orange & Rockland Utilities',
    domain: 'oru.com',
  },
  'National Grid': {
    name: 'National Grid', abbr: 'NG', color: '#003DA5', bgColor: '#003DA5', textColor: '#FFFFFF',
    fullName: 'National Grid USA',
    domain: 'nationalgridus.com',
  },
  'NYSEG': {
    name: 'NYSEG', abbr: 'SEG', color: '#00A651', bgColor: '#00A651', textColor: '#FFFFFF',
    fullName: 'New York State Electric & Gas',
    domain: 'nyseg.com',
  },
  'RG&E': {
    name: 'RG&E', abbr: 'RGE', color: '#00A651', bgColor: '#00A651', textColor: '#FFFFFF',
    fullName: 'Rochester Gas & Electric',
    domain: 'rge.com',
  },
  'Central Hudson': {
    name: 'Central Hudson', abbr: 'CH', color: '#005596', bgColor: '#005596', textColor: '#FFFFFF',
    fullName: 'Central Hudson Gas & Electric',
    domain: 'cenhud.com',
  },
  'PSEG Long Island': {
    name: 'PSEG Long Island', abbr: 'PSE', color: '#0072CE', bgColor: '#0072CE', textColor: '#FFFFFF',
    fullName: 'PSEG Long Island',
    domain: 'psegliny.com',
  },
  'LIPA': {
    name: 'LIPA', abbr: 'LIPA', color: '#1B75BC', bgColor: '#1B75BC', textColor: '#FFFFFF',
    fullName: 'Long Island Power Authority',
    domain: 'lipower.org',
  },
  'NYPA': {
    name: 'NYPA', abbr: 'NYP', color: '#1D4289', bgColor: '#1D4289', textColor: '#FFFFFF',
    fullName: 'New York Power Authority',
    domain: 'nypa.gov',
  },
  'Joint Utilities of NY': {
    name: 'Joint Utilities of NY', abbr: 'JU', color: '#2E3B4E', bgColor: '#2E3B4E', textColor: '#FFFFFF',
    fullName: 'Joint Utilities of New York',
    domain: 'jointutilitiesofny.org',
  },
  'Commonwealth Edison': {
    name: 'Commonwealth Edison', abbr: 'ComEd', color: '#005596', bgColor: '#005596', textColor: '#FFFFFF',
    fullName: 'Commonwealth Edison (ComEd)',
    domain: 'comed.com',
  },
  'Ameren Illinois': {
    name: 'Ameren Illinois', abbr: 'AIL', color: '#0066B3', bgColor: '#0066B3', textColor: '#FFFFFF',
    fullName: 'Ameren Illinois',
    domain: 'ameren.com',
  },
  'Austin Energy': {
    name: 'Austin Energy', abbr: 'AE', color: '#007788', bgColor: '#007788', textColor: '#FFFFFF',
    fullName: 'Austin Energy',
    domain: 'austinenergy.com',
  },
  'CPS Energy': {
    name: 'CPS Energy', abbr: 'CPS', color: '#E65100', bgColor: '#E65100', textColor: '#FFFFFF',
    fullName: 'CPS Energy (San Antonio)',
    domain: 'cpsenergy.com',
  },
  'DTE Energy': {
    name: 'DTE Energy', abbr: 'DTE', color: '#005A9C', bgColor: '#005A9C', textColor: '#FFFFFF',
    fullName: 'DTE Energy Company',
    domain: 'dteenergy.com',
  },
  'Consumers Energy': {
    name: 'Consumers Energy', abbr: 'CMS', color: '#0068B3', bgColor: '#0068B3', textColor: '#FFFFFF',
    fullName: 'Consumers Energy (Michigan)',
    domain: 'consumersenergy.com',
  },
  'Baltimore Gas and Electric': {
    name: 'Baltimore Gas and Electric', abbr: 'BGE', color: '#0072CE', bgColor: '#0072CE', textColor: '#FFFFFF',
    fullName: 'Baltimore Gas and Electric (BGE)',
    domain: 'bge.com',
  },
  'Pacific Gas and Electric': {
    name: 'Pacific Gas and Electric', abbr: 'PG&E', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF',
    fullName: 'Pacific Gas and Electric Company',
    domain: 'pge.com',
  },
  'Southern California Edison': {
    name: 'Southern California Edison', abbr: 'SCE', color: '#C53030', bgColor: '#C53030', textColor: '#FFFFFF',
    fullName: 'Southern California Edison',
    domain: 'sce.com',
  },
  'San Diego Gas & Electric': {
    name: 'San Diego Gas & Electric', abbr: 'SDG&E', color: '#00838F', bgColor: '#00838F', textColor: '#FFFFFF',
    fullName: 'San Diego Gas & Electric',
    domain: 'sdge.com',
  },
  'American Electric Power (AEP)': {
    name: 'American Electric Power (AEP)', abbr: 'AEP', color: '#CC0000', bgColor: '#CC0000', textColor: '#FFFFFF',
    fullName: 'American Electric Power',
    domain: 'aep.com',
  },
  'Duke Energy': {
    name: 'Duke Energy', abbr: 'DUK', color: '#005596', bgColor: '#005596', textColor: '#FFFFFF',
    fullName: 'Duke Energy Corporation',
    domain: 'duke-energy.com',
  },
  'Southern Company': {
    name: 'Southern Company', abbr: 'SO', color: '#C8102E', bgColor: '#C8102E', textColor: '#FFFFFF',
    fullName: 'Southern Company',
    domain: 'southerncompany.com',
  },
  'Xcel Energy': {
    name: 'Xcel Energy', abbr: 'XEL', color: '#D9381E', bgColor: '#D9381E', textColor: '#FFFFFF',
    fullName: 'Xcel Energy Inc.',
    domain: 'xcelenergy.com',
  },
  'Dominion Energy': {
    name: 'Dominion Energy', abbr: 'DOM', color: '#004B87', bgColor: '#004B87', textColor: '#FFFFFF',
    fullName: 'Dominion Energy, Inc.',
    domain: 'dominionenergy.com',
  },
  'Entergy': {
    name: 'Entergy', abbr: 'ENT', color: '#CC0000', bgColor: '#CC0000', textColor: '#FFFFFF',
    fullName: 'Entergy Corporation',
    domain: 'entergy.com',
  },
  'NextEra Energy': {
    name: 'NextEra Energy', abbr: 'NEE', color: '#78BE20', bgColor: '#78BE20', textColor: '#FFFFFF',
    fullName: 'NextEra Energy, Inc.',
    domain: 'nexteraenergy.com',
  },
  'Eversource Energy': {
    name: 'Eversource Energy', abbr: 'ES', color: '#003366', bgColor: '#003366', textColor: '#FFFFFF',
    fullName: 'Eversource Energy',
    domain: 'eversource.com',
  },
  'Avangrid, Inc.': {
    name: 'Avangrid, Inc.', abbr: 'AGR', color: '#008751', bgColor: '#008751', textColor: '#FFFFFF',
    fullName: 'Avangrid, Inc.',
    domain: 'avangrid.com',
  },
  'Hawaiian Electric Company': {
    name: 'Hawaiian Electric Company', abbr: 'HECO', color: '#007788', bgColor: '#007788', textColor: '#FFFFFF',
    fullName: 'Hawaiian Electric Company (HECO)',
    domain: 'hawaiianelectric.com',
  },
  'Salt River Project': {
    name: 'Salt River Project', abbr: 'SRP', color: '#005596', bgColor: '#005596', textColor: '#FFFFFF',
    fullName: 'Salt River Project (SRP)',
    domain: 'srpnet.com',
  },
  'Seattle City Light': {
    name: 'Seattle City Light', abbr: 'SCL', color: '#005A9C', bgColor: '#005A9C', textColor: '#FFFFFF',
    fullName: 'Seattle City Light',
    domain: 'seattle.gov/city-light',
  },
  'Sacramento Municipal Utility District (SMUD)': {
    name: 'Sacramento Municipal Utility District (SMUD)', abbr: 'SMUD', color: '#F37023', bgColor: '#F37023', textColor: '#FFFFFF',
    fullName: 'Sacramento Municipal Utility District',
    domain: 'smud.org',
  },
  'Tennessee Valley Authority (TVA)': {
    name: 'Tennessee Valley Authority (TVA)', abbr: 'TVA', color: '#C8102E', bgColor: '#C8102E', textColor: '#FFFFFF',
    fullName: 'Tennessee Valley Authority',
    domain: 'tva.com',
  },
  // ── CLEAN TECH STARTUPS & COMMERCIAL SCALE-UPS ──
  'Form Energy': {
    name: 'Form Energy', abbr: 'FE', color: '#0F766E', bgColor: '#0F766E', textColor: '#FFFFFF',
    fullName: 'Form Energy, Inc.', domain: 'formenergy.com',
  },
  'FORM ENERGY, INC.': {
    name: 'Form Energy', abbr: 'FE', color: '#0F766E', bgColor: '#0F766E', textColor: '#FFFFFF',
    fullName: 'Form Energy, Inc.', domain: 'formenergy.com',
  },
  'Amogy': {
    name: 'Amogy', abbr: 'AMG', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'Amogy Inc.', domain: 'amogy.co',
  },
  'Amogy Inc.': {
    name: 'Amogy', abbr: 'AMG', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'Amogy Inc.', domain: 'amogy.co',
  },
  'Sublime Systems': {
    name: 'Sublime Systems', abbr: 'SUB', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Sublime Systems, Inc.', domain: 'sublimesystems.com',
  },
  'Sublime Systems, Inc.': {
    name: 'Sublime Systems', abbr: 'SUB', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Sublime Systems, Inc.', domain: 'sublimesystems.com',
  },
  'Redwood Materials': {
    name: 'Redwood Materials', abbr: 'RWD', color: '#DC2626', bgColor: '#DC2626', textColor: '#FFFFFF',
    fullName: 'Redwood Materials, Inc.', domain: 'redwoodmaterials.com',
  },
  'Eos Energy Enterprises': {
    name: 'Eos Energy Enterprises', abbr: 'EOS', color: '#EA580C', bgColor: '#EA580C', textColor: '#FFFFFF',
    fullName: 'Eos Energy Enterprises', domain: 'eose.com',
  },
  'Antora Energy': {
    name: 'Antora Energy', abbr: 'ANT', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Antora Energy, Inc.', domain: 'antoraenergy.com',
  },
  'ANTORA ENERGY, INC.': {
    name: 'Antora Energy', abbr: 'ANT', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Antora Energy, Inc.', domain: 'antoraenergy.com',
  },
  'Fervo Energy': {
    name: 'Fervo Energy', abbr: 'FRV', color: '#E11D48', bgColor: '#E11D48', textColor: '#FFFFFF',
    fullName: 'Fervo Energy Company', domain: 'fervoenergy.com',
  },
  'FERVO ENERGY COMPANY': {
    name: 'Fervo Energy', abbr: 'FRV', color: '#E11D48', bgColor: '#E11D48', textColor: '#FFFFFF',
    fullName: 'Fervo Energy Company', domain: 'fervoenergy.com',
  },
  'Natron Energy': {
    name: 'Natron Energy', abbr: 'NAT', color: '#2563EB', bgColor: '#2563EB', textColor: '#FFFFFF',
    fullName: 'Natron Energy, Inc.', domain: 'natron.energy',
  },
  'NATRON ENERGY, INC.': {
    name: 'Natron Energy', abbr: 'NAT', color: '#2563EB', bgColor: '#2563EB', textColor: '#FFFFFF',
    fullName: 'Natron Energy, Inc.', domain: 'natron.energy',
  },
  'Group14 Technologies': {
    name: 'Group14 Technologies', abbr: 'G14', color: '#4F46E5', bgColor: '#4F46E5', textColor: '#FFFFFF',
    fullName: 'Group14 Technologies, Inc.', domain: 'group14.technology',
  },
  'GROUP14 TECHNOLOGIES, INC': {
    name: 'Group14 Technologies', abbr: 'G14', color: '#4F46E5', bgColor: '#4F46E5', textColor: '#FFFFFF',
    fullName: 'Group14 Technologies, Inc.', domain: 'group14.technology',
  },
  'Verdox': {
    name: 'Verdox', abbr: 'VDX', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'Verdox, Inc.', domain: 'verdox.com',
  },
  'Verdox, Inc.': {
    name: 'Verdox', abbr: 'VDX', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'Verdox, Inc.', domain: 'verdox.com',
  },
  'Ascend Elements': {
    name: 'Ascend Elements', abbr: 'ASC', color: '#16A34A', bgColor: '#16A34A', textColor: '#FFFFFF',
    fullName: 'Ascend Elements, Inc.', domain: 'ascendelements.com',
  },
  'ASCEND ELEMENTS, INC.': {
    name: 'Ascend Elements', abbr: 'ASC', color: '#16A34A', bgColor: '#16A34A', textColor: '#FFFFFF',
    fullName: 'Ascend Elements, Inc.', domain: 'ascendelements.com',
  },
  'LineVision': {
    name: 'LineVision', abbr: 'LV', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'LineVision, Inc.', domain: 'linevisioninc.com',
  },
  'LineVision, Inc.': {
    name: 'LineVision', abbr: 'LV', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'LineVision, Inc.', domain: 'linevisioninc.com',
  },
  'TerraPower': {
    name: 'TerraPower', abbr: 'TP', color: '#1E3A8A', bgColor: '#1E3A8A', textColor: '#FFFFFF',
    fullName: 'TerraPower, LLC', domain: 'terrapower.com',
  },
  'TerraPower, LLC': {
    name: 'TerraPower', abbr: 'TP', color: '#1E3A8A', bgColor: '#1E3A8A', textColor: '#FFFFFF',
    fullName: 'TerraPower, LLC', domain: 'terrapower.com',
  },
  'Swift Solar': {
    name: 'Swift Solar', abbr: 'SWF', color: '#CA8A04', bgColor: '#CA8A04', textColor: '#FFFFFF',
    fullName: 'Swift Solar Inc.', domain: 'swiftsolar.com',
  },
  'SWIFT SOLAR INC': {
    name: 'Swift Solar', abbr: 'SWF', color: '#CA8A04', bgColor: '#CA8A04', textColor: '#FFFFFF',
    fullName: 'Swift Solar Inc.', domain: 'swiftsolar.com',
  },
  'VEIR': {
    name: 'VEIR', abbr: 'VEIR', color: '#7C3AED', bgColor: '#7C3AED', textColor: '#FFFFFF',
    fullName: 'VEIR Inc.', domain: 'veir.com',
  },
  'VEIR INC': {
    name: 'VEIR', abbr: 'VEIR', color: '#7C3AED', bgColor: '#7C3AED', textColor: '#FFFFFF',
    fullName: 'VEIR Inc.', domain: 'veir.com',
  },
  'Brimstone Energy': {
    name: 'Brimstone Energy', abbr: 'BRM', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Brimstone Energy, Inc.', domain: 'brimstone.com',
  },
  'BRIMSTONE ENERGY, INC.': {
    name: 'Brimstone Energy', abbr: 'BRM', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Brimstone Energy, Inc.', domain: 'brimstone.com',
  },
  'Sila Nanotechnologies': {
    name: 'Sila Nano', abbr: 'SILA', color: '#0891B2', bgColor: '#0891B2', textColor: '#FFFFFF',
    fullName: 'Sila Nanotechnologies, Inc.', domain: 'silanano.com',
  },
  'SILA NANOTECHNOLOGIES, INC.': {
    name: 'Sila Nano', abbr: 'SILA', color: '#0891B2', bgColor: '#0891B2', textColor: '#FFFFFF',
    fullName: 'Sila Nanotechnologies, Inc.', domain: 'silanano.com',
  },
  'Solid Power': {
    name: 'Solid Power', abbr: 'SLD', color: '#BE185D', bgColor: '#BE185D', textColor: '#FFFFFF',
    fullName: 'Solid Power, Inc.', domain: 'solidpowerbattery.com',
  },
  'SOLID POWER OPERATING, INC': {
    name: 'Solid Power', abbr: 'SLD', color: '#BE185D', bgColor: '#BE185D', textColor: '#FFFFFF',
    fullName: 'Solid Power, Inc.', domain: 'solidpowerbattery.com',
  },
  'Ecolectro': {
    name: 'Ecolectro', abbr: 'ECO', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Ecolectro Inc.', domain: 'ecolectro.com',
  },
  'ECOLECTRO INC': {
    name: 'Ecolectro', abbr: 'ECO', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Ecolectro Inc.', domain: 'ecolectro.com',
  },
  'ElectraTherm': {
    name: 'ElectraTherm', abbr: 'ETH', color: '#C026D3', bgColor: '#C026D3', textColor: '#FFFFFF',
    fullName: 'ElectraTherm, Inc.', domain: 'electratherm.com',
  },
  'ELECTRATHERM, INC.': {
    name: 'ElectraTherm', abbr: 'ETH', color: '#C026D3', bgColor: '#C026D3', textColor: '#FFFFFF',
    fullName: 'ElectraTherm, Inc.', domain: 'electratherm.com',
  },
  'Nth Cycle': {
    name: 'Nth Cycle', abbr: 'NTH', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'Nth Cycle Inc.', domain: 'nthcycle.com',
  },
  'NTH CYCLE INC': {
    name: 'Nth Cycle', abbr: 'NTH', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'Nth Cycle Inc.', domain: 'nthcycle.com',
  },
  'Boston Metal': {
    name: 'Boston Metal', abbr: 'BM', color: '#334155', bgColor: '#334155', textColor: '#FFFFFF',
    fullName: 'Boston Electrometallurgical Corp.', domain: 'bostonmetal.com',
  },
  'Urban Electric Power': {
    name: 'Urban Electric Power', abbr: 'UEP', color: '#2563EB', bgColor: '#2563EB', textColor: '#FFFFFF',
    fullName: 'Urban Electric Power Inc.', domain: 'urbanelectricpower.com',
  },
  'URBAN ELECTRIC POWER INCORPORATED': {
    name: 'Urban Electric Power', abbr: 'UEP', color: '#2563EB', bgColor: '#2563EB', textColor: '#FFFFFF',
    fullName: 'Urban Electric Power Inc.', domain: 'urbanelectricpower.com',
  },
  // ── VENTURE CAPITAL & CLIMATE FUNDS ──
  'Breakthrough Energy Ventures': {
    name: 'Breakthrough Energy', abbr: 'BEV', color: '#00A3E0', bgColor: '#00A3E0', textColor: '#FFFFFF',
    fullName: 'Breakthrough Energy Ventures', domain: 'breakthroughenergy.org',
  },
  'Energy Impact Partners': {
    name: 'Energy Impact Partners', abbr: 'EIP', color: '#0F766E', bgColor: '#0F766E', textColor: '#FFFFFF',
    fullName: 'Energy Impact Partners (EIP)', domain: 'energyimpactpartners.com',
  },
  'Prelude Ventures': {
    name: 'Prelude Ventures', abbr: 'PV', color: '#1E3A8A', bgColor: '#1E3A8A', textColor: '#FFFFFF',
    fullName: 'Prelude Ventures', domain: 'preludeventures.com',
  },
  'Lowercarbon Capital': {
    name: 'Lowercarbon Capital', abbr: 'LCC', color: '#16A34A', bgColor: '#16A34A', textColor: '#FFFFFF',
    fullName: 'Lowercarbon Capital', domain: 'lowercarboncapital.com',
  },
  'Energy Innovation Ventures': {
    name: 'Energy Innovation Ventures', abbr: 'CEV', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Energy Innovation Ventures', domain: 'cleanenergyventures.com',
  },
  'DCVC': {
    name: 'DCVC', abbr: 'DCVC', color: '#4F46E5', bgColor: '#4F46E5', textColor: '#FFFFFF',
    fullName: 'DCVC (Data Collective)', domain: 'dcvc.com',
  },
  'Khosla Ventures': {
    name: 'Khosla Ventures', abbr: 'KV', color: '#DC2626', bgColor: '#DC2626', textColor: '#FFFFFF',
    fullName: 'Khosla Ventures', domain: 'khoslaventures.com',
  },
  'Amazon Climate Pledge Fund': {
    name: 'Amazon Climate Pledge', abbr: 'AMZ', color: '#FF9900', bgColor: '#FF9900', textColor: '#111827',
    fullName: 'Amazon Climate Pledge Fund', domain: 'amazon.com',
  },
  'Temasek': {
    name: 'Temasek', abbr: 'TEM', color: '#C8102E', bgColor: '#C8102E', textColor: '#FFFFFF',
    fullName: 'Temasek Holdings', domain: 'temasek.com.sg',
  },
  'Congruent Ventures': {
    name: 'Congruent Ventures', abbr: 'CV', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'Congruent Ventures', domain: 'congruentvc.com',
  },
  'The Engine': {
    name: 'The Engine', abbr: 'ENG', color: '#111827', bgColor: '#111827', textColor: '#FFFFFF',
    fullName: 'The Engine (MIT)', domain: 'engine.xyz',
  },
  'Capricorn Investment Group': {
    name: 'Capricorn', abbr: 'CAP', color: '#7C3AED', bgColor: '#7C3AED', textColor: '#FFFFFF',
    fullName: 'Capricorn Investment Group', domain: 'capricornllc.com',
  },
  // ── NATIONAL LABS & RESEARCH INSTITUTES ──
  'NREL': {
    name: 'NREL', abbr: 'NREL', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'National Renewable Energy Laboratory', domain: 'nrel.gov',
  },
  'LBNL': {
    name: 'LBNL', abbr: 'LBNL', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Lawrence Berkeley National Laboratory', domain: 'lbl.gov',
  },
  'PNNL': {
    name: 'PNNL', abbr: 'PNNL', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Pacific Northwest National Laboratory', domain: 'pnnl.gov',
  },
  'ORNL': {
    name: 'ORNL', abbr: 'ORNL', color: '#15803D', bgColor: '#15803D', textColor: '#FFFFFF',
    fullName: 'Oak Ridge National Laboratory', domain: 'ornl.gov',
  },
  'ANL': {
    name: 'Argonne', abbr: 'ANL', color: '#1E40AF', bgColor: '#1E40AF', textColor: '#FFFFFF',
    fullName: 'Argonne National Laboratory', domain: 'anl.gov',
  },
  'SNL': {
    name: 'Sandia', abbr: 'SNL', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF',
    fullName: 'Sandia National Laboratories', domain: 'sandia.gov',
  },
  'INL': {
    name: 'Idaho National Lab', abbr: 'INL', color: '#047857', bgColor: '#047857', textColor: '#FFFFFF',
    fullName: 'Idaho National Laboratory', domain: 'inl.gov',
  },
  'LLNL': {
    name: 'Livermore', abbr: 'LLNL', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'Lawrence Livermore National Laboratory', domain: 'llnl.gov',
  },
  'EPRI': {
    name: 'EPRI', abbr: 'EPRI', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF',
    fullName: 'Electric Power Research Institute', domain: 'epri.com',
  },
  'GTI Energy': {
    name: 'GTI Energy', abbr: 'GTI', color: '#0D9488', bgColor: '#0D9488', textColor: '#FFFFFF',
    fullName: 'GTI Energy', domain: 'gti.energy',
  },

  // ── UNIVERSITIES & RESEARCH INSTITUTIONS ──
  'MIT': {
    name: 'MIT', abbr: 'MIT', color: '#A31F34', bgColor: '#A31F34', textColor: '#FFFFFF',
    fullName: 'Massachusetts Institute of Technology', domain: 'mit.edu',
  },
  'Cornell University': {
    name: 'Cornell', abbr: 'CU', color: '#B31B1B', bgColor: '#B31B1B', textColor: '#FFFFFF',
    fullName: 'Cornell University', domain: 'cornell.edu',
  },
  'Stanford University': {
    name: 'Stanford', abbr: 'SU', color: '#8C1515', bgColor: '#8C1515', textColor: '#FFFFFF',
    fullName: 'Stanford University', domain: 'stanford.edu',
  },
  'Purdue University': {
    name: 'Purdue', abbr: 'PUR', color: '#CEB888', bgColor: '#CEB888', textColor: '#000000',
    fullName: 'Purdue University', domain: 'purdue.edu',
  },
  'UC Berkeley': {
    name: 'UC Berkeley', abbr: 'CAL', color: '#003262', bgColor: '#003262', textColor: '#FDB515',
    fullName: 'University of California, Berkeley', domain: 'berkeley.edu',
  },
  'Caltech': {
    name: 'Caltech', abbr: 'CIT', color: '#FF6C0C', bgColor: '#FF6C0C', textColor: '#FFFFFF',
    fullName: 'California Institute of Technology', domain: 'caltech.edu',
  },
  'Harvard University': {
    name: 'Harvard', abbr: 'HAR', color: '#A51C30', bgColor: '#A51C30', textColor: '#FFFFFF',
    fullName: 'Harvard University', domain: 'harvard.edu',
  },
  'Princeton University': {
    name: 'Princeton', abbr: 'PRI', color: '#FF6000', bgColor: '#FF6000', textColor: '#000000',
    fullName: 'Princeton University', domain: 'princeton.edu',
  },
  'Columbia University': {
    name: 'Columbia', abbr: 'COL', color: '#75AADB', bgColor: '#75AADB', textColor: '#FFFFFF',
    fullName: 'Columbia University', domain: 'columbia.edu',
  },
  'Carnegie Mellon University': {
    name: 'Carnegie Mellon', abbr: 'CMU', color: '#C41230', bgColor: '#C41230', textColor: '#FFFFFF',
    fullName: 'Carnegie Mellon University', domain: 'cmu.edu',
  },
  'Georgia Tech': {
    name: 'Georgia Tech', abbr: 'GT', color: '#B3A369', bgColor: '#003057', textColor: '#B3A369',
    fullName: 'Georgia Institute of Technology', domain: 'gatech.edu',
  },
  'University of Michigan': {
    name: 'Michigan', abbr: 'UM', color: '#00274C', bgColor: '#00274C', textColor: '#FFCB05',
    fullName: 'University of Michigan', domain: 'umich.edu',
  },
  'University of Illinois': {
    name: 'UIUC', abbr: 'UIUC', color: '#13294B', bgColor: '#13294B', textColor: '#E84A27',
    fullName: 'University of Illinois Urbana-Champaign', domain: 'illinois.edu',
  },
  'UT Austin': {
    name: 'UT Austin', abbr: 'TEX', color: '#BF5700', bgColor: '#BF5700', textColor: '#FFFFFF',
    fullName: 'University of Texas at Austin', domain: 'utexas.edu',
  },
  'University of Washington': {
    name: 'UW', abbr: 'UW', color: '#4B2E83', bgColor: '#4B2E83', textColor: '#B7A57A',
    fullName: 'University of Washington', domain: 'washington.edu',
  },
  'UC Davis': {
    name: 'UC Davis', abbr: 'UCD', color: '#002855', bgColor: '#002855', textColor: '#DAAA00',
    fullName: 'University of California, Davis', domain: 'ucdavis.edu',
  },
  'UC San Diego': {
    name: 'UCSD', abbr: 'UCSD', color: '#182B49', bgColor: '#182B49', textColor: '#FFCD00',
    fullName: 'University of California, San Diego', domain: 'ucsd.edu',
  },
  'UCLA': {
    name: 'UCLA', abbr: 'UCLA', color: '#2774AE', bgColor: '#2774AE', textColor: '#FFD100',
    fullName: 'University of California, Los Angeles', domain: 'ucla.edu',
  },
  'Penn State': {
    name: 'Penn State', abbr: 'PSU', color: '#1E407C', bgColor: '#1E407C', textColor: '#FFFFFF',
    fullName: 'Pennsylvania State University', domain: 'psu.edu',
  },

  // ── CLEAN TECH STARTUPS & SCALE-UPS ──
  'Heirloom Carbon': {
    name: 'Heirloom', abbr: 'HLM', color: '#059669', bgColor: '#059669', textColor: '#FFFFFF',
    fullName: 'Heirloom Carbon Technologies', domain: 'heirloomcarbon.com',
  },
  'Electric Hydrogen': {
    name: 'Electric Hydrogen', abbr: 'EH2', color: '#0284C7', bgColor: '#0284C7', textColor: '#FFFFFF',
    fullName: 'Electric Hydrogen (EH2)', domain: 'eh2.com',
  },
  'Commonwealth Fusion Systems': {
    name: 'CFS', abbr: 'CFS', color: '#7C3AED', bgColor: '#7C3AED', textColor: '#FFFFFF',
    fullName: 'Commonwealth Fusion Systems', domain: 'cfs.energy',
  },
  'Helion Energy': {
    name: 'Helion', abbr: 'HLN', color: '#D97706', bgColor: '#D97706', textColor: '#FFFFFF',
    fullName: 'Helion Energy', domain: 'helionenergy.com',
  },
  'QuantumScape': {
    name: 'QuantumScape', abbr: 'QS', color: '#2563EB', bgColor: '#2563EB', textColor: '#FFFFFF',
    fullName: 'QuantumScape Corporation', domain: 'quantumscape.com',
  },
  'Fluence': {
    name: 'Fluence', abbr: 'FLNC', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF',
    fullName: 'Fluence Energy', domain: 'fluenceenergy.com',
  },
};

// Aliases mapping for common names & variations
const ORG_ALIASES: Record<string, string> = {
  'Advanced Research Projects Agency-Energy': 'ARPA-E',
  'Advanced Research Projects Agency–Energy': 'ARPA-E',
  'Advanced Research Projects Agency - Energy': 'ARPA-E',
  'ARPA-E Program Management & Inquiries': 'ARPA-E',
  'California Energy Commission': 'CEC',
  'California Energy Commission (CEC)': 'CEC',
  'Bill & Melinda Gates Foundation': 'Gates Foundation',
  'Massachusetts Energy Innovation Center': 'MassCEC',
  'Massachusetts Energy Innovation Center (MassCEC)': 'MassCEC',
  'New York State Energy Research and Development Authority': 'NYSERDA',
  'New York State Energy Research and Development Authority (NYSERDA)': 'NYSERDA',
  'U.S. Department of Energy': 'DOE',
  'Department of Energy': 'DOE',
  'DOE Solar Energy Technologies Office': 'DOE',
  'DOE Hydrogen and Fuel Cell Technologies Office': 'DOE',
  'DOE Building Technologies Office': 'DOE',
  'DOE Vehicle Technologies Office': 'DOE',
  'DOE Office of Energy Innovation Demonstrations': 'DOE',
  'DOE Grid Deployment Office': 'DOE',
  'DOE Office of Fossil Energy and Carbon Management': 'DOE',
  'National Science Foundation': 'NSF',
  'Environmental Protection Agency': 'EPA',
  'U.S. Environmental Protection Agency': 'EPA',
  'Department of Defense': 'DOD',
  'U.S. Department of Defense': 'DOD',
  'Department of Transportation': 'DOT',
  'Department of Agriculture': 'USDA',
  'National Aeronautics and Space Administration': 'NASA',
  'Consolidated Edison, Inc.': 'Con Edison',
  'Consolidated Edison': 'Con Edison',
  'Consolidated Edison Company of New York (Con Edison)': 'Con Edison',
  'National Grid USA': 'National Grid',
  'New York State Electric & Gas': 'NYSEG',
  'Rochester Gas & Electric': 'RG&E',
  'Central Hudson Gas & Electric': 'Central Hudson',
  'Long Island Power Authority': 'LIPA',
  'New York Power Authority': 'NYPA',
  'Joint Utilities of New York': 'Joint Utilities of NY',
  'Pacific Gas and Electric Company': 'Pacific Gas and Electric',
  'Pacific Gas and Electric Company (PG&E)': 'Pacific Gas and Electric',
  'Southern California Edison (SCE)': 'Southern California Edison',
  'National Renewable Energy Laboratory': 'NREL',
  'National Renewable Energy Laboratory (NREL)': 'NREL',
  'Pacific Northwest National Laboratory': 'PNNL',
  'Pacific Northwest National Laboratory (PNNL)': 'PNNL',
  'Lawrence Berkeley National Laboratory': 'LBNL',
  'Lawrence Berkeley National Laboratory (LBNL)': 'LBNL',
  'Oak Ridge National Laboratory': 'ORNL',
  'Oak Ridge National Laboratory (ORNL)': 'ORNL',
  'Massachusetts Institute of Technology': 'MIT',
  'Massachusetts Institute of Technology (MIT)': 'MIT',
  'University of California, Berkeley': 'UC Berkeley',
  'California Institute of Technology': 'Caltech',
  'California Institute of Technology (Caltech)': 'Caltech',
  'University of California, Davis': 'UC Davis',
  'University of California, San Diego': 'UC San Diego',
  'University of California, Los Angeles': 'UCLA',
  'University of Texas at Austin': 'UT Austin',
  'Pennsylvania State University': 'Penn State',
  'Form Energy, Inc.': 'Form Energy',
  'Form Energy Inc': 'Form Energy',
  'Electric Hydrogen (EH2)': 'Electric Hydrogen',
  'Heirloom Carbon Technologies': 'Heirloom Carbon',
  'TerraPower, LLC': 'TerraPower',
};

// Map org names to their logo image filenames (in /logos/ directory)
const ORG_LOGO_FILES: Record<string, string> = {
  'NYSERDA': 'nyserda.jpg',
  'DOE': 'doe.jpg',
  'NSF': 'nsf.jpg',
  'ARPA-E': 'arpa_e.jpg',
  'EPA': 'epa.jpg',
  'NASA': 'nasa.jpg',
  'USDA': 'usda.jpg',
  'DOD': 'dod.jpg',
  'DOC': 'doc.jpg',
  'DOT': 'dot.jpg',
  'Gates Foundation': 'gates_foundation.jpg',
  'CEC': 'cec.jpg',
  'MassCEC': 'masscec.jpg',
};

// Heuristic keyword-to-domain mapping for prominent energy innovation entities
const INFERRED_DOMAINS: [RegExp, string][] = [
  [/nyserda/i, 'nyserda.ny.gov'],
  [/energy\.gov|department of energy|\bdoe\b/i, 'energy.gov'],
  [/arpa-e/i, 'arpa-e.energy.gov'],
  [/masscec/i, 'masscec.com'],
  [/california energy commission|\bcec\b/i, 'energy.ca.gov'],
  [/national science foundation|\bnsf\b/i, 'nsf.gov'],
  [/nrel|national renewable energy/i, 'nrel.gov'],
  [/pnnl|pacific northwest national/i, 'pnnl.gov'],
  [/lbl\.gov|lbnl|lawrence berkeley/i, 'lbl.gov'],
  [/ornl|oak ridge national/i, 'ornl.gov'],
  [/coned|con edison|consolidated edison/i, 'coned.com'],
  [/national grid/i, 'nationalgridus.com'],
  [/pge\.com|pacific gas and electric|\bpg&e\b/i, 'pge.com'],
  [/sce\.com|southern california edison/i, 'sce.com'],
  [/eversource/i, 'eversource.com'],
  [/mit\.edu|massachusetts institute of tech/i, 'mit.edu'],
  [/cornell/i, 'cornell.edu'],
  [/stanford/i, 'stanford.edu'],
  [/caltech|california institute of tech/i, 'caltech.edu'],
  [/harvard/i, 'harvard.edu'],
  [/princeton/i, 'princeton.edu'],
  [/columbia/i, 'columbia.edu'],
  [/berkeley/i, 'berkeley.edu'],
  [/uc davis|ucdavis/i, 'ucdavis.edu'],
  [/purdue/i, 'purdue.edu'],
  [/umich|university of michigan/i, 'umich.edu'],
  [/uiuc|illinois\.edu/i, 'illinois.edu'],
  [/utexas|university of texas/i, 'utexas.edu'],
  [/form energy/i, 'formenergy.com'],
  [/sublime systems/i, 'sublimesystems.com'],
  [/boston metal/i, 'bostonmetal.com'],
  [/heirloom/i, 'heirloomcarbon.com'],
  [/terrapower/i, 'terrapower.com'],
  [/praeses/i, 'praeses.com'],
  [/earthscope/i, 'earthscope.org'],
  [/maalka/i, 'maalka.com'],
  [/mainspring energy/i, 'mainspringenergy.com'],
  [/cuberg/i, 'cuberg.net'],
  [/ge hitachi/i, 'gehitachinuclear.com'],
  [/plus power/i, 'pluspower.com'],
  [/mitsubishi/i, 'mitsubishipower.com'],
  [/mainstream engineering/i, 'mainstream-engr.com'],
];

/**
 * Get brand info for an organization. Falls back to a generic brand.
 */
export function getOrgBrand(orgName: string): OrgBrand {
  if (!orgName) {
    return { name: 'Organization', abbr: 'ORG', color: '#005D95', bgColor: '#005D95', textColor: '#FFFFFF', fullName: 'Organization' };
  }

  // Check aliases directly
  const canonicalName = ORG_ALIASES[orgName] || orgName;
  if (ORG_BRANDS[canonicalName]) return ORG_BRANDS[canonicalName];
  if (ORG_BRANDS[orgName]) return ORG_BRANDS[orgName];

  // Try normalized name
  const stripped = orgName
    .replace(/\s*\(.*?\)\s*/g, ' ')
    .replace(/,\s*(Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Co\.?)$/i, '')
    .trim();

  if (ORG_ALIASES[stripped] && ORG_BRANDS[ORG_ALIASES[stripped]]) return ORG_BRANDS[ORG_ALIASES[stripped]];
  if (ORG_BRANDS[stripped]) return ORG_BRANDS[stripped];

  // Try domain inference
  let inferredDomain: string | undefined = undefined;
  for (const [pattern, dom] of INFERRED_DOMAINS) {
    if (pattern.test(orgName)) {
      inferredDomain = dom;
      break;
    }
  }

  // Generate clean initials / monogram
  const clean = stripped.replace(/[^a-zA-Z0-9\s]/g, '').trim();
  const words = clean.split(/\s+/).filter(Boolean);
  const abbr = words.length >= 2 
    ? (words[0][0] + words[1][0]).toUpperCase()
    : orgName.substring(0, 3).toUpperCase();

  // Hash org name to a rich deterministic brand color
  const palette = ['#005D95', '#003A5C', '#2B6CB0', '#0D9488', '#0077B6', '#1E40AF', '#047857', '#B45309', '#C53030', '#7C3AED'];
  let hash = 0;
  for (let i = 0; i < orgName.length; i++) hash = orgName.charCodeAt(i) + ((hash << 5) - hash);
  const color = palette[Math.abs(hash) % palette.length];

  return {
    name: orgName,
    abbr,
    color,
    bgColor: color,
    textColor: '#FFFFFF',
    fullName: orgName,
    domain: inferredDomain,
  };
}

const sizeMap = {
  xs: { wh: 'w-5 h-5', text: 'text-[7px]', imgPx: 20 },
  sm: { wh: 'w-7 h-7', text: 'text-[9px]', imgPx: 28 },
  md: { wh: 'w-9 h-9', text: 'text-[10px]', imgPx: 36 },
  lg: { wh: 'w-12 h-12', text: 'text-[12px]', imgPx: 48 },
  xl: { wh: 'w-16 h-16', text: 'text-[14px]', imgPx: 64 },
};

interface OrgLogoProps {
  org: string;
  domain?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showTooltip?: boolean;
}

/**
 * Renders an organization logo.
 * Priority 1: Static bundled logo from /logos/
 * Priority 2: Google Favicon CDN via domain (100% uptime, 128px high-res)
 * Priority 3: DuckDuckGo CDN via domain
 * Priority 4: Branded CSS monogram badge with official organization styling.
 */
export const OrgLogo: React.FC<OrgLogoProps> = ({ org, domain, size = 'sm', className = '', showTooltip = true }) => {
  const brand = getOrgBrand(org);
  const canonicalName = ORG_ALIASES[org] || org;
  const logoFile = ORG_LOGO_FILES[canonicalName] || ORG_LOGO_FILES[brand.name] || ORG_LOGO_FILES[org];
  
  // Resolve effective domain
  let rawDomain = domain || brand.domain;
  if (!rawDomain && org) {
    for (const [pattern, dom] of INFERRED_DOMAINS) {
      if (pattern.test(org)) {
        rawDomain = dom;
        break;
      }
    }
  }

  const [localImgError, setLocalImgError] = useState(false);
  const [googleImgError, setGoogleImgError] = useState(false);
  const [ddgImgError, setDdgImgError] = useState(false);

  const s = sizeMap[size];

  // Clean domain helper
  const cleanDomain = rawDomain
    ? rawDomain.replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/^www\./, '').trim()
    : null;

  // Priority 1: Static bundled logo in /logos/
  if (logoFile && !localImgError) {
    return (
      <img
        src={`/logos/${logoFile}`}
        alt={brand.fullName}
        title={showTooltip ? brand.fullName : undefined}
        className={`${s.wh} rounded-md object-contain shrink-0 bg-white border border-slate-100 p-0.5 shadow-2xs ${className}`}
        onError={() => setLocalImgError(true)}
        loading="lazy"
      />
    );
  }

  // Priority 2: Google Favicon CDN (High-res 128px)
  if (cleanDomain && !googleImgError) {
    return (
      <img
        src={`https://www.google.com/s2/favicons?domain=${cleanDomain}&sz=128`}
        alt={brand.fullName}
        title={showTooltip ? brand.fullName : undefined}
        className={`${s.wh} rounded-md object-contain bg-white border border-slate-100 p-0.5 shadow-2xs shrink-0 ${className}`}
        onError={() => setGoogleImgError(true)}
        loading="lazy"
      />
    );
  }

  // Priority 3: DuckDuckGo Icon CDN
  if (cleanDomain && !ddgImgError) {
    return (
      <img
        src={`https://icons.duckduckgo.com/ip3/${cleanDomain}.ico`}
        alt={brand.fullName}
        title={showTooltip ? brand.fullName : undefined}
        className={`${s.wh} rounded-md object-contain bg-white border border-slate-100 p-0.5 shadow-2xs shrink-0 ${className}`}
        onError={() => setDdgImgError(true)}
        loading="lazy"
      />
    );
  }

  // Priority 4: Branded monogram badge with official colors
  return (
    <div
      className={`inline-flex items-center justify-center rounded-md font-bold tracking-tight select-none shadow-2xs shrink-0 ${s.wh} ${s.text} ${className}`}
      style={{ backgroundColor: brand.bgColor, color: brand.textColor }}
      title={showTooltip ? brand.fullName : undefined}
    >
      {brand.abbr}
    </div>
  );
};

interface OrgLogoWithNameProps extends OrgLogoProps {
  nameClassName?: string;
}

export const OrgLogoWithName: React.FC<OrgLogoWithNameProps> = ({ org, domain, size = 'sm', className = '', nameClassName = '', showTooltip = true }) => {
  const brand = getOrgBrand(org);
  return (
    <div className={`inline-flex items-center gap-2 ${className}`} title={showTooltip ? brand.fullName : undefined}>
      <OrgLogo org={org} domain={domain} size={size} showTooltip={false} />
      <span className={`font-medium ${nameClassName}`}>{org}</span>
    </div>
  );
};

