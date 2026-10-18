/-
Copyright (c) 2026 Klemen. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Klemen
-/
import Mathlib

/-!
# Proofs
-/

theorem euclid_triple (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by
    ring

theorem two_mul_le (a b : ℝ) : 2 * a * b ≤ a^2 + b^2 := by
    nlinarith [sq_nonneg (a - b)]
