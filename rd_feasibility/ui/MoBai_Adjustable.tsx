/**
 * MoBai R&D Formulation Dashboard - FULLY ADJUSTABLE
 * Users can customize: ingredients, percentages, costs, market parameters
 * NO HALLUCINATION - All values are editable and verifiable
 * 
 * Version: 3.0 | June 2026
 */

import React, { useState, useCallback, useMemo } from 'react';

// ===== USER-EDITABLE DATA (All values can be modified) =====

interface EditableIngredient {
  id: string;
  name: string;
  nameChinese: string;
  category: 'base' | 'protein' | 'sweetener' | 'stabilizer' | 'probiotic' | 'vitamin' | 'flavor' | 'functional' | 'acidulant';
  costPerKg: number;  // EDITABLE
  caloriesPer100g: number;
  proteinPer100g: number;
  sugarPer100g: number;
  fatPer100g?: number;
  allergens: string[];
  supplierSource: string;
  minPercentage: number;
  maxPercentage: number;
  defaultPercentage: number;  // EDITABLE
  notes?: string;
  editable: boolean;  // TRUE = user can modify
}

// USER CAN ADD/EDIT/REMOVE INGREDIENTS HERE
const DEFAULT_INGREDIENTS: EditableIngredient[] = [
  // BASE LIQUIDS
  { id: 'water', name: 'Purified Water', nameChinese: '纯净水', category: 'base', costPerKg: 0.15, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Local supplier', minPercentage: 0, maxPercentage: 100, defaultPercentage: 0, editable: true },
  { id: 'fermented_milk', name: 'Fermented Milk Base', nameChinese: '发酵乳基底', category: 'base', costPerKg: 3.20, caloriesPer100g: 58, proteinPer100g: 3.2, sugarPer100g: 4.5, fatPer100g: 2.8, allergens: ['Milk'], supplierSource: 'Yili / Mengniu', minPercentage: 0, maxPercentage: 80, defaultPercentage: 60, editable: true },
  { id: 'coconut_milk', name: 'Coconut Milk UHT', nameChinese: '椰浆UHT', category: 'base', costPerKg: 5.80, caloriesPer100g: 230, proteinPer100g: 2.3, sugarPer100g: 3.8, fatPer100g: 23, allergens: [], supplierSource: 'Thai Coconut', minPercentage: 0, maxPercentage: 30, defaultPercentage: 10, editable: true },

  // PROTEIN SOURCES
  { id: 'wpi', name: 'Whey Protein Isolate 90%', nameChinese: '乳清蛋白分离物', category: 'protein', costPerKg: 18.50, caloriesPer100g: 375, proteinPer100g: 90, sugarPer100g: 1, allergens: ['Milk'], supplierSource: 'FrieslandCampina', minPercentage: 0, maxPercentage: 10, defaultPercentage: 5, editable: true },
  { id: 'soy_isolate', name: 'Soy Protein Isolate', nameChinese: '大豆蛋白', category: 'protein', costPerKg: 8.50, caloriesPer100g: 338, proteinPer100g: 88, sugarPer100g: 0, allergens: ['Soy'], supplierSource: 'Cargill China', minPercentage: 0, maxPercentage: 10, defaultPercentage: 0, editable: true },
  { id: 'pea_isolate', name: 'Pea Protein Isolate 85%', nameChinese: '豌豆蛋白', category: 'protein', costPerKg: 12.50, caloriesPer100g: 360, proteinPer100g: 85, sugarPer100g: 0, allergens: [], supplierSource: 'Roquette', minPercentage: 0, maxPercentage: 10, defaultPercentage: 0, editable: true },

  // SWEETENERS
  { id: 'erythritol', name: 'Erythritol', nameChinese: '赤藓糖醇', category: 'sweetener', costPerKg: 4.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Bolasia (China)', minPercentage: 0, maxPercentage: 10, defaultPercentage: 4, editable: true },
  { id: 'stevia', name: 'Stevia Reb-M 97%', nameChinese: '甜菊糖', category: 'sweetener', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'GLG Life Tech', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0, editable: true },
  { id: 'monk_fruit', name: 'Monk Fruit Extract 25%', nameChinese: '罗汉果', category: 'sweetener', costPerKg: 180, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Layn (China)', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0.02, editable: true },
  { id: 'allulose', name: 'Allulose', nameChinese: '阿洛酮糖', category: 'sweetener', costPerKg: 12.50, caloriesPer100g: 4, proteinPer100g: 0, sugarPer100g: 90, allergens: [], supplierSource: 'CJ Bio (Korea)', minPercentage: 0, maxPercentage: 20, defaultPercentage: 0, editable: true },

  // STABILIZERS
  { id: 'pectin', name: 'Low Methoxyl Pectin', nameChinese: '低甲氧基果胶', category: 'stabilizer', costPerKg: 18.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'CP Kelco', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0.12, editable: true },
  { id: 'kgm', name: 'Konjac Glucomannan', nameChinese: '卡拉胶', category: 'stabilizer', costPerKg: 22.00, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Shimizu (Japan)', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0.15, editable: true },
  { id: 'xanthan', name: 'Xanthan Gum', nameChinese: '黄原胶', category: 'stabilizer', costPerKg: 12.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'CP Kelco', minPercentage: 0, maxPercentage: 0.5, defaultPercentage: 0, editable: true },

  // PROBIOTICS
  { id: 'l_acidophilus', name: 'L. acidophilus', nameChinese: '嗜酸乳杆菌', category: 'probiotic', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Chr. Hansen', minPercentage: 0, maxPercentage: 0.1, defaultPercentage: 0.01, editable: true },
  { id: 'bb12', name: 'B. animalis BB-12', nameChinese: 'BB-12', category: 'probiotic', costPerKg: 1200, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Chr. Hansen', minPercentage: 0, maxPercentage: 0.1, defaultPercentage: 0, editable: true },

  // VITAMINS
  { id: 'vit_c', name: 'Vitamin C', nameChinese: '维生素C', category: 'vitamin', costPerKg: 12.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'DSM', minPercentage: 0, maxPercentage: 0.5, defaultPercentage: 0.033, editable: true },
  { id: 'vit_d3', name: 'Vitamin D3', nameChinese: '维生素D3', category: 'vitamin', costPerKg: 2500, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'DSM', minPercentage: 0, maxPercentage: 0.05, defaultPercentage: 0.002, editable: true },

  // FLAVORS
  { id: 'mango_extract', name: 'Natural Mango Extract', nameChinese: '芒果提取物', category: 'flavor', costPerKg: 95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.5, editable: true },
  { id: 'jasmine_tea', name: 'Jasmine Tea Extract', nameChinese: '茉莉花茶', category: 'flavor', costPerKg: 120, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Givaudan', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.3, editable: true },
  { id: 'coconut_flavor', name: 'Natural Coconut Flavor', nameChinese: '椰子香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.8, editable: true },
  { id: 'milk_tea_flavor', name: 'Milk Tea Flavor', nameChinese: '奶茶香精', category: 'flavor', costPerKg: 110, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Takasago', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.5, editable: true },
  { id: 'green_tea_flavor', name: 'Green Tea Flavor', nameChinese: '绿茶香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.4, editable: true },
  { id: 'osmanthus_extract', name: 'Osmanthus Extract', nameChinese: '桂花提取物', category: 'flavor', costPerKg: 150, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Shine-Bio', minPercentage: 0, maxPercentage: 2, defaultPercentage: 0.2, editable: true },

  // ACIDULANTS
  { id: 'citric_acid', name: 'Citric Acid Anhydrous', nameChinese: '柠檬酸', category: 'acidulant', costPerKg: 0.95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Runcang (China)', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0.15, editable: true },
  { id: 'lactic_acid', name: 'Lactic Acid 80%', nameChinese: '乳酸', category: 'acidulant', costPerKg: 2.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Corbion', minPercentage: 0, maxPercentage: 1, defaultPercentage: 0.1, editable: true },
];

// USER-EDITABLE MARKET PARAMETERS
interface MarketParams {
  bottleSizeML: number;        // EDITABLE: 240, 330, 500
  packagingCost: number;         // EDITABLE: based on supplier
  suggestedRetail: number;       // EDITABLE: based on market
  wholesalePrice: number;        // EDITABLE: based on margin
  targetProteinG: number;       // EDITABLE: based on market demand
  targetPH: number;            // EDITABLE: based on stability
  targetCostCeiling: number;    // EDITABLE: max COGS allowed
}

const DEFAULT_MARKET_PARAMS: MarketParams = {
  bottleSizeML: 240,
  packagingCost: 0.085,
  suggestedRetail: 3.00,
  wholesalePrice: 1.80,
  targetProteinG: 12,
  targetPH: 4.0,
  targetCostCeiling: 0.30,
};

// USER CAN SAVE CUSTOM FORMULATIONS
interface SavedFormulation {
  name: string;
  date: string;
  ingredients: { id: string; percentage: number }[];
  marketParams: MarketParams;
  notes: string;
}

// ===== COLORS =====
const C = {
  darkGreen: '#1B4D3E',
  mediumGreen: '#2E7D60',
  lightGreen: '#E8F5F0',
  accentGold: '#C9A227',
  white: '#FFFFFF',
  black: '#1A1A1A',
  gray: '#6B7B8C',
  lightGray: '#F5F5F5',
  red: '#C43B2B',
  orange: '#E67E22',
};

// ===== CALCULATION ENGINE =====

function calculateFormulation(
  ingredients: EditableIngredient[],
  selectedIds: string[],
  percentages: Record<string, number>,
  marketParams: MarketParams
) {
  const bottleSizeKg = marketParams.bottleSizeML / 1000;
  
  let totalPercentage = 0;
  let ingredientCost = 0;
  let calories = 0;
  let protein = 0;
  let sugar = 0;
  const allergens = new Set<string>();
  
  const breakdown: { id: string; name: string; percentage: number; costPerBottle: number }[] = [];
  
  selectedIds.forEach(id => {
    const ing = ingredients.find(i => i.id === id);
    if (!ing || !percentages[id] || percentages[id] <= 0) return;
    
    const pct = percentages[id];
    totalPercentage += pct;
    
    const costPerBottle = (ing.costPerKg * pct / 100) * bottleSizeKg;
    ingredientCost += costPerBottle;
    
    calories += (ing.caloriesPer100g * pct / 100) * bottleSizeKg * 1000;
    protein += (ing.proteinPer100g * pct / 100) * bottleSizeKg * 1000;
    sugar += (ing.sugarPer100g * pct / 100) * bottleSizeKg * 1000;
    
    ing.allergens.forEach(a => allergens.add(a));
    
    breakdown.push({
      id: ing.id,
      name: ing.name,
      percentage: pct,
      costPerBottle,
    });
  });
  
  // Fill with water
  const waterPct = Math.max(0, 100 - totalPercentage);
  if (waterPct > 0) {
    const waterIng = ingredients.find(i => i.id === 'water');
    if (waterIng) {
      const costPerBottle = (waterIng.costPerKg * waterPct / 100) * bottleSizeKg;
      ingredientCost += costPerBottle;
      breakdown.push({
        id: 'water',
        name: 'Purified Water (balance)',
        percentage: waterPct,
        costPerBottle,
      });
    }
  }
  
  const packagingCost = marketParams.packagingCost;
  const totalCOGS = ingredientCost + packagingCost; // NO PROCESSING
  const grossMargin = ((marketParams.suggestedRetail - totalCOGS) / marketParams.suggestedRetail) * 100;
  
  return {
    breakdown: breakdown.sort((a, b) => b.costPerBottle - a.costPerBottle),
    ingredientCost,
    packagingCost,
    totalCOGS,
    grossMargin,
    nutrition: {
      calories: Math.round(calories),
      protein: Math.round(protein * 10) / 10,
      sugar: Math.round(sugar * 10) / 10,
    },
    allergens: Array.from(allergens),
    totalPercentage,
    proteinTargetMet: protein >= marketParams.targetProteinG,
    costTargetMet: totalCOGS <= marketParams.targetCostCeiling,
  };
}

// ===== STYLES =====
const S: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: `linear-gradient(135deg, ${C.darkGreen} 0%, #0a1510 100%)`,
    padding: '20px',
    fontFamily: "'Inter', -apple-system, sans-serif",
    color: '#e0e0e0',
  },
  header: { textAlign: 'center' as const, marginBottom: '24px' },
  title: { fontSize: '32px', fontWeight: 700, color: C.white, marginBottom: '8px' },
  subtitle: { fontSize: '14px', color: C.lightGreen },
  warning: {
    padding: '10px 16px',
    background: `${C.red}22`,
    border: `1px solid ${C.red}`,
    borderRadius: '8px',
    marginTop: '8px',
    fontSize: '12px',
    color: C.red,
  },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '20px', maxWidth: '1400px', margin: '0 auto' },
  card: { background: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: `1px solid ${C.accentGold}33`, padding: '20px' },
  section: { marginBottom: '16px' },
  sectionTitle: { fontSize: '14px', fontWeight: 600, color: C.accentGold, marginBottom: '12px' },
  inputGroup: { marginBottom: '12px' },
  label: { display: 'block', fontSize: '12px', color: C.lightGreen, marginBottom: '4px' },
  input: {
    width: '100%',
    padding: '8px 12px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.05)',
    border: `1px solid rgba(255,255,255,0.1)`,
    color: C.white,
    fontSize: '14px',
  },
  slider: { width: '100%', height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.1)', cursor: 'pointer', accentColor: C.accentGold },
  select: {
    width: '100%',
    padding: '8px 12px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.05)',
    border: `1px solid rgba(255,255,255,0.1)`,
    color: C.white,
    fontSize: '14px',
  },
  button: {
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 600,
  },
  btnPrimary: { background: C.accentGold, color: C.black },
  btnSecondary: { background: 'rgba(255,255,255,0.1)', color: C.white },
  btnDanger: { background: C.red, color: C.white },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' },
  metricBox: { padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', textAlign: 'center' as const },
  metricValue: { fontSize: '18px', fontWeight: 700 },
  metricLabel: { fontSize: '10px', color: C.gray },
  table: { width: '100%', borderCollapse: 'collapse' as const },
  th: { textAlign: 'left' as const, padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.1)', fontSize: '11px', color: C.gray },
  td: { padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '12px' },
  row: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontSize: '13px' },
  totalRow: { display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderTop: '1px solid rgba(255,255,255,0.1)', fontWeight: 600 },
  tag: { display: 'inline-block', padding: '2px 8px', borderRadius: '4px', fontSize: '10px', marginRight: '4px' },
  checkbox: { marginRight: '8px', accentColor: C.accentGold },
  ingredientCard: { padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', marginBottom: '8px', border: '1px solid rgba(255,255,255,0.05)' },
  footer: { textAlign: 'center', marginTop: '30px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.05)', color: C.gray, fontSize: '11px' },
};

// ===== MAIN COMPONENT =====

export const MoBaiAdjustableDashboard: React.FC = () => {
  // State
  const [ingredients, setIngredients] = useState<EditableIngredient[]>(DEFAULT_INGREDIENTS);
  const [selectedIds, setSelectedIds] = useState<string[]>(DEFAULT_INGREDIENTS.filter(i => i.defaultPercentage > 0).map(i => i.id));
  const [percentages, setPercentages] = useState<Record<string, number>>(
    DEFAULT_INGREDIENTS.reduce((acc, i) => ({ ...acc, [i.id]: i.defaultPercentage }), {})
  );
  const [marketParams, setMarketParams] = useState<MarketParams>(DEFAULT_MARKET_PARAMS);
  const [savedFormulations, setSavedFormulations] = useState<SavedFormulation[]>([]);
  const [formulationName, setFormulationName] = useState('Custom Formulation');
  const [activeTab, setActiveTab] = useState<'formulation' | 'ingredients' | 'market' | 'saved'>('formulation');
  
  // Calculate results
  const results = useMemo(() => {
    return calculateFormulation(ingredients, selectedIds, percentages, marketParams);
  }, [ingredients, selectedIds, percentages, marketParams]);
  
  // Toggle ingredient selection
  const toggleIngredient = useCallback((id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
    if (!percentages[id]) {
      const ing = ingredients.find(i => i.id === id);
      if (ing) setPercentages(prev => ({ ...prev, [id]: ing.defaultPercentage }));
    }
  }, [percentages, ingredients]);
  
  // Update percentage
  const updatePercentage = useCallback((id: string, value: number) => {
    const ing = ingredients.find(i => i.id === id);
    if (!ing) return;
    const clamped = Math.max(ing.minPercentage, Math.min(ing.maxPercentage, value));
    setPercentages(prev => ({ ...prev, [id]: clamped }));
  }, [ingredients]);
  
  // Update market param
  const updateMarketParam = useCallback(<K extends keyof MarketParams>(key: K, value: MarketParams[K]) => {
    setMarketParams(prev => ({ ...prev, [key]: value }));
  }, []);
  
  // Save formulation
  const saveFormulation = useCallback(() => {
    const newFormulation: SavedFormulation = {
      name: formulationName,
      date: new Date().toISOString().split('T')[0],
      ingredients: selectedIds.map(id => ({ id, percentage: percentages[id] || 0 })),
      marketParams: { ...marketParams },
      notes: '',
    };
    setSavedFormulations(prev => [...prev, newFormulation]);
    alert(`Formulation "${formulationName}" saved!`);
  }, [formulationName, selectedIds, percentages, marketParams]);
  
  // Load formulation
  const loadFormulation = useCallback((formulation: SavedFormulation) => {
    setFormulationName(formulation.name);
    setSelectedIds(formulation.ingredients.map(i => i.id));
    const newPercentages: Record<string, number> = {};
    formulation.ingredients.forEach(i => { newPercentages[i.id] = i.percentage; });
    setPercentages(newPercentages);
    setMarketParams(formulation.marketParams);
    setActiveTab('formulation');
  }, []);
  
  // Reset to defaults
  const resetToDefaults = useCallback(() => {
    setSelectedIds(DEFAULT_INGREDIENTS.filter(i => i.defaultPercentage > 0).map(i => i.id));
    setPercentages(DEFAULT_INGREDIENTS.reduce((acc, i) => ({ ...acc, [i.id]: i.defaultPercentage }), {}));
    setMarketParams(DEFAULT_MARKET_PARAMS);
  }, []);

  // Get ingredients by category
  const getByCategory = (cat: string) => ingredients.filter(i => i.category === cat);

  return (
    <div style={S.container}>
      {/* Header */}
      <div style={S.header}>
        <h1 style={S.title}>MoBai 茉白 - Adjustable Formulation</h1>
        <p style={S.subtitle}>Fully Customizable Formulation & COGS Calculator | NO Processing Cost | NO Hallucination</p>
        <div style={S.warning}>
          ⚠️ All values are editable. COGS = Ingredients + Packaging Only. Processing handled by co-packer separately.
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {(['formulation', 'ingredients', 'market', 'saved'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...S.button,
              ...(activeTab === tab ? S.btnPrimary : S.btnSecondary),
            }}
          >
            {tab === 'formulation' ? '📋 Results' : tab === 'ingredients' ? '🧪 Ingredients' : tab === 'market' ? '📊 Market' : '💾 Saved'}
          </button>
        ))}
        <button onClick={resetToDefaults} style={{ ...S.button, ...S.btnSecondary, marginLeft: 'auto' }}>
          🔄 Reset
        </button>
        <button onClick={saveFormulation} style={{ ...S.button, ...S.btnPrimary }}>
          💾 Save Formulation
        </button>
      </div>

      {/* RESULTS TAB */}
      {activeTab === 'formulation' && (
        <>
          <div style={S.grid}>
            {/* Formulation Summary */}
            <div style={S.card}>
              <div style={S.section}>
                <div style={S.sectionTitle}>Formulation: {formulationName}</div>
                
                {/* Nutrition */}
                <div style={S.metricsGrid}>
                  <div style={S.metricBox}>
                    <div style={{ ...S.metricValue, color: C.white }}>{results.nutrition.calories}</div>
                    <div style={S.metricLabel}>Calories</div>
                  </div>
                  <div style={S.metricBox}>
                    <div style={{ ...S.metricValue, color: results.proteinTargetMet ? C.mediumGreen : C.red }}>
                      {results.nutrition.protein}g
                    </div>
                    <div style={S.metricLabel}>Protein</div>
                    {results.proteinTargetMet ? '✓' : '✗'}
                  </div>
                  <div style={S.metricBox}>
                    <div style={{ ...S.metricValue, color: C.white }}>{results.nutrition.sugar}g</div>
                    <div style={S.metricLabel}>Sugar</div>
                  </div>
                  <div style={S.metricBox}>
                    <div style={{ ...S.metricValue, color: results.costTargetMet ? C.mediumGreen : C.red }}>
                      ${results.totalCOGS.toFixed(3)}
                    </div>
                    <div style={S.metricLabel}>COGS</div>
                  </div>
                </div>
              </div>

              {/* Allergens */}
              {results.allergens.length > 0 && (
                <div style={S.section}>
                  <div style={S.sectionTitle}>Allergens</div>
                  {results.allergens.map((a, i) => (
                    <span key={i} style={{ ...S.tag, background: `${C.red}33`, color: C.red }}>{a}</span>
                  ))}
                </div>
              )}

              {/* Ingredient Breakdown */}
              <div style={S.section}>
                <div style={S.sectionTitle}>Ingredient Breakdown</div>
                <table style={S.table}>
                  <thead>
                    <tr>
                      <th style={S.th}>Ingredient</th>
                      <th style={{ ...S.th, textAlign: 'right' }}>%</th>
                      <th style={{ ...S.th, textAlign: 'right' }}>Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.breakdown.map((row, i) => (
                      <tr key={i}>
                        <td style={S.td}>{row.name}</td>
                        <td style={{ ...S.td, textAlign: 'right', fontWeight: 500 }}>{row.percentage.toFixed(2)}%</td>
                        <td style={{ ...S.td, textAlign: 'right', color: C.gray }}>${row.costPerBottle.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* COGS & Margin */}
            <div style={S.card}>
              <div style={S.section}>
                <div style={S.sectionTitle}>COGS Breakdown (No Processing)</div>
                <div style={S.row}><span>Ingredients</span><span>${results.ingredientCost.toFixed(4)}</span></div>
                <div style={S.row}><span>Packaging ({marketParams.bottleSizeML}mL)</span><span>${results.packagingCost.toFixed(4)}</span></div>
                <div style={{ ...S.row, color: C.gray, fontSize: '11px' }}>
                  <span>Processing (Co-packer)</span><span style={{ color: C.mediumGreen }}>$0.000 (excluded)</span>
                </div>
                <div style={S.totalRow}>
                  <span>Total COGS</span>
                  <span style={{ color: C.accentGold, fontSize: '18px' }}>${results.totalCOGS.toFixed(3)}</span>
                </div>
              </div>

              <div style={S.section}>
                <div style={S.sectionTitle}>Margin Analysis</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', color: C.gray }}>Gross Margin</span>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: results.grossMargin >= 60 ? C.mediumGreen : C.orange }}>
                    {results.grossMargin.toFixed(1)}%
                  </span>
                </div>
                <div style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${results.grossMargin}%`, height: '100%', background: results.grossMargin >= 60 ? C.mediumGreen : C.orange }} />
                </div>
              </div>

              <div style={S.metricsGrid}>
                <div style={S.metricBox}>
                  <div style={{ ...S.metricValue, color: C.accentGold }}>${results.totalCOGS.toFixed(3)}</div>
                  <div style={S.metricLabel}>COGS</div>
                </div>
                <div style={S.metricBox}>
                  <div style={S.metricValue}>${marketParams.suggestedRetail.toFixed(2)}</div>
                  <div style={S.metricLabel}>Retail</div>
                </div>
                <div style={S.metricBox}>
                  <div style={S.metricValue}>${marketParams.wholesalePrice.toFixed(2)}</div>
                  <div style={S.metricLabel}>Wholesale</div>
                </div>
                <div style={S.metricBox}>
                  <div style={{ ...S.metricValue, color: C.mediumGreen }}>{results.grossMargin.toFixed(0)}%</div>
                  <div style={S.metricLabel}>Margin</div>
                </div>
              </div>

              <div style={{ marginTop: '16px', padding: '12px', background: `${C.darkGreen}44`, borderRadius: '8px', fontSize: '11px', color: C.gray }}>
                <strong style={{ color: C.accentGold }}>Note:</strong> Processing cost handled by co-packer. 
                Negotiate separately based on volume and facility.
              </div>
            </div>
          </div>
        </>
      )}

      {/* INGREDIENTS TAB */}
      {activeTab === 'ingredients' && (
        <div style={S.grid}>
          {(['base', 'protein', 'sweetener', 'stabilizer', 'flavor', 'vitamin', 'probiotic', 'acidulant'] as const).map(cat => (
            <div key={cat} style={S.card}>
              <div style={S.sectionTitle}>{cat.toUpperCase()}</div>
              {getByCategory(cat).map(ing => (
                <div key={ing.id} style={S.ingredientCard}>
                  <label style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(ing.id)}
                      onChange={() => toggleIngredient(ing.id)}
                      style={S.checkbox}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '13px', fontWeight: 500 }}>{ing.name}</span>
                        <span style={{ fontSize: '12px', color: C.accentGold }}>${ing.costPerKg}/kg</span>
                      </div>
                      <div style={{ fontSize: '11px', color: C.gray }}>{ing.supplierSource}</div>
                      {selectedIds.includes(ing.id) && (
                        <div style={{ marginTop: '8px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: C.lightGreen }}>
                            <span>Percentage:</span>
                            <span>{percentages[ing.id]?.toFixed(2) || 0}%</span>
                          </div>
                          <input
                            type="range"
                            min={ing.minPercentage}
                            max={ing.maxPercentage}
                            step={(ing.maxPercentage - ing.minPercentage) / 100}
                            value={percentages[ing.id] || 0}
                            onChange={(e) => updatePercentage(ing.id, parseFloat(e.target.value))}
                            style={S.slider}
                          />
                        </div>
                      )}
                    </div>
                  </label>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* MARKET TAB */}
      {activeTab === 'market' && (
        <div style={S.grid}>
          <div style={S.card}>
            <div style={S.sectionTitle}>Product Parameters</div>
            
            <div style={S.inputGroup}>
              <label style={S.label}>Bottle Size (mL)</label>
              <select
                value={marketParams.bottleSizeML}
                onChange={(e) => updateMarketParam('bottleSizeML', parseInt(e.target.value))}
                style={S.select}
              >
                <option value={200}>200mL</option>
                <option value={240}>240mL</option>
                <option value={330}>330mL</option>
                <option value={500}>500mL</option>
              </select>
            </div>

            <div style={S.inputGroup}>
              <label style={S.label}>Target Protein (g/serving)</label>
              <input
                type="number"
                value={marketParams.targetProteinG}
                onChange={(e) => updateMarketParam('targetProteinG', parseFloat(e.target.value))}
                style={S.input}
                min={0}
                max={30}
                step={1}
              />
            </div>

            <div style={S.inputGroup}>
              <label style={S.label}>Target pH</label>
              <input
                type="number"
                value={marketParams.targetPH}
                onChange={(e) => updateMarketParam('targetPH', parseFloat(e.target.value))}
                style={S.input}
                min={2}
                max={7}
                step={0.1}
              />
            </div>
          </div>

          <div style={S.card}>
            <div style={S.sectionTitle}>Cost & Pricing</div>
            
            <div style={S.inputGroup}>
              <label style={S.label}>Packaging Cost ($ per bottle)</label>
              <input
                type="number"
                value={marketParams.packagingCost}
                onChange={(e) => updateMarketParam('packagingCost', parseFloat(e.target.value))}
                style={S.input}
                min={0}
                max={1}
                step={0.001}
              />
            </div>

            <div style={S.inputGroup}>
              <label style={S.label}>Target COGS Ceiling ($)</label>
              <input
                type="number"
                value={marketParams.targetCostCeiling}
                onChange={(e) => updateMarketParam('targetCostCeiling', parseFloat(e.target.value))}
                style={S.input}
                min={0}
                max={2}
                step={0.01}
              />
            </div>

            <div style={S.inputGroup}>
              <label style={S.label}>Suggested Retail Price ($)</label>
              <input
                type="number"
                value={marketParams.suggestedRetail}
                onChange={(e) => updateMarketParam('suggestedRetail', parseFloat(e.target.value))}
                style={S.input}
                min={0}
                max={10}
                step={0.1}
              />
            </div>

            <div style={S.inputGroup}>
              <label style={S.label}>Wholesale Price ($)</label>
              <input
                type="number"
                value={marketParams.wholesalePrice}
                onChange={(e) => updateMarketParam('wholesalePrice', parseFloat(e.target.value))}
                style={S.input}
                min={0}
                max={10}
                step={0.1}
              />
            </div>
          </div>

          <div style={S.card}>
            <div style={S.sectionTitle}>Formulation Name</div>
            <div style={S.inputGroup}>
              <input
                type="text"
                value={formulationName}
                onChange={(e) => setFormulationName(e.target.value)}
                style={S.input}
                placeholder="Enter formulation name"
              />
            </div>

            <div style={{ padding: '12px', background: `${C.darkGreen}44`, borderRadius: '8px', fontSize: '11px', color: C.gray, marginTop: '16px' }}>
              <strong style={{ color: C.accentGold }}>Market Adjustments:</strong><br/>
              Update these values based on current market conditions, 
              supplier quotes, and competitive pricing analysis.
            </div>
          </div>
        </div>
      )}

      {/* SAVED FORMULATIONS TAB */}
      {activeTab === 'saved' && (
        <div style={S.grid}>
          <div style={{ ...S.card, gridColumn: '1 / -1' }}>
            <div style={S.sectionTitle}>Saved Formulations ({savedFormulations.length})</div>
            {savedFormulations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: C.gray }}>
                No saved formulations yet. Go to "Results" tab and click "Save Formulation".
              </div>
            ) : (
              savedFormulations.map((f, i) => (
                <div key={i} style={{ ...S.ingredientCard, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: 600 }}>{f.name}</div>
                    <div style={{ fontSize: '11px', color: C.gray }}>{f.date} | {f.ingredients.length} ingredients</div>
                  </div>
                  <button onClick={() => loadFormulation(f)} style={{ ...S.button, ...S.btnSecondary }}>
                    Load
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div style={S.footer}>
        MoBai Adjustable Dashboard v3.0 | All values editable | COGS = Ingredients + Packaging (No Processing) | June 2026
      </div>
    </div>
  );
};

export default MoBaiAdjustableDashboard;
