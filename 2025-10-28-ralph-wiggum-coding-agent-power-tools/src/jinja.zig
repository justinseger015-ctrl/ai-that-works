const std = @import("std");

/// Jinja token types for template parsing
pub const JinjaTokenType = enum {
    text, // Plain text outside Jinja constructs
    variable_start, // {{
    variable_end, // }}
    statement_start, // {%
    statement_end, // %}
    comment_start, // {#
    comment_end, // #}
    identifier, // Variable or function names
    dot, // . for property access
    pipe, // | for filters
    lparen, // (
    rparen, // )
    comma, // ,
    string_literal, // "..." or '...'
    number, // Integer or float
    eof,
};

/// A single token in a Jinja template
pub const JinjaToken = struct {
    type: JinjaTokenType,
    lexeme: []const u8,
    line: usize,
    column: usize,
};

/// Lexer state for tracking context
const LexerState = enum {
    in_text,
    in_variable,
    in_statement,
    in_comment,
};

/// Jinja template lexer
pub const JinjaLexer = struct {
    source: []const u8,
    pos: usize,
    line: usize,
    column: usize,
    state: LexerState,

    pub fn init(source: []const u8) JinjaLexer {
        return JinjaLexer{
            .source = source,
            .pos = 0,
            .line = 1,
            .column = 1,
            .state = .in_text,
        };
    }

    pub fn tokenize(self: *JinjaLexer, allocator: std.mem.Allocator) !std.ArrayList(JinjaToken) {
        var tokens = std.ArrayList(JinjaToken){};
        errdefer tokens.deinit(allocator);

        while (self.pos < self.source.len) {
            const token = try self.nextToken();
            try tokens.append(allocator, token);
            if (token.type == .eof) break;
        }

        return tokens;
    }

    fn nextToken(self: *JinjaLexer) !JinjaToken {
        if (self.pos >= self.source.len) {
            return JinjaToken{
                .type = .eof,
                .lexeme = "",
                .line = self.line,
                .column = self.column,
            };
        }

        // Check for Jinja delimiters
        if (self.peek2() == '{' and self.peekAhead(1) == '{') {
            self.state = .in_variable;
            return self.makeToken(.variable_start, 2);
        }
        if (self.peek2() == '}' and self.peekAhead(1) == '}') {
            self.state = .in_text;
            return self.makeToken(.variable_end, 2);
        }
        if (self.peek2() == '{' and self.peekAhead(1) == '%') {
            self.state = .in_statement;
            return self.makeToken(.statement_start, 2);
        }
        if (self.peek2() == '%' and self.peekAhead(1) == '}') {
            self.state = .in_text;
            return self.makeToken(.statement_end, 2);
        }
        if (self.peek2() == '{' and self.peekAhead(1) == '#') {
            self.state = .in_comment;
            return self.makeToken(.comment_start, 2);
        }
        if (self.peek2() == '#' and self.peekAhead(1) == '}') {
            self.state = .in_text;
            return self.makeToken(.comment_end, 2);
        }

        // Tokenize based on state
        switch (self.state) {
            .in_text => return self.scanText(),
            .in_variable, .in_statement => return self.scanExpression(),
            .in_comment => return self.scanCommentContent(),
        }
    }

    fn scanText(self: *JinjaLexer) !JinjaToken {
        const start = self.pos;
        const start_line = self.line;
        const start_column = self.column;

        // Scan until we hit a Jinja delimiter
        while (self.pos < self.source.len) {
            if (self.peek2() == '{' and
                (self.peekAhead(1) == '{' or self.peekAhead(1) == '%' or self.peekAhead(1) == '#')) {
                break;
            }
            if (self.peek2() == '\n') {
                self.line += 1;
                self.column = 1;
                self.pos += 1;
            } else {
                self.column += 1;
                self.pos += 1;
            }
        }

        const lexeme = self.source[start..self.pos];
        return JinjaToken{
            .type = .text,
            .lexeme = lexeme,
            .line = start_line,
            .column = start_column,
        };
    }

    fn scanExpression(self: *JinjaLexer) !JinjaToken {
        self.skipWhitespace();

        if (self.pos >= self.source.len) {
            return JinjaToken{
                .type = .eof,
                .lexeme = "",
                .line = self.line,
                .column = self.column,
            };
        }

        const c = self.peek2();

        // Single-character tokens
        if (c == '.') return self.makeToken(.dot, 1);
        if (c == '|') return self.makeToken(.pipe, 1);
        if (c == '(') return self.makeToken(.lparen, 1);
        if (c == ')') return self.makeToken(.rparen, 1);
        if (c == ',') return self.makeToken(.comma, 1);

        // String literals
        if (c == '"' or c == '\'') return self.scanString(c);

        // Numbers
        if (std.ascii.isDigit(c)) return self.scanNumber();

        // Identifiers
        if (std.ascii.isAlphabetic(c) or c == '_') return self.scanIdentifier();

        // Unknown character - treat as text
        return self.makeToken(.text, 1);
    }

    fn scanIdentifier(self: *JinjaLexer) !JinjaToken {
        const start = self.pos;
        const start_line = self.line;
        const start_column = self.column;

        while (self.pos < self.source.len) {
            const c = self.peek2();
            if (!std.ascii.isAlphanumeric(c) and c != '_') break;
            self.advance();
        }

        const lexeme = self.source[start..self.pos];
        return JinjaToken{
            .type = .identifier,
            .lexeme = lexeme,
            .line = start_line,
            .column = start_column,
        };
    }

    fn scanNumber(self: *JinjaLexer) !JinjaToken {
        const start = self.pos;
        const start_line = self.line;
        const start_column = self.column;

        while (self.pos < self.source.len and std.ascii.isDigit(self.peek2())) {
            self.advance();
        }

        // Check for decimal point
        if (self.pos < self.source.len and self.peek2() == '.' and
            self.pos + 1 < self.source.len and std.ascii.isDigit(self.peekAhead(1))) {
            self.advance(); // consume '.'
            while (self.pos < self.source.len and std.ascii.isDigit(self.peek2())) {
                self.advance();
            }
        }

        const lexeme = self.source[start..self.pos];
        return JinjaToken{
            .type = .number,
            .lexeme = lexeme,
            .line = start_line,
            .column = start_column,
        };
    }

    fn scanString(self: *JinjaLexer, quote: u8) !JinjaToken {
        const start = self.pos;
        const start_line = self.line;
        const start_column = self.column;

        self.advance(); // consume opening quote

        while (self.pos < self.source.len and self.peek2() != quote) {
            if (self.peek2() == '\\' and self.pos + 1 < self.source.len) {
                self.advance(); // skip escape
            }
            self.advance();
        }

        if (self.pos < self.source.len) {
            self.advance(); // consume closing quote
        }

        const lexeme = self.source[start..self.pos];
        return JinjaToken{
            .type = .string_literal,
            .lexeme = lexeme,
            .line = start_line,
            .column = start_column,
        };
    }

    fn skipWhitespace(self: *JinjaLexer) void {
        while (self.pos < self.source.len) {
            const c = self.peek2();
            if (c == ' ' or c == '\t' or c == '\r') {
                self.advance();
            } else if (c == '\n') {
                self.line += 1;
                self.column = 1;
                self.pos += 1;
            } else {
                break;
            }
        }
    }

    fn peek2(self: *JinjaLexer) u8 {
        if (self.pos >= self.source.len) return 0;
        return self.source[self.pos];
    }

    fn peekAhead(self: *JinjaLexer, offset: usize) u8 {
        const pos = self.pos + offset;
        if (pos >= self.source.len) return 0;
        return self.source[pos];
    }

    fn advance(self: *JinjaLexer) void {
        self.pos += 1;
        self.column += 1;
    }

    fn scanCommentContent(self: *JinjaLexer) !JinjaToken {
        const start = self.pos;
        const start_line = self.line;
        const start_column = self.column;

        // Scan until we hit comment end
        while (self.pos < self.source.len) {
            if (self.peek2() == '#' and self.peekAhead(1) == '}') {
                break;
            }
            if (self.peek2() == '\n') {
                self.line += 1;
                self.column = 1;
                self.pos += 1;
            } else {
                self.column += 1;
                self.pos += 1;
            }
        }

        const lexeme = self.source[start..self.pos];
        return JinjaToken{
            .type = .text,
            .lexeme = lexeme,
            .line = start_line,
            .column = start_column,
        };
    }

    fn makeToken(self: *JinjaLexer, token_type: JinjaTokenType, len: usize) JinjaToken {
        const start = self.pos;
        const start_column = self.column;
        self.pos += len;
        self.column += len;
        return JinjaToken{
            .type = token_type,
            .lexeme = self.source[start..self.pos],
            .line = self.line,
            .column = start_column,
        };
    }
};

