const { saveSubmission, init } = require('../../lib/db')

module.exports = async function handler(req, res){
  if(req.method !== 'POST') return res.status(405).json({error:'Method not allowed'})
  const { form_type, payload } = req.body || {}
  if(!form_type || !payload) return res.status(400).json({error:'Missing form_type or payload'})

  try{
    if(!process.env.DATABASE_URL) return res.status(500).json({error:'Database not configured. Set DATABASE_URL environment variable.'})
    await init()
    const saved = await saveSubmission(form_type, payload)
    return res.status(200).json({ok:true, id: saved.id, created_at: saved.created_at})
  }catch(err){
    if(err.code === 'DUPLICATE') return res.status(409).json({error:'Duplicate submission'})
    console.error('[API /submit] Error:', err.code, err.message)
    return res.status(500).json({error: process.env.NODE_ENV === 'development' ? err.message : 'Server error'})
  }
}
