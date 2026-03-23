import { jwtVerify } from 'jose';
import { readFileSync } from 'fs';
import { join } from 'path';

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
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

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Extract Bearer token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Pricing access required' });
    }

    const token = authHeader.slice(7);
    const secret = new TextEncoder().encode(process.env.JWT_SECRET);

    // Verify the access JWT
    let payload;
    try {
      const result = await jwtVerify(token, secret);
      payload = result.payload;
    } catch (err) {
      return res.status(401).json({ error: 'Pricing access required' });
    }

    // Ensure this is a verified access token
    if (!payload.verified) {
      return res.status(401).json({ error: 'Pricing access required' });
    }

    // Read and return pricing data
    const pricingPath = join(process.cwd(), 'data', 'pricing.json');
    const pricingData = JSON.parse(readFileSync(pricingPath, 'utf-8'));

    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).json(pricingData);
  } catch (err) {
    console.error('pricing error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
