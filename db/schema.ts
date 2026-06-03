import { pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";

export const records = pgTable("records", {
  id: serial().primaryKey(),
  title: text("title").notNull(),
  content: text("content").notNull().default(""),
  category: text("category").notNull().default("general"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const conversations = pgTable("conversations", {
  id: serial().primaryKey(),
  role: text("role").notNull(),
  content: text("content").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});
