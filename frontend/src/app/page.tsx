import { ShieldCheck, Car, KeyRound, CalendarCheck2, Building2, Zap } from "lucide-react";

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Engine Active • Single-City Launch (Bangalore Hubs)
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900">
          Drive on Your Terms. <br />
          <span className="text-blue-600">Fixed Rentals & Flex Subscriptions.</span>
        </h1>
        <p className="text-lg text-slate-600">
          Production-grade vehicle rental and partner fleet platform. Concurrency-safe reservations, immutable price snapshots, and verified inspections.
        </p>
      </div>

      {/* Architectural Pillars Grid */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Car className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Dual Fleet Ownership</h3>
          <p className="text-sm text-slate-600">
            Seamlessly handles both company-owned inventory and vetted partner-owned vehicles with automated commission reconciliation.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <CalendarCheck2 className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Zero Overbooking Engine</h3>
          <p className="text-sm text-slate-600">
            Backed by PostgreSQL range types and btree_gist exclusion constraints to guarantee zero overlapping bookings under high concurrent traffic.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Financial Integrity</h3>
          <p className="text-sm text-slate-600">
            Integer minor-unit precision (paise). Security deposits strictly isolated in escrow from operational revenue and partner payables.
          </p>
        </div>
      </div>

      {/* Platform Roles Navigation Cards */}
      <div className="mt-16 bg-slate-900 rounded-3xl p-8 sm:p-12 text-white">
        <div className="max-w-2xl">
          <h2 className="text-2xl font-bold tracking-tight">Explore Platform Portals</h2>
          <p className="mt-2 text-slate-400 text-sm">
            Role-based interfaces for Customers, Fleet Partners, and Operations Staff.
          </p>
        </div>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-800/80 p-5 rounded-xl border border-slate-700 space-y-2">
            <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
              <KeyRound className="w-4 h-4" /> Customer Experience
            </div>
            <p className="text-xs text-slate-400">Search vehicles, compare rental vs subscription rates, hold slots, and manage reservations.</p>
          </div>

          <div className="bg-slate-800/80 p-5 rounded-xl border border-slate-700 space-y-2">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
              <Building2 className="w-4 h-4" /> Partner Portal
            </div>
            <p className="text-xs text-slate-400">Onboard vehicles, track fleet utilization, inspect earnings breakdown, and audit settlement runs.</p>
          </div>

          <div className="bg-slate-800/80 p-5 rounded-xl border border-slate-700 space-y-2">
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
              <Zap className="w-4 h-4" /> Admin & Operations
            </div>
            <p className="text-xs text-slate-400">Perform digital pickup/return inspections, log fuel and damage, approve partners, and monitor audit trails.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