/// Jinja template node types
pub const JinjaNodeType = enum {
    text,
    variable, // {{ expr }}
    statement, // {% statement %}
    comment, // {# comment #}
};

/// A parsed Jinja template node
pub const JinjaNode = union(JinjaNodeType) {
    text: []const u8,
    variable: JinjaVariable,
    statement: JinjaStatement,
    comment: []const u8,

    pub fn deinit(self: *JinjaNode, allocator: std.mem.Allocator) void {
        switch (self.*) {
            .variable => |*v| v.deinit(allocator),
            .statement => |*s| s.deinit(allocator),
            else => {},
        }
    }
};

/// A variable expression: {{ x.y.z }}
pub const JinjaVariable = struct {
    path: std.ArrayList([]const u8), // e.g., ["p", "name"]
    filters: std.ArrayList([]const u8),
    line: usize,
    column: usize,

    pub fn init(allocator: std.mem.Allocator, line: usize, column: usize) JinjaVariable {
        _ = allocator;
        return JinjaVariable{
            .path = std.ArrayList([]const u8){},
            .filters = std.ArrayList([]const u8){},
            .line = line,
            .column = column,
        };
    }

    pub fn deinit(self: *JinjaVariable, allocator: std.mem.Allocator) void {
        self.path.deinit(allocator);
        self.filters.deinit(allocator);
    }
};

