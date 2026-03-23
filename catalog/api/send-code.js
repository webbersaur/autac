import { SignJWT } from 'jose';
import { Resend } from 'resend';
import { createHash, randomInt } from 'crypto';

const resend = new Resend(process.env.RESEND_API_KEY);

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
}

export default async function handler(req, res) {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, corsHeaders());
    return res.end();
  }

  // Set CORS headers on all responses
  Object.entries(corsHeaders()).forEach(([key, value]) => {
    res.setHeader(key, value);
  });

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { email } = req.body || {};

    // Validate email
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ error: 'Valid email address required' });
    }

    // Generate secure 6-digit code
    const code = String(randomInt(100000, 999999));

    // Hash the code with SHA-256 before storing in JWT
    const codeHash = createHash('sha256').update(code).digest('hex');

    // Create a short-lived "pending" JWT (10 min) with email + hashed code
    const secret = new TextEncoder().encode(process.env.JWT_SECRET);
    const pendingToken = await new SignJWT({ email, codeHash, type: 'pending' })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('10m')
      .sign(secret);

    // Send code via Resend
    const { error: sendError } = await resend.emails.send({
      from: 'Autac Catalog <catalog@autacusa.com>',
      to: [email],
      subject: 'Your Autac Catalog Access Code',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0; padding:0; background-color:#f4f4f5; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5; padding:40px 20px;">
            <tr>
              <td align="center">
                <table width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                  <tr>
                    <td style="background-color:#1a1a2e; padding:24px 32px;">
                      <h1 style="margin:0; color:#ffffff; font-size:20px; font-weight:600; letter-spacing:0.5px;">AUTAC</h1>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:32px;">
                      <p style="margin:0 0 16px; color:#374151; font-size:15px; line-height:1.6;">
                        Your verification code for the Autac product catalog is:
                      </p>
                      <div style="background-color:#f0f4ff; border:2px solid #3b82f6; border-radius:8px; padding:20px; text-align:center; margin:24px 0;">
                        <span style="font-size:36px; font-weight:700; letter-spacing:8px; color:#1a1a2e; font-family:'Courier New', monospace;">${code}</span>
                      </div>
                      <p style="margin:16px 0 0; color:#6b7280; font-size:13px; line-height:1.5;">
                        This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td style="background-color:#f9fafb; padding:16px 32px; border-top:1px solid #e5e7eb;">
                      <p style="margin:0; color:#9ca3af; font-size:12px;">
                        Autac USA &mdash; Pneumatic Automation Components
                      </p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </body>
        </html>
      `,
    });

    if (sendError) {
      console.error('Resend error:', sendError);
      return res.status(500).json({ error: 'Failed to send verification email' });
    }

    return res.status(200).json({ success: true, token: pendingToken });
  } catch (err) {
    console.error('send-code error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
