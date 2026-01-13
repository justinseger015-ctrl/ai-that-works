import { existsSync, unlinkSync } from "node:fs";
import { OrderStore } from "./order-store";
import { createCustomer, createMenuItem } from "../models/types";

// ============================================================================
// Order Store Tests
// ============================================================================

const TEST_FILE = "data/orders-test.json";

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

async function testOrderStore() {
  console.log("🧪 Testing Order Store...\n");

  // Clean up any existing test file
  if (existsSync(TEST_FILE)) {
    unlinkSync(TEST_FILE);
  }

  const store = new OrderStore(TEST_FILE);

  // Test data
  const customer = createCustomer("John Doe", "+1-555-0100", "123 Main St");
  const menuItem1 = createMenuItem("Classic Burrito", 8.99, "Rice, beans, meat");
  const menuItem2 = createMenuItem("Veggie Burrito", 7.99, "Rice, beans, veggies");

  // ============================================================================
  // Test 1: Create Order
  // ============================================================================
  console.log("📝 Test 1: Create Order");
  const order = store.create(
    customer,
    [
      { menuItem: menuItem1, quantity: 2 },
      { menuItem: menuItem2, quantity: 1 },
    ],
    "Extra hot sauce",
  );

  assert(order.id.startsWith("ord-"), "Order ID should start with 'ord-'");
  assert(order.status === "pending", "New order status should be 'pending'");
  assert(order.items.length === 2, "Order should have 2 items");
  assert(
    order.totalAmount === 8.99 * 2 + 7.99 * 1,
    "Total amount should be calculated correctly",
  );
  assert(order.notes === "Extra hot sauce", "Notes should be saved");
  console.log("✅ Order created successfully:", order.id);
  console.log(`   Total: $${order.totalAmount.toFixed(2)}\n`);

  // ============================================================================
  // Test 2: Read Order
  // ============================================================================
  console.log("📖 Test 2: Read Order");
  const readOrder = store.read(order.id);
  assert(readOrder !== undefined, "Order should be readable");
  assert(readOrder!.id === order.id, "Read order should match created order");
  console.log("✅ Order read successfully:", readOrder!.id);
  console.log(`   Customer: ${readOrder!.customerSnapshot.name}\n`);

  // ============================================================================
  // Test 3: Update Order
  // ============================================================================
  console.log("🔄 Test 3: Update Order Status");
  // Add small delay to ensure timestamp changes
  await new Promise(resolve => setTimeout(resolve, 10));
  const updatedOrder = store.update(order.id, {
    status: "confirmed",
    notes: "Extra hot sauce - CONFIRMED",
  });
  assert(
    updatedOrder.status === "confirmed",
    "Order status should be updated",
  );
  assert(
    updatedOrder.notes === "Extra hot sauce - CONFIRMED",
    "Notes should be updated",
  );
  assert(
    updatedOrder.updatedAt !== order.updatedAt,
    "Updated timestamp should change",
  );
  console.log("✅ Order updated successfully");
  console.log(`   Status: ${updatedOrder.status}\n`);

  // ============================================================================
  // Test 4: List Orders
  // ============================================================================
  console.log("📋 Test 4: List Orders");
  const order2 = store.create(
    customer,
    [{ menuItem: menuItem1, quantity: 1 }],
    "No onions",
  );

  const allOrders = store.list();
  assert(allOrders.length === 2, "Should have 2 orders");
  console.log(`✅ Listed ${allOrders.length} orders\n`);

  // Test filtering
  console.log("🔍 Test 5: Filter Orders by Status");
  store.update(order2.id, { status: "preparing" });
  const confirmedOrders = store.list({ status: "confirmed" });
  const preparingOrders = store.list({ status: "preparing" });
  assert(confirmedOrders.length === 1, "Should have 1 confirmed order");
  assert(preparingOrders.length === 1, "Should have 1 preparing order");
  console.log(`✅ Filtered confirmed: ${confirmedOrders.length}`);
  console.log(`   Filtered preparing: ${preparingOrders.length}\n`);

  // ============================================================================
  // Test 6: Count and Exists
  // ============================================================================
  console.log("🔢 Test 6: Count and Exists");
  const count = store.count();
  assert(count === 2, "Should have 2 orders in total");
  assert(store.exists(order.id), "Order should exist");
  assert(!store.exists("invalid-id"), "Invalid order should not exist");
  console.log(`✅ Total count: ${count}`);
  console.log(`   Order ${order.id} exists: true\n`);

  // ============================================================================
  // Test 7: Delete Order
  // ============================================================================
  console.log("🗑️  Test 7: Delete Order");
  const deleted = store.delete(order.id);
  assert(deleted === true, "Delete should return true");
  assert(!store.exists(order.id), "Deleted order should not exist");
  assert(store.count() === 1, "Count should be reduced");
  console.log("✅ Order deleted successfully");
  console.log(`   Remaining orders: ${store.count()}\n`);

  // ============================================================================
  // Test 8: Clear Store
  // ============================================================================
  console.log("🧹 Test 8: Clear Store");
  const cleared = store.clear();
  assert(cleared === 1, "Should clear 1 order");
  assert(store.count() === 0, "Store should be empty");
  console.log(`✅ Cleared ${cleared} order(s)`);
  console.log(`   Final count: ${store.count()}\n`);

  // ============================================================================
  // Test 9: Error Handling
  // ============================================================================
  console.log("⚠️  Test 9: Error Handling");
  try {
    store.update("non-existent-id", { status: "confirmed" });
    assert(false, "Should throw error for non-existent order");
  } catch (error) {
    assert(
      error instanceof Error && error.message.includes("not found"),
      "Should throw 'not found' error",
    );
    console.log("✅ Error handling works correctly\n");
  }

  // ============================================================================
  // Test 10: Persistence
  // ============================================================================
  console.log("💾 Test 10: Persistence - Save and Load");

  // Create some orders in the current store
  const persistOrder1 = store.create(customer, [{ menuItem: menuItem1, quantity: 1 }]);
  const persistOrder2 = store.create(customer, [{ menuItem: menuItem2, quantity: 2 }]);
  store.update(persistOrder1.id, { status: "confirmed" });

  assert(store.count() === 2, "Should have 2 orders before reload");

  // Create a new store instance with the same file path
  // This will trigger load() in the constructor
  const newStore = new OrderStore(TEST_FILE);

  assert(newStore.count() === 2, "Should have 2 orders after reload");
  assert(newStore.exists(persistOrder1.id), "Order 1 should exist after reload");
  assert(newStore.exists(persistOrder2.id), "Order 2 should exist after reload");

  const loadedOrder1 = newStore.read(persistOrder1.id);
  assert(loadedOrder1?.status === "confirmed", "Order 1 status should be confirmed");
  assert(loadedOrder1?.customerId === customer.id, "Order 1 customer should match");

  console.log("✅ Persistence works correctly");
  console.log(`   Loaded ${newStore.count()} orders from disk\n`);

  console.log("🎉 All tests passed!\n");

  // Clean up test file
  if (existsSync(TEST_FILE)) {
    unlinkSync(TEST_FILE);
  }
}

// Run tests
if (import.meta.main) {
  try {
    await testOrderStore();
    process.exit(0);
  } catch (error) {
    console.error("❌ Test failed:", error);
    // Clean up test file on error
    if (existsSync(TEST_FILE)) {
      unlinkSync(TEST_FILE);
    }
    process.exit(1);
  }
}
