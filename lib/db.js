const { Pool } = require('pg')
const crypto = require('crypto')

const connectionString = process.env.DATABASE_URL || ''
if(!connectionString){
  console.warn('Warning: DATABASE_URL not set. API calls will fail until configured.')
}

const pool = new Pool({ connectionString })

async function init(){
  const client = await pool.connect()
  try{
    await client.query(`
      CREATE TABLE IF NOT EXISTS submissions (
        id SERIAL PRIMARY KEY,
        form_type TEXT NOT NULL,
        payload JSONB NOT NULL,
        payload_hash TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
      );
    `)
  }finally{
    client.release()
  }
}

function hashPayload(payload){
  return crypto.createHash('sha256').update(JSON.stringify(payload)).digest('hex')
}

async function saveSubmission(form_type, payload){
  const hash = hashPayload(payload)
  const client = await pool.connect()
  try{
    const res = await client.query(
      'INSERT INTO submissions (form_type, payload, payload_hash) VALUES ($1, $2, $3) RETURNING id, created_at',
      [form_type, payload, hash]
    )
    return res.rows[0]
  }catch(err){
    if(err.code === '23505'){
      const duplicate = new Error('Duplicate submission')
      duplicate.code = 'DUPLICATE'
      throw duplicate
    }
    throw err
  }finally{
    client.release()
  }
}

async function listSubmissions({form_type, from, to} = {}){
  const client = await pool.connect()
  try{
    let sql = 'SELECT id, form_type, payload, created_at FROM submissions WHERE 1=1'
    const params = []
    if(form_type){ params.push(form_type); sql += ` AND form_type = $${params.length}` }
    if(from){ params.push(from); sql += ` AND created_at >= $${params.length}` }
    if(to){ params.push(to); sql += ` AND created_at <= $${params.length}` }
    sql += ' ORDER BY created_at DESC LIMIT 1000'
    const res = await client.query(sql, params)
    return res.rows
  }finally{
    client.release()
  }
}

module.exports = { pool, init, saveSubmission, listSubmissions }
