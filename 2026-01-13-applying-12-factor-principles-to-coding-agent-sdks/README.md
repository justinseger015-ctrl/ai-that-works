# 🌯 BurritoOps

A **SaaS platform for burrito delivery operators** built with AI agents, following 12-Factor App principles.

BurritoOps demonstrates how to build production-grade AI agent systems with:
- **Structured outputs** using Zod schemas
- **State persistence** via JSON logs
- **Modular agent workflows** for complex operations
- **Event-driven architecture** with comprehensive logging

## 🏗️ Architecture

BurritoOps follows a clean, modular architecture:

```
src/
├── models/
│   └── types.ts              # Zod schemas and TypeScript types
├── store/
│   ├── order-store.ts        # Order CRUD with persistence
│   └── driver-store.ts       # Driver CRUD with persistence
├── order-agent.ts            # Interactive order management
├── assignment-workflow.ts    # AI-powered order assignment
├── delivery-tracking-agent.ts # Automated delivery tracking
└── dashboard-agent.ts        # Analytics and insights
```

## 🎯 12-Factor App Principles

BurritoOps demonstrates key 12-factor principles:

### 1. **Codebase**: Single codebase tracked in git
- All code in one repository
- Shared dependencies across agents

### 2. **Dependencies**: Explicit dependency declaration
- Using `package.json` and Bun
- No implicit system dependencies
- All deps installable via `bun install`

### 3. **Config**: Store config in environment
- API keys via environment variables
- No hardcoded secrets in code

### 4. **Backing Services**: Treat backing services as attached resources
- JSON file storage for persistence
- Easy to swap for database later
- Clean abstractions (OrderStore, DriverStore)

### 5. **Build, Release, Run**: Strict separation
- TypeScript compilation separate from runtime
- Clear npm scripts for different modes

### 6. **Processes**: Execute as stateless processes
- Each agent run is independent
- State stored externally in JSON files
- Agents load state on startup

### 7. **Port Binding**: Export services via port binding
- CLI agents can be wrapped as HTTP services
- Self-contained execution model

### 8. **Concurrency**: Scale out via process model
- Multiple agents can run concurrently
- Each agent is independent
- Shared state via file system (or DB in production)

### 9. **Disposability**: Fast startup and graceful shutdown
- Agents start in milliseconds
- Clean shutdown handling
- Persisted state survives restarts

### 10. **Dev/Prod Parity**: Keep development and production similar
- Same tools in dev and prod
- JSON files work everywhere
- Easy to migrate to production DB

### 11. **Logs**: Treat logs as event streams
- JSONL format for structured logging
- All events timestamped
- Easy to aggregate and analyze

### 12. **Admin Processes**: Run admin tasks as one-off processes
- Dashboard agent for analytics
- Demo script for seeding data
- Each task is a separate process

## 🚀 Getting Started

### Prerequisites

