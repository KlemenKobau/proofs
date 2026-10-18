/-
Copyright (c) 2026 Klemen. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Klemen
-/
import Mathlib

/-!
# Proofs

Elementary theorems formalized while learning Lean 4.
-/

/-- (m² − n²)² + (2mn)² = (m² + n²)²

**Euclid's formula**: any two integers generate a Pythagorean triple. -/
theorem euclid_triple (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by
    ring

/-- 2ab ≤ a² + b²

For all real numbers `a` and `b`, a consequence of (a − b)² ≥ 0. -/
theorem two_mul_le (a b : ℝ) : 2 * a * b ≤ a^2 + b^2 := by
    nlinarith [sq_nonneg (a - b)]

/-- n odd ⟹ n² odd

The square of an odd natural number is odd. -/
theorem odd_sq (n : ℕ) (h : Odd n) : Odd (n ^ 2) := by
    obtain ⟨k, rfl⟩ := h
    use (2 * k^2 + 2 * k)
    ring

/-- 2 · (0 + 1 + ⋯ + n) = n(n + 1)

**Gauss's sum** of the first `n` natural numbers, proved by induction. -/
theorem gauss_sum (n : ℕ) :
    2 * ∑ i ∈ Finset.range (n + 1), i = n * (n + 1) := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ]
    rw [mul_add 2]
    rw [ih]
    ring

/-- 1 + 3 + 5 + ⋯ + (2n − 1) = n²

The first `n` odd numbers add up to a perfect square. -/
theorem sum_odds (n : ℕ) :
    ∑ i ∈ Finset.range n, (2 * i + 1) = n ^ 2 := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ]
    rw [ih]
    ring


namespace Fib

/-- The Fibonacci sequence: `fib 0 = 0`, `fib 1 = 1`, `fib (n + 2) = fib n + fib (n + 1)`. -/
def fib : ℕ → ℕ
  | 0 => 0
  | 1 => 1
  | n + 2 => fib n + fib (n + 1)

/-- F₀ + F₁ + ⋯ + Fₙ₋₁ + 1 = Fₙ₊₁

Summing Fibonacci numbers, using my own definition of the sequence. -/
theorem fib_sum (n : ℕ) :
    ∑ i ∈ Finset.range n, fib i + 1 = fib (n + 1) := by
  induction n with
  | zero => simp [fib]
  | succ k ih =>
    rw [Finset.sum_range_succ]
    rw [fib]
    rw [← ih] /- Proof is in form A = B, rw searches for A and replaces with B, ←
                makes it search by B and replace with A -/
    ring

end Fib
