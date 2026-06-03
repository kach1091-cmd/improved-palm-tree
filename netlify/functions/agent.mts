import type { Context } from "@netlify/functions";
import Anthropic from "@anthropic-ai/sdk";
import { db } from "../../db/index.js";
import { records, conversations } from "../../db/schema.js";
import { eq, desc, like, or } from "drizzle-orm";

const anthropic = new Anthropic();

const TOOLS: Anthropic.Tool[] = [
  {
    name: "list_records",
    description: "List all records in the database, optionally filtered by category",
    input_schema: {
      type: "object" as const,
      properties: {
        category: {
          type: "string",
          description: "Optional category filter",
        },
        limit: {
          type: "number",
          description: "Max number of records to return (default 20)",
        },
      },
      required: [],
    },
  },
  {
    name: "search_records",
    description: "Search records by title or content keyword",
    input_schema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "Search keyword",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "create_record",
    description: "Create a new record in the database",
    input_schema: {
      type: "object" as const,
      properties: {
        title: { type: "string", description: "Title of the record" },
        content: { type: "string", description: "Content or details of the record" },
        category: { type: "string", description: "Category for the record (e.g. task, note, contact)" },
      },
      required: ["title"],
    },
  },
  {
    name: "update_record",
    description: "Update an existing record by ID",
    input_schema: {
      type: "object" as const,
      properties: {
        id: { type: "number", description: "Record ID to update" },
        title: { type: "string" },
        content: { type: "string" },
        category: { type: "string" },
      },
      required: ["id"],
    },
  },
  {
    name: "delete_record",
    description: "Delete a record by ID",
    input_schema: {
      type: "object" as const,
      properties: {
        id: { type: "number", description: "Record ID to delete" },
      },
      required: ["id"],
    },
  },
  {
    name: "get_record",
    description: "Get a single record by ID",
    input_schema: {
      type: "object" as const,
      properties: {
        id: { type: "number", description: "Record ID" },
      },
      required: ["id"],
    },
  },
];

async function runTool(name: string, input: Record<string, unknown>): Promise<unknown> {
  switch (name) {
    case "list_records": {
      const { category, limit = 20 } = input as { category?: string; limit?: number };
      let query = db.select().from(records).orderBy(desc(records.createdAt)).limit(limit);
      if (category) {
        const filtered = await db.select().from(records).where(eq(records.category, category)).orderBy(desc(records.createdAt)).limit(limit);
        return filtered;
      }
      return await query;
    }

    case "search_records": {
      const { query } = input as { query: string };
      const pattern = `%${query}%`;
      return await db
        .select()
        .from(records)
        .where(or(like(records.title, pattern), like(records.content, pattern)))
        .orderBy(desc(records.createdAt));
    }

    case "create_record": {
      const { title, content = "", category = "general" } = input as { title: string; content?: string; category?: string };
      const [created] = await db.insert(records).values({ title, content, category }).returning();
      return created;
    }

    case "update_record": {
      const { id, ...updates } = input as { id: number; title?: string; content?: string; category?: string };
      const [updated] = await db
        .update(records)
        .set({ ...updates, updatedAt: new Date() })
        .where(eq(records.id, id))
        .returning();
      return updated ?? { error: "Record not found" };
    }

    case "delete_record": {
      const { id } = input as { id: number };
      const [deleted] = await db.delete(records).where(eq(records.id, id)).returning();
      return deleted ? { success: true, deleted } : { error: "Record not found" };
    }

    case "get_record": {
      const { id } = input as { id: number };
      const [record] = await db.select().from(records).where(eq(records.id, id));
      return record ?? { error: "Record not found" };
    }

    default:
      return { error: `Unknown tool: ${name}` };
  }
}

export default async (req: Request, _context: Context) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  let userMessage: string;
  let history: Array<{ role: "user" | "assistant"; content: string }> = [];

  try {
    const body = await req.json();
    userMessage = body.message;
    history = body.history ?? [];
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!userMessage?.trim()) {
    return new Response(JSON.stringify({ error: "message is required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const messages: Anthropic.MessageParam[] = [
    ...history.map((h) => ({ role: h.role, content: h.content })),
    { role: "user", content: userMessage },
  ];

  let response = await anthropic.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 4096,
    system:
      "You are a helpful database assistant. You help users manage their records using the available tools. " +
      "When users ask to view, create, update, delete, or search records, use the appropriate tool. " +
      "Always confirm actions taken and provide friendly, concise responses. " +
      "When listing records, format them clearly. When creating or updating, confirm what was saved.",
    messages,
    tools: TOOLS,
  });

  // Agentic tool-use loop
  while (response.stop_reason === "tool_use") {
    const toolUseBlocks = response.content.filter((b): b is Anthropic.ToolUseBlock => b.type === "tool_use");

    const toolResults: Anthropic.ToolResultBlockParam[] = await Promise.all(
      toolUseBlocks.map(async (block) => ({
        type: "tool_result" as const,
        tool_use_id: block.id,
        content: JSON.stringify(await runTool(block.name, block.input as Record<string, unknown>)),
      }))
    );

    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });

    response = await anthropic.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 4096,
      system:
        "You are a helpful database assistant. You help users manage their records using the available tools. " +
        "When users ask to view, create, update, delete, or search records, use the appropriate tool. " +
        "Always confirm actions taken and provide friendly, concise responses. " +
        "When listing records, format them clearly. When creating or updating, confirm what was saved.",
      messages,
      tools: TOOLS,
    });
  }

  const textContent = response.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n");

  // Persist conversation turn
  await db.insert(conversations).values([
    { role: "user", content: userMessage },
    { role: "assistant", content: textContent },
  ]);

  return Response.json(
    { response: textContent },
    {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
    }
  );
};

export const config = {
  path: "/api/agent",
};