/// A statement: {% for x in y %}, {% if x %}, etc.
pub const JinjaStatement = struct {
    statement_type: []const u8, // "for", "if", "endfor", etc.
    content: []const u8,
    line: usize,
    column: usize,

    pub fn deinit(self: *JinjaStatement, allocator: std.mem.Allocator) void {
        _ = self;
        _ = allocator;
    }
};

/// Jinja template parser
pub const JinjaParser = struct {
    tokens: []const JinjaToken,
    pos: usize,

    pub fn init(tokens: []const JinjaToken) JinjaParser {
        return JinjaParser{
            .tokens = tokens,
            .pos = 0,
        };
    }

    pub fn parse(self: *JinjaParser, allocator: std.mem.Allocator) !std.ArrayList(JinjaNode) {
        var nodes = std.ArrayList(JinjaNode){};
        errdefer {
            for (nodes.items) |*node| {
                node.deinit(allocator);
            }
            nodes.deinit(allocator);
        }

        while (self.pos < self.tokens.len and self.peek().type != .eof) {
            const node = try self.parseNode(allocator);
            try nodes.append(allocator, node);
        }

        return nodes;
    }

    fn parseNode(self: *JinjaParser, allocator: std.mem.Allocator) !JinjaNode {
        const token = self.peek();

        switch (token.type) {
            .text => {
                self.advance();
                return JinjaNode{ .text = token.lexeme };
            },
            .variable_start => {
                return try self.parseVariable(allocator);
            },
            .statement_start => {
                return try self.parseStatement(allocator);
            },
            .comment_start => {
                return try self.parseComment(allocator);
            },
            else => {
                // Treat unexpected tokens as text
                self.advance();
                return JinjaNode{ .text = token.lexeme };
            },
        }
    }

    fn parseVariable(self: *JinjaParser, allocator: std.mem.Allocator) !JinjaNode {
        const start_token = self.expect(.variable_start);
        var variable = JinjaVariable.init(allocator, start_token.line, start_token.column);
        errdefer variable.deinit(allocator);

        // Parse variable path (e.g., p.name.first)
        while (self.pos < self.tokens.len) {
            const token = self.peek();

            if (token.type == .variable_end) {
                self.advance();
                break;
            }

            if (token.type == .identifier) {
                try variable.path.append(allocator, token.lexeme);
                self.advance();

                // Check for dot accessor
                if (self.pos < self.tokens.len and self.peek().type == .dot) {
                    self.advance(); // consume dot
                }
            } else if (token.type == .pipe) {
                self.advance(); // consume pipe
                // Parse filter name
                if (self.pos < self.tokens.len and self.peek().type == .identifier) {
                    const filter_token = self.peek();
                    try variable.filters.append(allocator, filter_token.lexeme);
                    self.advance();
                }
            } else {
                self.advance(); // skip unknown tokens
            }
        }

        return JinjaNode{ .variable = variable };
    }

    fn parseStatement(self: *JinjaParser, allocator: std.mem.Allocator) !JinjaNode {
        const start_token = self.expect(.statement_start);
        _ = allocator;

        // Get statement type (for, if, etc.)
        var statement_type: []const u8 = "";
        const content_start: usize = self.pos;

        if (self.pos < self.tokens.len and self.peek().type == .identifier) {
            statement_type = self.peek().lexeme;
            self.advance();
        }

        // Skip to end of statement
        while (self.pos < self.tokens.len and self.peek().type != .statement_end) {
            self.advance();
        }

        const content_end = self.pos;
        if (self.pos < self.tokens.len) {
            _ = self.expect(.statement_end);
        }

        // Build content string from tokens
        var content: []const u8 = "";
        if (content_start < content_end and content_start < self.tokens.len) {
            content = self.tokens[content_start].lexeme;
        }

        return JinjaNode{
            .statement = JinjaStatement{
                .statement_type = statement_type,
                .content = content,
                .line = start_token.line,
                .column = start_token.column,
            },
        };
    }

    fn parseComment(self: *JinjaParser, allocator: std.mem.Allocator) !JinjaNode {
        _ = allocator;
        _ = self.expect(.comment_start);

        var content: []const u8 = "";

        // Collect comment content
        while (self.pos < self.tokens.len and self.peek().type != .comment_end) {
            const token = self.peek();
            if (token.type == .text or token.type == .identifier) {
                content = token.lexeme;
            }
            self.advance();
        }

        if (self.pos < self.tokens.len) {
            _ = self.expect(.comment_end);
        }

        return JinjaNode{ .comment = content };
    }

    fn peek(self: *JinjaParser) JinjaToken {
        if (self.pos >= self.tokens.len) {
            return JinjaToken{
                .type = .eof,
                .lexeme = "",
                .line = 0,
                .column = 0,
            };
        }
        return self.tokens[self.pos];
    }

    fn advance(self: *JinjaParser) void {
        if (self.pos < self.tokens.len) {
            self.pos += 1;
        }
    }

    fn expect(self: *JinjaParser, expected: JinjaTokenType) JinjaToken {
        const token = self.peek();
        if (token.type == expected) {
            self.advance();
            return token;
        }
        return token;
    }
};

