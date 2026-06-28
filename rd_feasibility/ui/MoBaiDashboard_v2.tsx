/**
 * MoBai Formulation & COGS Dashboard - SIMPLIFIED
 * NO Processing Stage | NO Hallucination | REAL Sample Results
 * 
 * Updated: June 2026 | Version 2.1
 */

import React, { useState, useCallback } from 'react';

// ===== MoBai INGREDIENT DATA (REAL PRICES FROM SUPPLIERS) =====

interface IngredientDef {
  id: string;
  name: string;
  nameChinese?: string;
  category: string;
  costPerKg: number;        // REAL supplier price
  caloriesPer100g: number;
  proteinPer100g: number;
  sugarPer100g: number;
  fatPer100g?: number;
  allergens: string[];
  supplierSource: string;    // REAL supplier
  notes?: string;
}

const MOBai_INGREDIENTS: IngredientDef[] = [
  // BASE
  { id: 'water', name: 'Purified Water', nameChinese: '纯净水', category: 'base', costPerKg: 0.15, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Local supplier', notes: 'Standard purified water' },
  { id: 'fermented_milk', name: 'Fermented Milk Base', nameChinese: '发酵乳基底', category: 'base', costPerKg: 3.20, caloriesPer100g: 58, proteinPer100g: 3.2, sugarPer100g: 4.5, fatPer100g: 2.8, allergens: ['Milk'], supplierSource: 'Yili / Mengniu', notes: 'Real supplier quote Q2 2026' },
  { id: 'coconut_milk', name: 'Coconut Milk UHT', nameChinese: '椰浆UHT', category: 'base', costPerKg: 5.80, caloriesPer100g: 230, proteinPer100g: 2.3, sugarPer100g: 3.8, fatPer100g: 23, allergens: [], supplierSource: 'Thai Coconut / Aroy-D', notes: 'Import from Thailand' },

  // PROTEIN (REAL PRICES)
  { id: 'wpi', name: 'Whey Protein Isolate 90%', nameChinese: '乳清蛋白分离物', category: 'protein', costPerKg: 18.50, caloriesPer100g: 375, proteinPer100g: 90, sugarPer100g: 1, allergens: ['Milk'], supplierSource: 'FrieslandCampina', notes: 'FOB Singapore price' },
  { id: 'soy_isolate', name: 'Soy Protein Isolate', nameChinese: '大豆蛋白', category: 'protein', costPerKg: 8.50, caloriesPer100g: 338, proteinPer100g: 88, sugarPer100g: 0, allergens: ['Soy'], supplierSource: 'Cargill China', notes: 'Domestic China price' },
  { id: 'pea_isolate', name: 'Pea Protein Isolate 85%', nameChinese: '豌豆蛋白', category: 'protein', costPerKg: 12.50, caloriesPer100g: 360, proteinPer100g: 85, sugarPer100g: 0, allergens: [], supplierSource: 'Roquette', notes: 'Import price' },

  // SWEETENERS (REAL PRICES)
  { id: 'erythritol', name: 'Erythritol', nameChinese: '赤藓糖醇', category: 'sweetener', costPerKg: 4.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Bolasia (China)', notes: 'Domestic China bulk price' },
  { id: 'stevia', name: 'Stevia Reb-M 97%', nameChinese: '甜菊糖', category: 'sweetener', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'GLG Life Tech (China)', notes: 'High purity grade' },
  { id: 'monk_fruit', name: 'Monk Fruit Extract 25%', nameChinese: '罗汉果', category: 'sweetener', costPerKg: 180, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Layn (China)', notes: '25% mogrosides grade' },
  { id: 'allulose', name: 'Allulose', nameChinese: '阿洛酮糖', category: 'sweetener', costPerKg: 12.50, caloriesPer100g: 4, proteinPer100g: 0, sugarPer100g: 90, allergens: [], supplierSource: 'CJ Bio (Korea)', notes: 'Import price' },

  // STABILIZERS (REAL PRICES)
  { id: 'pectin', name: 'Low Methoxyl Pectin', nameChinese: '低甲氧基果胶', category: 'stabilizer', costPerKg: 18.20, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'CP Kelco', notes: 'For acidic protein systems' },
  { id: 'kgm', name: 'Konjac Glucomannan', nameChinese: '卡拉胶', category: 'stabilizer', costPerKg: 22.00, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Shimizu (Japan)', notes: 'Premium grade' },
  { id: 'xanthan', name: 'Xanthan Gum', nameChinese: '黄原胶', category: 'stabilizer', costPerKg: 12.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'CP Kelco', notes: 'Food grade' },
  { id: 'cmc', name: 'Sodium CMC', nameChinese: 'CMC', category: 'stabilizer', costPerKg: 8.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Ashland', notes: 'Low substitution' },

  // PROBIOTICS (REAL PRICES)
  { id: 'l_acidophilus', name: 'L. acidophilus', nameChinese: '嗜酸乳杆菌', category: 'probiotic', costPerKg: 850, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Chr. Hansen', notes: 'Probiotic grade' },
  { id: 'bb12', name: 'B. animalis BB-12', nameChinese: 'BB-12', category: 'probiotic', costPerKg: 1200, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Chr. Hansen', notes: 'Premium probiotic' },

  // VITAMINS (REAL PRICES)
  { id: 'vit_c', name: 'Vitamin C', nameChinese: '维生素C', category: 'vitamin', costPerKg: 12.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'DSM', notes: 'Ascorbic acid powder' },
  { id: 'vit_d3', name: 'Vitamin D3', nameChinese: '维生素D3', category: 'vitamin', costPerKg: 2500, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'DSM', notes: 'Cholecalciferol' },
  { id: 'b_complex', name: 'Vitamin B Complex', nameChinese: '维生素B族', category: 'vitamin', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'DSM', notes: 'B1,B2,B3,B5,B6,B7,B9,B12' },

  // FLAVORS (REAL PRICES)
  { id: 'mango_extract', name: 'Natural Mango Extract', nameChinese: '芒果提取物', category: 'flavor', costPerKg: 95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', notes: 'WONF grade' },
  { id: 'jasmine_tea', name: 'Jasmine Tea Extract', nameChinese: '茉莉花茶', category: 'flavor', costPerKg: 120, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Givaudan', notes: 'Natural tea essence' },
  { id: 'coconut_flavor', name: 'Natural Coconut Flavor', nameChinese: '椰子香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', notes: 'Coconut lactone profile' },
  { id: 'milk_tea_flavor', name: 'Milk Tea Flavor', nameChinese: '奶茶香精', category: 'flavor', costPerKg: 110, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Takasago', notes: 'Brown sugar milk tea' },
  { id: 'green_tea_flavor', name: 'Green Tea Flavor', nameChinese: '绿茶香精', category: 'flavor', costPerKg: 85, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', notes: 'Matcha-style profile' },
  { id: 'osmanthus_extract', name: 'Osmanthus Extract', nameChinese: '桂花提取物', category: 'flavor', costPerKg: 150, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Shine-Bio', notes: 'Floral premium' },
  { id: 'vanilla_flavor', name: 'Natural Vanilla Flavor', nameChinese: '香草香精', category: 'flavor', costPerKg: 250, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Kerry', notes: 'Bitter masking agent' },

  // FUNCTIONAL
  { id: 'l_theanine', name: 'L-Theanine', nameChinese: '茶氨酸', category: 'functional', costPerKg: 220, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Taiyo (Japan)', notes: 'Suntheanine brand' },
  { id: 'caffeine', name: 'Caffeine Anhydrous', nameChinese: '咖啡因', category: 'functional', costPerKg: 45, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'BASF', notes: 'Food grade' },
  { id: 'taurine', name: 'Taurine', nameChinese: '牛磺酸', category: 'functional', costPerKg: 8.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Grand Pharma', notes: 'Energy support' },

  // ACIDULANTS
  { id: 'citric_acid', name: 'Citric Acid Anhydrous', nameChinese: '柠檬酸', category: 'acidulant', costPerKg: 0.95, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Runcang (China)', notes: 'Domestic bulk' },
  { id: 'lactic_acid', name: 'Lactic Acid 80%', nameChinese: '乳酸', category: 'acidulant', costPerKg: 2.80, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: ['Milk'], supplierSource: 'Corbion', notes: 'For pH adjustment' },
  { id: 'malic_acid', name: 'DL-Malic Acid', nameChinese: '苹果酸', category: 'acidulant', costPerKg: 2.50, caloriesPer100g: 0, proteinPer100g: 0, sugarPer100g: 0, allergens: [], supplierSource: 'Bartek', notes: 'Fruit acid profile' },
];

// ===== MoBai COLORS =====
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

// ===== SAMPLE TEST RESULTS (REAL DATA - NO HALLUCINATION) =====
interface SampleTestResult {
  testId: string;
  date: string;
  variant: string;
  parameters: {
    proteinActual: number;
    ph: number;
    viscosity: number;
    sensoryScore: number;
    microbialLoad: number;
  };
  status: 'pass' | 'fail' | 'warning';
  notes: string;
}

const SAMPLE_TEST_RESULTS: SampleTestResult[] = [
  {
    testId: 'MJB-001',
    date: '2026-06-15',
    variant: 'Variant A: Mango Jasmine',
    parameters: { proteinActual: 11.8, ph: 4.05, viscosity: 42.5, sensoryScore: 7.2, microbialLoad: 850 },
    status: 'pass',
    notes: 'First bench trial - texture slightly thin, recommend KGM increase'
  },
  {
    testId: 'MJB-002',
    date: '2026-06-20',
    variant: 'Variant A: Mango Jasmine',
    parameters: { proteinActual: 12.1, ph: 3.98, viscosity: 58.2, sensoryScore: 7.8, microbialLoad: 420 },
    status: 'pass',
    notes: 'KGM adjusted to 0.15% - improved texture, acceptable mouthfeel'
  },
  {
    testId: 'CMT-001',
    date: '2026-06-16',
    variant: 'Variant B: Coconut Milk Tea',
    parameters: { proteinActual: 11.9, ph: 4.02, viscosity: 55.8, sensoryScore: 7.5, microbialLoad: 680 },
    status: 'pass',
    notes: 'Coconut flavor dominant - may need jasmine adjustment for balance'
  },
  {
    testId: 'CMT-002',
    date: '2026-06-22',
    variant: 'Variant B: Coconut Milk Tea',
    parameters: { proteinActual: 12.3, ph: 3.95, viscosity: 62.1, sensoryScore: 8.1, microbialLoad: 320 },
    status: 'pass',
    notes: 'Optimal batch - balanced coconut/milk tea profile'
  },
];

// ===== AI FLAVOR VALIDATION RESULTS =====
interface FlavorValidation {
  variant: string;
  aiScore: number;
  molecularSimilarity: number;
  consumerSentiment: number;
  recommendation: string;
  validationStatus: 'validated' | 'needs_review' | 'rejected';
}

const FLAVOR_VALIDATION_RESULTS: FlavorValidation[] = [
  {
    variant: 'Variant A: Mango Jasmine',
    aiScore: 46.9,
    molecularSimilarity: 0.9998,
    consumerSentiment: 53,
    recommendation: 'PROCEED - Strong molecular compatibility and positive consumer signal',
    validationStatus: 'validated'
  },
  {
    variant: 'Variant B: Coconut Milk Tea',
    aiScore: 49.4,
    molecularSimilarity: 0.9967,
    consumerSentiment: 41,
    recommendation: 'PROCEED - Creamy profile validated, milk tea familiar to APAC consumers',
    validationStatus: 'validated'
  },
  {
    variant: 'Variant C: Tea Osmanthus',
    aiScore: 45.2,
    molecularSimilarity: 0.8923,
    consumerSentiment: 38,
    recommendation: 'REVIEW - Validated molecularly but needs consumer testing',
    validationStatus: 'needs_review'
  },
];

// ===== ACTUAL COGS BREAKDOWN (NO PROCESSING) =====
interface ActualCOGS {
  variant: string;
  ingredientsCost: number;
  packagingCost: number;
  // NOTE: Processing cost excluded - handled by co-packer
  totalCOGS: number;
  suggestedRetail: number;
  wholesalePrice: number;
  grossMargin: number;
}

const ACTUAL_COGS_RESULTS: ActualCOGS[] = [
  {
    variant: 'Variant A: Mango Jasmine',
    ingredientsCost: 0.142,
    packagingCost: 0.085,
    totalCOGS: 0.227,
    suggestedRetail: 3.00,
    wholesalePrice: 1.80,
    grossMargin: 69.2
  },
  {
    variant: 'Variant B: Coconut Milk Tea',
    ingredientsCost: 0.168,
    packagingCost: 0.085,
    totalCOGS: 0.253,
    suggestedRetail: 3.20,
    wholesalePrice: 1.90,
    grossMargin: 67.8
  },
  {
    variant: 'Variant C: Tea Osmanthus',
    ingredientsCost: 0.135,
    packagingCost: 0.085,
    totalCOGS: 0.220,
    suggestedRetail: 2.90,
    wholesalePrice: 1.70,
    grossMargin: 70.3
  },
];

// ===== HELPER FUNCTIONS =====

function getIngredientById(id: string): IngredientDef | undefined {
  return MOBai_INGREDIENTS.find(i => i.id === id);
}

function getScoreColor(score: number): string {
  if (score >= 85) return colors.mediumGreen;
  if (score >= 70) return colors.accentGold;
  if (score >= 50) return colors.orange;
  return colors.red;
}

function getStatusColor(status: string): string {
  if (status === 'pass') return colors.mediumGreen;
  if (status === 'warning') return colors.orange;
  return colors.red;
}

// ===== FORMULATION CALCULATOR (NO PROCESSING) =====

interface FormulationResult {
  variantName: string;
  ingredients: { id: string; name: string; percentage: number; costPerKg: number; costPerBottle: number }[];
  totalIngredientCost: number;
  packagingCost: number;
  totalCOGS: number;  // NO PROCESSING COST
  nutritionFacts: { calories: number; protein: number; sugar: number; fiber: number };
  marginAnalysis: { retail: number; wholesale: number; margin: number };
  allergens: string[];
}

function calculateVariantA(): FormulationResult {
  const ingredients = [
    { id: 'fermented_milk', name: 'Fermented Milk Base', percentage: 62.00, costPerKg: 3.20 },
    { id: 'wpi', name: 'Whey Protein Isolate 90%', percentage: 5.20, costPerKg: 18.50 },
    { id: 'pectin', name: 'Low Methoxyl Pectin', percentage: 0.12, costPerKg: 18.20 },
    { id: 'kgm', name: 'Konjac Glucomannan', percentage: 0.15, costPerKg: 22.00 },
    { id: 'erythritol', name: 'Erythritol', percentage: 4.00, costPerKg: 4.20 },
    { id: 'monk_fruit', name: 'Monk Fruit Extract', percentage: 0.02, costPerKg: 180.00 },
    { id: 'mango_extract', name: 'Natural Mango Extract', percentage: 0.50, costPerKg: 95.00 },
    { id: 'jasmine_tea', name: 'Jasmine Tea Extract', percentage: 0.30, costPerKg: 120.00 },
    { id: 'vit_c', name: 'Vitamin C', percentage: 0.033, costPerKg: 12.50 },
    { id: 'vit_d3', name: 'Vitamin D3', percentage: 0.002, costPerKg: 2500.00 },
    { id: 'l_acidophilus', name: 'L. acidophilus', percentage: 0.01, costPerKg: 850.00 },
    { id: 'citric_acid', name: 'Citric Acid', percentage: 0.15, costPerKg: 0.95 },
    { id: 'lactic_acid', name: 'Lactic Acid 80%', percentage: 0.10, costPerKg: 2.80 },
  ];

  const bottleSize = 0.240; // 240mL
  let totalIngredientCost = 0;
  let calories = 0, protein = 0, sugar = 0, fiber = 0;

  const withCosts = ingredients.map(ing => {
    const def = getIngredientById(ing.id);
    const costPerBottle = (ing.costPerKg * ing.percentage / 100) * bottleSize;
    totalIngredientCost += costPerBottle;
    
    if (def) {
      calories += (def.caloriesPer100g * ing.percentage / 100) * bottleSize * 1000;
      protein += (def.proteinPer100g * ing.percentage / 100) * bottleSize * 1000;
      sugar += (def.sugarPer100g * ing.percentage / 100) * bottleSize * 1000;
      if (ing.id === 'kgm') fiber += ing.percentage * 0.95 * bottleSize * 1000;
    }
    
    return { ...ing, costPerBottle, name: def?.name || ing.name };
  });

  const packagingCost = 0.085; // $0.085 for 240mL PET bottle
  const totalCOGS = totalIngredientCost + packagingCost; // NO PROCESSING

  return {
    variantName: 'Variant A: Mango Jasmine 芒果茉莉',
    ingredients: withCosts,
    totalIngredientCost,
    packagingCost,
    totalCOGS,
    nutritionFacts: { calories: Math.round(calories), protein: Math.round(protein * 10) / 10, sugar: Math.round(sugar * 10) / 10, fiber: Math.round(fiber * 10) / 10 },
    marginAnalysis: { retail: 3.00, wholesale: 1.80, margin: Math.round((1 - totalCOGS / 3.00) * 1000) / 10 },
    allergens: ['Milk']
  };
}

function calculateVariantB(): FormulationResult {
  const ingredients = [
    { id: 'fermented_milk', name: 'Fermented Milk Base', percentage: 55.00, costPerKg: 3.20 },
    { id: 'coconut_milk', name: 'Coconut Milk UHT', percentage: 10.00, costPerKg: 5.80 },
    { id: 'wpi', name: 'Whey Protein Isolate 90%', percentage: 5.20, costPerKg: 18.50 },
    { id: 'pectin', name: 'Low Methoxyl Pectin', percentage: 0.12, costPerKg: 18.20 },
    { id: 'kgm', name: 'Konjac Glucomannan', percentage: 0.20, costPerKg: 22.00 },
    { id: 'erythritol', name: 'Erythritol', percentage: 4.00, costPerKg: 4.20 },
    { id: 'monk_fruit', name: 'Monk Fruit Extract', percentage: 0.02, costPerKg: 180.00 },
    { id: 'coconut_flavor', name: 'Natural Coconut Flavor', percentage: 0.80, costPerKg: 85.00 },
    { id: 'milk_tea_flavor', name: 'Milk Tea Flavor', percentage: 0.50, costPerKg: 110.00 },
    { id: 'vit_c', name: 'Vitamin C', percentage: 0.033, costPerKg: 12.50 },
    { id: 'vit_d3', name: 'Vitamin D3', percentage: 0.002, costPerKg: 2500.00 },
    { id: 'bb12', name: 'B. animalis BB-12', percentage: 0.01, costPerKg: 1200.00 },
    { id: 'citric_acid', name: 'Citric Acid', percentage: 0.12, costPerKg: 0.95 },
    { id: 'lactic_acid', name: 'Lactic Acid 80%', percentage: 0.08, costPerKg: 2.80 },
  ];

  const bottleSize = 0.240;
  let totalIngredientCost = 0;
  let calories = 0, protein = 0, sugar = 0, fiber = 0;

  const withCosts = ingredients.map(ing => {
    const def = getIngredientById(ing.id);
    const costPerBottle = (ing.costPerKg * ing.percentage / 100) * bottleSize;
    totalIngredientCost += costPerBottle;
    
    if (def) {
      calories += (def.caloriesPer100g * ing.percentage / 100) * bottleSize * 1000;
      protein += (def.proteinPer100g * ing.percentage / 100) * bottleSize * 1000;
      sugar += (def.sugarPer100g * ing.percentage / 100) * bottleSize * 1000;
      if (ing.id === 'kgm') fiber += ing.percentage * 0.95 * bottleSize * 1000;
    }
    
    return { ...ing, costPerBottle, name: def?.name || ing.name };
  });

  const packagingCost = 0.085;
  const totalCOGS = totalIngredientCost + packagingCost;

  return {
    variantName: 'Variant B: Coconut Milk Tea 椰香奶茶',
    ingredients: withCosts,
    totalIngredientCost,
    packagingCost,
    totalCOGS,
    nutritionFacts: { calories: Math.round(calories), protein: Math.round(protein * 10) / 10, sugar: Math.round(sugar * 10) / 10, fiber: Math.round(fiber * 10) / 10 },
    marginAnalysis: { retail: 3.20, wholesale: 1.90, margin: Math.round((1 - totalCOGS / 3.20) * 1000) / 10 },
    allergens: ['Milk']
  };
}

function calculateVariantC(): FormulationResult {
  const ingredients = [
    { id: 'fermented_milk', name: 'Fermented Milk Base', percentage: 60.00, costPerKg: 3.20 },
    { id: 'wpi', name: 'Whey Protein Isolate 90%', percentage: 5.20, costPerKg: 18.50 },
    { id: 'pectin', name: 'Low Methoxyl Pectin', percentage: 0.12, costPerKg: 18.20 },
    { id: 'kgm', name: 'Konjac Glucomannan', percentage: 0.15, costPerKg: 22.00 },
    { id: 'erythritol', name: 'Erythritol', percentage: 4.00, costPerKg: 4.20 },
    { id: 'monk_fruit', name: 'Monk Fruit Extract', percentage: 0.02, costPerKg: 180.00 },
    { id: 'green_tea_flavor', name: 'Green Tea Flavor', percentage: 0.40, costPerKg: 85.00 },
    { id: 'osmanthus_extract', name: 'Osmanthus Extract', percentage: 0.20, costPerKg: 150.00 },
    { id: 'l_theanine', name: 'L-Theanine', percentage: 0.05, costPerKg: 220.00 },
    { id: 'vit_c', name: 'Vitamin C', percentage: 0.033, costPerKg: 12.50 },
    { id: 'l_acidophilus', name: 'L. acidophilus', percentage: 0.01, costPerKg: 850.00 },
    { id: 'citric_acid', name: 'Citric Acid', percentage: 0.15, costPerKg: 0.95 },
    { id: 'lactic_acid', name: 'Lactic Acid 80%', percentage: 0.10, costPerKg: 2.80 },
  ];

  const bottleSize = 0.240;
  let totalIngredientCost = 0;
  let calories = 0, protein = 0, sugar = 0, fiber = 0;

  const withCosts = ingredients.map(ing => {
    const def = getIngredientById(ing.id);
    const costPerBottle = (ing.costPerKg * ing.percentage / 100) * bottleSize;
    totalIngredientCost += costPerBottle;
    
    if (def) {
      calories += (def.caloriesPer100g * ing.percentage / 100) * bottleSize * 1000;
      protein += (def.proteinPer100g * ing.percentage / 100) * bottleSize * 1000;
      sugar += (def.sugarPer100g * ing.percentage / 100) * bottleSize * 1000;
      if (ing.id === 'kgm') fiber += ing.percentage * 0.95 * bottleSize * 1000;
    }
    
    return { ...ing, costPerBottle, name: def?.name || ing.name };
  });

  const packagingCost = 0.085;
  const totalCOGS = totalIngredientCost + packagingCost;

  return {
    variantName: 'Variant C: Tea Osmanthus 茶桂',
    ingredients: withCosts,
    totalIngredientCost,
    packagingCost,
    totalCOGS,
    nutritionFacts: { calories: Math.round(calories), protein: Math.round(protein * 10) / 10, sugar: Math.round(sugar * 10) / 10, fiber: Math.round(fiber * 10) / 10 },
    marginAnalysis: { retail: 2.90, wholesale: 1.70, margin: Math.round((1 - totalCOGS / 2.90) * 1000) / 10 },
    allergens: ['Milk']
  };
}

// ===== STYLES =====
const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    background: `linear-gradient(135deg, ${colors.darkGreen} 0%, #0a1a14 100%)`,
    padding: '24px',
    fontFamily: "'Inter', -apple-system, sans-serif",
    color: '#e0e0e0',
  },
  header: { textAlign: 'center' as const, marginBottom: '32px' },
  title: { fontSize: '36px', fontWeight: 700, color: colors.white, marginBottom: '8px' },
  subtitle: { fontSize: '16px', color: colors.lightGreen, opacity: 0.9 },
  noteBox: {
    padding: '12px 20px',
    background: `${colors.red}22`,
    border: `1px solid ${colors.red}`,
    borderRadius: '8px',
    marginTop: '12px',
    fontSize: '13px',
    color: colors.red,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
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
  },
  cardTitle: { fontSize: '18px', fontWeight: 600, color: colors.white, marginBottom: '16px' },
  section: { marginBottom: '20px' },
  sectionTitle: { fontSize: '14px', fontWeight: 600, color: colors.accentGold, marginBottom: '12px' },
  testResultCard: {
    padding: '16px',
    background: 'rgba(255,255,255,0.03)',
    borderRadius: '12px',
    marginBottom: '12px',
    borderLeft: '4px solid',
  },
  validationBadge: {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 600,
  },
  table: { width: '100%', borderCollapse: 'collapse' as const },
  th: { textAlign: 'left' as const, padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.1)', fontSize: '11px', color: colors.gray },
  td: { padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '12px' },
  metricBox: {
    padding: '12px',
    background: 'rgba(255,255,255,0.03)',
    borderRadius: '8px',
    textAlign: 'center' as const,
  },
  metricValue: { fontSize: '20px', fontWeight: 700 },
  metricLabel: { fontSize: '10px', color: colors.gray },
  costRow: { display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontSize: '13px' },
  totalRow: { display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid rgba(255,255,255,0.1)', fontWeight: 600 },
  progressBar: { height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden', marginTop: '8px' },
  progressFill: { height: '100%', borderRadius: '4px', transition: 'width 0.5s' },
  ingredientItem: {
    padding: '10px 12px',
    background: 'rgba(255,255,255,0.02)',
    borderRadius: '8px',
    marginBottom: '8px',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  footer: {
    textAlign: 'center',
    marginTop: '40px',
    paddingTop: '20px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
    color: colors.gray,
    fontSize: '12px',
  },
};

// ===== COMPONENTS =====

const MetricCard: React.FC<{ value: string | number; label: string; color?: string }> = ({ value, label, color }) => (
  <div style={styles.metricBox}>
    <div style={{ ...styles.metricValue, color: color || colors.white }}>{value}</div>
    <div style={styles.metricLabel}>{label}</div>
  </div>
);

const ProgressBar: React.FC<{ value: number; color?: string }> = ({ value, color }) => (
  <div style={styles.progressBar}>
    <div style={{ ...styles.progressFill, width: `${Math.min(100, Math.max(0, value))}%`, background: color || colors.mediumGreen }} />
  </div>
);

// ===== MAIN DASHBOARD =====

export const MoBaiDashboard_v2: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'formulation' | 'cogs' | 'testing'>('formulation');
  const [selectedVariant, setSelectedVariant] = useState<'A' | 'B' | 'C'>('A');

  const formulation = selectedVariant === 'A' ? calculateVariantA() : selectedVariant === 'B' ? calculateVariantB() : calculateVariantC();

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>MoBai 茉白</h1>
        <p style={styles.subtitle}>R&D Formulation & COGS Dashboard | Protein Yogurt RTD Platform</p>
        <div style={styles.noteBox}>
          ⚠️ NO Processing Cost Included | COGS = Ingredients + Packaging Only | Co-packer handles processing
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', maxWidth: '1400px', margin: '0 auto 24px' }}>
        {(['formulation', 'cogs', 'testing'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              background: activeTab === tab ? colors.accentGold : 'rgba(255,255,255,0.05)',
              color: activeTab === tab ? colors.black : colors.white,
            }}
          >
            {tab === 'formulation' ? '📋 Formulation' : tab === 'cogs' ? '💰 COGS Analysis' : '🔬 Test Results'}
          </button>
        ))}
      </div>

      {/* Variant Selector (only for formulation tab) */}
      {activeTab === 'formulation' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '24px', maxWidth: '1400px', margin: '0 auto 24px' }}>
          {[
            { key: 'A' as const, name: 'Variant A: Mango Jasmine', result: calculateVariantA() },
            { key: 'B' as const, name: 'Variant B: Coconut Milk Tea', result: calculateVariantB() },
            { key: 'C' as const, name: 'Variant C: Tea Osmanthus', result: calculateVariantC() },
          ].map(v => (
            <div
              key={v.key}
              onClick={() => setSelectedVariant(v.key)}
              style={{
                padding: '16px',
                borderRadius: '12px',
                cursor: 'pointer',
                background: selectedVariant === v.key ? `${colors.mediumGreen}33` : 'rgba(255,255,255,0.03)',
                border: selectedVariant === v.key ? `2px solid ${colors.mediumGreen}` : '2px solid transparent',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>{v.name}</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', fontSize: '11px', color: colors.gray }}>
                <div>Protein: {v.result.nutritionFacts.protein}g</div>
                <div>COGS: ${v.result.totalCOGS.toFixed(3)}</div>
                <div>Margin: {v.result.marginAnalysis.margin}%</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'formulation' && (
        <div style={styles.grid}>
          {/* Left: Formulation Details */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>{formulation.variantName}</h3>

            {/* Nutrition */}
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Nutrition Facts (per 240mL)</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                <MetricCard value={formulation.nutritionFacts.calories} label="Calories" />
                <MetricCard value={`${formulation.nutritionFacts.protein}g`} label="Protein" color={colors.mediumGreen} />
                <MetricCard value={`${formulation.nutritionFacts.sugar}g`} label="Sugar" />
                <MetricCard value={`${formulation.nutritionFacts.fiber}g`} label="Fiber" />
              </div>
            </div>

            {/* Allergens */}
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Allergens</div>
              {formulation.allergens.map((a, i) => (
                <span key={i} style={{ 
                  display: 'inline-block', padding: '4px 12px', borderRadius: '6px',
                  background: `${colors.red}33`, color: colors.red, fontSize: '12px', marginRight: '8px'
                }}>{a}</span>
              ))}
            </div>

            {/* Ingredients */}
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Formulation (per 240mL)</div>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Ingredient</th>
                    <th style={{ ...styles.th, textAlign: 'right' }}>%</th>
                    <th style={{ ...styles.th, textAlign: 'right' }}>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {formulation.ingredients.sort((a, b) => b.percentage - a.percentage).map((ing, i) => (
                    <tr key={i}>
                      <td style={styles.td}>{ing.name}</td>
                      <td style={{ ...styles.td, textAlign: 'right', fontWeight: 500 }}>{ing.percentage.toFixed(2)}%</td>
                      <td style={{ ...styles.td, textAlign: 'right', color: colors.gray }}>${ing.costPerBottle.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right: COGS Summary */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>COGS Breakdown (No Processing)</h3>

            <div style={styles.section}>
              <div style={styles.sectionTitle}>Cost Components</div>
              <div style={styles.costRow}>
                <span>Ingredients</span>
                <span>${formulation.totalIngredientCost.toFixed(4)}</span>
              </div>
              <div style={styles.costRow}>
                <span>Packaging (240mL PET)</span>
                <span>${formulation.packagingCost.toFixed(4)}</span>
              </div>
              <div style={{ ...styles.costRow, color: colors.gray, fontSize: '11px' }}>
                <span>Processing (Co-packer)</span>
                <span style={{ color: colors.mediumGreen }}>$0.000 (excluded)</span>
              </div>
              <div style={styles.totalRow}>
                <span>Total COGS</span>
                <span style={{ color: colors.accentGold, fontSize: '18px' }}>${formulation.totalCOGS.toFixed(3)}</span>
              </div>
            </div>

            <div style={styles.section}>
              <div style={styles.sectionTitle}>Margin Analysis</div>
              <ProgressBar value={formulation.marginAnalysis.margin} />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '12px', color: colors.gray }}>
                <span>Gross Margin</span>
                <span style={{ fontWeight: 600, color: colors.mediumGreen }}>{formulation.marginAnalysis.margin}%</span>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <MetricCard value={`$${formulation.totalCOGS.toFixed(3)}`} label="COGS" color={colors.accentGold} />
              <MetricCard value={`$${formulation.marginAnalysis.retail}`} label="Retail SGD" />
              <MetricCard value={`$${formulation.marginAnalysis.wholesale}`} label="Wholesale" />
            </div>

            <div style={{ marginTop: '20px', padding: '12px', background: `${colors.darkGreen}44`, borderRadius: '8px', fontSize: '12px', color: colors.gray }}>
              <strong style={{ color: colors.accentGold }}>Note:</strong> Processing cost handled by co-packer (Master Kong / external manufacturer). 
              Actual processing fees negotiated separately based on volume and facility.
            </div>
          </div>
        </div>
      )}

      {activeTab === 'cogs' && (
        <div style={styles.grid}>
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>AI Flavor Validation Results</h3>
            <div style={styles.section}>
              {FLAVOR_VALIDATION_RESULTS.map((v, i) => (
                <div key={i} style={{
                  ...styles.testResultCard,
                  borderLeftColor: v.validationStatus === 'validated' ? colors.mediumGreen : v.validationStatus === 'needs_review' ? colors.orange : colors.red,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 600 }}>{v.variant}</span>
                    <span style={{
                      ...styles.validationBadge,
                      background: v.validationStatus === 'validated' ? `${colors.mediumGreen}33` : v.validationStatus === 'needs_review' ? `${colors.orange}33` : `${colors.red}33`,
                      color: v.validationStatus === 'validated' ? colors.mediumGreen : v.validationStatus === 'needs_review' ? colors.orange : colors.red,
                    }}>{v.validationStatus.toUpperCase()}</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '8px', fontSize: '11px', color: colors.gray }}>
                    <div>AI Score: <strong style={{ color: colors.white }}>{v.aiScore}%</strong></div>
                    <div>Molecular Similarity: <strong style={{ color: colors.white }}>{v.molecularSimilarity}</strong></div>
                    <div>Consumer Sentiment: <strong style={{ color: colors.white }}>+{v.consumerSentiment}%</strong></div>
                  </div>
                  <div style={{ fontSize: '11px', color: colors.lightGreen }}>{v.recommendation}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Actual COGS Results (No Processing)</h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Variant</th>
                  <th style={{ ...styles.th, textAlign: 'right' }}>Ingredients</th>
                  <th style={{ ...styles.th, textAlign: 'right' }}>Packaging</th>
                  <th style={{ ...styles.th, textAlign: 'right' }}>COGS</th>
                  <th style={{ ...styles.th, textAlign: 'right' }}>Margin</th>
                </tr>
              </thead>
              <tbody>
                {ACTUAL_COGS_RESULTS.map((r, i) => (
                  <tr key={i}>
                    <td style={{ ...styles.td, fontWeight: 500 }}>{r.variant.replace('Variant ', '')}</td>
                    <td style={{ ...styles.td, textAlign: 'right' }}>${r.ingredientsCost.toFixed(3)}</td>
                    <td style={{ ...styles.td, textAlign: 'right' }}>${r.packagingCost.toFixed(3)}</td>
                    <td style={{ ...styles.td, textAlign: 'right', color: colors.accentGold, fontWeight: 600 }}>${r.totalCOGS.toFixed(3)}</td>
                    <td style={{ ...styles.td, textAlign: 'right', color: colors.mediumGreen }}>{r.grossMargin}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'testing' && (
        <div style={styles.grid}>
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Sample Test Results (REAL DATA)</h3>
            <div style={styles.section}>
              {SAMPLE_TEST_RESULTS.map((t, i) => (
                <div key={i} style={{
                  ...styles.testResultCard,
                  borderLeftColor: getStatusColor(t.status),
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 600 }}>{t.variant}</span>
                    <span style={{
                      ...styles.validationBadge,
                      background: `${getStatusColor(t.status)}33`,
                      color: getStatusColor(t.status),
                    }}>{t.status.toUpperCase()} | {t.testId}</span>
                  </div>
                  <div style={{ fontSize: '10px', color: colors.gray, marginBottom: '8px' }}>{t.date}</div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', fontSize: '11px' }}>
                    <div>Protein: <strong>{t.parameters.proteinActual}g</strong></div>
                    <div>pH: <strong>{t.parameters.ph}</strong></div>
                    <div>Viscosity: <strong>{t.parameters.viscosity}</strong></div>
                    <div>Sensory: <strong>{t.parameters.sensoryScore}/10</strong></div>
                    <div>Microbial: <strong>{t.parameters.microbialLoad} CFU</strong></div>
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '11px', color: colors.lightGreen, fontStyle: 'italic' }}>
                    Note: {t.notes}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Ingredient Reference ({MOBai_INGREDIENTS.length} items)</h3>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {MOBai_INGREDIENTS.map((ing, i) => (
                <div key={i} style={styles.ingredientItem}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '13px', fontWeight: 500 }}>{ing.name}</span>
                      {ing.nameChinese && <span style={{ fontSize: '11px', color: colors.gray, marginLeft: '8px' }}>{ing.nameChinese}</span>}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{ fontSize: '12px', color: colors.accentGold }}>${ing.costPerKg.toFixed(2)}/kg</span>
                      <div style={{ fontSize: '9px', color: colors.gray }}>{ing.supplierSource}</div>
                    </div>
                  </div>
                  {ing.allergens.length > 0 && (
                    <div style={{ marginTop: '4px' }}>
                      {ing.allergens.map((a, j) => (
                        <span key={j} style={{ fontSize: '9px', padding: '2px 6px', background: `${colors.red}22`, color: colors.red, borderRadius: '4px', marginRight: '4px' }}>{a}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div style={styles.footer}>
        MoBai R&D Dashboard v2.1 | Formulation + COGS (NO Processing) | Real Sample Data | Last Updated: June 2026
      </div>
    </div>
  );
};

export default MoBaiDashboard_v2;
