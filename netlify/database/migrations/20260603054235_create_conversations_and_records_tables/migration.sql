CREATE TABLE "conversations" (
	"id" serial PRIMARY KEY,
	"role" text NOT NULL,
	"content" text NOT NULL,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "records" (
	"id" serial PRIMARY KEY,
	"title" text NOT NULL,
	"content" text DEFAULT '' NOT NULL,
	"category" text DEFAULT 'general' NOT NULL,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now()
);
