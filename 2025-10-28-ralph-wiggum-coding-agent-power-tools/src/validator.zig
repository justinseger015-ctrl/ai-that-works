const std = @import("std");
const ast = @import("ast.zig");

/// Validation error types
pub const ValidationError = error{
    DuplicateDefinition,
    UndefinedType,
    CircularDependency,
    InvalidType,
    InvalidAttribute,
    OutOfMemory,
};

/// Validation diagnostic message
pub const Diagnostic = struct {
    message: []const u8,
    line: usize,
    column: usize,
    severity: Severity,

    pub const Severity = enum {
        err,
        warning,
        info,
    };

    pub fn deinit(self: *Diagnostic, allocator: std.mem.Allocator) void {
        allocator.free(self.message);
    }
};

/// Type kind in the symbol table
pub const TypeKind = enum {
    class,
    enum_type,
    primitive,
};

/// Symbol table entry for a type
pub const TypeSymbol = struct {
    name: []const u8,
    kind: TypeKind,
    location: ast.Location,
};

/// Type registry for tracking all declared types
pub const TypeRegistry = struct {
    types: std.StringHashMap(TypeSymbol),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) TypeRegistry {
        var registry = TypeRegistry{
            .types = std.StringHashMap(TypeSymbol).init(allocator),
            .allocator = allocator,
        };

        // Register primitive types
        registry.registerPrimitive("string") catch {};
        registry.registerPrimitive("int") catch {};
        registry.registerPrimitive("float") catch {};
        registry.registerPrimitive("bool") catch {};
        registry.registerPrimitive("null") catch {};
        registry.registerPrimitive("image") catch {};
        registry.registerPrimitive("audio") catch {};
        registry.registerPrimitive("video") catch {};
        registry.registerPrimitive("pdf") catch {};

        return registry;
    }

    pub fn deinit(self: *TypeRegistry) void {
        self.types.deinit();
    }

    fn registerPrimitive(self: *TypeRegistry, name: []const u8) !void {
        try self.types.put(name, TypeSymbol{
            .name = name,
            .kind = .primitive,
            .location = .{ .line = 0, .column = 0 },
        });
    }

    pub fn registerClass(self: *TypeRegistry, name: []const u8, location: ast.Location) !void {
        if (self.types.contains(name)) {
            return ValidationError.DuplicateDefinition;
        }
        try self.types.put(name, TypeSymbol{
            .name = name,
            .kind = .class,
            .location = location,
        });
    }

    pub fn registerEnum(self: *TypeRegistry, name: []const u8, location: ast.Location) !void {
        if (self.types.contains(name)) {
            return ValidationError.DuplicateDefinition;
        }
        try self.types.put(name, TypeSymbol{
            .name = name,
            .kind = .enum_type,
            .location = location,
        });
    }

    pub fn isDefined(self: *const TypeRegistry, name: []const u8) bool {
        return self.types.contains(name);
    }

    pub fn getType(self: *const TypeRegistry, name: []const u8) ?TypeSymbol {
        return self.types.get(name);
    }
};

/// Function registry for tracking all declared functions
pub const FunctionRegistry = struct {
    functions: std.StringHashMap(ast.Location),
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator) FunctionRegistry {
        return FunctionRegistry{
            .functions = std.StringHashMap(ast.Location).init(allocator),
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *FunctionRegistry) void {
        self.functions.deinit();
    }

    pub fn registerFunction(self: *FunctionRegistry, name: []const u8, location: ast.Location) !void {
        if (self.functions.contains(name)) {
            return ValidationError.DuplicateDefinition;
        }
        try self.functions.put(name, location);
    }

    pub fn isDefined(self: *const FunctionRegistry, name: []const u8) bool {
        return self.functions.contains(name);
    }
};

