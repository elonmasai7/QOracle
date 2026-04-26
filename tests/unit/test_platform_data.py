from backend.services.platform_data import build_dashboard_snapshot, stress_scenario_catalog, validate_portfolio_payload


def test_dashboard_snapshot_contains_expected_sections():
    snapshot = build_dashboard_snapshot()

    assert "metrics" in snapshot
    assert "recommendations" in snapshot
    assert len(snapshot["metrics"]) == 5
    assert len(snapshot["scenarios"]) >= 4


def test_stress_scenario_catalog_has_standard_scenarios():
    catalog = stress_scenario_catalog()

    names = {item["name"] for item in catalog}
    assert "Fed hike +200bps" in names
    assert "Liquidity crunch" in names


def test_validate_portfolio_payload_flags_errors():
    result = validate_portfolio_payload(
        [
            {"symbol": "AAPL", "quantity": "10", "price": "190"},
            {"symbol": "MSFT", "quantity": "bad", "price": "420"},
        ]
    )

    assert result["valid"] is False
    assert result["rows"] == 2
    assert result["errors"]
