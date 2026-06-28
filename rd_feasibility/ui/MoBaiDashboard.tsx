/**
 * MoBai Formulation Prediction & COGS Dashboard
 * Simplified: Only Formulation + Cost Analysis (NO Processing Stage)
 * 
 * Updated: June 2026 | Version 2.0.0
 */

import React, { useState, useCallback } from 'react';

// ===== MoBai INGREDIENT DATA =====

interface IngredientDef {
  id: string;
  name: string;
  nameChinese?: string;
  category: string;
  costPerKg: number;
  caloriesPer100g: number;
  proteinPer100g: number;
  sugarPer100g: number;
  fatPer100g?: number;
  allergens: string[];
  notes?: string;
}

const MOBai_INGREDIENTS: IngredientDef[] = [
  // BASE LIQUIDS
  { id: 'water', name: 'Purified Water', nameChinese: '纯净水', category: 'base', costPerKg: 0.15, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [] },
  { id: 'fermented_milk', name: 'Fermented Milk Base', nameChinese: '发酵乳基底', category: 'base', costPerKg: 3.20, caloriesPer100g: 58, proteinPer100g: 3.2, sugarPer100g: 4.5, fatPer100g: 2.8, allergens: ['Milk'], notes: 'Lactic acid masking' },
  { id: 'coconut_milk', name: 'Coconut Milk (UHT)', nameChinese: '椰浆', category: 'base', costPerKg: 5.80, caloriesPer100g: 230, proteinPer100g: 2.3, sugarPer100g: 3.8, fatPer100g: 23, allergens: [], notes: 'Astringency buffering' },

  // PROTEIN SOURCES
  { id: 'wpi', name: 'Whey Protein Isolate 90%', nameChinese: '乳清蛋白分离物', category: 'protein', costPerKg: 18.50, caloriesPer100g: 375, proteinPer100g: 90, sugarPer100g: 1, allergens: ['Milk'], notes: 'Core protein source' },
  { id: 'soy_isolate', name: 'Soy Protein Isolate', nameChinese: '大豆蛋白分离物', category: 'protein', costPerKg: 8.50, caloriesPer100g: 338, proteinPer100g: 88, sugarPer100g: 0, allergens: ['Soy'], notes: 'Vegan alternative' },
  { id: 'pea_isolate', name: 'Pea Protein Isolate 85%', nameChinese: '豌豆蛋白分离物', category: 'protein', costPerKg: 12.50, caloriesPer100g: 360, proteinPer100g: 85, sugarPer100g: 0, allergens: [], notes: 'Plant-based option' },
  { id: 'collagen', name: 'Collagen Peptides', nameChinese: '胶原蛋白肽', category: 'protein', costPerKg: 28.00, caloriesPer100g: 360, proteinPer100g: 90, sugarPer100g: 0, allergens: [], notes: 'Skin health positioning' },

  // SWEETENERS
  { id: 'erythritol', name: 'Erythritol', nameChinese: '赤藓糖醇', category: 'sweetener', costPerKg: 4.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Sugar-free' },
  { id: 'stevia', name: 'Stevia Reb-M 97%', nameChinese: '甜菊糖', category: 'sweetener', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Zero calorie' },
  { id: 'monk_fruit', name: 'Monk Fruit Extract', nameChinese: '罗汉果提取物', category: 'sweetener', costPerKg: 180, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Natural sweetener' },
  { id: 'allulose', name: 'Allulose', nameChinese: '阿洛酮糖', category: 'sweetener', costPerKg: 12.50, caloriesPer100g: 4, proteinPer100g: 0, sugarPer100g: 90, allergens: [], notes: 'Rare sugar' },

  // STABILIZERS
  { id: 'pectin', name: 'Low Methoxyl Pectin', nameChinese: '低甲氧基果胶', category: 'stabilizer', costPerKg: 18.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'WPI stabilizer at pH 3.8-4.2' },
  { id: 'kgm', name: 'Konjac Glucomannan (KGM)', nameChinese: '卡拉胶', category: 'stabilizer', costPerKg: 22.00, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Texture + volatile entrapment' },
  { id: 'xanthan', name: 'Xanthan Gum', nameChinese: '黄原胶', category: 'stabilizer', costPerKg: 12.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Viscosity control' },
  { id: 'cmc', name: 'Sodium CMC', nameChinese: '羧甲基纤维素钠', category: 'stabilizer', costPerKg: 8.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Synergistic with pectin' },

  // PROBIOTICS
  { id: 'l_acidophilus', name: 'L. acidophilus', nameChinese: '嗜酸乳杆菌', category: 'probiotic', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], notes: 'Gut health claim' },
  { id: 'bb12', name: 'B. animalis BB-12', nameChinese: '动物双歧杆菌', category: 'probiotic', costPerKg: 1200, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], notes: 'Premium probiotic' },

  // VITAMINS
  { id: 'vit_c', name: 'Vitamin C', nameChinese: '维生素C', category: 'vitamin', costPerKg: 12.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: '80mg/serve - antioxidant' },
  { id: 'vit_d3', name: 'Vitamin D3', nameChinese: '维生素D3', category: 'vitamin', costPerKg: 2500, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: '5ug/serve - bone health' },
  { id: 'b_complex', name: 'Vitamin B Complex', nameChinese: '维生素B族', category: 'vitamin', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Energy metabolism' },

  // FLAVORS - VARIANT A: MANGO JASMINE
  { id: 'mango_extract', name: 'Natural Mango Extract', nameChinese: '天然芒果提取物', category: 'flavor', costPerKg: 95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant A - tropical terpenes' },
  { id: 'jasmine_tea', name: 'Jasmine Tea Extract', nameChinese: '茉莉花茶提取物', category: 'flavor', costPerKg: 120, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant A - floral notes' },

  // FLAVORS - VARIANT B: COCONUT MILK TEA
  { id: 'coconut_flavor', name: 'Natural Coconut Flavor', nameChinese: '天然椰子香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant B - lactone esters' },
  { id: 'milk_tea_flavor', name: 'Milk Tea Flavor', nameChinese: '奶茶香精', category: 'flavor', costPerKg: 110, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], notes: 'Variant B - caramelized' },

  // FLAVORS - VARIANT C CANDIDATES
  { id: 'green_tea_flavor', name: 'Green Tea Flavor', nameChinese: '绿茶香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant C - tea-forward' },
  { id: 'osmanthus_extract', name: 'Osmanthus Extract', nameChinese: '桂花提取物', category: 'flavor', costPerKg: 150, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant C - floral premium' },
  { id: 'passion_fruit', name: 'Passion Fruit Flavor', nameChinese: '百香果香精', category: 'flavor', costPerKg: 95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Variant C - tropical tangy' },
  { id: 'vanilla_flavor', name: 'Natural Vanilla Flavor', nameChinese: '天然香草香精', category: 'flavor', costPerKg: 250, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Bitter masking agent' },

  // FUNCTIONAL ADDITIVES
  { id: 'l_theanine', name: 'L-Theanine', nameChinese: '茶氨酸', category: 'functional', costPerKg: 220, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Calm focus' },
  { id: 'caffeine', name: 'Caffeine Anhydrous', nameChinese: '咖啡因', category: 'functional', costPerKg: 45, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Bitter masking competitor' },
  { id: 'taurine', name: 'Taurine', nameChinese: '牛磺酸', category: 'functional', costPerKg: 8.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Energy support' },

  // ACIDULANTS
  { id: 'citric_acid', name: 'Citric Acid Anhydrous', nameChinese: '柠檬酸', category: 'acidulant', costPerKg: 0.95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'pH adjustment' },
  { id: 'lactic_acid', name: 'Lactic Acid 80%', nameChinese: '乳酸', category: 'acidulant', costPerKg: 2.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], notes: 'Sulphury masking' },
  { id: 'malic_acid', name: 'DL-Malic Acid', nameChinese: '苹果酸', category: 'acidulant', costPerKg: 2.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], notes: 'Sweeter acid profile' },
];


// ===== MoBai BRAND COLORS =====
const colors = {
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

// ===== STYLES =====
const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: `linear-gradient(135deg, ${colors.darkGreen} 0%, #0f2920 100%)`,
    padding: '24px',
    fontFamily: "'Inter', -apple-system, sans-serif",
    color: '#e0e0e0',
  },
  header: { textAlign: 'center' as const, marginBottom: '32px' },
  title: {
    fontSize: '36px',
    fontWeight: 700,
    color: colors.white,
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: colors.lightGreen,
    opacity: 0.9,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))',
    gap: '24px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(20px)',
    borderRadius: '16px',
    border: `1px solid ${colors.accentGold}33`,
    padding: '24px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '20px',
  },
  cardTitle: { fontSize: '18px', fontWeight: 600, color: colors.white },
  inputGroup: { marginBottom: '16px' },
  label: { display: 'block', fontSize: '13px', color: colors.lightGreen, marginBottom: '6px', fontWeight: 500 },
  slider: { 
    width: '100%', 
    height: '6px', 
    borderRadius: '3px', 
    background: 'rgba(255,255,255,0.1)', 
    cursor: 'pointer',
    appearance: 'none' as React.CSSProperties['appearance'],
  },
  select: {
    width: '100%',
    padding: '10px 14px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.05)',
    border: `1px solid ${colors.accentGold}44`,
    color: colors.white,
    fontSize: '14px',
  },
  button: {
    width: '100%',
    padding: '14px 24px',
    borderRadius: '12px',
    border: 'none',
    background: `linear-gradient(135deg, ${colors.accentGold} 0%, #D4AF37 100%)`,
    color: colors.black,
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: '16px',
  },
  badge: {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: 600,
  },
  table: { width: '100%', borderCollapse: 'collapse' as const, marginTop: '12px' },
  th: { textAlign: 'left' as const, padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.1)', fontSize: '12px', color: colors.lightGreen },
  td: { padding: '10px 8px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '13px', color: colors.white },
  tag: {
    display: 'inline-block',
    padding: '3px 8px',
    borderRadius: '6px',
    fontSize: '10px',
    marginRight: '4px',
    marginBottom: '2px',
  },
  variantBox: {
    padding: '16px',
    borderRadius: '12px',
    marginBottom: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
};

// ===== HELPER FUNCTIONS =====

function formatCurrency(value: number): string {
  return `$${value.toFixed(4)}`;
}

function getIngredientById(id: string): IngredientDef | undefined {
  return MOBai_INGREDIENTS.find(i => i.id === id);
}

function getScoreColor(score: number): string {
  if (score >= 85) return colors.mediumGreen;
  if (score >= 70) return colors.accentGold;
  if (score >= 50) return colors.orange;
  return colors.red;
}

// ===== FORMULATION PREDICTION ENGINE =====

interface FormulationPrediction {
  variantName: string;
  ingredients: { id: string; percentage: number }[];
  nutritionFacts: { calories: number; protein: number; sugar: number; fiber: number };
  costBreakdown: { ingredientCost: number; packaging: number; processing: number; total: number };
  marginAnalysis: { suggestedMSRP: number; wholesale: number; margin: number };
  score: number;
  rationale: string[];
  warnings: string[];
  allergens: string[];
}

function predictVariantA(targetProtein: number, sugarFree: boolean): FormulationPrediction {
  const ingredients: { id: string; percentage: number }[] = [];
  const rationale: string[] = [];
  const warnings: string[] = [];
  const allergens = new Set<string>();

  // Base
  ingredients.push({ id: 'fermented_milk', percentage: 62 });
  rationale.push('Fermented milk base provides yogurt matrix and lactic acid masking');

  // Protein
  const proteinAmount = Math.min(targetProtein + 0.5, 6);
  ingredients.push({ id: 'wpi', percentage: proteinAmount });
  rationale.push(`Whey Protein Isolate: ${(proteinAmount * 0.24).toFixed(1)}g per serving`);
  allergens.add('Milk');

  // Stabilizers for protein
  ingredients.push({ id: 'pectin', percentage: 0.12 });
  rationale.push('Low Methoxyl Pectin: WPI stabilizer at pH 3.8-4.2');
  ingredients.push({ id: 'kgm', percentage: 0.15 });
  rationale.push('Konjac Glucomannan: Texture control + volatile entrapment');

  // Sweetener
  if (sugarFree) {
    ingredients.push({ id: 'erythritol', percentage: 4 });
    rationale.push('Erythritol: Sugar-free, keto-friendly sweetness');
    ingredients.push({ id: 'monk_fruit', percentage: 0.02 });
    rationale.push('Monk Fruit: Natural sweetener synergy');
  }

  // Flavors - Mango Jasmine
  ingredients.push({ id: 'mango_extract', percentage: 0.5 });
  rationale.push('Natural Mango Extract: Bright, fruity tropical notes');
  ingredients.push({ id: 'jasmine_tea', percentage: 0.3 });
  rationale.push('Jasmine Tea Extract: Floral, tea-inspired aroma');

  // Vitamins
  ingredients.push({ id: 'vit_c', percentage: 0.033 }); // 80mg/240ml
  ingredients.push({ id: 'vit_d3', percentage: 0.002 }); // 5ug/240ml

  // Probiotic
  ingredients.push({ id: 'l_acidophilus', percentage: 0.01 });
  rationale.push('Lactobacillus acidophilus: Gut health claim (≥10⁷ CFU/ml)');

  // Acidulant
  ingredients.push({ id: 'citric_acid', percentage: 0.15 });
  ingredients.push({ id: 'lactic_acid', percentage: 0.1 });

  // Water to 100%
  const total = ingredients.reduce((sum, i) => sum + i.percentage, 0);
  ingredients.push({ id: 'water', percentage: Math.max(0, 100 - total) });

  return buildPrediction('Variant A: Mango Jasmine 芒果茉莉', ingredients, rationale, warnings, Array.from(allergens));
}

function predictVariantB(targetProtein: number, sugarFree: boolean): FormulationPrediction {
  const ingredients: { id: string; percentage: number }[] = [];
  const rationale: string[] = [];
  const warnings: string[] = [];
  const allergens = new Set<string>();

  // Base
  ingredients.push({ id: 'fermented_milk', percentage: 55 });
  rationale.push('Fermented milk base for yogurt profile');

  // Coconut milk
  ingredients.push({ id: 'coconut_milk', percentage: 10 });
  rationale.push('Coconut Milk: Fat content provides astringency buffering');
  allergens.add('Milk');

  // Protein
  const proteinAmount = Math.min(targetProtein + 0.5, 6);
  ingredients.push({ id: 'wpi', percentage: proteinAmount });
  rationale.push(`Whey Protein Isolate: ${(proteinAmount * 0.24).toFixed(1)}g per serving`);
  allergens.add('Milk');

  // Stabilizers
  ingredients.push({ id: 'pectin', percentage: 0.12 });
  ingredients.push({ id: 'kgm', percentage: 0.2 });
  rationale.push('KGM 0.2%: Creamy to thick texture');

  // Sweetener
  if (sugarFree) {
    ingredients.push({ id: 'erythritol', percentage: 4 });
    ingredients.push({ id: 'monk_fruit', percentage: 0.02 });
  }

  // Flavors - Coconut Milk Tea
  ingredients.push({ id: 'coconut_flavor', percentage: 0.8 });
  rationale.push('Natural Coconut Flavor: Creamy lactone esters');
  ingredients.push({ id: 'milk_tea_flavor', percentage: 0.5 });
  rationale.push('Milk Tea Flavor: Caramelized, comforting notes');

  // Vitamins
  ingredients.push({ id: 'vit_c', percentage: 0.033 });
  ingredients.push({ id: 'vit_d3', percentage: 0.002 });

  // Probiotic
  ingredients.push({ id: 'bb12', percentage: 0.01 });
  rationale.push('B. animalis BB-12: Premium probiotic viability');

  // Acidulant
  ingredients.push({ id: 'citric_acid', percentage: 0.12 });
  ingredients.push({ id: 'lactic_acid', percentage: 0.08 });

  // Water
  const total = ingredients.reduce((sum, i) => sum + i.percentage, 0);
  ingredients.push({ id: 'water', percentage: Math.max(0, 100 - total) });

  return buildPrediction('Variant B: Coconut Milk Tea 椰香奶茶', ingredients, rationale, warnings, Array.from(allergens));
}

function predictVariantC(targetProtein: number, sugarFree: boolean): FormulationPrediction {
  const ingredients: { id: string; percentage: number }[] = [];
  const rationale: string[] = [];
  const warnings: string[] = [];
  const allergens: string[] = [];

  // Base
  ingredients.push({ id: 'fermented_milk', percentage: 60 });

  // Protein
  const proteinAmount = Math.min(targetProtein + 0.5, 6);
  ingredients.push({ id: 'wpi', percentage: proteinAmount });
  rationale.push(`Whey Protein Isolate: ${(proteinAmount * 0.24).toFixed(1)}g per serving`);

  // Stabilizers
  ingredients.push({ id: 'pectin', percentage: 0.12 });
  ingredients.push({ id: 'kgm', percentage: 0.15 });

  // Sweetener
  if (sugarFree) {
    ingredients.push({ id: 'erythritol', percentage: 4 });
    ingredients.push({ id: 'monk_fruit', percentage: 0.02 });
  }

  // Flavors - Tea-forward
  ingredients.push({ id: 'green_tea_flavor', percentage: 0.4 });
  rationale.push('Green Tea Flavor: Lighter, refreshing tea note');
  ingredients.push({ id: 'osmanthus_extract', percentage: 0.2 });
  rationale.push('Osmanthus Extract: Premium floral complexity');

  // L-Theanine
  ingredients.push({ id: 'l_theanine', percentage: 0.05 });
  rationale.push('L-Theanine: Calm focus, tea authenticity');

  // Vitamins & Probiotic
  ingredients.push({ id: 'vit_c', percentage: 0.033 });
  ingredients.push({ id: 'l_acidophilus', percentage: 0.01 });

  // Acidulant
  ingredients.push({ id: 'citric_acid', percentage: 0.15 });
  ingredients.push({ id: 'lactic_acid', percentage: 0.1 });

  // Water
  const total = ingredients.reduce((sum, i) => sum + i.percentage, 0);
  ingredients.push({ id: 'water', percentage: Math.max(0, 100 - total) });

  return buildPrediction('Variant C: Tea Osmanthus 茶桂', ingredients, rationale, warnings, allergens);
}

function buildPrediction(
  variantName: string,
  ingredients: { id: string; percentage: number }[],
  rationale: string[],
  warnings: string[],
  allergens: string[]
): FormulationPrediction {
  // Calculate nutrition
  let calories = 0, protein = 0, sugar = 0, fiber = 0;
  for (const ing of ingredients) {
    const def = getIngredientById(ing.id);
    if (def) {
      const factor = (ing.percentage / 100) * 2.4; // per 240mL
      calories += (def.caloriesPer100g * ing.percentage) / 100 * 2.4;
      protein += (def.proteinPer100g * ing.percentage) / 100 * 2.4;
      sugar += (def.sugarPer100g * ing.percentage) / 100 * 2.4;
      if (def.id === 'kgm') fiber += ing.percentage * 0.95 * 2.4;
    }
  }

  // Calculate costs
  let ingredientCost = 0;
  for (const ing of ingredients) {
    const def = getIngredientById(ing.id);
    if (def) {
      ingredientCost += (def.costPerKg * ing.percentage) / 100 * 0.24;
    }
  }

  const packaging = 0.08; // $0.08 for 240mL PET
  const processing = 0.06; // HTST simplified
  const totalCost = ingredientCost + packaging + processing;

  // Margins
  const suggestedMSRP = 3.00; // SGD 3.00
  const wholesale = 1.80;
  const margin = ((suggestedMSRP - totalCost) / suggestedMSRP) * 100;

  // Score
  let score = 75;
  if (margin >= 65) score += 10;
  if (protein >= 10) score += 8;
  if (allergens.length <= 1) score += 5;

  return {
    variantName,
    ingredients,
    nutritionFacts: {
      calories: Math.round(calories),
      protein: Math.round(protein * 10) / 10,
      sugar: Math.round(sugar * 10) / 10,
      fiber: Math.round(fiber * 10) / 10,
    },
    costBreakdown: {
      ingredientCost: Math.round(ingredientCost * 10000) / 10000,
      packaging: Math.round(packaging * 10000) / 10000,
      processing: Math.round(processing * 10000) / 10000,
      total: Math.round(totalCost * 10000) / 10000,
    },
    marginAnalysis: {
      suggestedMSRP,
      wholesale,
      margin: Math.round(margin),
    },
    score: Math.min(100, score),
    rationale,
    warnings,
    allergens,
  };
}

// ===== PROGRESS BAR COMPONENT =====

const ProgressBar: React.FC<{ value: number; label?: string; color?: string }> = ({ value, label, color }) => (
  <div style={{ marginBottom: '12px' }}>
    {label && (
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <span style={{ fontSize: '12px', color: colors.lightGreen }}>{label}</span>
        <span style={{ fontSize: '12px', fontWeight: 600, color: colors.white }}>{value.toFixed(0)}%</span>
      </div>
    )}
    <div style={{ height: '8px', borderRadius: '4px', background: 'rgba(255,255,255,0.1)', overflow: 'hidden' }}>
      <div
        style={{
          width: `${Math.min(100, Math.max(0, value))}%`,
          height: '100%',
          borderRadius: '4px',
          background: color || colors.mediumGreen,
          transition: 'width 0.5s ease',
        }}
      />
    </div>
  </div>
);

// ===== VARIANT CARD COMPONENT =====

const VariantCard: React.FC<{
  variant: string;
  prediction: FormulationPrediction;
  isSelected: boolean;
  onSelect: () => void;
  accentColor: string;
}> = ({ variant, prediction, isSelected, onSelect, accentColor }) => (
  <div
    style={{
      ...styles.variantBox,
      background: isSelected ? `linear-gradient(135deg, ${accentColor}22 0%, ${accentColor}11 100%)` : 'rgba(255,255,255,0.02)',
      border: isSelected ? `2px solid ${accentColor}` : '2px solid transparent',
    }}
    onClick={onSelect}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
      <span style={{ fontSize: '14px', fontWeight: 600, color: colors.white }}>{variant}</span>
      <span style={{
        ...styles.badge,
        background: getScoreColor(prediction.score),
        color: colors.white,
      }}>
        {prediction.score}%
      </span>
    </div>
    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: colors.gray }}>
      <span>Protein: {prediction.nutritionFacts.protein}g</span>
      <span>COGS: ${prediction.costBreakdown.total.toFixed(2)}</span>
      <span>Margin: {prediction.marginAnalysis.margin}%</span>
    </div>
  </div>
);

// ===== MAIN DASHBOARD =====

export const MoBaiDashboard: React.FC = () => {
  const [selectedVariant, setSelectedVariant] = useState<'A' | 'B' | 'C'>('A');
  const [targetProtein, setTargetProtein] = useState(12);
  const [sugarFree, setSugarFree] = useState(true);
  const [prediction, setPrediction] = useState<FormulationPrediction | null>(null);

  // Generate prediction
  const generatePrediction = useCallback(() => {
    let result: FormulationPrediction;
    switch (selectedVariant) {
      case 'A':
        result = predictVariantA(targetProtein, sugarFree);
        break;
      case 'B':
        result = predictVariantB(targetProtein, sugarFree);
        break;
      case 'C':
        result = predictVariantC(targetProtein, sugarFree);
        break;
    }
    setPrediction(result);
  }, [selectedVariant, targetProtein, sugarFree]);

  // Auto-generate on load and changes
  React.useEffect(() => {
    generatePrediction();
  }, [generatePrediction]);

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>MoBai 茉白</h1>
        <p style={styles.subtitle}>AI-Powered Formulation & COGS Predictor | Protein Yogurt RTD Platform</p>
        <p style={{ fontSize: '12px', color: colors.accentGold, marginTop: '4px' }}>
          Simplified Prediction: Formulation + Cost Only (No Processing Stage)
        </p>
      </div>

      {/* Variant Selector */}
      <div style={{ maxWidth: '1400px', margin: '0 auto 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <VariantCard
            variant="Variant A: Mango Jasmine"
            prediction={predictVariantA(targetProtein, sugarFree)}
            isSelected={selectedVariant === 'A'}
            onSelect={() => setSelectedVariant('A')}
            accentColor={colors.mediumGreen}
          />
          <VariantCard
            variant="Variant B: Coconut Milk Tea"
            prediction={predictVariantB(targetProtein, sugarFree)}
            isSelected={selectedVariant === 'B'}
            onSelect={() => setSelectedVariant('B')}
            accentColor={colors.accentGold}
          />
          <VariantCard
            variant="Variant C: Tea Osmanthus"
            prediction={predictVariantC(targetProtein, sugarFree)}
            isSelected={selectedVariant === 'C'}
            onSelect={() => setSelectedVariant('C')}
            accentColor={colors.orange}
          />
        </div>
      </div>

      <div style={styles.grid}>
        {/* Left: Controls */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>Target Parameters</h3>
          </div>

          {/* Protein Target */}
          <div style={styles.inputGroup}>
            <label style={styles.label}>Target Protein: {targetProtein}g per serving</label>
            <input
              type="range"
              min="0"
              max="20"
              step="1"
              value={targetProtein}
              onChange={(e) => setTargetProtein(parseInt(e.target.value))}
              style={styles.slider}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: colors.gray }}>
              <span>0g</span>
              <span>20g</span>
            </div>
          </div>

          {/* Sugar Free Toggle */}
          <div style={styles.inputGroup}>
            <label style={styles.label}>Sweetener Option</label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={sugarFree}
                onChange={(e) => setSugarFree(e.target.checked)}
                style={{ accentColor: colors.accentGold, width: '16px', height: '16px' }}
              />
              <span style={{ fontSize: '14px', color: colors.white }}>Sugar-Free (Erythritol + Monk Fruit)</span>
            </label>
          </div>

          {/* Health Claims */}
          <div style={styles.inputGroup}>
            <label style={styles.label}>Health Claims Stack</label>
            <div style={{ fontSize: '12px', color: colors.gray, lineHeight: 1.6 }}>
              <div>• Source of Protein: ≥3g/100ml</div>
              <div>• Vitamin C: ≥7.5mg/100ml (80mg/serve)</div>
              <div>• Vitamin D: ≥0.75ug/100ml (5ug/serve)</div>
              <div>• Live Probiotics: ≥10⁶ CFU/ml</div>
              <div>• Dietary Fiber (KGM): ≥1.5g/100ml</div>
            </div>
          </div>

          {/* Processing Note */}
          <div style={{
            padding: '12px',
            background: `${colors.darkGreen}44`,
            borderRadius: '8px',
            marginTop: '16px',
          }}>
            <div style={{ fontSize: '12px', color: colors.accentGold, fontWeight: 600, marginBottom: '4px' }}>
              Processing: HTST Pasteurization
            </div>
            <div style={{ fontSize: '11px', color: colors.gray }}>
              72°C/15s → Rapid cooling to 4-10°C<br/>
              Probiotic viability: Post-heating addition<br/>
              Shelf life: 28 days (chilled)
            </div>
          </div>

          <button style={styles.button} onClick={generatePrediction}>
            Generate Formulation
          </button>
        </div>

        {/* Right: Results */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <h3 style={styles.cardTitle}>
              {prediction?.variantName || 'Predicted Formulation'}
            </h3>
            {prediction && (
              <span style={{
                ...styles.badge,
                background: getScoreColor(prediction.score),
                color: colors.white,
              }}>
                Score: {prediction.score}%
              </span>
            )}
          </div>

          {prediction && (
            <>
              {/* Nutrition Facts */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: colors.lightGreen }}>Nutrition Facts (per 240mL)</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: colors.white }}>{prediction.nutritionFacts.calories}</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Calories</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: `${colors.mediumGreen}22`, borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: colors.mediumGreen }}>{prediction.nutritionFacts.protein}g</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Protein</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: colors.white }}>{prediction.nutritionFacts.sugar}g</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Sugar</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: colors.white }}>{prediction.nutritionFacts.fiber}g</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Fiber</div>
                  </div>
                </div>
              </div>

              {/* Allergens */}
              {prediction.allergens.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '12px', color: colors.gray, marginBottom: '6px' }}>Allergens</h4>
                  {prediction.allergens.map((a, i) => (
                    <span key={i} style={{ ...styles.tag, background: `${colors.red}33`, color: colors.red }}>
                      {a}
                    </span>
                  ))}
                </div>
              )}

              {/* Ingredients Table */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: colors.lightGreen }}>Formulation</h4>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Ingredient</th>
                      <th style={{ ...styles.th, textAlign: 'right' }}>%</th>
                      <th style={{ ...styles.th, textAlign: 'right' }}>Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prediction.ingredients
                      .filter(i => i.id !== 'water')
                      .sort((a, b) => b.percentage - a.percentage)
                      .map((ing, i) => {
                      const def = getIngredientById(ing.id);
                      const cost = def ? (def.costPerKg * ing.percentage) / 100 * 0.24 : 0;
                      return (
                        <tr key={i}>
                          <td style={styles.td}>
                            <span style={{ color: colors.white }}>{def?.name || ing.id}</span>
                            {def?.notes && (
                              <span style={{ display: 'block', fontSize: '10px', color: colors.gray }}>{def.notes}</span>
                            )}
                          </td>
                          <td style={{ ...styles.td, textAlign: 'right', fontWeight: 500 }}>
                            {ing.percentage.toFixed(2)}%
                          </td>
                          <td style={{ ...styles.td, textAlign: 'right', color: colors.gray }}>
                            {formatCurrency(cost)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Cost Breakdown */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', color: colors.lightGreen }}>Cost Breakdown (per 240mL bottle)</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: colors.gray }}>Ingredients</span>
                    <span style={{ fontSize: '13px', fontWeight: 500, color: colors.white }}>{formatCurrency(prediction.costBreakdown.ingredientCost)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: colors.gray }}>Packaging (PET)</span>
                    <span style={{ fontSize: '13px', fontWeight: 500, color: colors.white }}>{formatCurrency(prediction.costBreakdown.packaging)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '13px', color: colors.gray }}>Processing (HTST)</span>
                    <span style={{ fontSize: '13px', fontWeight: 500, color: colors.white }}>{formatCurrency(prediction.costBreakdown.processing)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <span style={{ fontSize: '14px', fontWeight: 600, color: colors.white }}>Total COGS</span>
                    <span style={{ fontSize: '14px', fontWeight: 700, color: colors.accentGold }}>${prediction.costBreakdown.total.toFixed(3)}</span>
                  </div>
                </div>
              </div>

              {/* Margin Analysis */}
              <div style={{
                background: `linear-gradient(135deg, ${colors.darkGreen}44 0%, ${colors.mediumGreen}22 100%)`,
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '16px',
              }}>
                <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '12px', color: colors.lightGreen }}>Margin Analysis</h4>
                <ProgressBar value={prediction.marginAnalysis.margin} label="Gross Margin" color={colors.mediumGreen} />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: colors.white }}>${prediction.marginAnalysis.suggestedMSRP.toFixed(2)}</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Suggested Retail (SGD)</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: colors.accentGold }}>${prediction.marginAnalysis.wholesale.toFixed(2)}</div>
                    <div style={{ fontSize: '10px', color: colors.gray }}>Wholesale (SGD)</div>
                  </div>
                </div>
              </div>

              {/* AI Rationale */}
              {prediction.rationale.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <h4 style={{ fontSize: '12px', fontWeight: 600, color: colors.mediumGreen, marginBottom: '8px' }}>AI Rationale</h4>
                  {prediction.rationale.map((r, i) => (
                    <p key={i} style={{ fontSize: '11px', color: colors.lightGreen, marginBottom: '4px', lineHeight: 1.5 }}>
                      • {r}
                    </p>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Ingredient Reference */}
      <div style={{ ...styles.card, marginTop: '24px', maxWidth: '1400px', margin: '24px auto 0' }}>
        <h3 style={styles.cardTitle}>MoBai Ingredient Reference ({MOBai_INGREDIENTS.length} ingredients)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px', marginTop: '16px' }}>
          {MOBai_INGREDIENTS.map((ing) => (
            <div key={ing.id} style={{
              padding: '12px',
              background: 'rgba(255,255,255,0.02)',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.05)',
            }}>
              <div style={{ fontSize: '13px', fontWeight: 600, marginBottom: '2px', color: colors.white }}>{ing.name}</div>
              {ing.nameChinese && <div style={{ fontSize: '11px', color: colors.gray, marginBottom: '4px' }}>{ing.nameChinese}</div>}
              <div style={{ fontSize: '11px', color: colors.accentGold }}>${ing.costPerKg.toFixed(2)}/kg</div>
              {ing.allergens.length > 0 && (
                <span style={{ ...styles.tag, background: `${colors.red}22`, color: colors.red }}>
                  {ing.allergens[0]}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        marginTop: '40px',
        paddingTop: '20px',
        borderTop: '1px solid rgba(255,255,255,0.05)',
        color: colors.gray,
        fontSize: '12px',
      }}>
        MoBai Formulation & COGS Predictor v2.0 | Simplified: Formulation + Cost Only | No Processing Stage
      </div>
    </div>
  );
};

export default MoBaiDashboard;