/// Validator for BAML AST
pub const Validator = struct {
    allocator: std.mem.Allocator,
    type_registry: TypeRegistry,
    function_registry: FunctionRegistry,
    diagnostics: std.ArrayList(Diagnostic),

    pub fn init(allocator: std.mem.Allocator) Validator {
        return Validator{
            .allocator = allocator,
            .type_registry = TypeRegistry.init(allocator),
            .function_registry = FunctionRegistry.init(allocator),
            .diagnostics = std.ArrayList(Diagnostic).init(allocator),
        };
    }

    pub fn deinit(self: *Validator) void {
        for (self.diagnostics.items) |*diag| {
            diag.deinit(self.allocator);
        }
        self.diagnostics.deinit();
        self.type_registry.deinit();
        self.function_registry.deinit();
    }

    /// Validate an entire AST
    pub fn validate(self: *Validator, tree: *const ast.Ast) !void {
        // Phase 1: Register all types and functions
        try self.registerDeclarations(tree);

        // Phase 2: Validate type references
        try self.validateTypeReferences(tree);

        // Phase 3: Check for circular dependencies
        try self.checkCircularDependencies(tree);
    }

    /// Register all declarations in the AST
    fn registerDeclarations(self: *Validator, tree: *const ast.Ast) !void {
        for (tree.declarations.items) |decl| {
            switch (decl) {
                .class_decl => |class| {
                    self.type_registry.registerClass(class.name, class.location) catch |err| {
                        if (err == ValidationError.DuplicateDefinition) {
                            try self.addError("Duplicate class definition: {s}", .{class.name}, class.location);
                        } else {
                            return err;
                        }
                    };
                },
                .enum_decl => |enum_decl| {
                    self.type_registry.registerEnum(enum_decl.name, enum_decl.location) catch |err| {
                        if (err == ValidationError.DuplicateDefinition) {
                            try self.addError("Duplicate enum definition: {s}", .{enum_decl.name}, enum_decl.location);
                        } else {
                            return err;
                        }
                    };
                },
                .function_decl => |func| {
                    self.function_registry.registerFunction(func.name, func.location) catch |err| {
                        if (err == ValidationError.DuplicateDefinition) {
                            try self.addError("Duplicate function definition: {s}", .{func.name}, func.location);
                        } else {
                            return err;
                        }
                    };
                },
                else => {},
            }
        }
    }

    /// Validate all type references in the AST
    fn validateTypeReferences(self: *Validator, tree: *const ast.Ast) !void {
        for (tree.declarations.items) |decl| {
            switch (decl) {
                .class_decl => |class| {
                    for (class.properties.items) |prop| {
                        try self.validateTypeExpr(prop.type_expr, prop.location);
                    }
                },
                .function_decl => |func| {
                    // Validate parameter types
                    for (func.parameters.items) |param| {
                        try self.validateTypeExpr(param.type_expr, param.location);
                    }
                    // Validate return type
                    try self.validateTypeExpr(func.return_type, func.location);
                },
                .template_string_decl => |tmpl| {
                    // Validate parameter types
                    for (tmpl.parameters.items) |param| {
                        try self.validateTypeExpr(param.type_expr, param.location);
                    }
                },
                .test_decl => |test_decl| {
                    // Validate function references in tests
                    for (test_decl.functions.items) |func_name| {
                        if (!self.function_registry.isDefined(func_name)) {
                            try self.addError("Undefined function in test: {s}", .{func_name}, test_decl.location);
                        }
                    }
                },
                else => {},
            }
        }
    }

    /// Validate a type expression
    fn validateTypeExpr(self: *Validator, type_expr: *const ast.TypeExpr, location: ast.Location) ValidationError!void {
        switch (type_expr.*) {
            .primitive => {
                // Primitive types are always valid
            },
            .named => |name| {
                if (!self.type_registry.isDefined(name)) {
                    try self.addError("Undefined type: {s}", .{name}, location);
                }
            },
            .array => |inner| {
                try self.validateTypeExpr(inner, location);
            },
            .optional => |inner| {
                try self.validateTypeExpr(inner, location);
            },
            .union_type => |union_type| {
                for (union_type.types.items) |inner| {
                    try self.validateTypeExpr(inner, location);
                }
            },
            .map => |map_type| {
                try self.validateTypeExpr(map_type.key_type, location);
                try self.validateTypeExpr(map_type.value_type, location);
            },
            .literal => {
                // Literal types are always valid
            },
        }
    }

    /// Check for circular dependencies in type definitions
    fn checkCircularDependencies(self: *Validator, tree: *const ast.Ast) !void {
        var visited = std.StringHashMap(void).init(self.allocator);
        defer visited.deinit();

        var visiting = std.StringHashMap(void).init(self.allocator);
        defer visiting.deinit();

        for (tree.declarations.items) |decl| {
            switch (decl) {
                .class_decl => |class| {
                    visited.clearRetainingCapacity();
                    visiting.clearRetainingCapacity();
                    try self.checkClassCircular(tree, class.name, &visited, &visiting, class.location);
                },
                else => {},
            }
        }
    }

    /// Check if a class has circular dependencies
    fn checkClassCircular(
        self: *Validator,
        tree: *const ast.Ast,
        class_name: []const u8,
        visited: *std.StringHashMap(void),
        visiting: *std.StringHashMap(void),
        location: ast.Location,
    ) !void {
        if (visited.contains(class_name)) {
            return;
        }

        if (visiting.contains(class_name)) {
            try self.addError("Circular dependency detected in type: {s}", .{class_name}, location);
            return;
        }

        try visiting.put(class_name, {});

        // Find the class declaration
        for (tree.declarations.items) |decl| {
            switch (decl) {
                .class_decl => |class| {
                    if (std.mem.eql(u8, class.name, class_name)) {
                        // Check all property types
                        for (class.properties.items) |prop| {
                            try self.checkTypeExprCircular(tree, prop.type_expr, visited, visiting, prop.location);
                        }
                        break;
                    }
                },
                else => {},
            }
        }

        _ = visiting.remove(class_name);
        try visited.put(class_name, {});
    }

    /// Check if a type expression leads to circular dependencies
    fn checkTypeExprCircular(
        self: *Validator,
        tree: *const ast.Ast,
        type_expr: *const ast.TypeExpr,
        visited: *std.StringHashMap(void),
        visiting: *std.StringHashMap(void),
        location: ast.Location,
    ) !void {
        switch (type_expr.*) {
            .named => |name| {
                // Only check class types for circular dependencies
                if (self.type_registry.getType(name)) |type_symbol| {
                    if (type_symbol.kind == .class) {
                        try self.checkClassCircular(tree, name, visited, visiting, location);
                    }
                }
            },
            .array => |inner| {
                try self.checkTypeExprCircular(tree, inner, visited, visiting, location);
            },
            .optional => |inner| {
                try self.checkTypeExprCircular(tree, inner, visited, visiting, location);
            },
            .union_type => |union_type| {
                for (union_type.types.items) |inner| {
                    try self.checkTypeExprCircular(tree, inner, visited, visiting, location);
                }
            },
            .map => |map_type| {
                try self.checkTypeExprCircular(tree, map_type.key_type, visited, visiting, location);
                try self.checkTypeExprCircular(tree, map_type.value_type, visited, visiting, location);
            },
            else => {},
        }
    }

    /// Add an error diagnostic
    fn addError(self: *Validator, comptime fmt: []const u8, args: anytype, location: ast.Location) !void {
        const message = try std.fmt.allocPrint(self.allocator, fmt, args);
        try self.diagnostics.append(Diagnostic{
            .message = message,
            .line = location.line,
            .column = location.column,
            .severity = .err,
        });
    }

    /// Add a warning diagnostic
    fn addWarning(self: *Validator, comptime fmt: []const u8, args: anytype, location: ast.Location) !void {
        const message = try std.fmt.allocPrint(self.allocator, fmt, args);
        try self.diagnostics.append(Diagnostic{
            .message = message,
            .line = location.line,
            .column = location.column,
            .severity = .warning,
        });
    }

    /// Check if validation found any errors
    pub fn hasErrors(self: *const Validator) bool {
        for (self.diagnostics.items) |diag| {
            if (diag.severity == .err) {
                return true;
            }
        }
        return false;
    }

    /// Get all diagnostics
    pub fn getDiagnostics(self: *const Validator) []const Diagnostic {
        return self.diagnostics.items;
    }
};

