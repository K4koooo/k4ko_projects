import { NextRequest } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://backend:8080'

export async function POST(_request: NextRequest) {
  const backendRes = await fetch(`${BACKEND_URL}/ingest`, { method: 'POST' })
  const data = await backendRes.json()
  return Response.json(data, { status: backendRes.status })
}
