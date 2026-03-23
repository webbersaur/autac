import { SignJWT, jwtVerify } from 'jose';
import { createHash } from 'crypto';

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

  Object.entries(corsHeaders()).forEach(([key, value]) => {
    res.setHeader(key, value);
  });

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { token, code } = req.body || {};

    if (!token || !code) {
      return res.status(400).json({ error: 'Token and code are required' });
    }

    const secret = new TextEncoder().encode(process.env.JWT_SECRET);

    // Verify the pending JWT
    let payload;
    try {
      const result = await jwtVerify(token, secret);
      payload = result.payload;
    } catch (err) {
      return res.status(401).json({ error: 'Invalid or expired code' });
    }

    // Ensure this is a pending token
    if (payload.type !== 'pending') {
      return res.status(401).json({ error: 'Invalid or expired code' });
    }

    // Hash the submitted code and compare to stored hash
    const submittedHash = createHash('sha256').update(String(code)).digest('hex');

    if (submittedHash !== payload.codeHash) {
      return res.status(401).json({ error: 'Invalid or expired code' });
    }

    // Code is valid — issue a long-lived access JWT (60 days)
    const accessToken = await new SignJWT({
      email: payload.email,
      verified: true,
    })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('60d')
      .sign(secret);

    return res.status(200).json({ success: true, token: accessToken });
  } catch (err) {
    console.error('verify-code error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
