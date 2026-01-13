import { z } from "zod";

// ============================================================================
// Zod Schemas (Runtime Validation)
// ============================================================================

export const MenuItemSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  price: z.number().positive(),
  description: z.string(),
});

export const CustomerSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  phone: z.string().regex(/^\+?[\d\s-()]+$/, "Invalid phone number"),
  address: z.string().min(1),
});

export const DeliveryDriverSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  status: z.enum(["available", "busy", "offline"]),
});

export const OrderStatusSchema = z.enum([
  "pending",
  "confirmed",
  "preparing",
  "ready",
  "out_for_delivery",
  "delivered",
  "cancelled",
]);

export const OrderItemSchema = z.object({
  menuItemId: z.string(),
  quantity: z.number().int().positive(),
  menuItemSnapshot: MenuItemSchema,
});

export const OrderSchema = z.object({
  id: z.string(),
  customerId: z.string(),
  customerSnapshot: CustomerSchema,
  items: z.array(OrderItemSchema).min(1),
  status: OrderStatusSchema,
  assignedDriverId: z.string().optional(),
  totalAmount: z.number().positive(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  notes: z.string().optional(),
});

// ============================================================================
// TypeScript Types (Static Typing)
// ============================================================================

export type MenuItem = z.infer<typeof MenuItemSchema>;
export type Customer = z.infer<typeof CustomerSchema>;
export type DeliveryDriver = z.infer<typeof DeliveryDriverSchema>;
export type OrderStatus = z.infer<typeof OrderStatusSchema>;
export type OrderItem = z.infer<typeof OrderItemSchema>;
export type Order = z.infer<typeof OrderSchema>;

// ============================================================================
// Validation Helpers
// ============================================================================

export function validateMenuItem(data: unknown): MenuItem {
  return MenuItemSchema.parse(data);
}

export function validateCustomer(data: unknown): Customer {
  return CustomerSchema.parse(data);
}

export function validateDeliveryDriver(data: unknown): DeliveryDriver {
  return DeliveryDriverSchema.parse(data);
}

export function validateOrder(data: unknown): Order {
  return OrderSchema.parse(data);
}

// ============================================================================
// Factory Functions
// ============================================================================

export function createMenuItem(
  name: string,
  price: number,
  description: string,
): MenuItem {
  const id = `menu-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  return validateMenuItem({ id, name, price, description });
}

export function createCustomer(
  name: string,
  phone: string,
  address: string,
): Customer {
  const id = `cust-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  return validateCustomer({ id, name, phone, address });
}

export function createDeliveryDriver(
  name: string,
  status: "available" | "busy" | "offline" = "available",
): DeliveryDriver {
  const id = `drv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  return validateDeliveryDriver({ id, name, status });
}

export function createOrder(
  customer: Customer,
  items: Array<{ menuItem: MenuItem; quantity: number }>,
  notes?: string,
): Order {
  const id = `ord-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  const timestamp = new Date().toISOString();

  const orderItems: OrderItem[] = items.map((item) => ({
    menuItemId: item.menuItem.id,
    quantity: item.quantity,
    menuItemSnapshot: item.menuItem,
  }));

  const totalAmount = orderItems.reduce(
    (sum, item) => sum + item.menuItemSnapshot.price * item.quantity,
    0,
  );

  return validateOrder({
    id,
    customerId: customer.id,
    customerSnapshot: customer,
    items: orderItems,
    status: "pending",
    totalAmount,
    createdAt: timestamp,
    updatedAt: timestamp,
    notes,
  });
}
