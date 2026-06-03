import type { Context } from "@netlify/functions";
import { db } from "../../db/index.js";
import { records } from "../../db/schema.js";
import { eq } from "drizzle-orm";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Content-Type": "application/json",
};

export default async (req: Request, _context: Context) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS });
  }

  const url = new URL(req.url);
  const idParam = url.searchParams.get("id");

  if (req.method === "GET") {
    if (idParam) {
      const [record] = await db.select().from(records).where(eq(records.id, Number(idParam)));
      return record
        ? Response.json(record, { headers: CORS })
        : new Response(JSON.stringify({ error: "Not found" }), { status: 404, headers: CORS });
    }
    const all = await db.select().from(records).orderBy(records.createdAt);
    return Response.json(all, { headers: CORS });
  }

  if (req.method === "POST") {
    const { title, content = "", category = "general" } = await req.json();
    if (!title) return new Response(JSON.stringify({ error: "title required" }), { status: 400, headers: CORS });
    const [created] = await db.insert(records).values({ title, content, category }).returning();
    return Response.json(created, { status: 201, headers: CORS });
  }

  if (req.method === "PUT") {
    if (!idParam) return new Response(JSON.stringify({ error: "id required" }), { status: 400, headers: CORS });
    const updates = await req.json();
    const [updated] = await db
      .update(records)
      .set({ ...updates, updatedAt: new Date() })
      .where(eq(records.id, Number(idParam)))
      .returning();
    return updated
      ? Response.json(updated, { headers: CORS })
      : new Response(JSON.stringify({ error: "Not found" }), { status: 404, headers: CORS });
  }

  if (req.method === "DELETE") {
    if (!idParam) return new Response(JSON.stringify({ error: "id required" }), { status: 400, headers: CORS });
    const [deleted] = await db.delete(records).where(eq(records.id, Number(idParam))).returning();
    return deleted
      ? Response.json({ success: true }, { headers: CORS })
      : new Response(JSON.stringify({ error: "Not found" }), { status: 404, headers: CORS });
  }

  return new Response("Method not allowed", { status: 405, headers: CORS });
};

export const config = {
  path: "/api/records",
};
