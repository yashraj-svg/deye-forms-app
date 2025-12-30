import { useRef, useEffect, useState } from 'react'

export default function SignaturePad({ label, value, onChange }){
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const drawing = useRef(false)
  const last = useRef({ x: 0, y: 0 })
  const [initialized, setInitialized] = useState(false)

  useEffect(()=>{
    const canvas = canvasRef.current
    if(!canvas) return
    const ctx = canvas.getContext('2d')
    const resize = ()=>{
      const ratio = window.devicePixelRatio || 1
      const rect = canvas.getBoundingClientRect()
      canvas.width = Math.floor(rect.width * ratio)
      canvas.height = Math.floor(rect.height * ratio)
      ctx.scale(ratio, ratio)
      ctx.lineCap = 'round'
      ctx.strokeStyle = '#000'
      ctx.lineWidth = 2
      // redraw existing image if value provided
      if(value){
        const img = new Image()
        img.onload = ()=>{ ctx.clearRect(0,0,rect.width,rect.height); ctx.drawImage(img,0,0,rect.width,rect.height) }
        img.src = value
      }
    }
    resize()
    setInitialized(true)
    window.addEventListener('resize', resize)
    return ()=> window.removeEventListener('resize', resize)
  }, [value])

  const pointerDown = (e)=>{
    const canvas = canvasRef.current
    if(!canvas) return
    drawing.current = true
    canvas.setPointerCapture(e.pointerId)
    const rect = canvas.getBoundingClientRect()
    last.current = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }

  const pointerMove = (e)=>{
    const canvas = canvasRef.current
    if(!canvas || !drawing.current) return
    const ctx = canvas.getContext('2d')
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    ctx.beginPath()
    ctx.moveTo(last.current.x, last.current.y)
    ctx.lineTo(x, y)
    ctx.stroke()
    last.current = { x, y }
  }

  const pointerUp = (e)=>{
    const canvas = canvasRef.current
    if(!canvas) return
    drawing.current = false
    try{ canvas.releasePointerCapture && canvas.releasePointerCapture(e.pointerId) }catch(_){}
    // emit data
    const data = canvas.toDataURL('image/png')
    onChange && onChange(data)
  }

  const clear = ()=>{
    const canvas = canvasRef.current
    if(!canvas) return
    const ctx = canvas.getContext('2d')
    const rect = canvas.getBoundingClientRect()
    ctx.clearRect(0,0,rect.width,rect.height)
    onChange && onChange('')
  }

  const onFile = (e)=>{
    const f = e.target.files && e.target.files[0]
    if(!f) return
    const reader = new FileReader()
    reader.onload = ()=>{
      const canvas = canvasRef.current
      if(!canvas) return
      const ctx = canvas.getContext('2d')
      const img = new Image()
      img.onload = ()=>{
        const rect = canvas.getBoundingClientRect()
        ctx.clearRect(0,0,rect.width,rect.height)
        ctx.drawImage(img,0,0,rect.width,rect.height)
        onChange && onChange(canvas.toDataURL('image/png'))
      }
      img.src = reader.result
    }
    reader.readAsDataURL(f)
  }

  return (
    <div className="border rounded p-3">
      <div className="text-sm font-medium mb-2">{label}</div>
      <div ref={containerRef} className="mb-2">
        <canvas
          ref={canvasRef}
          onPointerDown={pointerDown}
          onPointerMove={pointerMove}
          onPointerUp={pointerUp}
          onPointerCancel={pointerUp}
          style={{ width: '100%', height: 200, touchAction: 'none', border: '1px solid #e5e7eb', borderRadius: 4 }}
        />
      </div>
      <div className="flex items-center gap-2">
        <button type="button" onClick={clear} className="px-3 py-1 bg-gray-200 rounded">Clear</button>
        <label className="px-3 py-1 bg-gray-200 rounded cursor-pointer">
          Upload
          <input type="file" accept="image/*" onChange={onFile} className="hidden" />
        </label>
        <div className="text-xs text-gray-500">(Draw or upload image)</div>
      </div>
    </div>
  )
}
