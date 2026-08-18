# Schema

To generate and validate data structures, we use schemas defined in JSON Schema format.
These schemas ensure that the data to fullfiled the expected format and constraints. Schema usually related to the response of an API endpoint.
To automatically generate TypeScript types from these JSON schemas, we can use
a tool called `transform`, which can be accessed via [this web](https://transform.tools/json-to-zod).

## Example Schema

Here is an example of a JSON schema for a task object:

```json
{
  "userId": 1,
  "id": 1,
  "title": "delectus aut autem",
  "completed": false
}
```

The schema would be pasted into the `transform` tool to generate the following TypeScript Zod schema object.

```typescript
import { z } from 'zod';

export const schema = z.object({
  userId: z.number(),
  id: z.number(),
  title: z.string(),
  completed: z.boolean(),
});
```

## Guide

To use the `transform` tool, follow these steps:

1. Go to [transform.tools/json-to-zod](https://transform.tools/json-to-zod).
2. Paste your JSON schema into the input field on the left side.
3. The tool will automatically generate the corresponding TypeScript Zod schema on the right side.
4. Copy the generated TypeScript code and use it in your project to validate data structures.
5. Make sure to import the `z` object from the `zod` library to use the generated schema.
6. You can now use the generated schema to validate data, ensuring it adheres to the defined structure and constraints.

> Please add `S` as prefix to the schema name to indicate that it is a Schema. For example, if your schema is for a `TaskResponse`, name it `STaskResponse`.

## Usage Example

Here is an example of how to use the generated schema to validate a task object:

```typescript
import { z } from 'zod';
import { STaskResponse } from './path-to-generated-schema-file';

const taskData = {
  userId: 1,
  id: 1,
  title: 'delectus aut autem',
  completed: false,
};

const parsedData = STaskResponse.parse(taskData);
console.log(parsedData);
```

This code imports the generated schema and uses it to validate a task object. If the object adheres to the schema, it will be parsed successfully; otherwise, an error will be thrown.
