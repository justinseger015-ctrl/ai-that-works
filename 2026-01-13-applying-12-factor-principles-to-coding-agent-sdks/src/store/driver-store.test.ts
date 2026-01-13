import { test, expect, beforeEach, afterEach } from "bun:test";
import { existsSync, unlinkSync } from "node:fs";
import { DriverStore } from "./driver-store";

const TEST_FILE = "data/drivers-test.json";
let store: DriverStore;

beforeEach(() => {
  // Remove test file if it exists
  if (existsSync(TEST_FILE)) {
    unlinkSync(TEST_FILE);
  }
  store = new DriverStore(TEST_FILE);
});

afterEach(() => {
  // Clean up test file
  if (existsSync(TEST_FILE)) {
    unlinkSync(TEST_FILE);
  }
});

// ============================================================================
// Create Tests
// ============================================================================

test("create: should create a driver with default available status", () => {
  const driver = store.create("John Doe");

  expect(driver).toBeDefined();
  expect(driver.id).toMatch(/^drv-/);
  expect(driver.name).toBe("John Doe");
  expect(driver.status).toBe("available");
});

test("create: should create a driver with specified status", () => {
  const driver = store.create("Jane Smith", "offline");

  expect(driver.status).toBe("offline");
});

test("create: should add driver to store", () => {
  const driver = store.create("Bob Johnson");

  expect(store.count()).toBe(1);
  expect(store.exists(driver.id)).toBe(true);
});

// ============================================================================
// Read Tests
// ============================================================================

test("read: should return driver by id", () => {
  const created = store.create("Alice Williams");
  const retrieved = store.read(created.id);

  expect(retrieved).toEqual(created);
});

test("read: should return undefined for non-existent driver", () => {
  const result = store.read("non-existent-id");

  expect(result).toBeUndefined();
});

// ============================================================================
// Update Tests
// ============================================================================

test("update: should update driver status", () => {
  const driver = store.create("Charlie Brown", "available");
  const updated = store.update(driver.id, { status: "busy" });

  expect(updated.status).toBe("busy");
  expect(updated.name).toBe("Charlie Brown");
});

test("update: should update driver name", () => {
  const driver = store.create("Old Name");
  const updated = store.update(driver.id, { name: "New Name" });

  expect(updated.name).toBe("New Name");
  expect(updated.status).toBe("available");
});

test("update: should throw error for non-existent driver", () => {
  expect(() => {
    store.update("non-existent-id", { status: "busy" });
  }).toThrow("Driver not found");
});

// ============================================================================
// Delete Tests
// ============================================================================

test("delete: should delete driver by id", () => {
  const driver = store.create("Delete Me");
  const deleted = store.delete(driver.id);

  expect(deleted).toBe(true);
  expect(store.exists(driver.id)).toBe(false);
  expect(store.count()).toBe(0);
});

test("delete: should return false for non-existent driver", () => {
  const deleted = store.delete("non-existent-id");

  expect(deleted).toBe(false);
});

// ============================================================================
// List Tests
// ============================================================================

test("list: should return all drivers", () => {
  store.create("Driver 1");
  store.create("Driver 2");
  store.create("Driver 3");

  const drivers = store.list();

  expect(drivers.length).toBe(3);
});

test("list: should filter drivers by status", () => {
  store.create("Available 1", "available");
  store.create("Busy 1", "busy");
  store.create("Available 2", "available");
  store.create("Offline 1", "offline");

  const available = store.list({ status: "available" });
  const busy = store.list({ status: "busy" });
  const offline = store.list({ status: "offline" });

  expect(available.length).toBe(2);
  expect(busy.length).toBe(1);
  expect(offline.length).toBe(1);
});

test("list: should return empty array when no drivers", () => {
  const drivers = store.list();

  expect(drivers.length).toBe(0);
});

test("list: should sort drivers by name", () => {
  store.create("Zoe");
  store.create("Alice");
  store.create("Mike");

  const drivers = store.list();

  expect(drivers[0].name).toBe("Alice");
  expect(drivers[1].name).toBe("Mike");
  expect(drivers[2].name).toBe("Zoe");
});

// ============================================================================
// getFirstAvailable Tests
// ============================================================================

test("getFirstAvailable: should return first available driver", () => {
  store.create("Busy Driver", "busy");
  const available1 = store.create("Available 1", "available");
  store.create("Available 2", "available");

  const result = store.getFirstAvailable();

  expect(result).toBeDefined();
  expect(result?.status).toBe("available");
});

test("getFirstAvailable: should return undefined when no available drivers", () => {
  store.create("Busy Driver", "busy");
  store.create("Offline Driver", "offline");

  const result = store.getFirstAvailable();

  expect(result).toBeUndefined();
});

test("getFirstAvailable: should return undefined when store is empty", () => {
  const result = store.getFirstAvailable();

  expect(result).toBeUndefined();
});

// ============================================================================
// Utility Tests
// ============================================================================

test("count: should return correct count", () => {
  expect(store.count()).toBe(0);

  store.create("Driver 1");
  expect(store.count()).toBe(1);

  store.create("Driver 2");
  expect(store.count()).toBe(2);
});

test("clear: should remove all drivers and return count", () => {
  store.create("Driver 1");
  store.create("Driver 2");
  store.create("Driver 3");

  const cleared = store.clear();

  expect(cleared).toBe(3);
  expect(store.count()).toBe(0);
});

test("exists: should return true for existing driver", () => {
  const driver = store.create("Exists");

  expect(store.exists(driver.id)).toBe(true);
});

test("exists: should return false for non-existent driver", () => {
  expect(store.exists("non-existent-id")).toBe(false);
});

// ============================================================================
// Persistence Tests
// ============================================================================

test("persistence: should save and load driver data", () => {
  // Create some drivers
  const driver1 = store.create("Alice", "available");
  const driver2 = store.create("Bob", "busy");
  const driver3 = store.create("Charlie", "offline");

  expect(store.count()).toBe(3);

  // Create a new store instance with the same file path
  // This will trigger load() in the constructor
  const newStore = new DriverStore(TEST_FILE);

  // Verify all data was loaded
  expect(newStore.count()).toBe(3);
  expect(newStore.exists(driver1.id)).toBe(true);
  expect(newStore.exists(driver2.id)).toBe(true);
  expect(newStore.exists(driver3.id)).toBe(true);

  // Verify driver details
  const loadedDriver1 = newStore.read(driver1.id);
  expect(loadedDriver1?.name).toBe("Alice");
  expect(loadedDriver1?.status).toBe("available");

  const loadedDriver2 = newStore.read(driver2.id);
  expect(loadedDriver2?.name).toBe("Bob");
  expect(loadedDriver2?.status).toBe("busy");
});
