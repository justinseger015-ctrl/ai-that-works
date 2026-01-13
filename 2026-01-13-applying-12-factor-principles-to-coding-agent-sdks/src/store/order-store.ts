import { z } from "zod";
import {
  Order,
  OrderSchema,
  OrderStatus,
  Customer,
  MenuItem,
  createOrder,
} from "../models/types";

// ============================================================================
// Order Store - In-Memory Implementation
// ============================================================================

/**
 * In-memory order store using Map for efficient CRUD operations.
 * Follows 12-factor app principles with validation at boundaries.
 */
export class OrderStore {
  private orders: Map<string, Order>;

  constructor() {
    this.orders = new Map();
  }

  /**
   * Create a new order
   * @param customer - Customer placing the order
   * @param items - Array of menu items with quantities
   * @param notes - Optional notes for the order
   * @returns The created order
   * @throws Error if validation fails
   */
  create(
    customer: Customer,
    items: Array<{ menuItem: MenuItem; quantity: number }>,
    notes?: string,
  ): Order {
    const order = createOrder(customer, items, notes);
    this.orders.set(order.id, order);
    return order;
  }

  /**
   * Read an order by ID
   * @param id - Order ID
   * @returns The order if found, undefined otherwise
   */
  read(id: string): Order | undefined {
    return this.orders.get(id);
  }

  /**
   * Update an existing order
   * @param id - Order ID
   * @param updates - Partial order updates (status, notes, assignedDriverId)
   * @returns The updated order
   * @throws Error if order not found or validation fails
   */
  update(
    id: string,
    updates: {
      status?: OrderStatus;
      notes?: string;
      assignedDriverId?: string;
    },
  ): Order {
    const existing = this.orders.get(id);
    if (!existing) {
      throw new Error(`Order not found: ${id}`);
    }

    const updated: Order = {
      ...existing,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    // Validate the updated order
    const validated = OrderSchema.parse(updated);
    this.orders.set(id, validated);
    return validated;
  }

  /**
   * Delete an order by ID
   * @param id - Order ID
   * @returns true if deleted, false if not found
   */
  delete(id: string): boolean {
    return this.orders.delete(id);
  }

  /**
   * List all orders with optional filtering
   * @param filter - Optional filter criteria
   * @returns Array of orders matching the filter
   */
  list(filter?: {
    status?: OrderStatus;
    customerId?: string;
    assignedDriverId?: string;
  }): Order[] {
    let orders = Array.from(this.orders.values());

    if (filter) {
      if (filter.status) {
        orders = orders.filter((o) => o.status === filter.status);
      }
      if (filter.customerId) {
        orders = orders.filter((o) => o.customerId === filter.customerId);
      }
      if (filter.assignedDriverId) {
        orders = orders.filter(
          (o) => o.assignedDriverId === filter.assignedDriverId,
        );
      }
    }

    // Sort by creation time (newest first)
    return orders.sort(
      (a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    );
  }

  /**
   * Get the total count of orders
   * @returns Total number of orders in the store
   */
  count(): number {
    return this.orders.size;
  }

  /**
   * Clear all orders (useful for testing)
   * @returns Number of orders cleared
   */
  clear(): number {
    const count = this.orders.size;
    this.orders.clear();
    return count;
  }

  /**
   * Check if an order exists
   * @param id - Order ID
   * @returns true if order exists, false otherwise
   */
  exists(id: string): boolean {
    return this.orders.has(id);
  }
}

// ============================================================================
// Singleton Instance (for convenience)
// ============================================================================

export const orderStore = new OrderStore();
