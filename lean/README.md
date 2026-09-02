# Delphi — machine-checked lemmas for the "Conformal Risk Control Condor"

Lean 4 + Mathlib formalisation of the *deterministic* part of the argument
behind the Delphi 0DTE SPY iron-condor sizing rule. Everything in
`Delphi/Condor.lean` compiles with **no `sorry`** and depends only on the three
standard Lean/Mathlib axioms (`propext`, `Classical.choice`, `Quot.sound`).

| | |
|---|---|
| Lean | `leanprover/lean4:v4.34.0-rc2` (see `lean-toolchain`) |
| Mathlib | tag `v4.34.0-rc2` (pinned in `lakefile.toml` / `lake-manifest.json`) |
| Source | `Delphi/Condor.lean` (single file, ~190 lines) |
| Axiom check | `CheckAxioms.lean` |

## What is proved

Namespace `Delphi.Condor`, all over `ℝ` with `Finset` sums.

**(a) Normalised condor loss** `loss x k ω := min (max (x - k) 0) ω / ω`
(spot move `x`, short-strike radius `k`, wing `ω > 0`, all in implied-move units):

- `loss_nonneg`, `loss_le_one`, `loss_mem_Icc` — `0 ≤ loss ≤ 1`.
- `loss_antitone` — non-increasing in the radius `k`.
- `loss_eq_zero_of_le` — `x ≤ k → loss = 0`; `loss_eq_one_of_ge` — `k + ω ≤ x → loss = 1`.

**(b) Payoff** `payoff c ω m x k := c - ω * loss x k ω * m` and `payoffOfLoss c w ℓ := c - w * ℓ`:

- `payoff_eq` — `payoff = payoffOfLoss c (ω·m) loss`.
- `payoffOfLoss_affine` — commutes with affine combinations of the loss (affinity).
- `payoffOfLoss_antitone` — non-increasing in the loss for `w ≥ 0`.
- `payoff_monotone` — non-decreasing in `k` for fixed `x` (`ω > 0`, `m ≥ 0`).

**(c) Finite-sample core** (`avg_payoff_ge`): for a nonempty `Finset` `s`
(`n = s.card`) of losses `ℓ i` with `(1/n) Σ ℓ i ≤ β`, a weight `w > 0` and a
credit `c ≥ (β + μ)·w`, the average payoff satisfies `(1/n) Σ (c - w·ℓ i) ≥ μ·w`.
`avg_condor_payoff_ge` specialises this to `ℓ i = loss (x i) k ω`, `w = ω·m`.
(No `[0,1]` bound on the losses is needed for this arithmetic step.)

**(d) Discrete layer-cake identity** (`sum_eq_sum_card_filter`): for
integer-valued `f i ≤ N`, `Σ_{i∈s} f i = Σ_{j<N} #{i ∈ s | j < f i}`.

## Prior art, stated narrowly

Option pricing and market mechanisms have been machine-checked before, and we cite them rather than claim
otherwise: Ushakov & Berdinsky (2026, arXiv:2608.19223) verify the Black–Scholes closed form with digital and
barrier options in Lean 4/Mathlib, sorry-free and on the same three axioms as this file; Coelho (2026,
arXiv:2606.01356) maintains a Lean 4 mathematical-finance library with several hundred sorry-free theorems;
Echenim, Guiol & Peltier (2018, arXiv:1807.09873) formalise markets, portfolios, arbitrage and the
Cox–Ross–Rubinstein model in Isabelle/HOL; Sarswat & Singh and successors (2019–2024) verify exchange
matching in Coq with checkers run against real exchange logs; and Imandra (Passmore & Ignatovich, FMCAD 2018)
is a commercial prover built for financial algorithms. What we did not find, in roughly ten targeted searches,
is a machine-checked risk-control lemma for a trading *decision rule* — the deterministic scaffolding by which a
rule bounds its own loss — or any formalisation of conformal prediction or exchangeability in Lean, Isabelle,
Coq, HOL, Imandra or Dafny. The surviving claim is that narrow one; "no prior formal verification of a trading
system" would be false and we do not make it. The nearest architectural peers are Koomullil's proof-carrying
certificates for LLM pipelines (2026, arXiv:2605.16407), which verify the deterministic computations around a
model rather than the model, with the same {propext, Classical.choice, Quot.sound} trust boundary, and the
"Type-Checked Compliance" line (arXiv:2604.01483). Three replies to "the theorems are elementary": the Lean file
is the specification, the artefact is the audited trust boundary, and formalising forced every hypothesis
(`ω > 0`, `m ≥ 0`, `w > 0`, nonempty calibration set) to become explicit.

## What is NOT proved (cited only)

The probabilistic step of Conformal Risk Control — for exchangeable
calibration/test moves and a monotone, bounded loss, the conformally chosen
radius `k̂` satisfies `E[loss(r_{n+1}, k̂)] ≤ β` — is **cited, not formalised**:

> Angelopoulos, Bates, Fisch, Lei, Schuster. *Conformal Risk Control.* ICLR 2024, Theorem 1.

The lemmas in (a) supply exactly the loss properties (bounded in `[0,1]`,
monotone in the parameter) that theorem assumes; (c) is the arithmetic that
turns a loss bound into a payoff bound. Nothing about exchangeability,
expectations or the choice of `k̂` is formalised here.

## Rebuild

Prerequisite: [elan](https://github.com/leanprover/elan) (user-level install,
no admin). On Windows, download `elan-x86_64-pc-windows-msvc.zip` from the
latest elan release, unzip and run `elan-init.exe -y` (this repo was set up
with `--no-modify-path`, so `~/.elan/bin` must be on `PATH` manually).

```sh
export PATH="$HOME/.elan/bin:$PATH"     # Git Bash; PowerShell: $env:Path = "$HOME\.elan\bin;$env:Path"
cd lean
lake exe cache get        # fetch prebuilt Mathlib oleans (~6.4 GB, several minutes); never build Mathlib from source
lake build                # builds Delphi.Condor; expect "Build completed successfully"
lake env lean CheckAxioms.lean   # prints the axioms of every theorem; must not contain sorryAx
```

`lake build` takes about 35–40 s on a laptop once the cache is in place
(≈ 15–20 s of that is elaborating `Condor.lean` against `import Mathlib`).
The `.lake/` directory (toolchain packages, Mathlib cache) is git-ignored.

## How the project was created

```sh
lake +leanprover-community/mathlib4:lean-toolchain init delphi math   # inside lean/
# (the math template's post-update hook runs `lake exe cache get` automatically)
```

`lakefile.toml` keeps Mathlib's standard linter set but disables
`linter.style.header`, because this repository is MIT-licensed and that linter
only accepts Mathlib's Apache-2.0 header wording.
