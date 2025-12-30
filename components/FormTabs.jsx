import { useState } from 'react'
import RepairingForm from './RepairingForm'
import InwardForm from './InwardForm'
import OutwardForm from './OutwardForm'
import ServiceReportForm from './ServiceReportForm'

export default function FormTabs() {
  const tabs = [
    { id: 'repair', label: 'Repairing Form', comp: <RepairingForm /> },
    { id: 'inward', label: 'Inward Tracking', comp: <InwardForm /> },
    { id: 'outward', label: 'Outward Tracking', comp: <OutwardForm /> },
    { id: 'service', label: 'Service Report', comp: <ServiceReportForm /> }
  ]
  const [active, setActive] = useState('repair')

  return (
    <section id="forms" className="forms-wrapper py-8">
      <div className="container">
        <div className="mb-4">
          <div className="overflow-x-auto tab-scroll">
            <div className="flex gap-3 py-2">
              {tabs.map(t => (
                <button
                  key={t.id}
                  onClick={() => setActive(t.id)}
                  aria-pressed={active===t.id}
                  className={`tab-btn ${active===t.id? 'active': ''}`}
                >
                  {/* simple icon placeholder */}
                  <span className="w-4 h-4 inline-block bg-gray-200 rounded-sm" aria-hidden></span>
                  <span>{t.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="transition-all">
          {tabs.map(t => (
            <div key={t.id} style={{ display: active===t.id? 'block':'none' }}>{t.comp}</div>
          ))}
        </div>
      </div>
    </section>
  )
}
