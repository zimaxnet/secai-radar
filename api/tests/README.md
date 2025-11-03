# Scoring Math Unit Tests

Unit tests for the scoring engine that validates coverage calculations, gap detection, and weight/minStrength thresholds.

## Running Tests

```bash
cd api
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -m unittest tests.test_scoring -v
```

Or using pytest (if installed):
```bash
pytest tests/test_scoring.py -v
```

## Test Coverage

The test suite covers:

### Core Calculations
- **Weighted coverage**: Verifies coverage = Σ(weight × best_tool_coverage)
- **Weight normalization**: Handles weights that don't sum to 1.0
- **ConfigScore impact**: Validates that ConfigScore multiplies tool strength

### Gap Detection
- **Hard gaps**: Capabilities with 0% coverage (no tool or tool has 0 strength)
- **Soft gaps**: Capabilities with coverage > 0 but < minStrength threshold
- **Mixed scenarios**: Controls with both hard and soft gaps

### Edge Cases
- Empty requirements
- Zero weights
- No tenant tools
- Disabled tools (ConfigScore = 0)
- Exact minStrength boundary conditions
- Multiple tools (best selection)

### Realistic Scenarios
- Multi-capability controls (e.g., firewall + URL filtering)
- Multiple tools competing for same capability
- High-weight vs low-weight gaps

## Test Results

All 17 tests should pass:
```
test_complex_multi_capability_scenario ... ok
test_configscore_impact ... ok
test_disabled_tool_excluded ... ok
test_empty_requirements ... ok
test_exact_minStrength_boundary ... ok
test_hard_and_soft_gaps ... ok
test_hard_gap_when_no_tool ... ok
test_high_weight_hard_gap_priority ... ok
test_minStrength_threshold ... ok
test_mixed_hard_and_soft_gaps ... ok
test_multiple_tools_best_selection ... ok
test_no_tenant_tools ... ok
test_soft_gap_with_multiple_capabilities ... ok
test_weights_calculation ... ok
test_weights_normalization ... ok
test_weights_sum_to_one_validation ... ok
test_zero_weights ... ok
```

## CI Integration

These tests should be run in CI/CD pipelines to ensure scoring math remains correct when:
- Seeds are updated (`control_requirements.json`, `tool_capabilities.json`)
- Scoring algorithm is modified
- New capabilities or tools are added