/// Jinja template validator
pub const JinjaValidator = struct {
    allocator: std.mem.Allocator,
    errors: std.ArrayList(ValidationError),
    param_names: std.StringHashMap(void),

    pub const ValidationError = struct {
        message: []const u8,
        line: usize,
        column: usize,
    };

    pub fn init(allocator: std.mem.Allocator) JinjaValidator {
        return JinjaValidator{
            .allocator = allocator,
            .errors = std.ArrayList(ValidationError){},
            .param_names = std.StringHashMap(void).init(allocator),
        };
    }

    pub fn deinit(self: *JinjaValidator) void {
        self.errors.deinit(self.allocator);
        self.param_names.deinit();
    }

    /// Add a parameter name to the list of valid variables
    pub fn addParameter(self: *JinjaValidator, name: []const u8) !void {
        try self.param_names.put(name, {});
    }

    /// Validate a Jinja template
    pub fn validate(self: *JinjaValidator, template: []const u8) !void {
        var lexer = JinjaLexer.init(template);
        var tokens = try lexer.tokenize(self.allocator);
        defer tokens.deinit(self.allocator);

        var parser = JinjaParser.init(tokens.items);
        var nodes = try parser.parse(self.allocator);
        defer {
            for (nodes.items) |*node| {
                node.deinit(self.allocator);
            }
            nodes.deinit(self.allocator);
        }

        // Validate each node
        for (nodes.items) |*node| {
            try self.validateNode(node);
        }
    }

    fn validateNode(self: *JinjaValidator, node: *const JinjaNode) !void {
        switch (node.*) {
            .variable => |*v| try self.validateVariable(v),
            .statement => |*s| try self.validateStatement(s),
            else => {},
        }
    }

    fn validateVariable(self: *JinjaValidator, variable: *const JinjaVariable) !void {
        if (variable.path.items.len == 0) {
            try self.addError("Empty variable reference", variable.line, variable.column);
            return;
        }

        const root = variable.path.items[0];

        // Check for BAML built-ins
        if (std.mem.eql(u8, root, "ctx") or std.mem.eql(u8, root, "_")) {
            // Built-in variables are always valid
            return;
        }

        // Check if it's a declared parameter
        if (!self.param_names.contains(root)) {
            const msg = try std.fmt.allocPrint(
                self.allocator,
                "Undefined variable '{s}' - not found in function parameters",
                .{root},
            );
            try self.addError(msg, variable.line, variable.column);
        }
    }

    fn validateStatement(self: *JinjaValidator, statement: *const JinjaStatement) !void {
        // Basic validation for statements
        if (statement.statement_type.len == 0) {
            try self.addError("Empty statement", statement.line, statement.column);
        }
    }

    fn addError(self: *JinjaValidator, message: []const u8, line: usize, column: usize) !void {
        try self.errors.append(self.allocator, ValidationError{
            .message = message,
            .line = line,
            .column = column,
        });
    }

    pub fn hasErrors(self: *const JinjaValidator) bool {
        return self.errors.items.len > 0;
    }

    pub fn getErrors(self: *const JinjaValidator) []const ValidationError {
        return self.errors.items;
    }
};

