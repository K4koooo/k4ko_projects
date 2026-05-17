import { NextRequest } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://backend:8080'

export async function GET(_request: NextRequest) {
  try {
    const backendRes = await fetch(`${BACKEND_URL}/stats`, {
      next: { revalidate: 0 },
    })
    const data = await backendRes.json()
    return Response.json(data, { status: backendRes.status })
  } catch {
    return Response.json(
      { total_documents: 0, source_files: [], collection_name: '' },
      { status: 503 }
    )
  }
}
