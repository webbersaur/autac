-- Anti-spam + lead-qualification fields
-- Adds: contact-form qualification (company, industry, application),
--       and submission telemetry (page_url, submitter_ip, submitter_country)
--       across all three lead-capture tables.
--
-- Locks down anon inserts on lead tables — only the submit-form edge
-- function (service_role) is authorized to write going forward. Form
-- traffic now passes through Turnstile verification before reaching the DB.

-- ─── contacts: qualification + telemetry ──────────────────────────
ALTER TABLE public.contacts
  ADD COLUMN IF NOT EXISTS company_name      text,
  ADD COLUMN IF NOT EXISTS industry          text,
  ADD COLUMN IF NOT EXISTS application_use   text,
  ADD COLUMN IF NOT EXISTS page_url          text,
  ADD COLUMN IF NOT EXISTS submitter_ip      inet,
  ADD COLUMN IF NOT EXISTS submitter_country text;

-- ─── quotes: telemetry only ───────────────────────────────────────
ALTER TABLE public.quotes
  ADD COLUMN IF NOT EXISTS page_url          text,
  ADD COLUMN IF NOT EXISTS submitter_ip      inet,
  ADD COLUMN IF NOT EXISTS submitter_country text;

-- ─── cord_configs: telemetry only ─────────────────────────────────
ALTER TABLE public.cord_configs
  ADD COLUMN IF NOT EXISTS page_url          text,
  ADD COLUMN IF NOT EXISTS submitter_ip      inet,
  ADD COLUMN IF NOT EXISTS submitter_country text;

-- ─── RLS: revoke anon insert; admin allowlist (incl. Chris) ───────
-- Existing anon-insert policies should be dropped via the Supabase
-- dashboard after confirming their exact names. The block below covers
-- the typical names; uncomment and edit as needed once verified:
--
-- DROP POLICY IF EXISTS "Allow anon insert"             ON public.contacts;
-- DROP POLICY IF EXISTS "Allow anon insert"             ON public.quotes;
-- DROP POLICY IF EXISTS "Allow anon insert"             ON public.cord_configs;
-- DROP POLICY IF EXISTS "anon can insert"               ON public.contacts;
-- DROP POLICY IF EXISTS "anon can insert"               ON public.quotes;
-- DROP POLICY IF EXISTS "anon can insert"               ON public.cord_configs;

-- service_role bypasses RLS automatically, so the submit-form edge
-- function continues to insert without an explicit policy.

-- Update admin allowlist to include chrishauman@gmail.com on every
-- table where the allowlist is referenced. Re-create the policies
-- with the expanded allowlist:
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['contacts','quotes','cord_configs','pricing_access_log','page_views']
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS "Admin allowlist can select %1$s" ON public.%1$s;', t);
    EXECUTE format('DROP POLICY IF EXISTS "Admin allowlist can delete %1$s" ON public.%1$s;', t);
    EXECUTE format($p$CREATE POLICY "Admin allowlist can select %1$s" ON public.%1$s
      FOR SELECT TO authenticated
      USING (auth.jwt() ->> 'email' IN ('marie@autacusa.com','sales@autacusa.com','chrishauman@gmail.com'));$p$, t);
    EXECUTE format($p$CREATE POLICY "Admin allowlist can delete %1$s" ON public.%1$s
      FOR DELETE TO authenticated
      USING (auth.jwt() ->> 'email' IN ('marie@autacusa.com','sales@autacusa.com','chrishauman@gmail.com'));$p$, t);
  END LOOP;
END $$;