// Tests
test "Validator: Create and cleanup" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    try std.testing.expect(validator.diagnostics.items.len == 0);
}

test "Validator: TypeRegistry primitives" {
    const allocator = std.testing.allocator;
    var registry = TypeRegistry.init(allocator);
    defer registry.deinit();

    try std.testing.expect(registry.isDefined("string"));
    try std.testing.expect(registry.isDefined("int"));
    try std.testing.expect(registry.isDefined("float"));
    try std.testing.expect(registry.isDefined("bool"));
    try std.testing.expect(registry.isDefined("image"));
    try std.testing.expect(!registry.isDefined("CustomType"));
}

test "Validator: Register class" {
    const allocator = std.testing.allocator;
    var registry = TypeRegistry.init(allocator);
    defer registry.deinit();

    try registry.registerClass("Person", .{ .line = 1, .column = 1 });
    try std.testing.expect(registry.isDefined("Person"));

    const symbol = registry.getType("Person").?;
    try std.testing.expectEqualStrings("Person", symbol.name);
    try std.testing.expect(symbol.kind == .class);
}

test "Validator: Detect duplicate class" {
    const allocator = std.testing.allocator;
    var registry = TypeRegistry.init(allocator);
    defer registry.deinit();

    try registry.registerClass("Person", .{ .line = 1, .column = 1 });
    const result = registry.registerClass("Person", .{ .line = 10, .column = 1 });
    try std.testing.expectError(ValidationError.DuplicateDefinition, result);
}

