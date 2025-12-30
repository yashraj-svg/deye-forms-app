import Head from 'next/head'
import Header from '../components/Header'
import FormTabs from '../components/FormTabs'

export default function Home(){
  return (
    <div className="min-h-screen">
      <Head>
        <title>DEYE Operational Forms</title>
      </Head>
      <Header />
      <main className="py-8">
        <div className="container">
          <div className="hero">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h1 className="hero-title">DEYE Operational Forms</h1>
                <p className="hero-sub">Fill Repairing, Inward, Outward tracking and Service Reports from a single responsive interface.</p>
              </div>
              <div className="flex items-center gap-3">
                <a href="#forms" className="cta-btn">Open Forms</a>
                <a href="/admin" className="text-sm text-gray-600">Admin</a>
              </div>
            </div>
          </div>
        </div>

        <FormTabs />
      </main>
    </div>
  )
}
