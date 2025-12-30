-- PostgreSQL schema for DEYE forms app

CREATE TABLE IF NOT EXISTS submissions (
  id SERIAL PRIMARY KEY,
  form_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  payload_hash TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
