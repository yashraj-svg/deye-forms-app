const { listSubmissions, init } = require('../../lib/db')

function flatten(payload){
  const out = {}
  function rec(obj, prefix=''){
    if(obj === null || obj === undefined) return
    if(typeof obj !== 'object') { out[prefix] = obj; return }
    if(Array.isArray(obj)) { out[prefix] = obj.join('; '); return }
    for(const k of Object.keys(obj)){
      const key = prefix ? `${prefix}.${k}` : k
      rec(obj[k], key)
    }
  }
  rec(payload, '')
  return out
}

function escapeCsv(val){
  if(val === null || val === undefined) return ''
  const s = String(val)
  if(s.includes(',') || s.includes('\n') || s.includes('"')){
    return '"' + s.replace(/"/g, '""') + '"'
  }
  return s
}

module.exports = async function handler(req, res){
  const token = req.headers['x-admin-token'] || req.query.token
  if(!process.env.ADMIN_TOKEN || token !== process.env.ADMIN_TOKEN){
    return res.status(401).json({error:'Unauthorized'})
  }

  const { form_type, from, to } = req.query
  try{
    await init()
    const rows = await listSubmissions({ form_type, from, to })
    // collect headers
    const all = []
    const headerSet = new Set(['id','form_type','created_at'])
    for(const r of rows){
      const flat = flatten(r.payload)
      all.push({id: r.id, form_type: r.form_type, created_at: r.created_at, ...flat})
      Object.keys(flat).forEach(k=>headerSet.add(k))
    }

    const headers = Array.from(headerSet)
    const csvRows = [headers.map(h=>escapeCsv(h)).join(',')]
    for(const r of all){
      const line = headers.map(h=>escapeCsv(r[h] ?? '')).join(',')
      csvRows.push(line)
    }

    res.setHeader('Content-Type','text/csv')
    res.setHeader('Content-Disposition', `attachment; filename="${form_type||'all'}-export.csv"`)
    res.status(200).send(csvRows.join('\n'))
  }catch(err){
    console.error(err)
    return res.status(500).json({error:'Server error'})
  }
}
