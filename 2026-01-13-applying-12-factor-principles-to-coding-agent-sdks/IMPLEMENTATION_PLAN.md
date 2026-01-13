# BurritoOps Implementation Plan

## Overview
BurritoOps is a SaaS platform for burrito delivery operators. This plan follows the Ralph Wiggum Loop Pattern: one step per loop, verifiable milestones, exit and rerun.

## Project Status
- **Current Phase**: Phase 1 - Foundation
- **Last Updated**: 2026-01-13

## Architecture Principles (12-Factor)
- State persistence via JSON logs
- Structured outputs with Zod schemas
- Modular agent workflows
- Clear separation of concerns

## Implementation Phases

### Phase 1: Foundation & Data Models ✅ IN PROGRESS
**Goal**: Set up basic data structures and persistence

#### TASK 1: Create Order Management Data Model ✅ COMPLETED
**Priority**: HIGHEST
**Status**: Completed (2026-01-13)

**Requirements**:
- Define TypeScript interfaces for:
  - Order (id, customer, items, status, timestamps)
  - MenuItem (id, name, price, description)
  - Customer (id, name, phone, address)
  - DeliveryDriver (id, name, status)
- Create Zod schemas for validation
- Add file: `src/models/types.ts`

**Success Criteria**:
- [x] File `src/models/types.ts` exists with all types
- [x] All types have corresponding Zod schemas
- [x] TypeScript compilation passes: `bunx tsc --noEmit`
- [x] Code follows existing project patterns (see src/structured-planning-with-json.ts)

**Completed**: All data models created with Zod schemas, factory functions, and validation helpers. TypeScript compilation verified.

---

#### TASK 2: Create Order Store (In-Memory) ✅ COMPLETED
**Priority**: HIGHEST
**Status**: Completed (2026-01-13)
**Depends On**: TASK 1 ✅

**Requirements**:
- Implement CRUD operations for orders
- Use in-memory storage (Map-based)
- Add file: `src/store/order-store.ts`
- Include methods: create, read, update, delete, list

**Success Criteria**:
- [x] Order store implements all CRUD operations
- [x] Store uses Zod schemas for validation
- [x] TypeScript compilation passes
- [x] Basic unit tests pass (if added)

**Completed**: OrderStore class created with Map-based in-memory storage. All CRUD operations implemented (create, read, update, delete, list) with filtering support. Comprehensive test suite with 9 test cases covering all functionality including error handling. All tests pass successfully.

---

#### TASK 3: Create Order Management Agent ✅ COMPLETED
**Priority**: HIGH
**Status**: Completed (2026-01-13)
**Depends On**: TASK 2 ✅

**Requirements**:
- Interactive agent for managing orders
- Commands: create order, list orders, update status, view order details
- Use structured outputs pattern from structured-planning-with-json.ts
- Add file: `src/order-agent.ts`
- Add npm script: `"orders": "bun run src/order-agent.ts"`

**Success Criteria**:
- [x] Agent can create new orders via CLI
- [x] Agent can list existing orders
- [x] Agent can update order status
- [x] Follows existing agent patterns
- [x] Script runs: `bun run orders`

**Completed**: Interactive order management agent created with structured outputs pattern. Supports all CRUD operations (create, list, view, update). Includes proper error handling for closed input streams and graceful exit. Event logging to JSONL files. Command execution follows existing patterns from structured-planning-with-json.ts.

---

### Phase 2: Agent Workflows ✅ IN PROGRESS
**Goal**: Implement workflow automation

#### TASK 4: Create Order Assignment Workflow ✅ COMPLETED
**Priority**: HIGH
**Status**: Completed (2026-01-13)
**Depends On**: TASK 3 ✅

**Requirements**:
- Auto-assign orders to available drivers
- Use structured planning pattern
- Log state changes

**Success Criteria**:
- [x] Workflow automatically assigns pending orders to available drivers
- [x] Driver status updates correctly (available -> busy)
- [x] State changes are logged
- [x] Follows structured output patterns

