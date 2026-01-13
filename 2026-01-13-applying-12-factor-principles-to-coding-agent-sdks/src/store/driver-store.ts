import { z } from "zod";
import { existsSync, writeFileSync, readFileSync, mkdirSync } from "node:fs";
import {
  DeliveryDriver,
  DeliveryDriverSchema,
  createDeliveryDriver,
} from "../models/types";

// ============================================================================
// Driver Store - Persistent Implementation
// ============================================================================

const DATA_DIR = "data";
const DEFAULT_DRIVERS_FILE = `${DATA_DIR}/drivers.json`;

// Ensure data directory exists
if (!existsSync(DATA_DIR)) {
  mkdirSync(DATA_DIR, { recursive: true });
}

/**
 * Persistent driver store using Map for efficient CRUD operations.
 * Automatically saves to and loads from JSON files.
 * Follows 12-factor app principles with validation at boundaries.
 */
export class DriverStore {
  private drivers: Map<string, DeliveryDriver>;
  private filePath: string;

  constructor(filePath: string = DEFAULT_DRIVERS_FILE) {
    this.drivers = new Map();
    this.filePath = filePath;
    this.load();
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
    this.save();
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
    this.save();
    return validated;
  }

  /**
   * Delete a driver by ID
   * @param id - Driver ID
   * @returns true if deleted, false if not found
   */
  delete(id: string): boolean {
    const result = this.drivers.delete(id);
    if (result) {
      this.save();
    }
    return result;
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
    this.save();
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

  /**
   * Save current state to JSON file
   * @returns true if saved successfully, false otherwise
   */
  save(): boolean {
    try {
      const drivers = Array.from(this.drivers.values());
      const data = {
        version: 1,
        timestamp: new Date().toISOString(),
        drivers,
      };
      writeFileSync(this.filePath, JSON.stringify(data, null, 2));
      return true;
    } catch (error) {
      console.error(`Failed to save drivers to ${this.filePath}:`, error);
      return false;
    }
  }

  /**
   * Load state from JSON file
   * If file doesn't exist or is invalid, starts with empty state
   * @returns Number of drivers loaded
   */
  load(): number {
    try {
      if (!existsSync(this.filePath)) {
        return 0;
      }

      const fileContent = readFileSync(this.filePath, "utf-8");
      const data = JSON.parse(fileContent);

      // Validate and load drivers
      if (data.drivers && Array.isArray(data.drivers)) {
        this.drivers.clear();
        for (const driver of data.drivers) {
          const validated = DeliveryDriverSchema.parse(driver);
          this.drivers.set(validated.id, validated);
        }
        return this.drivers.size;
      }

      return 0;
    } catch (error) {
      console.error(`Failed to load drivers from ${this.filePath}:`, error);
      return 0;
    }
  }
}

// ============================================================================
// Singleton Instance (for convenience)
// ============================================================================

export const driverStore = new DriverStore();
