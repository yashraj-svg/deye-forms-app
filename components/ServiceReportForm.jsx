import { useState, useRef, useEffect } from 'react'
import SignaturePad from './SignaturePad'

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

export default function ServiceReportForm(){
  const [form, setForm] = useState({
    contact_no: '',
    engineer_first_name: '',
    engineer_last_name: '',
    customer_first_name: '',
    customer_last_name: '',
    date_of_service: '',
    address_street: '',
    address_city: '',
    address_state: '',
    address_zip: '',
    phone_number: '',
    email: '',
    product_type: '',
    inverter_capacity: '',
    no_of_mppt: '',
    serial_number: '',
    lcd_version: '',
    mcu_version: '',
    pv_capacity_kw: '',
    dc_spd: false,
    dc_switch: false,
    dc_fuse: false,
    ac_spd: false,
    ac_switch: false,
    ac_fuse: false,
    earthing_panel: false,
    earthing_inverter: false,
    earthing_ac_neutral: false,
    ac_neutral_earth_voltage: '',
    ac_cable_size: '',
    physical_observation: '',
    pv_data: Array(8).fill({voltage: '', current: '', earthing: '', panel: '', observation: ''}),
    ac_data: {
      r_to_n: {voltage: '', current: '', earthing: ''},
      y_to_n: {voltage: '', current: '', earthing: ''},
      b_to_n: {voltage: '', current: '', earthing: ''},
      r_to_y: {voltage: '', current: '', earthing: ''},
      y_to_b: {voltage: '', current: '', earthing: ''},
      b_to_r: {voltage: '', current: '', earthing: ''},
      n_to_pe: {voltage: '', current: '', earthing: ''}
    },
    repair_inverter: '',
    repair_dust: '',
    repair_cabling: '',
    repair_other: '',
    actual_work_done: '',
    cause_of_failure: '',
    battery_type: '',
    battery_make: '',
    battery_voltage: '',
    battery_protection: '',
    no_of_battery: '',
    battery_bms_make: '',
    battery_bms_model: '',
    battery_bms_ratings: '',
    protocol: '',
    conclusion: '',
    customer_ratings: '',
    suggestions: '',
    engineer_signature_data: '',
    customer_signature_data: ''
  })
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = (e) => {
    const { name, value, type, checked } = e.target
    setForm(prev=> ({...prev, [name]: type === 'checkbox' ? checked : value}))
  }

  const handlePVData = (idx, field, value) => {
    setForm(prev=> {
      const newPV = [...prev.pv_data]
      newPV[idx] = {...(newPV[idx] || {}), [field]: value}
      return {...prev, pv_data: newPV}
    })
  }

  const handleACData = (row, field, value) => {
    setForm(prev=> ({
      ...prev,
      ac_data: {
        ...prev.ac_data,
        [row]: {...prev.ac_data[row], [field]: value}
      }
    }))
  }

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    try{
      const res = await fetch('/api/submit', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({form_type: 'service_report', payload: form})})
      if(res.ok){ setStatus({ok:true, msg:'Saved'}) ; e.target.reset(); setForm({}) }
      else { const d = await res.json(); setStatus({ok:false, msg: d.error || 'Failed'}) }
    }catch(err){ setStatus({ok:false, msg: err.message}) }
    setLoading(false)
  }

  return (
    <div className="card max-w-4xl">
      <h3 className="text-lg font-semibold mb-4">DEYE Inverter Service Report</h3>
      <form onSubmit={submit} className="space-y-6">
        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Contact Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Contact No." name="contact_no" onChange={handle} />
            <TextInput label="Phone Number" name="phone_number" required onChange={handle} type="tel" />
            <TextInput label="Email" name="email" required onChange={handle} type="email" />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Engineer Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Engineer First Name" name="engineer_first_name" required onChange={handle} />
            <TextInput label="Engineer Last Name" name="engineer_last_name" required onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Customer Details</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Customer First Name" name="customer_first_name" required onChange={handle} />
            <TextInput label="Customer Last Name" name="customer_last_name" required onChange={handle} />
            <TextInput label="Date of Service" name="date_of_service" type="date" onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Address</legend>
          <div className="grid gap-4">
            <TextInput label="Street Address" name="address_street" required onChange={handle} />
            <div className="grid md:grid-cols-3 gap-4">
              <TextInput label="City" name="address_city" onChange={handle} />
              <TextInput label="State" name="address_state" onChange={handle} />
              <TextInput label="Zip Code" name="address_zip" onChange={handle} />
            </div>
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Product & Device Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <SelectInput label="Product Type" name="product_type" required onChange={handle} options={['Inverter']} />
            <TextInput label="Inverter Capacity" name="inverter_capacity" required onChange={handle} />
            <TextInput label="Serial Number" name="serial_number" required onChange={handle} />
            <TextInput label="LCD Version" name="lcd_version" required onChange={handle} />
            <TextInput label="MCU Version" name="mcu_version" required onChange={handle} />
            <TextInput label="PV Capacity (KW)" name="pv_capacity_kw" required onChange={handle} type="number" />
            <TextInput label="No of MPPT" name="no_of_mppt" required onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Component Checks</legend>
          <div className="grid gap-4">
            <div>
              <div className="font-medium mb-2">DC Side Components</div>
              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="dc_spd" onChange={handle} /> SPD
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="dc_switch" onChange={handle} /> Switch
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="dc_fuse" onChange={handle} /> Fuse
                </label>
              </div>
            </div>
            <div>
              <div className="font-medium mb-2">AC Side Components</div>
              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="ac_spd" onChange={handle} /> SPD
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="ac_switch" onChange={handle} /> Switch
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="ac_fuse" onChange={handle} /> Fuse
                </label>
              </div>
            </div>
            <div>
              <div className="font-medium mb-2">Earthing</div>
              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="earthing_panel" onChange={handle} /> Panel
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="earthing_inverter" onChange={handle} /> Inverter
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" name="earthing_ac_neutral" onChange={handle} /> AC Neutral To Earth
                </label>
              </div>
            </div>
          </div>
          <TextInput label="AC Neutral To Earth Voltage (V)" name="ac_neutral_earth_voltage" onChange={handle} className="mt-4" />
          <TextInput label="AC Cable Size / Type" name="ac_cable_size" onChange={handle} className="mt-4" />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Physical Observation</legend>
          <TextArea label="Physical Observation Details" name="physical_observation" onChange={handle} rows={4} />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">DC Side Measurements (PV Data)</legend>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border p-2">PV</th>
                  <th className="border p-2">Voltage (V)</th>
                  <th className="border p-2">Current (A)</th>
                  <th className="border p-2">Earthing</th>
                  <th className="border p-2">PV Panel</th>
                  <th className="border p-2">Observation</th>
                </tr>
              </thead>
              <tbody>
                {Array(8).fill(null).map((_, idx) => (
                  <tr key={idx}>
                    <td className="border p-2">PV {idx + 1}</td>
                    <td className="border p-2"><input type="text" value={form.pv_data[idx]?.voltage || ''} onChange={(e)=>handlePVData(idx, 'voltage', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.pv_data[idx]?.current || ''} onChange={(e)=>handlePVData(idx, 'current', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.pv_data[idx]?.earthing || ''} onChange={(e)=>handlePVData(idx, 'earthing', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.pv_data[idx]?.panel || ''} onChange={(e)=>handlePVData(idx, 'panel', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.pv_data[idx]?.observation || ''} onChange={(e)=>handlePVData(idx, 'observation', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">AC Side Measurements</legend>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border p-2">Phase</th>
                  <th className="border p-2">Voltage (V)</th>
                  <th className="border p-2">Current (A)</th>
                  <th className="border p-2">Earthing</th>
                </tr>
              </thead>
              <tbody>
                {['r_to_n', 'y_to_n', 'b_to_n', 'r_to_y', 'y_to_b', 'b_to_r', 'n_to_pe'].map(row => (
                  <tr key={row}>
                    <td className="border p-2">{row.replace(/_/g, ' ').toUpperCase()}</td>
                    <td className="border p-2"><input type="text" value={form.ac_data[row]?.voltage || ''} onChange={(e)=>handleACData(row, 'voltage', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.ac_data[row]?.current || ''} onChange={(e)=>handleACData(row, 'current', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                    <td className="border p-2"><input type="text" value={form.ac_data[row]?.earthing || ''} onChange={(e)=>handleACData(row, 'earthing', e.target.value)} className="w-full border rounded px-2 py-1" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Repair Details</legend>
          <div className="grid gap-4">
            <TextArea label="Inverter" name="repair_inverter" onChange={handle} rows={2} />
            <TextArea label="Dust" name="repair_dust" onChange={handle} rows={2} />
            <TextArea label="Cabling" name="repair_cabling" onChange={handle} rows={2} />
            <TextArea label="Other" name="repair_other" onChange={handle} rows={2} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Work Details</legend>
          <TextArea label="Actual Work Done at Site" name="actual_work_done" onChange={handle} rows={3} />
          <TextArea label="Cause of Failure" name="cause_of_failure" onChange={handle} rows={3} />
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Battery Information</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <TextInput label="Battery Type" name="battery_type" onChange={handle} />
            <TextInput label="Make" name="battery_make" onChange={handle} />
            <TextInput label="Voltage" name="battery_voltage" onChange={handle} />
            <TextInput label="Protection" name="battery_protection" onChange={handle} />
            <TextInput label="No. of Battery" name="no_of_battery" onChange={handle} />
          </div>
          <div className="mt-4 grid md:grid-cols-3 gap-4">
            <TextInput label="BMS Make" name="battery_bms_make" onChange={handle} />
            <TextInput label="BMS Model" name="battery_bms_model" onChange={handle} />
            <TextInput label="BMS Ratings" name="battery_bms_ratings" onChange={handle} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Final Assessment</legend>
          <div className="grid gap-4">
            <TextArea label="Protocol" name="protocol" required onChange={handle} rows={2} />
            <TextArea label="Conclusion" name="conclusion" required onChange={handle} rows={2} />
            <TextArea label="Customer Ratings" name="customer_ratings" onChange={handle} rows={2} />
            <TextArea label="Any Suggestions" name="suggestions" onChange={handle} rows={2} />
          </div>
        </fieldset>

        <fieldset className="border-b pb-4">
          <legend className="text-md font-semibold mb-3">Signatures</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <SignaturePad label="Engineer Signature" value={form.engineer_signature_data} onChange={(v)=>setForm(prev=>({...prev, engineer_signature_data: v}))} />
            </div>
            <div>
              <SignaturePad label="Customer Signature" value={form.customer_signature_data} onChange={(v)=>setForm(prev=>({...prev, customer_signature_data: v}))} />
            </div>
          </div>
        </fieldset>

        <div className="border-t pt-4">
          <p className="text-sm text-gray-600 mb-4">Note: Engineer and Customer signatures can be captured via canvas or file upload in production.</p>
          <div className="mt-4 flex items-center gap-3">
            <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white">{loading? 'Saving...':'Submit'}</button>
            {status && <div className={`${status.ok? 'text-green-600':'text-red-600'}`}>{status.msg}</div>}
          </div>
        </div>
      </form>
    </div>
  )
}
