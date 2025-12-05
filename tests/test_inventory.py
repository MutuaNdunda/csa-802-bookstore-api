from services.inventory_service import InventoryService

def test_stock_check():
    inv = InventoryService()
    assert inv.is_in_stock("B001", 1) == True