/// Validate a function's prompt template against its parameters
pub fn validateFunctionPrompt(
    allocator: std.mem.Allocator,
    prompt: []const u8,
    parameters: []const []const u8,
) ![]const JinjaValidator.ValidationError {
    var validator = JinjaValidator.init(allocator);
    defer validator.deinit();

    // Add all parameter names
    for (parameters) |param_name| {
        try validator.addParameter(param_name);
    }

    // Validate the template
    try validator.validate(prompt);

    // Return a copy of the errors
    const errors = try allocator.alloc(JinjaValidator.ValidationError, validator.errors.items.len);
    @memcpy(errors, validator.errors.items);
    return errors;
}

// Tests
test "JinjaLexer: tokenize simple text" {
    var lexer = JinjaLexer.init("Hello, world!");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    try std.testing.expectEqual(@as(usize, 2), tokens.items.len);
    try std.testing.expectEqual(JinjaTokenType.text, tokens.items[0].type);
    try std.testing.expectEqual(JinjaTokenType.eof, tokens.items[1].type);
}

test "JinjaLexer: tokenize variable" {
    var lexer = JinjaLexer.init("{{ name }}");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    try std.testing.expectEqual(@as(usize, 3), tokens.items.len);
    try std.testing.expectEqual(JinjaTokenType.variable_start, tokens.items[0].type);
    try std.testing.expectEqual(JinjaTokenType.variable_end, tokens.items[1].type);
}

