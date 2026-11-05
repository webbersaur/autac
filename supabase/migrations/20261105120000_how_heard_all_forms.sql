-- Lead source on every form. quotes.how_heard already exists; these two tables
-- need it before submit-form can write the field. Deploy this first: the
-- function fails the insert (and loses the lead) if the column is missing.
ALTER TABLE public.contacts     ADD COLUMN IF NOT EXISTS how_heard text;
ALTER TABLE public.cord_configs ADD COLUMN IF NOT EXISTS how_heard text;
