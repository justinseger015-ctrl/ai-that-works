/**
 * BurritoOps Demo Script
 *
 * This script demonstrates all features of the BurritoOps platform:
 * 1. Data seeding (menu items, drivers, orders)
 * 2. Order assignment workflow
 * 3. Delivery tracking simulation
 * 4. Dashboard analytics
 *
 * Run with: bun run demo
 */

import { existsSync, mkdirSync } from "node:fs";
import { orderStore } from "./store/order-store";
import { driverStore } from "./store/driver-store";
import {
  createMenuItem,
  createCustomer,
  type MenuItem,
} from "./models/types";
import {
  BLUE,
  GREEN,
  YELLOW,
  CYAN,
  RESET,
} from "./utils";

// Additional colors not in utils
const RED = "\x1b[31m";
const BOLD = "\x1b[1m";

// ============================================================================
// Demo Configuration
// ============================================================================

const DEMO_CONFIG = {
  numDrivers: 5,
  numOrders: 8,
  clearExistingData: true,
};

// ============================================================================
// Utility Functions
// ============================================================================

function section(title: string) {
  console.log("\n" + "=".repeat(80));
  console.log(`${BOLD}${BLUE}${title}${RESET}`);
  console.log("=".repeat(80) + "\n");
}

function subsection(title: string) {
  console.log(`\n${CYAN}▸ ${title}${RESET}`);
}

function success(message: string) {
  console.log(`${GREEN}✓${RESET} ${message}`);
}

function info(message: string) {
  console.log(`${BLUE}ℹ${RESET} ${message}`);
}

