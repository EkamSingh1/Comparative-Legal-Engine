"use client";

import Link from "next/link";

type HeaderNavProps = {
  activePage: "analyzer" | "bibliography";
};

export function HeaderNav({ activePage }: HeaderNavProps) {
  return (
    <nav className="header-nav" aria-label="Primary">
      <Link href="/" className={`header-link ${activePage === "analyzer" ? "active" : ""}`}>
        Analyzer
      </Link>
      <Link
        href="/bibliography"
        className={`header-link ${activePage === "bibliography" ? "active" : ""}`}
      >
        Bibliography
      </Link>
    </nav>
  );
}
