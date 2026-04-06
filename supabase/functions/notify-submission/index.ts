import "@supabase/functions-js/edge-runtime.d.ts";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY")!;
const NOTIFY_EMAILS = ["marie@autacusa.com", "sales@autacusa.com"];

Deno.serve(async (req) => {
  try {
    const payload = await req.json();
    const { type, table, record } = payload;

    if (type !== "INSERT") {
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    let subject = "";
    let body = "";

    if (table === "contacts") {
      subject = `New Contact: ${record.first_name} ${record.last_name}`;
      body = `
        <h2>New Contact Form Submission</h2>
        <table style="border-collapse:collapse;font-family:sans-serif;font-size:14px;">
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Name</td><td style="padding:6px 12px;">${record.first_name} ${record.last_name}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Email</td><td style="padding:6px 12px;"><a href="mailto:${record.email}">${record.email}</a></td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Phone</td><td style="padding:6px 12px;">${record.phone || "—"}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Subject</td><td style="padding:6px 12px;">${record.subject}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Message</td><td style="padding:6px 12px;">${record.message}</td></tr>
        </table>
        <p style="margin-top:20px;font-size:13px;color:#888;"><a href="https://www.autacusa.com/admin.html">View in Dashboard</a></p>
      `;
    } else if (table === "quotes") {
      subject = `New Quote Request: ${record.reference_number}`;
      const timeline = record.timeline || "";
      const isUrgent = timeline === "ASAP / Rush order" || timeline === "Within 2 weeks";
      const urgentTag = isUrgent ? ' <span style="background:#fef2f2;color:#b91c1c;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:bold;">URGENT</span>' : "";
      body = `
        <h2>New Quote Request${urgentTag}</h2>
        <table style="border-collapse:collapse;font-family:sans-serif;font-size:14px;">
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Ref #</td><td style="padding:6px 12px;">${record.reference_number}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Name</td><td style="padding:6px 12px;">${record.first_name} ${record.last_name}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Company</td><td style="padding:6px 12px;">${record.company_name}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Email</td><td style="padding:6px 12px;"><a href="mailto:${record.email}">${record.email}</a></td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Phone</td><td style="padding:6px 12px;">${record.phone}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Product</td><td style="padding:6px 12px;">${record.product_type}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Industry</td><td style="padding:6px 12px;">${record.industry}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Quantity</td><td style="padding:6px 12px;">${record.quantity}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Timeline</td><td style="padding:6px 12px;font-weight:${isUrgent ? "bold;color:#b91c1c" : "normal;color:#333"}">${timeline}</td></tr>
        </table>
        <p style="margin-top:20px;font-size:13px;color:#888;"><a href="https://www.autacusa.com/admin.html">View in Dashboard</a></p>
      `;
    } else if (table === "cord_configs") {
      subject = `New Cord Config: ${record.contact_name}`;
      body = `
        <h2>New Custom Cord Configuration</h2>
        <table style="border-collapse:collapse;font-family:sans-serif;font-size:14px;">
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Name</td><td style="padding:6px 12px;">${record.contact_name}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Company</td><td style="padding:6px 12px;">${record.company}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Email</td><td style="padding:6px 12px;"><a href="mailto:${record.email}">${record.email}</a></td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Phone</td><td style="padding:6px 12px;">${record.phone}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Material</td><td style="padding:6px 12px;">${record.material}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Jacket</td><td style="padding:6px 12px;">${record.jacket || "—"}</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Conductors</td><td style="padding:6px 12px;">${record.conductors || "—"} × ${record.gauge || "—"} AWG</td></tr>
          <tr><td style="padding:6px 12px;font-weight:bold;color:#666;">Shield</td><td style="padding:6px 12px;">${record.shield}</td></tr>
        </table>
        <p style="margin-top:20px;font-size:13px;color:#888;"><a href="https://www.autacusa.com/admin.html">View in Dashboard</a></p>
      `;
    } else {
      return new Response(JSON.stringify({ ok: true, skipped: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: "Autac USA <notifications@autacusa.com>",
        to: NOTIFY_EMAILS,
        subject: `[Autac] ${subject}`,
        html: body,
      }),
    });

    const resData = await res.json();
    return new Response(JSON.stringify({ ok: res.ok, resend: resData }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
});
