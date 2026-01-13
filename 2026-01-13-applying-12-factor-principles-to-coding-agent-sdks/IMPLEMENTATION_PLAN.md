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

### Phase 2: Agent Workflows (Not Started)
**Goal**: Implement workflow automation

#### TASK 4: Create Order Assignment Workflow [NEXT]
**Priority**: HIGH
**Status**: Not Started
**Depends On**: TASK 3 ✅

**Requirements**:
- Auto-assign orders to available drivers
- Use structured planning pattern
- Log state changes

**Success Criteria**:
- [ ] Workflow automatically assigns pending orders to available drivers
- [ ] Driver status updates correctly (available -> busy)
- [ ] State changes are logged
- [ ] Follows structured output patterns

#### TASK 5: Create Delivery Tracking Agent
- Track delivery status
- Update order status automatically
- Send notifications (simulated)

---

### Phase 3: Integration & Polish (Not Started)
**Goal**: Connect everything and add finishing touches

#### TASK 6: Create Dashboard Agent
- Overview of all orders
- Driver status
- System metrics

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
