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

const CheckboxGroup = ({label, name, options, onChange, values={}}) => {
  const sanitize = (str) => str.replace(/[^a-z0-9]/gi, '_').toLowerCase()
  return (
    <fieldset className="mb-3">
      <div className="text-sm font-medium mb-2">{label}</div>
      <div className="space-y-2">
        {options.map(opt => {
          const key = sanitize(opt)
          return (
            <label key={opt} className="flex items-center gap-2">
              <input type="checkbox" name={key} onChange={onChange} checked={values[key] || false} />
              <span>{opt}</span>
            </label>
          )
        })}
      </div>
    </fieldset>
  )
}

export default function RepairingForm(){
  const [form, setForm] = useState({})
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [faultProblems, setFaultProblems] = useState({})

  const handle = (e) => {
    const { name, value } = e.target
    setForm(prev=> ({...prev, [name]: value}))
  }

  const handleCheckbox = (e) => {
    const { name, checked } = e.target
    if(checked) {
      setFaultProblems(prev=> ({...prev, [name]: checked}))
    } else {
      setFaultProblems(prev=> {
        const updated = {...prev}
        delete updated[name]
        return updated
      })
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try{
      const res = await fetch('/api/submit', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({form_type: 'repairing', payload: {...form, fault_problems: faultProblems}})})
      if(res.ok){ setStatus({ok:true, msg:'Saved'}) ; e.target.reset(); setForm({}); setFaultProblems({}) }
      else { const d = await res.json(); setStatus({ok:false, msg: d.error || 'Failed'}) }
    }catch(err){ setStatus({ok:false, msg: err.message}) }
    setLoading(false)
  }

  return (
    <div className="card max-w-4xl">
      <h3 className="text-lg font-semibold mb-4">Daily Inverter / PCB Repair Form</h3>
      <form onSubmit={submit} className="space-y-6">
        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Customer Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Customer Abbreviation" name="customer_abbrev" required onChange={handle} options={['Alternative Energy','Aps','Arkay Solar','Avirat Energy','Brither World Engineering Works','Ceyone Solar','Chetanbhai Trimandir','Deye','Eco Active Energy & Solution','Envest Energy Solutions Llp','Evaanta Solar','Evvo','Ferus Solar Energy Solution','Feston','Fine Vibes Renewable Pvt Ltd (Cg)','Glowx','Green Energy','Green Era','Green Watt Energy','Greenedge','Gujarat Energy','Invergy','Jaffins Enterprise','Jay Aditya Solar','Ksolare','Madhav Enterprise','Madhya Pradesh Solar9','Mindra','Mp Engineering','Navi Energy','Next Tech Solar Energy','Nil Electronics','Nk Construction','Powerone','Pushan Renewable Energy Pvt Ltd','Radiant Sun Energy','Railway Station Dhanera','Roshni Solar','Rudra Solar','Saan Electrical','Shantimani Enterprises','Smart Solar Bidgely Solution Pvt Ltd','Solaryaan','Suntech Energy','Swami Solar','Symbroz Solar Pvt Ltd','Tecnogoods Energy','Trambaka Solar Pvt Ltd','Urja Strot','Utl','Utl Solar','Vsole','Waaree','Water Sun Solar','Watthut','Yamas Solar']} />
            <TextInput label="Case Number" name="case_number" onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Repairing Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Repairing Object" name="repairing_object" required onChange={handle} options={['Inverter','PCB','Battery','BMS']} />
            <TextInput label="Inverter ID (Multiple - separate with comma)" name="inverter_id" onChange={handle} />
            <SelectInput label="Inverter / PCB Specification" name="inverter_spec" required onChange={handle} options={['1PH - Hybrid','3PH - Hybrid','1PH - Ongrid','3PH - Ongrid','All In One - Hybrid','Other']} />
            <SelectInput label="Inverter / PCB Rating" name="inverter_rating" onChange={handle} options={['2.2 KW','3 KW','3.3 KW','4 KW','5 KW','6 KW','8 KW','10 KW','12 KW','15 KW','18 KW','20 KW','25 KW','30 KW','33 KW','35 KW','40 KW','50 KW','60 KW','75 KW','80 KW','100 KW','125 KW','136 KW']} />
            <SelectInput label="Battery" name="battery" onChange={handle} options={['RW - L 2.5 Neutral','RW - M 5.3 Neutral','RW - M 5.3 Pro Neutral (M6)','RW - M 6.1 Neutral','RW - M 6.1 B Neutral No Remark','SE - G 5.1 - Pro B Neutral No Remark','AI - W 5.1 Neutral','AI - W 5.1 - B Neutral No Remark','BOS - GM 5.1 Neutral','GB - LM 4.0 Neutral','GB - LB Neutral','SE - G 5.3','SE - G 5.3 Pro','SE - F 5','Other']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Fault Details</legend>
          <CheckboxGroup label="Fault Problem In (select all that apply)" name="fault_problem" options={['IGBT Board','Relay Board','Control Board','Display Board','Power Board','Generation Relay','Grid Relay','Communication Card','IGBT','Resistor','Capacitor','Opto','SPD on PV Board','Other']} onChange={handleCheckbox} values={faultProblems} />
          <TextArea label="Fault Problem Description" name="fault_description" required onChange={handle} rows={3} />
          <TextInput label="PCBA Serial Number (If repairing PCB)" name="pcba_serial" onChange={handle} />
          <TextArea label="Fault Location" name="fault_location" required onChange={handle} rows={2} />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Repair Work</legend>
          <TextArea label="Repair Content" name="repair_content" required onChange={handle} rows={3} />
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Repaired By" name="repaired_by" required onChange={handle} options={['Arun','Bhuvan','Jayesh','Kankan','Mukesh','Neeraj','Pranav','Rushikesh','Sagar W','Sagar K','Sandeep','Shashikant','Shivendra','Shrikant','Vishal','Vivek','Sanjay Kumar','Rahul','Vinayak Sutar','Harihara','Ranjan','Harpreet Singh']} />
            <SelectInput label="Tested By" name="tested_by" required onChange={handle} options={['Arun','Bhuvan','Jayesh','Kankan','Mukesh','Neeraj','Pranav','Rushikesh','Sagar','Sagar K','Sandeep','Shashikant','Shivendra','Shrikant','Vishal','Vivek','Rahul','Sanjay Kumar','Vinayak Sutar','Harihara','Ranjan']} />
            <TextInput label="Repaired On (Date)" name="repaired_on_date" type="date" required onChange={handle} />
            <SelectInput label="Repaired On (Location)" name="repaired_location" required onChange={handle} options={['Repaired On Site','Repaired At Service Center']} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Status & Remarks</legend>
          <SelectInput label="Remark" name="remark" required onChange={handle} options={['Test Failed','Unable To Repair','Pending Cause of Component','Just Tested','Repairing Done']} />
          <TextArea label="If Pending - Mention Component Name" name="pending_component" onChange={handle} rows={2} />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Images</legend>
          <p className="text-sm text-gray-600 mb-3">Note: Image uploads can be implemented with file input fields. For now, provide descriptions or paths.</p>
          <TextInput label="Before Repair - Description/Path" name="image_before" onChange={handle} />
          <TextInput label="After Repaired - Description/Path" name="image_after" onChange={handle} />
        </fieldset>

        <div className="mt-4 flex items-center gap-3">
          <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white">{loading? 'Saving...':'Submit'}</button>
          {status && <div className={`${status.ok? 'text-green-600':'text-red-600'}`}>{status.msg}</div>}
        </div>
      </form>
    </div>
  )
}
