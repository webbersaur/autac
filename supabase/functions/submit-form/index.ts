import "@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "@supabase/supabase-js";
import { isDisposableEmail } from "../_shared/disposable.ts";

const TURNSTILE_SECRET_KEY = Deno.env.get("TURNSTILE_SECRET_KEY") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const ALLOWED_ORIGINS = new Set([
  "https://autacusa.com",
  "https://www.autacusa.com",
  "https://webbersaur.github.io",
]);

function isAllowedOrigin(origin: string | null): boolean {
  if (!origin) return false;
  if (ALLOWED_ORIGINS.has(origin)) return true;
  // Allow any localhost / 127.0.0.1 port for local dev
  return /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
}

function corsHeaders(origin: string | null): Record<string, string> {
  const allow = isAllowedOrigin(origin) ? origin! : "https://www.autacusa.com";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey, x-client-info",
    "Vary": "Origin",
  };
}

function json(body: unknown, status: number, origin: string | null): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(origin) },
  });
}

async function verifyTurnstile(token: string, ip: string | null): Promise<boolean> {
  if (!TURNSTILE_SECRET_KEY) {
    // Soft-fail open ONLY in local dev (no secret configured) — production
    // deploys must have TURNSTILE_SECRET_KEY set or every request is denied.
    console.warn("[submit-form] TURNSTILE_SECRET_KEY not set — denying.");
    return false;
  }
  const body = new URLSearchParams();
  body.set("secret", TURNSTILE_SECRET_KEY);
  body.set("response", token);
  if (ip) body.set("remoteip", ip);
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body,
  });
  if (!res.ok) return false;
  const data = await res.json() as { success?: boolean };
  return data.success === true;
}

const FORM_TYPES = new Set(["contact", "quote", "cord_config"]);

Deno.serve(async (req) => {
  const origin = req.headers.get("origin");

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(origin) });
  }
  if (req.method !== "POST") {
    return json({ error: "method_not_allowed" }, 405, origin);
  }

  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "invalid_json" }, 400, origin);
  }

  const formType = String(payload.form_type ?? "");
  if (!FORM_TYPES.has(formType)) {
    return json({ error: "invalid_form_type" }, 400, origin);
  }

  const token = String(payload.turnstile_token ?? "");
  if (!token) {
    return json({ error: "missing_turnstile_token" }, 400, origin);
  }

  const ip =
    req.headers.get("cf-connecting-ip") ??
    (req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || null);
  const country = req.headers.get("cf-ipcountry");

  const verified = await verifyTurnstile(token, ip);
  if (!verified) {
    return json({ error: "turnstile_failed" }, 400, origin);
  }

  const email = String(payload.email ?? "").trim().toLowerCase();
  if (email && isDisposableEmail(email)) {
    return json({ error: "disposable_email" }, 400, origin);
  }

  const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
    auth: { persistSession: false },
  });

  const pageUrl = String(payload.page_url ?? "").slice(0, 500) || null;
  const telemetry = {
    page_url: pageUrl,
    submitter_ip: ip,
    submitter_country: country || null,
  };

  let row: Record<string, unknown>;
  let table: string;

  if (formType === "contact") {
    table = "contacts";
    row = {
      first_name: String(payload.first_name ?? "").slice(0, 100),
      last_name: String(payload.last_name ?? "").slice(0, 100),
      email,
      phone: payload.phone ? String(payload.phone).slice(0, 50) : null,
      subject: String(payload.subject ?? "").slice(0, 100),
      message: String(payload.message ?? "").slice(0, 5000),
      company_name: String(payload.company_name ?? "").slice(0, 200) || null,
      industry: String(payload.industry ?? "").slice(0, 100) || null,
      application_use: String(payload.application_use ?? "").slice(0, 2000) || null,
      ...telemetry,
    };
  } else if (formType === "quote") {
    table = "quotes";
    const env = Array.isArray(payload.environment)
      ? payload.environment.map((v) => String(v).slice(0, 100)).slice(0, 20)
      : null;
    row = {
      reference_number: String(payload.reference_number ?? "").slice(0, 50),
      product_type: String(payload.product_type ?? "").slice(0, 100),
      part_numbers: payload.part_numbers ? String(payload.part_numbers).slice(0, 1000) : null,
      industry: String(payload.industry ?? "").slice(0, 100),
      application: String(payload.application ?? "").slice(0, 2000),
      environment: env,
      quantity: String(payload.quantity ?? "").slice(0, 100),
      timeline: String(payload.timeline ?? "").slice(0, 100),
      order_frequency: payload.order_frequency ? String(payload.order_frequency).slice(0, 100) : null,
      additional_notes: payload.additional_notes ? String(payload.additional_notes).slice(0, 5000) : null,
      first_name: String(payload.first_name ?? "").slice(0, 100),
      last_name: String(payload.last_name ?? "").slice(0, 100),
      company_name: String(payload.company_name ?? "").slice(0, 200),
      email,
      phone: String(payload.phone ?? "").slice(0, 50),
      job_title: payload.job_title ? String(payload.job_title).slice(0, 100) : null,
      how_heard: payload.how_heard ? String(payload.how_heard).slice(0, 100) : null,
      ...telemetry,
    };
  } else {
    table = "cord_configs";
    const s = (key: string, max = 200): string | null => {
      const v = payload[key];
      if (v == null || v === "") return null;
      return String(v).slice(0, max);
    };
    row = {
      material: s("material", 100) ?? "",
      jacket: s("jacket", 100),
      conductors: s("conductors", 50),
      gauge: s("gauge", 50),
      conductor_type: s("conductor_type", 100),
      stranding: s("stranding", 100),
      shield: s("shield", 100) ?? "",
      drain: s("drain", 50),
      ul_required: s("ul_required", 50),
      retracted_length: s("retracted_length", 50),
      extended_length: s("extended_length", 50),
      coil_od: s("coil_od", 50),
      cable_od: s("cable_od", 50),
      jacket_color: s("jacket_color", 100),
      color_code: s("color_code", 100),
      tangent_a_type: s("tangent_a_type", 100),
      tangent_a_length: s("tangent_a_length", 50),
      tangent_a_roj: s("tangent_a_roj", 50),
      tangent_b_type: s("tangent_b_type", 100),
      tangent_b_length: s("tangent_b_length", 50),
      tangent_b_roj: s("tangent_b_roj", 50),
      comments: s("comments", 5000),
      contact_name: s("contact_name", 200) ?? "",
      company: s("company", 200) ?? "",
      email,
      phone: s("phone", 50) ?? "",
      ...telemetry,
    };
  }

  const { error } = await sb.from(table).insert([row]);
  if (error) {
    console.error("[submit-form] insert failed", { table, error });
    return json({ error: "insert_failed", detail: error.message }, 500, origin);
  }

  return json({ ok: true }, 200, origin);
});
