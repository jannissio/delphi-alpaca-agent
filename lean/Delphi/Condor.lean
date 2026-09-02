/-
Copyright (c) 2026 jannissio. Released under the MIT License (see ../LICENSE).
Authors: Jannis (with Claude Code)
-/
import Mathlib

/-!
# Deterministic lemmas behind the "Conformal Risk Control Condor"

This file machine-checks the *deterministic* part of the argument used by the
Delphi 0DTE SPY iron-condor agent.  Everything here is elementary real
arithmetic over finite sums.

**What is NOT formalised here.**  The probabilistic step of Conformal Risk
Control — that for exchangeable calibration/test moves `r₁, …, rₙ, r_{n+1}`
and a monotone bounded loss the conformally chosen radius `k̂` satisfies
`E[loss(r_{n+1}, k̂)] ≤ β` — is *cited*, not proved:

  Angelopoulos, Bates, Fisch, Lei, Schuster, "Conformal Risk Control",
  ICLR 2024 (Theorem 1).

The lemmas below establish exactly the hypotheses that theorem needs from the
loss (boundedness in `[0,1]` and monotonicity in the radius `k`), and the
purely arithmetic consequence that, once the *empirical* average loss on a
finite calibration set is at most `β`, a credit of at least `(β + μ)·w`
guarantees an average payoff of at least `μ·w`.
-/

namespace Delphi.Condor

open Finset

/-! ### (a) The normalised condor loss -/

/-- Normalised loss of a short iron condor with half-width (short-strike
radius) `k` and wing width `ω`, as a function of the absolute spot move `x`
(all in implied-move units): `loss x k ω = min (max (x - k) 0) ω / ω`.
It is `0` inside the short strikes, ramps linearly across the wing, and
saturates at `1` once the wing is breached.  This is the bounded, monotone
loss required by Angelopoulos et al., "Conformal Risk Control", ICLR 2024. -/
noncomputable def loss (x k ω : ℝ) : ℝ := min (max (x - k) 0) ω / ω

/-- `0 ≤ loss` for a positive wing (lower half of the `[0,1]` bound needed by
Angelopoulos et al., "Conformal Risk Control", ICLR 2024). -/
theorem loss_nonneg {ω : ℝ} (hω : 0 < ω) (x k : ℝ) : 0 ≤ loss x k ω :=
  div_nonneg (le_min (le_max_right _ _) hω.le) hω.le

/-- `loss ≤ 1` for a positive wing (upper half of the `[0,1]` bound needed by
Angelopoulos et al., "Conformal Risk Control", ICLR 2024). -/
theorem loss_le_one {ω : ℝ} (hω : 0 < ω) (x k : ℝ) : loss x k ω ≤ 1 := by
  unfold loss
  rw [div_le_iff₀ hω, one_mul]
  exact min_le_right _ _

/-- `loss x k ω ∈ [0,1]`; packages `loss_nonneg` and `loss_le_one`
(the boundedness hypothesis of Angelopoulos et al., ICLR 2024). -/
theorem loss_mem_Icc {ω : ℝ} (hω : 0 < ω) (x k : ℝ) : loss x k ω ∈ Set.Icc (0 : ℝ) 1 :=
  ⟨loss_nonneg hω x k, loss_le_one hω x k⟩

/-- The loss is antitone (non-increasing) in the radius `k`: widening the
condor can only reduce the loss.  This is the monotonicity hypothesis of
Angelopoulos et al., "Conformal Risk Control", ICLR 2024 (their losses are
required to be non-increasing in the parameter `λ`). -/
theorem loss_antitone {ω : ℝ} (hω : 0 < ω) (x : ℝ) : Antitone (fun k => loss x k ω) := by
  intro k₁ k₂ hk
  unfold loss
  apply div_le_div_of_nonneg_right _ hω.le
  apply min_le_min _ le_rfl
  apply max_le_max _ le_rfl
  linarith

/-- Zero loss inside the short strikes: `x ≤ k → loss x k ω = 0`
(used by the deterministic gates of the agent; cf. Angelopoulos et al.,
ICLR 2024, where such a loss is the natural "miscoverage" loss). -/
theorem loss_eq_zero_of_le {ω : ℝ} (hω : 0 < ω) {x k : ℝ} (h : x ≤ k) : loss x k ω = 0 := by
  unfold loss
  rw [max_eq_right (by linarith), min_eq_left hω.le, zero_div]

