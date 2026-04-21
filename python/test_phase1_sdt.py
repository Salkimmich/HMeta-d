import math
import pathlib
import sys
import unittest

# Ensure local `python/` modules are importable when tests run from repo root.
sys.path.append(str(pathlib.Path(__file__).resolve().parent))

from phase1_sdt import prepare_sdt_data


class TestPhase1SDT(unittest.TestCase):
    def test_reference_inputs_match_expected_type1_estimates(self) -> None:
        nR_S1 = [36, 24, 17, 20, 10, 12, 34, 22]
        nR_S2 = [21, 19, 23, 28, 33, 28, 20, 19]

        sdt_data = prepare_sdt_data(nR_S1, nR_S2)

        self.assertEqual(sdt_data.nratings, 4)
        self.assertEqual(sdt_data.nTot, sum(nR_S1) + sum(nR_S2))
        self.assertEqual(len(sdt_data.counts), 16)

        # MATLAB-equivalent values from fit_meta_d_mcmc pre-JAGS calculations.
        self.assertTrue(math.isclose(sdt_data.d1, 0.1945, abs_tol=0.01))
        self.assertTrue(math.isclose(sdt_data.c1, 0.0385, abs_tol=0.01))


if __name__ == "__main__":
    unittest.main()
