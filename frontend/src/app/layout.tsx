import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vroom Vroom | Vehicle Rental & Subscription Platform",
  description: "Production-oriented vehicle rental and subscription platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <header className="border-b bg-white/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl font-black tracking-tight text-blue-600">VROOM VROOM</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                MVP v1.0
              </span>
            </div>
            <nav className="flex items-center gap-6 text-sm font-medium text-slate-600">
              <a href="#vehicles" className="hover:text-blue-600 transition">Explore Cars</a>
              <a href="#partner" className="hover:text-blue-600 transition">Partner With Us</a>
              <a href="#admin" className="hover:text-blue-600 transition">Operations</a>
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
