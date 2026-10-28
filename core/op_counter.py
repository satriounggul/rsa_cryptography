"""
Operation Counter for Cryptographic Operations.
Used to measure the exact number of arithmetic operations (multiplications, modulos,
bit shifts, additions) per decryption method, avoiding misleading timing results in Python (R-28).

Optional bit-weighted cost (OperationCounter(track_bits=True)): the plain counts treat a 2048-bit and a
512-bit multiplication alike, so they cannot show the advantage of CRT (smaller operands). With
track_bits=True each counted multiplication/modulo/division that is given its operands also adds to
  weighted_cost            = bitlen(a) * bitlen(b)                         (literal)
  weighted_cost_schoolbook = bitlen(a) * bitlen(b) for multiplication, and
                             max(bitlen(a) - bitlen(m) + 1, 1) * bitlen(m) for modulo/division
The plain counts are unchanged and the bit-weighted fields are absent from to_dict() unless track_bits is set.
modinv / extended_gcd / miller_rabin are not instrumented, so the legacy (inline-inverse) Gauss path
does not include its modular inverses in any of these figures.
"""

from typing import Dict, Optional


class OperationCounter:
    """Tracks arithmetic operations during modular arithmetic and decryption."""

    def __init__(self, track_bits: bool = False) -> None:
        self.track_bits = track_bits
        self.reset()

    def reset(self) -> None:
        self.multiplications: int = 0
        self.modulo_ops: int = 0
        self.bit_shifts: int = 0
        self.additions: int = 0
        self.divisions: int = 0
        self.weighted_cost: int = 0
        self.weighted_cost_schoolbook: int = 0

    def count_mul(self, count: int = 1, a: Optional[int] = None, b: Optional[int] = None) -> None:
        self.multiplications += count
        if self.track_bits and a is not None and b is not None:
            cost = (abs(a).bit_length() or 1) * (abs(b).bit_length() or 1)
            self.weighted_cost += cost
            self.weighted_cost_schoolbook += cost

    def _count_reduction(self, a: Optional[int], m: Optional[int]) -> None:
        if self.track_bits and a is not None and m is not None:
            la = abs(a).bit_length() or 1
            lm = abs(m).bit_length() or 1
            self.weighted_cost += la * lm
            self.weighted_cost_schoolbook += max(la - lm + 1, 1) * lm

    def count_mod(self, count: int = 1, a: Optional[int] = None, m: Optional[int] = None) -> None:
        self.modulo_ops += count
        self._count_reduction(a, m)

    def count_shift(self, count: int = 1) -> None:
        self.bit_shifts += count

    def count_add(self, count: int = 1) -> None:
        self.additions += count

    def count_div(self, count: int = 1, a: Optional[int] = None, m: Optional[int] = None) -> None:
        self.divisions += count
        self._count_reduction(a, m)

    def to_dict(self) -> Dict[str, int]:
        total_arithmetic = self.multiplications + self.modulo_ops + self.bit_shifts + self.additions + self.divisions
        result = {
            "multiplications": self.multiplications,
            "modulo_ops": self.modulo_ops,
            "bit_shifts": self.bit_shifts,
            "additions": self.additions,
            "divisions": self.divisions,
            "total_operations": total_arithmetic
        }
        if self.track_bits:
            result["weighted_cost"] = self.weighted_cost
            result["weighted_cost_schoolbook"] = self.weighted_cost_schoolbook
        return result

    def copy(self) -> "OperationCounter":
        other = OperationCounter(track_bits=self.track_bits)
        other.multiplications = self.multiplications
        other.modulo_ops = self.modulo_ops
        other.bit_shifts = self.bit_shifts
        other.additions = self.additions
        other.divisions = self.divisions
        other.weighted_cost = self.weighted_cost
        other.weighted_cost_schoolbook = self.weighted_cost_schoolbook
        return other
