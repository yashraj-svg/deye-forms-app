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

const TextArea = ({label, name, onChange, rows=3}) => (
  <label className="block mb-3">
    <div className="text-sm font-medium">{label}</div>
    <textarea name={name} onChange={onChange} className="mt-1 w-full border rounded px-3 py-2" rows={rows}></textarea>
  </label>
)

export default function InwardForm(){
  const [form, setForm] = useState({})
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = (e) => {
    const { name, value } = e.target
    setForm(prev=> ({...prev, [name]: value}))
  }

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try{
      const res = await fetch('/api/submit', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({form_type: 'inward', payload: form})})
      if(res.ok){ setStatus({ok:true, msg:'Saved'}) ; e.target.reset(); setForm({}) }
      else { const d = await res.json(); setStatus({ok:false, msg: d.error || 'Failed'}) }
    }catch(err){ setStatus({ok:false, msg: err.message}) }
    setLoading(false)
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Inward Tracking</h3>
      <form onSubmit={submit}>
        <fieldset className="border-b pb-4 mb-4">
          <legend className="text-md font-semibold mb-3">Contact Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Email" name="email" required onChange={handle} type="email" />
            <SelectInput label="Received By" name="received_by" required onChange={handle} options={['Shrikant','Rushikesh','Sagar K','Arun','Vinayak','Bhuvan','Sandeep','Pranav','Jayesh','Sanjay','Mukesh']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4 mb-4">
          <legend className="text-md font-semibold mb-3">Customer Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Customer Abbreviation" name="customer_abbrev" required onChange={handle} options={['Aps','Deye','Evvo','Feston','Greenedge','Mindra','Powerone','Solaryan','Utl','Vsole','Waaree','Other']} />
            <TextInput label="Customer Name" name="customer_name" required onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4 mb-4">
          <legend className="text-md font-semibold mb-3">Location Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Received From Location" name="received_from_location" onChange={handle} />
            <TextInput label="Received From District" name="received_from_district" onChange={handle} />
            <SelectInput label="Received From State" name="received_from_state" onChange={handle} options={['Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Jammu & Kashmir']} />
            <TextInput label="Pincode" name="pincode" onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4 mb-4">
          <legend className="text-md font-semibold mb-3">Inverter / Battery Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Inverter ID / Battery ID" name="inverter_id" required onChange={handle} />
            <SelectInput label="Inverter Specifications" name="inverter_specs" required onChange={handle} options={['1PH - Hybrid','3PH - Hybrid','1PH - Ongrid','3PH - Ongrid','All In One - Hybrid','Micro Inverter','Battery']} />
            <SelectInput label="Inverter Ratings" name="inverter_ratings" onChange={handle} options={['2.2 KW','3 KW','3.3 KW','4 KW','5 KW','6 KW','8 KW','10 KW','12 KW','15 KW','18 KW','20 KW','25 KW','30 KW','33 KW','35 KW','40 KW','50 KW','60 KW','75 KW','80 KW','100 KW','125 KW','136 KW']} />
            <SelectInput label="Battery" name="battery" onChange={handle} options={['RW - L 2.5 Neutral','RW - M 5.3 Neutral','RW - M 5.3 Pro Neutral (M6)','RW - M 6.1 Neutral','RW - M 6.1 B Neutral No Remark','SE - G 5.1 - Pro B Neutral No Remark','AI - W 5.1 Neutral','AI - W 5.1 - B Neutral No Remark','BOS - GM 5.1 Neutral','GB - LM 4.0 Neutral','GB - LB Neutral','SE - G 5.3','SE - G 5.3 Pro','SE - F 5','SE - F5 Plus']} />
            <SelectInput label="No of MPPT" name="no_of_mppt" onChange={handle} options={['1','2','3','4','5','6','7','8']} />
            <SelectInput label="Current / MPPT" name="current_mppt" onChange={handle} options={['1','3','18','20','40']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4 mb-4">
          <legend className="text-md font-semibold mb-3">Service Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Case Handled By" name="case_handled_by" onChange={handle} options={['Mr. Rakesh Kumar','Mr. Pranav Rajeshbhai Dalwadi','Mr. Prajapati Vishal Atmarambhai','Mr. Bhuvan D','Mr. Jayesh khodabhai Solanki','Mr. Mahamadhusen Daud Mahagonde','Mr. Ranjan kumar Yadav','Mr. Mohit Kumawat','Mr. Tirupathi Vasu','Mr. Elson Eldo','Mr. Arun Hanumantrao Kardile','Mr. Sagar Prakash Katkar','Mr. Uttam Naskar','Mr. Tanaji Sampath Jadhav','Mr. Shrikant Chandu Rathod','Mr. Rushikesh Mohan Kolape','Mr. Sagar LaxmanBhai Wagh','Mr. Sanjay Kumar C N','Mr. Harihara Vishnu Prabu B','Mr. Sandeep Kumar','Mr. Harpreet Singh','Mr. Kankan Mandal','Mr. Mukesh']} />
            <SelectInput label="Reason" name="reason" required onChange={handle} options={['Repairing Purpose','Replacement Purpose']} />
            <SelectInput label="Transportation Mode" name="transportation_mode" onChange={handle} options={['Bigship','Blue Dart','Anjani','Other']} />
            <TextInput label="AWB / LR Number" name="awb_lr_number" onChange={handle} />
          </div>
        </fieldset>

        <TextArea label="Remarks" name="remarks" onChange={handle} rows={3} />

        <div className="mt-4 flex items-center gap-3">
          <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white">{loading? 'Saving...':'Submit'}</button>
          {status && <div className={`${status.ok? 'text-green-600':'text-red-600'}`}>{status.msg}</div>}
        </div>
      </form>
    </div>
  )
}
