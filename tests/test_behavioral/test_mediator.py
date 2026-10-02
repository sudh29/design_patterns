"""Tests for the Mediator pattern implementation."""

import pytest

from design_patterns.behavioral.mediator import (
    CommercialAirliner,
    ControlTower,
)


class TestMediatorPattern:
    def test_single_flight_landing(self) -> None:
        tower = ControlTower()
        f1 = CommercialAirliner("AI-101", tower)

        assert f1.request_landing() is True
        assert "CLEAR for landing" in f1.inbox[-1]

    def test_runway_congestion_holding_pattern(self) -> None:
        tower = ControlTower()
        f1 = CommercialAirliner("FL-1", tower)
        f2 = CommercialAirliner("FL-2", tower)

        # F1 gets clearance
        assert f1.request_landing() is True

        # F2 must hold
        assert f2.request_landing() is False
        assert "Entering holding pattern" in f2.inbox[-1]

        # F1 vacates -> F2 receives clearance
        f1.vacate_runway()
        assert "CLEAR for landing" in f2.inbox[-1]

    def test_unregistered_flight_raises(self) -> None:
        tower = ControlTower()
        with pytest.raises(ValueError, match="Unregistered flight"):
            tower.request_landing("GHOST-9")