/-- Full loss once the wing is breached: `k + ω ≤ x → loss x k ω = 1`
(the saturation that makes the loss bounded, cf. Angelopoulos et al., ICLR 2024). -/
theorem loss_eq_one_of_ge {ω : ℝ} (hω : 0 < ω) {x k : ℝ} (h : k + ω ≤ x) : loss x k ω = 1 := by
  unfold loss
  rw [max_eq_left (by linarith), min_eq_right (by linarith), div_self hω.ne']

/-! ### (b) The payoff is affine in the loss and monotone in the radius -/

/-- Payoff of one condor with credit `c`, wing `ω`, multiplier `m`, spot move
`x` and radius `k`: `payoff = c - ω · loss · m`
(the affine payoff whose expectation the conformal bound of Angelopoulos et
al., ICLR 2024, controls). -/
noncomputable def payoff (c ω m x k : ℝ) : ℝ := c - ω * loss x k ω * m

/-- Payoff as a function of the loss alone: `payoffOfLoss c w ℓ = c - w · ℓ`
with `w = ω · m` (Angelopoulos et al., ICLR 2024 bound the expectation of `ℓ`). -/
def payoffOfLoss (c w ℓ : ℝ) : ℝ := c - w * ℓ

/-- `payoff` is `payoffOfLoss` evaluated at the condor loss with `w = ω · m`
(bookkeeping identity; cf. Angelopoulos et al., ICLR 2024). -/
theorem payoff_eq (c ω m x k : ℝ) : payoff c ω m x k = payoffOfLoss c (ω * m) (loss x k ω) := by
  unfold payoff payoffOfLoss
  ring

/-- `payoffOfLoss c w` is affine: it commutes with affine combinations of the
loss.  (Affinity is what lets the expectation bound of Angelopoulos et al.,
ICLR 2024 pass through to the payoff.) -/
theorem payoffOfLoss_affine (c w t ℓ₁ ℓ₂ : ℝ) :
    payoffOfLoss c w (t * ℓ₁ + (1 - t) * ℓ₂)
      = t * payoffOfLoss c w ℓ₁ + (1 - t) * payoffOfLoss c w ℓ₂ := by
  unfold payoffOfLoss
  ring

/-- `payoffOfLoss c w` is antitone in the loss when `0 ≤ w`
(cf. Angelopoulos et al., ICLR 2024). -/
theorem payoffOfLoss_antitone {w : ℝ} (hw : 0 ≤ w) (c : ℝ) : Antitone (payoffOfLoss c w) := by
  intro ℓ₁ ℓ₂ h
  unfold payoffOfLoss
  exact sub_le_sub_left (mul_le_mul_of_nonneg_left h hw) c

/-- For fixed spot move `x`, the payoff is monotone (non-decreasing) in the
radius `k`: widening the condor never lowers the payoff for a given move.
Follows from `loss_antitone` (the monotonicity Angelopoulos et al., ICLR 2024
require of the loss). -/
theorem payoff_monotone {ω m : ℝ} (hω : 0 < ω) (hm : 0 ≤ m) (c x : ℝ) :
    Monotone (fun k => payoff c ω m x k) := by
  intro k₁ k₂ hk
  have hl : loss x k₂ ω ≤ loss x k₁ ω := loss_antitone hω x hk
  unfold payoff
  exact sub_le_sub_left (mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left hl hω.le) hm) c

/-! ### (c) The finite-sample core -/

/-- **Deterministic core.**  For a nonempty finite index set `s` (so `n = s.card`
losses), if the empirical average loss `(1/n) Σ ℓᵢ` is at most `β` and the
credit satisfies `c ≥ (β + μ) · w` with `w > 0`, then the average payoff
`(1/n) Σ (c - w · ℓᵢ)` is at least `μ · w`.