**Completed**: Created DriverStore with CRUD operations and comprehensive tests (21 test cases). Implemented assignment-workflow.ts that uses AI to intelligently assign pending orders to available drivers. The workflow logs all state changes to JSON files, updates driver status from available to busy when assigned, and follows structured output patterns with Zod schemas. Added `bun run assign` npm script. All tests pass successfully.

---

#### TASK 5: Create Delivery Tracking Agent ✅ COMPLETED
**Priority**: MEDIUM
**Status**: Completed (2026-01-13)
**Depends On**: TASK 4 ✅

**Requirements**:
- Track delivery status
- Update order status automatically
- Send notifications (simulated)

**Success Criteria**:
- [x] Agent can track delivery progress
- [x] Order status updates automatically as delivery progresses
- [x] Simulated notifications are logged
- [x] Follows existing agent patterns

**Completed**: Created delivery-tracking-agent.ts that uses AI to intelligently track active orders (confirmed, preparing, ready, out_for_delivery) and automatically progress them through the delivery lifecycle. The agent:
- Tracks orders in active delivery states
- Uses structured outputs with Zod schemas (TrackingOutputSchema)
- Progresses orders through status flow: confirmed → preparing → ready → out_for_delivery → delivered
- Simulates realistic timing (10-30 minutes per stage)
- Sends notifications (customer SMS, driver notifications, status changes) logged to JSONL files
- Updates driver status to available when delivery is completed
- Logs all state changes and events to JSON/JSONL files
- Follows existing patterns from assignment-workflow.ts
- Added `bun run track` npm script
- All existing tests pass successfully

---

### Phase 3: Integration & Polish ✅ IN PROGRESS
**Goal**: Connect everything and add finishing touches

#### TASK 6: Create Dashboard Agent ✅ COMPLETED
**Priority**: MEDIUM
**Status**: Completed (2026-01-13)
**Depends On**: TASK 5 ✅

**Requirements**:
- Overview of all orders
- Driver status
- System metrics

**Success Criteria**:
- [x] Dashboard displays comprehensive system overview
- [x] Shows order statistics (total, by status, revenue, average order value)
- [x] Shows driver status (available, busy, offline counts)
- [x] Calculates and displays key metrics (orders per driver, revenue per driver, utilization rate)
- [x] Uses AI to generate insights and recommendations
- [x] Identifies and highlights alerts/issues
- [x] Logs dashboard snapshots to JSON files
- [x] Follows structured output patterns with Zod schemas
- [x] Added `bun run dashboard` npm script
- [x] All existing tests pass

**Completed**: Created dashboard-agent.ts that provides comprehensive system analytics:
- Collects data from orderStore and driverStore
- Calculates key performance metrics (orders per driver, revenue per driver, utilization rate)
- Uses AI with structured outputs (DashboardOutputSchema) to generate insights
- Provides conversational overview, order summary, driver summary, and metrics summary
- Generates actionable recommendations based on current system state
- Identifies and highlights alerts/issues (e.g., pending orders, low utilization)
- Logs dashboard snapshots to JSON files with timestamps
- Logs all AI events to JSONL files
- Follows existing patterns from assignment-workflow.ts and delivery-tracking-agent.ts
- Added `bun run dashboard` npm script to package.json
- Tested with sample data showing accurate metrics and insights
- All existing tests pass successfully

#### TASK 7: Add Persistence Layer
- Replace in-memory store with JSON file persistence
- Load/save state between runs
- Migration from in-memory data

#### TASK 8: Documentation & Demo
- Create README.md with usage examples
- Add demo script showing all features
- Document 12-factor principles used

---

## Current Blockers
None

## Notes
- Each task should be completed in a single Ralph loop iteration
- Commit after each successful task completion
- If tests fail, fix before moving to next task
- Follow existing code style from project examples