function warning(message: string) {
  console.log(`${YELLOW}⚠${RESET} ${message}`);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ============================================================================
// Sample Data
// ============================================================================

const MENU_ITEMS = [
  { name: "Carnitas Burrito", price: 12.0, description: "Slow-cooked pork with rice, beans, and salsa" },
  { name: "Veggie Burrito", price: 10.0, description: "Grilled vegetables with black beans and guacamole" },
  { name: "Chicken Burrito", price: 11.0, description: "Grilled chicken with cilantro-lime rice" },
  { name: "Steak Burrito", price: 13.0, description: "Grilled steak with peppers and onions" },
  { name: "Chips & Guac", price: 4.0, description: "Fresh tortilla chips with house-made guacamole" },
  { name: "Chips & Salsa", price: 3.0, description: "Fresh tortilla chips with pico de gallo" },
  { name: "Quesadilla", price: 8.0, description: "Cheese quesadilla with sour cream" },
  { name: "Churros", price: 5.0, description: "Cinnamon sugar churros with chocolate sauce" },
];

const DRIVER_NAMES = [
  "Maria Garcia",
  "James Chen",
  "Fatima Hassan",
  "Carlos Rodriguez",
  "Aisha Patel",
  "Mike O'Brien",
  "Yuki Tanaka",
  "Sofia Müller",
];

const SAMPLE_CUSTOMERS = [
  { name: "Alice Johnson", phone: "+1-555-0101", address: "123 Oak Street, Suite 4B" },
  { name: "Bob Smith", phone: "+1-555-0102", address: "456 Maple Avenue" },
  { name: "Carol White", phone: "+1-555-0103", address: "789 Pine Road, Apt 12" },
  { name: "David Brown", phone: "+1-555-0104", address: "321 Elm Drive" },
  { name: "Eve Davis", phone: "+1-555-0105", address: "654 Cedar Lane" },
  { name: "Frank Miller", phone: "+1-555-0106", address: "987 Birch Court" },
  { name: "Grace Lee", phone: "+1-555-0107", address: "147 Willow Way" },
  { name: "Henry Wilson", phone: "+1-555-0108", address: "258 Ash Boulevard" },
  { name: "Iris Taylor", phone: "+1-555-0109", address: "369 Spruce Street" },
  { name: "Jack Anderson", phone: "+1-555-0110", address: "741 Redwood Place" },
];

// ============================================================================
// Seeding Functions
// ============================================================================

function seedMenuItems(): MenuItem[] {
  subsection("Creating Menu Items");
  const menuItems: MenuItem[] = [];

  for (const item of MENU_ITEMS) {
    const menuItem = createMenuItem(item.name, item.price, item.description);
    menuItems.push(menuItem);
    success(`Created: ${item.name} - $${item.price.toFixed(2)}`);
  }

  return menuItems;
}

function seedDrivers() {
  subsection("Creating Drivers");
  const drivers = [];

  for (let i = 0; i < DEMO_CONFIG.numDrivers; i++) {
    const name = DRIVER_NAMES[i % DRIVER_NAMES.length];
    const status = i < 3 ? "available" : i < 5 ? "busy" : "offline";
    const driver = driverStore.create(name, status as "available" | "busy" | "offline");
    drivers.push(driver);

    const statusColor = status === "available" ? GREEN : status === "busy" ? YELLOW : RED;
    success(`Created: ${name} - ${statusColor}${status}${RESET}`);
  }

  return drivers;
}

function seedOrders(menuItems: MenuItem[]) {
  subsection("Creating Orders");
  const orders = [];

  for (let i = 0; i < DEMO_CONFIG.numOrders; i++) {
    const customerData = SAMPLE_CUSTOMERS[i % SAMPLE_CUSTOMERS.length];
    const customer = createCustomer(
      customerData.name,
      customerData.phone,
      customerData.address
    );

    // Create order with 1-3 random items
    const numItems = Math.floor(Math.random() * 3) + 1;
    const orderItems = [];

    for (let j = 0; j < numItems; j++) {
      const menuItem = menuItems[Math.floor(Math.random() * menuItems.length)];
      const quantity = Math.floor(Math.random() * 2) + 1;
      orderItems.push({ menuItem, quantity });
    }

    const notes = i % 3 === 0 ? "Extra napkins please" : undefined;
    const order = orderStore.create(customer, orderItems, notes);

    // Vary order statuses
    let updatedOrder = order;
    if (i < 2) {
      // Keep as pending
    } else if (i < 4) {
      updatedOrder = orderStore.update(order.id, { status: "confirmed" });
    } else if (i < 6) {
      updatedOrder = orderStore.update(order.id, { status: "preparing" });
    } else {
      updatedOrder = orderStore.update(order.id, { status: "ready" });
    }

    orders.push(updatedOrder);

    const itemsSummary = orderItems
      .map((item) => `${item.quantity}x ${item.menuItem.name}`)
      .join(", ");
    success(
      `Created: Order for ${customer.name} - ${itemsSummary} - $${updatedOrder.totalAmount.toFixed(2)} [${updatedOrder.status}]`
    );
  }

  return orders;
}

// ============================================================================
// Demo Stages
// ============================================================================

async function stageSystemOverview() {
  section("🌯 BurritoOps Demo - System Overview");

  info("BurritoOps is a SaaS platform for burrito delivery operators");
  info("Built with AI agents following 12-Factor App principles");

  console.log("\n" + "Features:".padEnd(40, " "));
  console.log("  • Interactive order management");
  console.log("  • AI-powered order assignment");
  console.log("  • Automated delivery tracking");
  console.log("  • Real-time analytics dashboard");

  console.log("\n" + "Architecture:".padEnd(40, " "));
  console.log("  • Modular agent workflows");
  console.log("  • Structured outputs with Zod schemas");
  console.log("  • JSON-based state persistence");
  console.log("  • JSONL event logging");

  await sleep(2000);
}

async function stageDataSeeding() {
  section("📊 Stage 1: Data Seeding");

  if (DEMO_CONFIG.clearExistingData) {
    subsection("Clearing Existing Data");
    orderStore.clear();
    driverStore.clear();
    success("Cleared all existing orders and drivers");
  }

  // Ensure data directory exists
  if (!existsSync("data")) {
    mkdirSync("data", { recursive: true });
  }

  const menuItems = seedMenuItems();
  await sleep(1000);

  seedDrivers();
  await sleep(1000);

  seedOrders(menuItems);
  await sleep(1000);

  subsection("Seeding Complete");
  const allOrders = orderStore.list();
  const allDrivers = driverStore.list();
  success(`Created ${allOrders.length} orders and ${allDrivers.length} drivers`);
}

async function stageCurrentState() {
  section("📋 Stage 2: Current System State");

  const allOrders = orderStore.list();
  const allDrivers = driverStore.list();

  subsection("Order Status Breakdown");
  const statusCounts = new Map<string, number>();
  for (const order of allOrders) {
    statusCounts.set(order.status, (statusCounts.get(order.status) || 0) + 1);
  }

  for (const [status, count] of statusCounts.entries()) {
    const color =
      status === "pending" ? YELLOW :
      status === "delivered" ? GREEN :
      CYAN;
    console.log(`  ${color}${status.padEnd(20)}${RESET}: ${count} orders`);
  }

  subsection("Driver Status Breakdown");
  const driverStatusCounts = new Map<string, number>();
  for (const driver of allDrivers) {
    driverStatusCounts.set(driver.status, (driverStatusCounts.get(driver.status) || 0) + 1);
  }

  for (const [status, count] of driverStatusCounts.entries()) {
    const color =
      status === "available" ? GREEN :
      status === "busy" ? YELLOW :
      RED;
    console.log(`  ${color}${status.padEnd(20)}${RESET}: ${count} drivers`);
  }

  const totalRevenue = allOrders.reduce((sum, order) => sum + order.totalAmount, 0);
  subsection("Revenue");
  console.log(`  Total: ${GREEN}$${totalRevenue.toFixed(2)}${RESET}`);

  await sleep(2000);
}

async function stageNextSteps() {
  section("🚀 Next Steps");

  console.log("Try these commands to interact with the system:\n");

  console.log(`${BOLD}${GREEN}Order Management:${RESET}`);
  console.log(`  ${CYAN}bun run orders${RESET}       - Interactive order management CLI`);
  console.log("                          Create, list, update, and view orders\n");

  console.log(`${BOLD}${GREEN}Automation:${RESET}`);
  console.log(`  ${CYAN}bun run assign${RESET}       - Run order assignment workflow`);
  console.log("                          AI assigns pending orders to available drivers");
  console.log(`  ${CYAN}bun run track${RESET}        - Run delivery tracking agent`);
  console.log("                          AI tracks and progresses active deliveries\n");

  console.log(`${BOLD}${GREEN}Analytics:${RESET}`);
  console.log(`  ${CYAN}bun run dashboard${RESET}    - View system analytics and insights`);
  console.log("                          AI-generated metrics and recommendations\n");

  console.log(`${BOLD}${GREEN}Testing:${RESET}`);
  console.log(`  ${CYAN}bun test${RESET}             - Run all tests`);
  console.log("                          Verify OrderStore and DriverStore functionality\n");

  info("All data persisted to:");
  console.log(`  • ${CYAN}data/orders.json${RESET}  - Order state`);
  console.log(`  • ${CYAN}data/drivers.json${RESET} - Driver state`);
  console.log(`  • ${CYAN}logs/*.jsonl${RESET}      - Event logs`);
}

// ============================================================================
// Main Demo Execution
// ============================================================================

async function main() {
  console.clear();

  try {
    await stageSystemOverview();
    await stageDataSeeding();
    await stageCurrentState();
    await stageNextSteps();

    section("✅ Demo Complete");
    success("Sample data has been created and persisted");
    success("System is ready for interaction");

  } catch (error) {
    console.error(`\n${RED}Demo failed:${RESET}`, error);
    process.exit(1);
  }
}

// Run the demo
main();
