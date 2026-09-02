-- Run with:  lake env lean CheckAxioms.lean
-- Prints the axioms each theorem depends on.  Expected: only Lean/Mathlib's
-- standard `propext`, `Classical.choice`, `Quot.sound` — never `sorryAx`.
import Delphi.Condor

open Delphi.Condor

#print axioms loss_nonneg
#print axioms loss_le_one
#print axioms loss_mem_Icc
#print axioms loss_antitone
#print axioms loss_eq_zero_of_le
#print axioms loss_eq_one_of_ge
#print axioms payoff_eq
#print axioms payoffOfLoss_affine
#print axioms payoffOfLoss_antitone
#print axioms payoff_monotone
#print axioms avg_payoff_ge
#print axioms avg_condor_payoff_ge
#print axioms sum_eq_sum_card_filter
