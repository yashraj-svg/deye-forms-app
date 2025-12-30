const { listSubmissions, init } = require('../../lib/db')

module.exports = async function handler(req, res){
  // Protected by token
  const token = req.headers['x-admin-token'] || req.query.token
  if(!process.env.ADMIN_TOKEN || token !== process.env.ADMIN_TOKEN){
    return res.status(401).json({error:'Unauthorized'})
  }

  const { form_type, from, to } = req.query
  try{
    await init()
    const rows = await listSubmissions({ form_type, from, to })
    return res.status(200).json({ok:true, rows})
  }catch(err){
    console.error(err)
    return res.status(500).json({error:'Server error'})
  }
}