No bound on the `ℓᵢ` is needed for this arithmetic step; boundedness in
`[0,1]` (`loss_mem_Icc`) is what the *probabilistic* step of Angelopoulos et
al., "Conformal Risk Control", ICLR 2024 needs to replace the empirical
average by an expectation. -/
theorem avg_payoff_ge {ι : Type*} (s : Finset ι) (hs : s.Nonempty) (ℓ : ι → ℝ)
    {β μ w c : ℝ} (hw : 0 < w)
    (havg : (1 / (s.card : ℝ)) * ∑ i ∈ s, ℓ i ≤ β) (hc : (β + μ) * w ≤ c) :
    μ * w ≤ (1 / (s.card : ℝ)) * ∑ i ∈ s, (c - w * ℓ i) := by
  have hn : (0 : ℝ) < s.card := by exact_mod_cast hs.card_pos
  rw [one_div_mul_eq_div] at havg ⊢
  rw [Finset.sum_sub_distrib, Finset.sum_const, ← Finset.mul_sum, nsmul_eq_mul]
  rw [le_div_iff₀ hn]
  rw [div_le_iff₀ hn] at havg
  nlinarith [mul_le_mul_of_nonneg_left havg hw.le, mul_le_mul_of_nonneg_right hc hn.le]

/-- The finite-sample core specialised to condor losses: for spot moves
`x i`, radius `k`, wing `ω > 0` and multiplier `m > 0`, if the empirical
average of `loss (x i) k ω` is at most `β` and the credit is at least
`(β + μ) · ω · m`, then the average `payoff` is at least `μ · ω · m`.
(Deterministic counterpart of the guarantee in Angelopoulos et al.,
"Conformal Risk Control", ICLR 2024.) -/
theorem avg_condor_payoff_ge {ι : Type*} (s : Finset ι) (hs : s.Nonempty) (x : ι → ℝ)
    {k ω m β μ c : ℝ} (hω : 0 < ω) (hm : 0 < m)
    (havg : (1 / (s.card : ℝ)) * ∑ i ∈ s, loss (x i) k ω ≤ β)
    (hc : (β + μ) * (ω * m) ≤ c) :
    μ * (ω * m) ≤ (1 / (s.card : ℝ)) * ∑ i ∈ s, payoff c ω m (x i) k := by
  have key := avg_payoff_ge s hs (fun i => loss (x i) k ω) (mul_pos hω hm) havg hc
  calc μ * (ω * m) ≤ (1 / (s.card : ℝ)) * ∑ i ∈ s, (c - ω * m * loss (x i) k ω) := key
    _ = (1 / (s.card : ℝ)) * ∑ i ∈ s, payoff c ω m (x i) k := by
        congr 1
        exact Finset.sum_congr rfl (fun i _ => by unfold payoff; ring)

/-! ### (d) Discrete layer-cake identity -/

/-- **Discrete layer-cake identity.**  For integer-valued losses `f i ≤ N` on a
finite index set `s`, the total loss equals the sum over layers `j < N` of
the number of samples whose loss exceeds `j`:
`Σᵢ f i = Σ_{j<N} #{i ∈ s | j < f i}`.
This is the finite analogue of `E[L] = ∫₀^∞ P(L > t) dt`, which is how the
wing-ramp loss decomposes into breach indicators at nested radii
(cf. the monotone-loss setting of Angelopoulos et al., "Conformal Risk
Control", ICLR 2024). -/
theorem sum_eq_sum_card_filter {ι : Type*} (s : Finset ι) (f : ι → ℕ) {N : ℕ}
    (hf : ∀ i ∈ s, f i ≤ N) :
    ∑ i ∈ s, f i = ∑ j ∈ range N, (s.filter (fun i => j < f i)).card := by
  have h : ∀ i ∈ s, f i = ∑ j ∈ range N, if j < f i then 1 else 0 := by
    intro i hi
    have hr : (range N).filter (fun j => j < f i) = range (f i) := by
      ext j
      simp only [Finset.mem_filter, Finset.mem_range]
      have := hf i hi
      omega
    rw [Finset.sum_boole, hr, Finset.card_range, Nat.cast_id]
  rw [Finset.sum_congr rfl h, Finset.sum_comm]
  exact Finset.sum_congr rfl (fun j _ => by rw [Finset.card_filter])

end Delphi.Condor
