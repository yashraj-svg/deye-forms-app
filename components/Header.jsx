export default function Header() {
  return (
    <header className="w-full bg-white border-b sticky top-0 z-30">
      <div className="container flex items-center justify-between py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-md flex items-center justify-center text-white font-bold">DE</div>
          <div>
            <div className="font-semibold">DEYE</div>
            <div className="text-xs text-gray-500">Operational Forms</div>
          </div>
        </div>

        <nav className="flex items-center gap-3">
          <a href="/admin" className="text-sm text-gray-600 hover:text-gray-900">Admin</a>
          <a href="#forms" className="cta-btn">Open Forms</a>
        </nav>
      </div>
    </header>
  )
}
