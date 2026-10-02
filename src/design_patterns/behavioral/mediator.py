"""Mediator Design Pattern.

Classification: Behavioral
Intent:
    Define an object that encapsulates how a set of objects interact.
    Mediator promotes loose coupling by keeping objects from referring to each
    other explicitly, and it lets you vary their interaction independently.

Motivation & Real-World Analogy:
    In a multi-user chat room or aircraft landing coordinator, if every participant
    or airplane maintained direct references to every other airplane, the system
    complexity would explode to O(N^2) tight couplings.
    An Air Traffic Control (ATC) tower acts as the Mediator: airplanes only talk to the
    tower, and the tower orchestrates runway clearance, holding patterns, and alerts.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class AirTrafficControl {
            <<protocol>>
            +request_landing(flight_number: str) bool
            +notify_runway_cleared(flight_number: str)
            +register_flight(airplane: Airplane)
        }
        class ControlTower {
            -runway_busy: bool
            -holding_queue: list[str]
            -airplanes: dict[str, Airplane]
            +request_landing(flight_number: str) bool
            +notify_runway_cleared(flight_number: str)
        }
        class Airplane {
            +flight_number: str
            #mediator: AirTrafficControl
            +land()
            +receive_instruction(msg: str)
        }
        AirTrafficControl <|.. ControlTower
        ControlTower o--> Airplane : mediates
        Airplane o--> AirTrafficControl : communicates with
    ```
"""

from __future__ import annotations

from typing import Protocol


# ==============================================================================
# 1. Protocols: Colleague and Mediator
# ==============================================================================
class Airplane(Protocol):
    """Colleague Protocol: Component that communicates through the Mediator."""

    flight_number: str

    def receive_instruction(self, message: str) -> None: ...


class AirTrafficControl(Protocol):
    """Mediator Protocol: Coordinates interactions among colleagues."""

    def register_flight(self, airplane: Airplane) -> None: ...
    def request_landing(self, flight_number: str) -> bool: ...
    def notify_runway_cleared(self, flight_number: str) -> None: ...


# ==============================================================================
# 2. Concrete Colleague
# ==============================================================================
class CommercialAirliner:
    """Concrete Colleague representing an individual flight."""

    def __init__(self, flight_number: str, mediator: AirTrafficControl) -> None:
        self.flight_number = flight_number
        self._mediator = mediator
        self.inbox: list[str] = []
        self._mediator.register_flight(self)

    def request_landing(self) -> bool:
        return self._mediator.request_landing(self.flight_number)

    def vacate_runway(self) -> None:
        self._mediator.notify_runway_cleared(self.flight_number)

    def receive_instruction(self, message: str) -> None:
        self.inbox.append(message)


# ==============================================================================
# 3. Concrete Mediator
# ==============================================================================
class ControlTower:
    """Concrete Mediator coordinating runway access."""

    def __init__(self) -> None:
        self._flights: dict[str, Airplane] = {}
        self._runway_occupied_by: str | None = None
        self._holding_queue: list[str] = []

    def register_flight(self, airplane: Airplane) -> None:
        self._flights[airplane.flight_number] = airplane

    def request_landing(self, flight_number: str) -> bool:
        airplane = self._flights.get(flight_number)
        if not airplane:
            raise ValueError(f"Unregistered flight: {flight_number}")

        if self._runway_occupied_by is None:
            self._runway_occupied_by = flight_number
            airplane.receive_instruction("Runway 09R CLEAR for landing.")
            return True
        else:
            self._holding_queue.append(flight_number)
            airplane.receive_instruction(
                f"Runway busy (occupied by {self._runway_occupied_by}). Entering holding pattern."
            )
            return False

    def notify_runway_cleared(self, flight_number: str) -> None:
        if self._runway_occupied_by == flight_number:
            self._runway_occupied_by = None

            # Promote next flight from holding pattern
            if self._holding_queue:
                next_flight = self._holding_queue.pop(0)
                self.request_landing(next_flight)


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    tower = ControlTower()

    flight_ua = CommercialAirliner("UA-101", tower)
    flight_ba = CommercialAirliner("BA-202", tower)
    flight_lh = CommercialAirliner("LH-303", tower)

    # First flight gets runway
    print(f"UA-101 landing request granted? {flight_ua.request_landing()}")
    print(f"UA-101 latest msg: {flight_ua.inbox[-1]}")

    # Second flight placed in holding queue
    print(f"BA-202 landing request granted? {flight_ba.request_landing()}")
    print(f"BA-202 latest msg: {flight_ba.inbox[-1]}")

    # First flight vacates runway -> BA-202 automatically promoted!
    flight_ua.vacate_runway()
    print(f"BA-202 latest msg after UA cleared: {flight_ba.inbox[-1]}")