test "Validator: Register enum" {
    const allocator = std.testing.allocator;
    var registry = TypeRegistry.init(allocator);
    defer registry.deinit();

    try registry.registerEnum("Status", .{ .line = 1, .column = 1 });
    try std.testing.expect(registry.isDefined("Status"));

    const symbol = registry.getType("Status").?;
    try std.testing.expectEqualStrings("Status", symbol.name);
    try std.testing.expect(symbol.kind == .enum_type);
}

test "Validator: FunctionRegistry" {
    const allocator = std.testing.allocator;
    var registry = FunctionRegistry.init(allocator);
    defer registry.deinit();

    try registry.registerFunction("greet", .{ .line = 1, .column = 1 });
    try std.testing.expect(registry.isDefined("greet"));
    try std.testing.expect(!registry.isDefined("other"));
}

test "Validator: Detect duplicate function" {
    const allocator = std.testing.allocator;
    var registry = FunctionRegistry.init(allocator);
    defer registry.deinit();

    try registry.registerFunction("greet", .{ .line = 1, .column = 1 });
    const result = registry.registerFunction("greet", .{ .line = 10, .column = 1 });
    try std.testing.expectError(ValidationError.DuplicateDefinition, result);
}

test "Validator: Validate simple class" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    var tree = ast.Ast.init(allocator);
    defer tree.deinit();

    // Create a simple class with primitive types
    var class = ast.ClassDecl.init(allocator, "Person", .{ .line = 1, .column = 1 });

    // Add property: name string
    const name_type = try allocator.create(ast.TypeExpr);
    name_type.* = ast.TypeExpr{ .primitive = .string };

    const name_prop = ast.Property{
        .name = "name",
        .type_expr = name_type,
        .attributes = std.ArrayList(ast.Attribute).init(allocator),
        .docstring = null,
        .location = .{ .line = 2, .column = 3 },
    };
    try class.properties.append(name_prop);

    try tree.declarations.append(ast.Declaration{ .class_decl = class });

    try validator.validate(&tree);
    try std.testing.expect(!validator.hasErrors());
}

