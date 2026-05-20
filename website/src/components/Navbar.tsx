import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Sparkles, ArrowLeft, Github } from "lucide-react";

function handleScroll(e: React.MouseEvent<HTMLAnchorElement>) {
  const href = e.currentTarget.getAttribute('href');
  if (href && href.startsWith('#')) {
    e.preventDefault();
    const id = href.replace('#', '');
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}

const Navbar: React.FC = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === "/";

  return (
    <nav className="fixed top-3 md:top-5 left-1/2 transform -translate-x-1/2 z-50 w-[94vw] max-w-6xl select-none">
      <div
        className="rounded-full backdrop-blur-2xl border px-4 md:px-6 py-2 flex items-center justify-between"
        style={{
          background: 'linear-gradient(to bottom, hsl(var(--card) / 0.7), hsl(var(--graph-node-1) / 0.15))',
          borderColor: 'rgba(255, 255, 255, 0.08)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
        }}
      >
        {/* Left: Brand Logo & Title */}
        <Link to="/" className="flex items-center gap-2.5 mr-4 shrink-0 group">
          <img
            src="/cgcIcon.png"
            className="w-8 h-8 drop-shadow-[0_0_8px_rgba(168,85,247,0.6)] group-hover:scale-105 transition-transform duration-300"
            alt="CodeGraphContext Logo"
          />
          <span className="font-extrabold text-base md:text-lg bg-gradient-primary bg-clip-text text-transparent tracking-tight">
            CodeGraphContext
          </span>
        </Link>

        {/* Center: Anchors (Only displayed on landing page for optimal UX) */}
        {isLandingPage ? (
          <ul className="hidden lg:flex items-center gap-1 font-semibold text-sm text-[hsl(var(--foreground))]">
            <li>
              <a
                href="#features"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Features
              </a>
            </li>
            <li>
              <a
                href="#bundle-registry"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Pre-indexed
              </a>
            </li>
            <li>
              <a
                href="#bundle-generator"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Generator
              </a>
            </li>
            <li>
              <a
                href="#cookbook"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Cookbook
              </a>
            </li>
            <li>
              <a
                href="#demo"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Demo
              </a>
            </li>
            <li>
              <a
                href="#installation"
                className="px-3 py-1.5 rounded-full hover:bg-[hsl(var(--primary)/0.12)] hover:text-[hsl(var(--primary))] transition-all duration-200"
                onClick={handleScroll}
              >
                Installation
              </a>
            </li>
          </ul>
        ) : null}

        {/* Right: Actions */}
        <div className="flex items-center gap-2 md:gap-3 shrink-0">
          {isLandingPage ? (
            <>
              <a
                href="https://github.com/CodeGraphContext/CodeGraphContext"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full hover:bg-white/5 text-muted-foreground hover:text-white transition-colors duration-200"
                title="View GitHub Repository"
              >
                <Github className="w-5 h-5" />
              </a>
              <Link to="/explore">
                <button className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold text-xs md:text-sm px-4 py-2 rounded-full flex items-center gap-1.5 shadow-[0_0_15px_rgba(59,130,246,0.35)] border-none transition-all duration-300 hover:scale-105">
                  Launch Explorer <Sparkles className="w-3.5 h-3.5" />
                </button>
              </Link>
            </>
          ) : (
            <Link to="/">
              <button className="border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/10 text-white font-bold text-xs md:text-sm px-4 py-2 rounded-full flex items-center gap-1.5 transition-all duration-300">
                <ArrowLeft className="w-4 h-4" /> Back to Home
              </button>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