- [Bun](https://bun.sh) runtime installed
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd burritoops

# Install dependencies
bun install

# Set up environment variables
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Quick Start

Run the demo to see all features:

```bash
bun run demo
```

## 📚 Usage Guide

### 1. Order Management Agent

Interactive CLI for creating and managing orders:

```bash
bun run orders
```

**Commands:**
- Create orders with customer info and items
- List all orders or filter by status
- View detailed order information
- Update order status
- Interactive AI-powered interface

**Example:**
```
> Create an order for John Doe at 123 Main St, phone 555-1234.
  He wants 2 carnitas burritos at $12 each and 1 chips at $4.
```

### 2. Order Assignment Workflow

AI-powered automatic assignment of orders to available drivers:

```bash
bun run assign
```

**Features:**
- Scans for pending orders
- Finds available drivers
- Intelligently assigns orders
- Updates driver status to "busy"
- Logs all assignments

**Output:**
- JSON workflow state in `logs/`
- JSONL event stream
- Console output of assignments

### 3. Delivery Tracking Agent

Automatically tracks and progresses orders through delivery stages:

```bash
bun run track
```

**Delivery Flow:**
```
pending → confirmed → preparing → ready → out_for_delivery → delivered
```

**Features:**
- Simulates realistic delivery timing (10-30 min per stage)
- Sends notifications (logged to JSONL)
- Updates order status automatically
- Marks drivers as available when delivery completes

### 4. Dashboard Agent

Real-time analytics and system insights:

```bash
bun run dashboard
```

**Metrics:**
- Total orders and revenue
- Orders by status breakdown
- Driver availability stats
- Orders per driver
- Revenue per driver
- Driver utilization rate
- AI-generated insights and recommendations

**Output:**
- Console: Conversational overview and metrics
- `logs/dashboard-snapshot-*.json`: Full metrics
- `logs/dashboard-events-*.jsonl`: Event stream

## 🔧 API Reference

### Data Models

All models defined in `src/models/types.ts`:

#### Order
```typescript
{
  id: string;
  customerId: string;
  customerSnapshot: Customer;
  items: OrderItem[];
  status: "pending" | "confirmed" | "preparing" | "ready" |
          "out_for_delivery" | "delivered" | "cancelled";
  assignedDriverId?: string;
  totalAmount: number;
  createdAt: string;  // ISO 8601
  updatedAt: string;  // ISO 8601
  notes?: string;
}
```

#### Customer
```typescript
{
  id: string;
  name: string;
  phone: string;  // Format: +1-234-567-8900
  address: string;
}
```

#### DeliveryDriver
```typescript
{
  id: string;
  name: string;
  status: "available" | "busy" | "offline";
}
```

#### MenuItem
```typescript
{
  id: string;
  name: string;
  price: number;  // Positive number
  description: string;
}
```

### Store APIs

#### OrderStore

```typescript
// Create a new order
orderStore.create(order: Order): Order

// Get order by ID
orderStore.read(id: string): Order | null

// Update existing order
orderStore.update(id: string, updates: Partial<Order>): Order

// Delete order
orderStore.delete(id: string): boolean

// List all orders with optional filter
orderStore.list(filter?: {
  status?: OrderStatus;
  customerId?: string;
}): Order[]

// Clear all orders
orderStore.clear(): void
```

#### DriverStore

```typescript
// Create a new driver
driverStore.create(driver: DeliveryDriver): DeliveryDriver

// Get driver by ID
driverStore.read(id: string): DeliveryDriver | null

// Update existing driver
driverStore.update(id: string, updates: Partial<DeliveryDriver>): DeliveryDriver

// Delete driver
driverStore.delete(id: string): boolean

// List all drivers with optional filter
driverStore.list(filter?: { status?: DriverStatus }): DeliveryDriver[]

// Clear all drivers
driverStore.clear(): void
```

### Factory Functions

Helper functions to create valid entities:

```typescript
import { createCustomer, createMenuItem, createOrder, createDeliveryDriver } from "./models/types";

// Create customer
const customer = createCustomer("John Doe", "+1-555-1234", "123 Main St");

// Create menu item
const burrito = createMenuItem("Carnitas Burrito", 12.00, "Slow-cooked pork");

// Create order
const order = createOrder(
  customer,
  [{ menuItem: burrito, quantity: 2 }],
  "Extra guacamole"
);

// Create driver
const driver = createDeliveryDriver("Maria Garcia", "available");
```

## 🧪 Testing

### Run All Tests

```bash
bun test
```

### Test Coverage

- **OrderStore**: 10 tests covering CRUD, filtering, persistence
- **DriverStore**: 22 tests covering CRUD, status filtering, persistence
- All tests verify Zod schema validation
- Persistence tests verify JSON save/load

### Test Files

- `src/store/order-store.test.ts`
- `src/store/driver-store.test.ts`

## 📊 Data Persistence

### Storage Location

All data stored in `data/` directory:
- `data/orders.json` - Order state
- `data/drivers.json` - Driver state

### Event Logs

All agent activity logged to `logs/` directory:
- `logs/order-agent-*.jsonl` - Order agent events
- `logs/workflow-*.json` - Assignment workflow state
- `logs/dashboard-*.json` - Dashboard snapshots
- `logs/dashboard-events-*.jsonl` - Dashboard events
- `logs/events-*.jsonl` - General events

### Log Format

All logs use JSONL (JSON Lines) format:
```jsonl
{"type":"user","timestamp":"2026-01-13T12:00:00Z","text":"Create an order"}
{"type":"assistant","timestamp":"2026-01-13T12:00:01Z","text":"I'll create that order"}
```

Snapshots use single-line JSON:
```json
{"timestamp":"2026-01-13T12:00:00Z","orders":5,"revenue":125.50}
```

## 🔄 Complete Workflow Example

Here's how a typical order flows through the system:

```bash
# 1. Create an order
bun run orders
> "Create an order for Alice at 456 Oak Ave, phone 555-5678.
   She wants 1 veggie burrito at $10."

# 2. Assign to a driver
bun run assign
# Output: Order ord-xxx assigned to driver Maria Garcia

# 3. Track delivery
bun run track
# Output: Order progressing through stages automatically

# 4. View metrics
bun run dashboard
# Output: System overview with insights
```

## 🛠️ Development

### Project Structure

```
├── src/
│   ├── models/types.ts          # Core data models
│   ├── store/                   # Data persistence layer
│   ├── order-agent.ts           # Order management CLI
│   ├── assignment-workflow.ts   # Assignment automation
│   ├── delivery-tracking-agent.ts # Tracking automation
│   ├── dashboard-agent.ts       # Analytics
│   └── utils.ts                 # Shared utilities
├── data/                        # Persisted state (JSON)
├── logs/                        # Event logs (JSONL)
├── baml_src/                    # BAML configuration
└── tests/                       # Test files
```

### Adding New Features

1. **Define models** in `src/models/types.ts`
   - Create Zod schema
   - Export TypeScript type
   - Add validation helper

2. **Create store** if needed
   - Implement CRUD operations
   - Add persistence
   - Write tests

3. **Build agent** following patterns
   - Use structured outputs with Zod
   - Log events to JSONL
   - Handle errors gracefully

4. **Add npm script** in `package.json`

### Code Style

- TypeScript with strict mode
- Zod for runtime validation
- Functional programming patterns
- Clear separation of concerns
- Comprehensive error handling

## 🎬 Demo Script

Run the full demo to see all features:

```bash
bun run demo
```

The demo:
1. Creates sample menu items
2. Creates sample drivers
3. Creates sample orders
4. Assigns orders to drivers
5. Tracks delivery progress
6. Shows dashboard analytics

## 📝 Notes

### Why JSON Files?

JSON files provide:
- **Simplicity**: Easy to inspect and debug
- **Portability**: Works everywhere
- **Version control friendly**: Can track changes in git
- **Easy migration**: Simple to move to a database later

### Production Considerations

For production deployment, consider:
- Replace JSON files with PostgreSQL/MongoDB
- Add API layer (REST/GraphQL)
- Implement authentication/authorization
- Add rate limiting and caching
- Deploy with Docker/Kubernetes
- Use proper secret management

### Scaling

Current architecture supports:
- Multiple agent processes reading same state
- File-based locking for writes
- Easy migration to database for true concurrency

## 🤝 Contributing

1. Follow the Ralph Wiggum Loop Pattern
2. One task per commit
3. Ensure all tests pass
4. Update IMPLEMENTATION_PLAN.md
5. Follow existing code style

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built as a demonstration of:
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
- [12-Factor App](https://12factor.net/) principles
- [BAML](https://www.boundaryml.com/) for structured outputs
- [Zod](https://zod.dev/) for schema validation

---

**Built with ❤️ and 🌯 by the BurritoOps team**
