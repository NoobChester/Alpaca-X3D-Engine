"""Smoke tests for the Alpaca engine package."""

import unittest

import numpy as np

from engine import engine
from engine.trading_bot import create_aligned_array


class EngineSmokeTests(unittest.TestCase):
    """Basic alignment and execution smoke tests for the compiled extension."""

    def test_rejects_misaligned_array(self) -> None:
        """The engine should reject a deliberately misaligned view."""
        raw_data = np.random.rand(1024).astype(np.float64)
        misaligned = raw_data[1:]

        with self.assertRaises(TypeError):
            engine.calculate_signal(misaligned)

    def test_accepts_aligned_array(self) -> None:
        """The engine should process a properly aligned array."""
        aligned_data = create_aligned_array(1024, dtype=np.float64)

        engine.calculate_signal(aligned_data)


if __name__ == "__main__":
    unittest.main()