test "JinjaLexer: tokenize statement" {
    var lexer = JinjaLexer.init("{% for x in items %}");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    try std.testing.expectEqual(@as(usize, 3), tokens.items.len);
    try std.testing.expectEqual(JinjaTokenType.statement_start, tokens.items[0].type);
    try std.testing.expectEqual(JinjaTokenType.statement_end, tokens.items[1].type);
}

test "JinjaLexer: tokenize comment" {
    var lexer = JinjaLexer.init("{# This is a comment #}");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    try std.testing.expectEqual(@as(usize, 3), tokens.items.len);
    try std.testing.expectEqual(JinjaTokenType.comment_start, tokens.items[0].type);
    try std.testing.expectEqual(JinjaTokenType.comment_end, tokens.items[1].type);
}

test "JinjaParser: parse simple variable" {
    var lexer = JinjaLexer.init("{{ name }}");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    var parser = JinjaParser.init(tokens.items);
    var nodes = try parser.parse(std.testing.allocator);
    defer {
        for (nodes.items) |*node| {
            node.deinit(std.testing.allocator);
        }
        nodes.deinit();
    }

    try std.testing.expectEqual(@as(usize, 1), nodes.items.len);
    try std.testing.expect(nodes.items[0] == .variable);
}

test "JinjaParser: parse text and variable" {
    var lexer = JinjaLexer.init("Hello {{ name }}!");
    var tokens = try lexer.tokenize(std.testing.allocator);
    defer tokens.deinit();

    var parser = JinjaParser.init(tokens.items);
    var nodes = try parser.parse(std.testing.allocator);
    defer {
        for (nodes.items) |*node| {
            node.deinit(std.testing.allocator);
        }
        nodes.deinit();
    }

    try std.testing.expectEqual(@as(usize, 3), nodes.items.len);
    try std.testing.expect(nodes.items[0] == .text);
    try std.testing.expect(nodes.items[1] == .variable);
    try std.testing.expect(nodes.items[2] == .text);
}

test "JinjaValidator: valid parameter reference" {
    const params = [_][]const u8{"name"};
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "Hello {{ name }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 0), errors.len);
}

test "JinjaValidator: undefined variable" {
    const params = [_][]const u8{"name"};
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "Hello {{ age }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 1), errors.len);
    try std.testing.expect(std.mem.indexOf(u8, errors[0].message, "Undefined variable") != null);
}

test "JinjaValidator: BAML built-in ctx" {
    const params = [_][]const u8{};
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "{{ ctx.output_format }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 0), errors.len);
}

test "JinjaValidator: BAML built-in underscore" {
    const params = [_][]const u8{};
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "{{ _.role(\"user\") }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 0), errors.len);
}

test "JinjaValidator: multiple valid parameters" {
    const params = [_][]const u8{ "text", "image" };
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "Text: {{ text }}\nImage: {{ image }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 0), errors.len);
}

test "JinjaValidator: property access on parameter" {
    const params = [_][]const u8{"person"};
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        "Hello {{ person.name }}",
        &params,
    );
    defer std.testing.allocator.free(errors);

    // Should not error - we validate the root variable, not nested properties
    try std.testing.expectEqual(@as(usize, 0), errors.len);
}

test "JinjaValidator: complex template with mixed content" {
    const params = [_][]const u8{ "p", "text" };
    const errors = try validateFunctionPrompt(
        std.testing.allocator,
        \\{{ _.role("user") }}
        \\Extract person from: {{ text }}
        \\Name: {{ p.name }}
        \\
        \\{{ ctx.output_format }}
    ,
        &params,
    );
    defer std.testing.allocator.free(errors);

    try std.testing.expectEqual(@as(usize, 0), errors.len);
}
