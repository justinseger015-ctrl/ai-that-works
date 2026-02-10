
class BasicSchema {
    type "number" | "text"
    description string?
}

class DropdownSchema {
    type "dropdown"
    options string[]
    description string?
}

class BulletListSchema {
    type "bulleted_list"
    description string?
}

type SchemaType = BasicSchema | DropdownSchema | BulletListSchema

function GenerateSchema(goal: string) -> map<string, SchemaType> {
    client "openai/gpt-4o-mini"
    prompt #"
      Generate a schema for the following goal:

      {{ ctx.output_format }}

      {{ _.role("user") }}
      {{ goal }}
    "#
}

test GenerateSchemaTest {
  functions [GenerateSchema]
  args {
    goal "I care about the patient's temperature, age, height, weight, and some bulleted notes about their health."
  }
}

function UpdateSchema(schema: map<string, SchemaType>, update: string) -> map<string, SchemaType> {
    client "openai/gpt-4o-mini"
    prompt #"
      Update the schema with the following update:

      {{ ctx.output_format }}

      {{ _.role("user") }}
      Current schema:
      {{ schema }}

      Additional information:
      {{ update }}
    "#
}