import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.scoring import compute_control_coverage

class TestScoring(unittest.TestCase):
    def test_hard_and_soft_gaps(self):
        """Test that coverage below minStrength creates soft gap"""
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
        self.assertAlmostEqual(soft[0]["best"], 0.4, places=6)
        self.assertAlmostEqual(soft[0]["min"], 0.7, places=6)

    def test_hard_gap_when_no_tool(self):
        """Test that missing capability creates hard gap"""
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
        self.assertEqual(hard[0]["capabilityId"], "ns-firewall")
        self.assertEqual(hard[0]["weight"], 0.6)

    def test_weights_calculation(self):
        """Test that weighted coverage is calculated correctly"""
        reqs = [
            {"capabilityId": "ns-firewall", "weight": 0.6, "minStrength": 0.6},
            {"capabilityId": "url-filtering", "weight": 0.4, "minStrength": 0.6},
        ]
        tenant_tools = {"palo-alto": 0.8}
        toolcap = {"palo-alto": {"ns-firewall": 0.9, "url-filtering": 0.85}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        # 0.6 * (0.9 * 0.8) + 0.4 * (0.85 * 0.8) = 0.6 * 0.72 + 0.4 * 0.68 = 0.432 + 0.272 = 0.704
        self.assertAlmostEqual(coverage, 0.704, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)

    def test_minStrength_threshold(self):
        """Test that minStrength correctly identifies soft gaps"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.7},
        ]
        tenant_tools = {"tool1": 0.8}
        toolcap = {"tool1": {"siem": 0.6}}  # 0.6 * 0.8 = 0.48 < 0.7
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.48, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 1)
        self.assertAlmostEqual(soft[0]["best"], 0.48, places=6)
        
        # Same tool but higher strength - should pass threshold
        toolcap = {"tool1": {"siem": 0.9}}  # 0.9 * 0.8 = 0.72 >= 0.7
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.72, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)

    def test_configscore_impact(self):
        """Test that ConfigScore affects coverage calculation"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.5},
        ]
        toolcap = {"tool1": {"siem": 0.9}}
        
        # High ConfigScore
        tenant_tools = {"tool1": 1.0}
        coverage1, _, _ = compute_control_coverage(reqs, tenant_tools, toolcap)
        
        # Low ConfigScore
        tenant_tools = {"tool1": 0.5}
        coverage2, _, _ = compute_control_coverage(reqs, tenant_tools, toolcap)
        
        self.assertAlmostEqual(coverage1, 0.9, places=6)  # 0.9 * 1.0
        self.assertAlmostEqual(coverage2, 0.45, places=6)  # 0.9 * 0.5
        self.assertGreater(coverage1, coverage2)

    def test_multiple_tools_best_selection(self):
        """Test that best tool is selected per capability"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.5},
        ]
        tenant_tools = {"tool1": 0.8, "tool2": 0.9}
        toolcap = {
            "tool1": {"siem": 0.7},  # 0.7 * 0.8 = 0.56
            "tool2": {"siem": 0.6},  # 0.6 * 0.9 = 0.54
        }
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        # Should pick tool1 (0.56 > 0.54)
        self.assertAlmostEqual(coverage, 0.56, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)

    def test_weights_normalization(self):
        """Test that weights are normalized correctly when they don't sum to 1.0"""
        reqs = [
            {"capabilityId": "cap1", "weight": 0.3, "minStrength": 0.5},
            {"capabilityId": "cap2", "weight": 0.2, "minStrength": 0.5},
        ]
        tenant_tools = {"tool1": 1.0}
        toolcap = {"tool1": {"cap1": 0.8, "cap2": 0.6}}
        coverage, _, _ = compute_control_coverage(reqs, tenant_tools, toolcap)
        # Coverage = (0.3 * 0.8 + 0.2 * 0.6) / (0.3 + 0.2) = 0.36 / 0.5 = 0.72
        self.assertAlmostEqual(coverage, 0.72, places=6)

    def test_zero_weights(self):
        """Test handling of zero weights"""
        reqs = [
            {"capabilityId": "cap1", "weight": 0.0, "minStrength": 0.5},
            {"capabilityId": "cap2", "weight": 1.0, "minStrength": 0.5},
        ]
        tenant_tools = {"tool1": 1.0}
        toolcap = {"tool1": {"cap1": 0.8, "cap2": 0.6}}
        coverage, _, _ = compute_control_coverage(reqs, tenant_tools, toolcap)
        # Coverage = (0.0 * 0.8 + 1.0 * 0.6) / (0.0 + 1.0) = 0.6
        self.assertAlmostEqual(coverage, 0.6, places=6)

    def test_empty_requirements(self):
        """Test handling of empty requirements"""
        reqs = []
        tenant_tools = {"tool1": 1.0}
        toolcap = {"tool1": {"cap1": 0.8}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.0, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)

    def test_no_tenant_tools(self):
        """Test handling when no tenant tools are available"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.7},
        ]
        tenant_tools = {}
        toolcap = {"tool1": {"siem": 0.9}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.0, places=6)
        self.assertEqual(len(hard), 1)
        self.assertEqual(len(soft), 0)

    def test_complex_multi_capability_scenario(self):
        """Test realistic scenario with multiple capabilities and tools"""
        reqs = [
            {"capabilityId": "ns-firewall", "weight": 0.6, "minStrength": 0.6},
            {"capabilityId": "url-filtering", "weight": 0.4, "minStrength": 0.6},
        ]
        tenant_tools = {"palo-alto": 0.8, "cloudflare": 0.9}
        toolcap = {
            "palo-alto": {"ns-firewall": 0.9, "url-filtering": 0.85},
            "cloudflare": {"ns-firewall": 0.3, "url-filtering": 0.9},
        }
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        # ns-firewall: max(0.9*0.8=0.72, 0.3*0.9=0.27) = 0.72
        # url-filtering: max(0.85*0.8=0.68, 0.9*0.9=0.81) = 0.81
        # Coverage = 0.6 * 0.72 + 0.4 * 0.81 = 0.432 + 0.324 = 0.756
        self.assertAlmostEqual(coverage, 0.756, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)

    def test_soft_gap_with_multiple_capabilities(self):
        """Test that soft gaps are correctly identified when some pass and some fail"""
        reqs = [
            {"capabilityId": "cap1", "weight": 0.5, "minStrength": 0.7},
            {"capabilityId": "cap2", "weight": 0.5, "minStrength": 0.7},
        ]
        tenant_tools = {"tool1": 0.8}
        toolcap = {"tool1": {"cap1": 0.9, "cap2": 0.6}}  # cap1: 0.72 >= 0.7, cap2: 0.48 < 0.7
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.6, places=6)  # (0.5*0.72 + 0.5*0.48) = 0.6
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 1)
        self.assertEqual(soft[0]["capabilityId"], "cap2")

    def test_exact_minStrength_boundary(self):
        """Test edge case where coverage exactly equals minStrength"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.7},
        ]
        tenant_tools = {"tool1": 0.875}  # 0.8 * 0.875 = 0.7 (exactly the threshold)
        toolcap = {"tool1": {"siem": 0.8}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.7, places=6)
        self.assertEqual(len(hard), 0)
        self.assertEqual(len(soft), 0)  # Should pass, not be a soft gap

    def test_disabled_tool_excluded(self):
        """Test that disabled tools (ConfigScore = 0) don't contribute"""
        reqs = [
            {"capabilityId": "siem", "weight": 1.0, "minStrength": 0.5},
        ]
        tenant_tools = {"tool1": 0.0}  # Disabled tool
        toolcap = {"tool1": {"siem": 0.9}}
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.0, places=6)
        self.assertEqual(len(hard), 1)
        self.assertEqual(len(soft), 0)

    def test_high_weight_hard_gap_priority(self):
        """Test that high-weight hard gaps are correctly identified"""
        reqs = [
            {"capabilityId": "critical-cap", "weight": 0.8, "minStrength": 0.6},
            {"capabilityId": "minor-cap", "weight": 0.2, "minStrength": 0.6},
        ]
        tenant_tools = {"tool1": 0.8}
        toolcap = {"tool1": {"minor-cap": 0.9}}  # Only minor-cap covered
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        self.assertAlmostEqual(coverage, 0.144, places=6)  # 0.2 * 0.9 * 0.8 = 0.144
        self.assertEqual(len(hard), 1)
        self.assertEqual(hard[0]["capabilityId"], "critical-cap")
        self.assertEqual(hard[0]["weight"], 0.8)

    def test_weights_sum_to_one_validation(self):
        """Test that weights are handled correctly when they sum to 1.0"""
        reqs = [
            {"capabilityId": "cap1", "weight": 0.6, "minStrength": 0.5},
            {"capabilityId": "cap2", "weight": 0.4, "minStrength": 0.5},
        ]
        tenant_tools = {"tool1": 1.0}
        toolcap = {"tool1": {"cap1": 0.8, "cap2": 0.6}}
        coverage, _, _ = compute_control_coverage(reqs, tenant_tools, toolcap)
        # Coverage = (0.6 * 0.8 + 0.4 * 0.6) / 1.0 = 0.72
        self.assertAlmostEqual(coverage, 0.72, places=6)

    def test_mixed_hard_and_soft_gaps(self):
        """Test scenario with both hard and soft gaps"""
        reqs = [
            {"capabilityId": "cap1", "weight": 0.4, "minStrength": 0.7},  # Hard gap
            {"capabilityId": "cap2", "weight": 0.3, "minStrength": 0.7},  # Soft gap
            {"capabilityId": "cap3", "weight": 0.3, "minStrength": 0.7},  # Pass
        ]
        tenant_tools = {"tool1": 0.8}
        toolcap = {"tool1": {"cap2": 0.6, "cap3": 0.9}}  # cap2: 0.48 < 0.7, cap3: 0.72 >= 0.7
        coverage, hard, soft = compute_control_coverage(reqs, tenant_tools, toolcap)
        # Coverage = (0.4*0 + 0.3*0.48 + 0.3*0.72) / 1.0 = 0.36
        self.assertAlmostEqual(coverage, 0.36, places=6)
        self.assertEqual(len(hard), 1)
        self.assertEqual(hard[0]["capabilityId"], "cap1")
        self.assertEqual(len(soft), 1)
        self.assertEqual(soft[0]["capabilityId"], "cap2")

if __name__ == '__main__':
    unittest.main()
