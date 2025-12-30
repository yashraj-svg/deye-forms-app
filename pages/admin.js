import { useState } from 'react'

export default function Admin(){
  const [token, setToken] = useState('')
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)

  async function fetchRecords(){
    setLoading(true)
    const res = await fetch(`/api/records?token=${encodeURIComponent(token)}`)
    if(res.ok){ const d = await res.json(); setRows(d.rows || []) }
    else { alert('Failed to fetch records') }
    setLoading(false)
  }

  function downloadCSV(formType){
    const url = `/api/export?token=${encodeURIComponent(token)}${formType?`&form_type=${encodeURIComponent(formType)}`:''}`
    window.location.href = url
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-semibold mb-4">Admin - Submissions</h2>
        <div className="mb-4 flex gap-2 items-center">
          <input className="border px-3 py-2 rounded w-80" placeholder="ADMIN TOKEN" value={token} onChange={e=>setToken(e.target.value)} />
          <button onClick={fetchRecords} disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">Load</button>
          <button onClick={()=>downloadCSV('repairing')} className="px-3 py-2 border rounded">Export Repairing CSV</button>
          <button onClick={()=>downloadCSV('inward')} className="px-3 py-2 border rounded">Export Inward CSV</button>
          <button onClick={()=>downloadCSV('outward')} className="px-3 py-2 border rounded">Export Outward CSV</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2 border">ID</th>
                <th className="p-2 border">Type</th>
                <th className="p-2 border">Created</th>
                <th className="p-2 border">Payload (JSON)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r=> (
                <tr key={r.id} className="odd:bg-white even:bg-gray-50">
                  <td className="p-2 border align-top">{r.id}</td>
                  <td className="p-2 border align-top">{r.form_type}</td>
                  <td className="p-2 border align-top">{new Date(r.created_at).toLocaleString()}</td>
                  <td className="p-2 border align-top"><pre className="whitespace-pre-wrap text-sm">{JSON.stringify(r.payload, null, 2)}</pre></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
