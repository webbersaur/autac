-- Drop any anon/public INSERT policies on the lead-capture tables.
--
-- After 20260509120000_anti_spam_fields.sql, the only path into these
-- tables is the submit-form edge function (running with service_role,
-- which bypasses RLS). Any remaining anon-insert policy lets attackers
-- POST directly to the Supabase REST API and skip Turnstile entirely.
--
-- This block self-discovers and drops INSERT-only policies for anon/public.
-- Policies with cmd='ALL' are flagged but not dropped automatically — those
-- need manual review since dropping them would also remove SELECT/UPDATE
-- access for those roles.

DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT tablename, policyname, cmd, roles
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename IN ('contacts', 'quotes', 'cord_configs')
      AND cmd IN ('INSERT', 'ALL')
      AND ('anon' = ANY(roles) OR 'public' = ANY(roles))
  LOOP
    IF r.cmd = 'ALL' THEN
      RAISE WARNING
        'Skipping ALL-command policy on %.%: % (manual review needed — dropping would also remove SELECT/UPDATE/DELETE access)',
        'public', r.tablename, r.policyname;
    ELSE
      EXECUTE format('DROP POLICY %I ON public.%I', r.policyname, r.tablename);
      RAISE NOTICE 'Dropped INSERT policy: %.% / % (roles: %)',
        'public', r.tablename, r.policyname, r.roles;
    END IF;
  END LOOP;
END $$;
