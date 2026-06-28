/**
 * MoBai R&D Feasibility Intelligence Layer
 * Simplified Version 2.0: Only Formulation & COGS (NO Processing Stage)
 *
 * Updated: June 2026 | Version 2.0.0
 */

export const MoBai_FEASIBILITY = {
  version: "2.0.0",
  lastUpdated: "2026-06-28",
  description: "MoBai AI-assisted Protein Yogurt RTD Platform - Simplified Formulation & Cost Analysis",
  simplified: true,
  features: [
    "Formulation Prediction (no processing stage)",
    "COGS Analysis",
    "Margin Projection",
    "AI Rationale Generation",
    "3 Pre-configured Variants (Mango Jasmine, Coconut Milk Tea, Tea Osmanthus)",
    "40+ MoBai-specific ingredients"
  ],
  variants: [
    { name: "Variant A: Mango Jasmine", score: 92, cogs: 0.28, margin: 68 },
    { name: "Variant B: Coconut Milk Tea", score: 89, cogs: 0.31, margin: 65 },
    { name: "Variant C: Tea Osmanthus", score: 85, cogs: 0.27, margin: 70 }
  ],
  removedModules: [
    "Thermal Degradation Calculator",
    "Stability Predictor",
    "Dashboard Evaluator",
    "Processing Stage Analysis"
  ]
};

// Export the MoBai dashboard component
export { MoBaiDashboard as default } from './ui/MoBaiDashboard';
