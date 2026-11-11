import uuid
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import InventoryItem, InventoryLot, Equipment, Ward, RosterAssignment
from backend.app.domain.fefo_dispenser import dispense_item_fefo, quarantine_expired_lots, InsufficientStockError


client = TestClient(app)


def test_fefo_dispensing_order():
    """Verify that FEFO strictly dispenses from earliest expiring lot first."""
    db = SessionLocal()
    today = date.today()
    sku = f"TEST-FEFO-{uuid.uuid4().hex[:6]}"

    # Create a test item with 2 lots
    test_item = InventoryItem(
        sku_code=sku,
        generic_name="Test Drug IV",
        category="Antibiotic",
        unit_of_measure="Vial",
        reorder_threshold=10,
        target_stock_level=50
    )
    db.add(test_item)
    db.flush()

    # Lot 1: Expires in 10 days, 15 qty (Should be dispensed first)
    lot_early = InventoryLot(
        item_id=test_item.id,
        lot_number="LOT-EARLY",
        quantity_on_hand=15,
        expiry_date=today + timedelta(days=10),
        received_date=today - timedelta(days=20)
    )
    # Lot 2: Expires in 60 days, 25 qty (Should be dispensed second)
    lot_later = InventoryLot(
        item_id=test_item.id,
        lot_number="LOT-LATER",
        quantity_on_hand=25,
        expiry_date=today + timedelta(days=60),
        received_date=today - timedelta(days=5)
    )
    db.add_all([lot_early, lot_later])
    db.commit()

    # Dispense 20 vials (should take all 15 from lot_early and 5 from lot_later)
    result = dispense_item_fefo(db, sku_code=sku, requested_qty=20)

    assert result["requested_qty"] == 20
    assert len(result["dispensed_allocations"]) == 2
    
    first_alloc = result["dispensed_allocations"][0]
    assert first_alloc["lot_number"] == "LOT-EARLY"
    assert first_alloc["quantity_deducted"] == 15
    assert first_alloc["remaining_in_lot"] == 0

    second_alloc = result["dispensed_allocations"][1]
    assert second_alloc["lot_number"] == "LOT-LATER"
    assert second_alloc["quantity_deducted"] == 5
    assert second_alloc["remaining_in_lot"] == 20

    # Remaining stock = 20
    assert result["remaining_stock"] == 20
    db.close()


def test_fefo_quarantine_expired_stock():
    """Verify that expired lots are automatically quarantined and excluded from dispensing."""
    db = SessionLocal()
    today = date.today()
    sku = f"TEST-EXP-{uuid.uuid4().hex[:6]}"

    test_item = InventoryItem(
        sku_code=sku,
        generic_name="Test Expired Drug",
        category="Analgesic",
        unit_of_measure="Tablet",
        reorder_threshold=5,
        target_stock_level=20
    )
    db.add(test_item)
    db.flush()

    # Expired lot (yesterday)
    expired_lot = InventoryLot(
        item_id=test_item.id,
        lot_number="LOT-ALREADY-EXP",
        quantity_on_hand=10,
        expiry_date=today - timedelta(days=1),
        received_date=today - timedelta(days=100)
    )
    # Valid lot
    valid_lot = InventoryLot(
        item_id=test_item.id,
        lot_number="LOT-VALID",
        quantity_on_hand=10,
        expiry_date=today + timedelta(days=30),
        received_date=today - timedelta(days=10)
    )
    db.add_all([expired_lot, valid_lot])
    db.commit()

    # Dispense 10 units: must take from valid lot, not expired lot
    result = dispense_item_fefo(db, sku_code=sku, requested_qty=10)
    assert len(result["dispensed_allocations"]) == 1
    assert result["dispensed_allocations"][0]["lot_number"] == "LOT-VALID"

    # Expired lot should now be marked quarantined
    db.refresh(expired_lot)
    assert expired_lot.is_quarantined is True

    # Requesting more than 0 now should fail because only the expired lot remains
    with pytest.raises(InsufficientStockError):
        dispense_item_fefo(db, sku_code=sku, requested_qty=5)

    db.close()


def test_api_inventory_items():
    response = client.get("/api/v1/inventory/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    first = items[0]
    assert "sku_code" in first
    assert "total_usable_stock" in first
    assert "reorder_required" in first


def test_api_dispense_endpoint():
    # Use seeded Amoxicillin (MED-AMOX-500)
    response = client.post(
        "/api/v1/inventory/dispense",
        json={"sku_code": "MED-AMOX-500", "requested_qty": 5, "dispensed_by": "TEST_NURSE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sku_code"] == "MED-AMOX-500"
    assert data["requested_qty"] == 5
    assert len(data["dispensed_allocations"]) >= 1


def test_api_equipment_telemetry():
    response = client.get("/api/v1/inventory/equipment-telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "ventilators" in data
    assert "oxygen_supply" in data
    assert data["ventilators"]["total"] >= 10
    assert "days_of_supply_remaining" in data["oxygen_supply"]


def test_api_workforce_deficits():
    response = client.get("/api/v1/workforce/deficits?shift=Morning")
    assert response.status_code == 200
    data = response.json()
    assert "ward_summaries" in data
    assert len(data["ward_summaries"]) == 8
    assert "hospital_coverage_pct" in data


def test_api_roster_and_status_update():
    # Get roster list
    response = client.get("/api/v1/workforce/roster")
    assert response.status_code == 200
    roster = response.json()
    assert len(roster) > 0

    first_assignment_id = roster[0]["id"]
    # Update to Absent
    patch_res = client.patch(
        f"/api/v1/workforce/assignments/{first_assignment_id}/status",
        json={"status": "Absent", "is_on_duty": False}
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["status"] == "Absent"
    assert updated["is_on_duty"] is False
