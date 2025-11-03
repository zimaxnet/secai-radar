import unittest
from api.shared.scoring import compute_control_coverage

class TestScoring(unittest.TestCase):
    def test_hard_and_soft_gaps(self):
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.7},
        ]
        tenant_tools = {"google-secops": 0.8}
        toolcap = {"google-secops": {"siem": 0.5}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.4, places=6)  # 0.5 * 0.8 * 1.0
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 1)
        self.assertEqual(soft[0]["capabilityId"], "siem")

    def test_hard_gap_when_no_tool(self):
        reqs = [
            {"capabilityId": "ns-firewall", "weight": 0.6, "minStrength": 0.6},
            {"capabilityId": "url-filtering", "weight": 0.4, "minStrength": 0.6},
        ]
        tenant_tools = {"wiz-cspm": 0.8}
        toolcap = {"wiz-cspm": {"cspm": 0.9}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.0, places=6)
        self.assertEqual(len(hard), 2)
        self.assertEqual(len(soft), 0)

if __name__ == '__main__':
    unittest.main()