test "Validator: Detect undefined type" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    var tree = ast.Ast.init(allocator);
    defer tree.deinit();

    // Create a class with undefined type
    var class = ast.ClassDecl.init(allocator, "Person", .{ .line = 1, .column = 1 });

    // Add property: address Address (Address not defined)
    const address_type = try allocator.create(ast.TypeExpr);
    address_type.* = ast.TypeExpr{ .named = "Address" };

    const address_prop = ast.Property{
        .name = "address",
        .type_expr = address_type,
        .attributes = std.ArrayList(ast.Attribute).init(allocator),
        .docstring = null,
        .location = .{ .line = 2, .column = 3 },
    };
    try class.properties.append(address_prop);

    try tree.declarations.append(ast.Declaration{ .class_decl = class });

    try validator.validate(&tree);
    try std.testing.expect(validator.hasErrors());
    try std.testing.expect(validator.diagnostics.items.len > 0);
}

test "Validator: Detect undefined function in test" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    var tree = ast.Ast.init(allocator);
    defer tree.deinit();

    // Create a test that references undefined function
    var test_decl = ast.TestDecl.init(allocator, "TestGreet", .{ .line = 1, .column = 1 });
    try test_decl.functions.append("UndefinedFunction");

    try tree.declarations.append(ast.Declaration{ .test_decl = test_decl });

    try validator.validate(&tree);
    try std.testing.expect(validator.hasErrors());
}

test "Validator: Detect circular dependency" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    var tree = ast.Ast.init(allocator);
    defer tree.deinit();

    // Create A -> B -> A circular dependency
    var class_a = ast.ClassDecl.init(allocator, "A", .{ .line = 1, .column = 1 });
    const b_type = try allocator.create(ast.TypeExpr);
    b_type.* = ast.TypeExpr{ .named = "B" };
    const b_prop = ast.Property{
        .name = "b",
        .type_expr = b_type,
        .attributes = std.ArrayList(ast.Attribute).init(allocator),
        .docstring = null,
        .location = .{ .line = 2, .column = 3 },
    };
    try class_a.properties.append(b_prop);

    var class_b = ast.ClassDecl.init(allocator, "B", .{ .line = 5, .column = 1 });
    const a_type = try allocator.create(ast.TypeExpr);
    a_type.* = ast.TypeExpr{ .named = "A" };
    const a_prop = ast.Property{
        .name = "a",
        .type_expr = a_type,
        .attributes = std.ArrayList(ast.Attribute).init(allocator),
        .docstring = null,
        .location = .{ .line = 6, .column = 3 },
    };
    try class_b.properties.append(a_prop);

    try tree.declarations.append(ast.Declaration{ .class_decl = class_a });
    try tree.declarations.append(ast.Declaration{ .class_decl = class_b });

    try validator.validate(&tree);
    try std.testing.expect(validator.hasErrors());
}

test "Validator: Complex types are valid" {
    const allocator = std.testing.allocator;
    var validator = Validator.init(allocator);
    defer validator.deinit();

    var tree = ast.Ast.init(allocator);
    defer tree.deinit();

    // Register Address class first
    const addr_class = ast.ClassDecl.init(allocator, "Address", .{ .line = 1, .column = 1 });
    try tree.declarations.append(ast.Declaration{ .class_decl = addr_class });

    // Create Person class with complex types
    var class = ast.ClassDecl.init(allocator, "Person", .{ .line = 5, .column = 1 });

    // Add property: addresses Address[]
    const inner_type = try allocator.create(ast.TypeExpr);
    inner_type.* = ast.TypeExpr{ .named = "Address" };
    const array_type = try allocator.create(ast.TypeExpr);
    array_type.* = ast.TypeExpr{ .array = inner_type };

    const addresses_prop = ast.Property{
        .name = "addresses",
        .type_expr = array_type,
        .attributes = std.ArrayList(ast.Attribute).init(allocator),
        .docstring = null,
        .location = .{ .line = 6, .column = 3 },
    };
    try class.properties.append(addresses_prop);

    try tree.declarations.append(ast.Declaration{ .class_decl = class });

    try validator.validate(&tree);
    try std.testing.expect(!validator.hasErrors());
}
