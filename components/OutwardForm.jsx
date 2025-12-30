import { useState } from 'react'

const TextInput = ({label, name, required=false, onChange, type='text'}) => (
  <label className="block mb-3">
    <div className="text-sm font-medium">{label} {required && <span className="text-red-500">*</span>}</div>
    <input type={type} name={name} required={required} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" />
  </label>
)

const SelectInput = ({label, name, required=false, onChange, options}) => (
  <label className="block mb-3">
    <div className="text-sm font-medium">{label} {required && <span className="text-red-500">*</span>}</div>
    <select name={name} required={required} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2">
      <option value="">Select...</option>
      {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
    </select>
  </label>
)

const TextArea = ({label, name, onChange, required=false, rows=3}) => (
  <label className="block mb-3">
    <div className="text-sm font-medium">{label} {required && <span className="text-red-500">*</span>}</div>
    <textarea name={name} onChange={onChange} required={required} className="mt-1 w-full border rounded px-3 py-2" rows={rows}></textarea>
  </label>
)

export default function OutwardForm(){
  const [form, setForm] = useState({})
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showReplaced, setShowReplaced] = useState(false)

  const handle = (e) => {
    const { name, value } = e.target
    setForm(prev=> ({...prev, [name]: value}))
    if(name === 'inverter_replaced'){
      setShowReplaced(value === 'Yes')
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try{
      const res = await fetch('/api/submit', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({form_type: 'outward', payload: form})})
      if(res.ok){ setStatus({ok:true, msg:'Saved'}) ; e.target.reset(); setForm({}) }
      else { const d = await res.json(); setStatus({ok:false, msg: d.error || 'Failed'}) }
    }catch(err){ setStatus({ok:false, msg: err.message}) }
    setLoading(false)
  }

  return (
    <div className="card max-w-4xl">
      <h3 className="text-lg font-semibold mb-4">Outward Tracking</h3>
      <form onSubmit={submit} className="space-y-6">
        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Authorization</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Sent By" name="sent_by" required onChange={handle} options={['Shrikant','Rushikesh','Sagar K','Arun','Vinayak','Bhuvan','Sandeep','Pranav','Jayesh','Sanjay','Mukesh']} />
            <SelectInput label="Approved By" name="approved_by" required onChange={handle} options={['Sagar K','Tanaji','Mahammad','Snehal','Sandeep','Akshay Sir','Bhuvan','Pranav','Rakesh']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Company Information</legend>
          <SelectInput label="Company Abbreviation" name="company_abbrev" required onChange={handle} options={['Aps','Deye','Evvo','Feston','Greenedge','Ksolare','Mindra','Powerone','Solaryaan','Utl','Vsole','Waaree','Other']} />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Destination Details</legend>
          <div className="grid gap-4">
            <TextInput label="Inverter Sent To Company Name" name="sent_to_company" required onChange={handle} />
            <TextInput label="Sent To Address" name="sent_to_address" required onChange={handle} />
            <div className="grid md:grid-cols-3 gap-4">
              <TextInput label="Sent To District" name="sent_to_district" required onChange={handle} />
              <SelectInput label="Sent To State" name="sent_to_state" required onChange={handle} options={['Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Jammu & Kashmir']} />
              <TextInput label="Pincode" name="pincode" required onChange={handle} />
            </div>
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Inverter Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Inverter ID - Outward" name="inverter_id_outward" required onChange={handle} />
            <SelectInput label="Inverter Specification" name="inverter_spec" required onChange={handle} options={['1PH - Hybrid','3PH - Hybrid','1PH - Ongrid','3PH - Ongrid','All In One - Hybrid','Micro Inverter','Battery']} />
            <SelectInput label="Inverter Rating" name="inverter_rating" onChange={handle} options={['2.2 KW','3 KW','3.3 KW','4 KW','5 KW','6 KW','8 KW','10 KW','12 KW','15 KW','18 KW','20 KW','25 KW','30 KW','33 KW','35 KW','40 KW','50 KW','60 KW','75 KW','80 KW','100 KW','125 KW','136 KW']} />
            <SelectInput label="Battery" name="battery" onChange={handle} options={['RW - L 2.5 Neutral','RW - M 5.3 Neutral','RW - M 5.3 Pro Neutral (M6)','RW - M 6.1 Neutral','RW - M 6.1 B Neutral No Remark','SE - G 5.1 - Pro B Neutral No Remark','AI - W 5.1 Neutral','AI - W 5.1 - B Neutral No Remark','BOS - GM 5.1 Neutral','GB - LM 4.0 Neutral','GB - LB Neutral','SE - G 5.3','SE - G 5.3 Pro','SE - F 5','SE - F5 Plus','Other']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Replacement Status</legend>
          <SelectInput label="Inverter Replaced?" name="inverter_replaced" required onChange={handle} options={['Yes','No']} />
          
          {showReplaced && (
            <>
              <SelectInput label="Which Inverter replaced with old?" name="replacement_type" onChange={handle} options={['New Inverter Replaced','Service Inverter Replaced']} />
              <TextInput label="Inverter ID - Inward (If replaced)" name="inverter_id_inward" onChange={handle} />
            </>
          )}
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Delivery Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Delivered Through" name="delivered_through" required onChange={handle} options={['Bigship','Blue Dart','Anjani','Other']} />
            <TextInput label="AWB Number" name="awb_number" required onChange={handle} />
          </div>
        </fieldset>

        <div className="mt-4 flex items-center gap-3">
          <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white">{loading? 'Saving...':'Submit'}</button>
          {status && <div className={`${status.ok? 'text-green-600':'text-red-600'}`}>{status.msg}</div>}
        </div>
      </form>
    </div>
  )
}
