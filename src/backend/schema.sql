CREATE TABLE "persons" (
  "person_id" integer PRIMARY KEY,
  "person_name" varchar,
  "person_birthdate" date
);

CREATE TABLE "persons_docs" (
  "person_id" integer,
  "doc_id" varchar
);

CREATE TABLE "docs" (
  "doc_id" varchar PRIMARY KEY,
  "doc_path" varchar UNIQUE,
  "doc_text_path" varchar,
  "doc_text_html" varchar,
  "doc_name" varchar,
  "created_at" timestamp
);

CREATE TABLE "labels" (
  "doc_id" varchar,
  "label_id" int PRIMARY KEY,
  "start_char" int,
  "end_char" int,
  "label_content" varchar,
  "label_category_id" int not null
);

CREATE TABLE "label_categories" (
  "label_category_id" int PRIMARY KEY,
  "label_category_name" varchar
);

ALTER TABLE "persons_docs" ADD FOREIGN KEY ("person_id") REFERENCES "persons" ("person_id");

ALTER TABLE "persons_docs" ADD FOREIGN KEY ("doc_id") REFERENCES "docs" ("doc_id");

ALTER TABLE "labels" ADD FOREIGN KEY ("label_category_id") REFERENCES "label_categories" ("label_category_id");

ALTER TABLE "labels" ADD FOREIGN KEY ("doc_id") REFERENCES "docs" ("doc_id");
