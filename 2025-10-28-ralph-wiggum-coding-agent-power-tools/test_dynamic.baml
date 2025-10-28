// Test file with dynamic types

class User {
  name string
  age int
  @@dynamic
}

enum Category {
  Tech
  Science
  @@dynamic
}

class StaticClass {
  id string
}
