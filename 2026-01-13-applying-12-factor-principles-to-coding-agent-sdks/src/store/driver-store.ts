import { z } from "zod";
import {
  DeliveryDriver,
  DeliveryDriverSchema,
  createDeliveryDriver,
} from "../models/types";

// ============================================================================
// Driver Store - In-Memory Implementation
// ============================================================================

/**
 * In-memory driver store using Map for efficient CRUD operations.
 * Follows 12-factor app principles with validation at boundaries.
 */
export class DriverStore {
  private drivers: Map<string, DeliveryDriver>;

  constructor() {
    this.drivers = new Map();
  }

  /**
   * Create a new driver
   * @param name - Driver's name
   * @param status - Initial status (defaults to "available")
   * @returns The created driver
   * @throws Error if validation fails
   */
  create(
    name: string,
    status: "available" | "busy" | "offline" = "available",
  ): DeliveryDriver {
    const driver = createDeliveryDriver(name, status);
    this.drivers.set(driver.id, driver);
    return driver;
  }

  /**
   * Read a driver by ID
   * @param id - Driver ID
   * @returns The driver if found, undefined otherwise
   */
  read(id: string): DeliveryDriver | undefined {
    return this.drivers.get(id);
  }

  /**
   * Update an existing driver
   * @param id - Driver ID
   * @param updates - Partial driver updates (status, name)
   * @returns The updated driver
   * @throws Error if driver not found or validation fails
   */
  update(
    id: string,
    updates: {
      name?: string;
      status?: "available" | "busy" | "offline";
    },
  ): DeliveryDriver {
    const existing = this.drivers.get(id);
    if (!existing) {
      throw new Error(`Driver not found: ${id}`);
    }

    const updated: DeliveryDriver = {
      ...existing,
      ...updates,
    };

    // Validate the updated driver
    const validated = DeliveryDriverSchema.parse(updated);
    this.drivers.set(id, validated);
    return validated;
  }

  /**
   * Delete a driver by ID
   * @param id - Driver ID
   * @returns true if deleted, false if not found
   */
  delete(id: string): boolean {
    return this.drivers.delete(id);
  }

  /**
   * List all drivers with optional filtering
   * @param filter - Optional filter criteria
   * @returns Array of drivers matching the filter
   */
  list(filter?: { status?: "available" | "busy" | "offline" }): DeliveryDriver[] {
    let drivers = Array.from(this.drivers.values());

    if (filter?.status) {
      drivers = drivers.filter((d) => d.status === filter.status);
    }

    // Sort by name for consistent ordering
    return drivers.sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Get the total count of drivers
   * @returns Total number of drivers in the store
   */
  count(): number {
    return this.drivers.size;
  }

  /**
   * Clear all drivers (useful for testing)
   * @returns Number of drivers cleared
   */
  clear(): number {
    const count = this.drivers.size;
    this.drivers.clear();
    return count;
  }

  /**
   * Check if a driver exists
   * @param id - Driver ID
   * @returns true if driver exists, false otherwise
   */
  exists(id: string): boolean {
    return this.drivers.has(id);
  }

  /**
   * Get the first available driver
   * @returns First available driver, or undefined if none available
   */
  getFirstAvailable(): DeliveryDriver | undefined {
    return Array.from(this.drivers.values()).find(
      (d) => d.status === "available",
    );
  }
}

// ============================================================================
// Singleton Instance (for convenience)
// ============================================================================

export const driverStore = new DriverStore();
