import "server-only";

import { readdir } from "node:fs/promises";
import path from "node:path";
import { sourceAnchorId } from "@/lib/bibliography-shared";

const SOURCE_METADATA: Record<string, { onlinePdfUrl: string; description: string }> = {
  "Quran.pdf": {
    onlinePdfUrl:
      "https://www.clearquran.com/downloads/quran-english-translation-clearquran-edition-allah.pdf",
    description:
      "The Quran is the foundational text of Islamic law and the highest authority across all schools. This translation is used as the primary textual reference for revealed legal principles."
  },
  "Sahih Bukhari.pdf": {
    onlinePdfUrl: "https://d1.islamhouse.com/data/en/ih_books/single/en_Sahih_Al-Bukhari.pdf",
    description:
      "Sahih al-Bukhari is one of the most authoritative Sunni hadith collections. It provides authenticated narrations used to derive legal rulings when read alongside the Quran."
  },
  "A Digest of Moohummudan Law.pdf": {
    onlinePdfUrl: "https://archive.org/details/dli.ministry.11968/mode/2up",
    description:
      "A Digest of Moohummudan Law is an English digest of Hanafi legal doctrine associated with the Fatawa 'Alamgiri tradition. It is used here to represent juristic consensus and applied Hanafi precedent."
  },
  "Al-Muwatta of Imam Malik.pdf": {
    onlinePdfUrl:
      "https://ia903201.us.archive.org/22/items/al-muwatta-of-imam-malik/Al-Muwatta%20of%20Imam%20Malik.pdf",
    description:
      "Al-Muwatta combines hadith reports with early Medinan legal practice collected by Imam Malik. It is central for modeling Maliki reliance on Amal and early communal transmission."
  },
  "Musnad Ahmad Bin Hanbal.pdf": {
    onlinePdfUrl: "https://archive.org/details/musnad-ahmad-bin-hanbal-english-translation/mode/2up",
    description:
      "Musnad Ahmad is a large hadith compilation arranged by narrator, preserving a broad textual record. It is used for the Hanbali profile, which strongly prioritizes transmitted reports."
  }
};

export type BibliographyEntry = {
  fileName: string;
  title: string;
  onlinePdfUrl: string;
  description: string;
  anchorId: string;
};

async function findSourcesDir(): Promise<string> {
  const candidates = [
    path.resolve(process.cwd(), "../sources"),
    path.resolve(process.cwd(), "sources"),
  ];

  for (const candidate of candidates) {
    try {
      const stat = await readdir(candidate);
      if (stat) {
        return candidate;
      }
    } catch {
      // Try next candidate directory.
    }
  }

  throw new Error("Unable to find sources directory.");
}

export async function getBibliographyEntries(): Promise<BibliographyEntry[]> {
  const sourcesDir = await findSourcesDir();
  const entries = await readdir(sourcesDir, { withFileTypes: true });
  const sourceFiles = entries
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".pdf"))
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));

  const unmappedSourceFiles = sourceFiles.filter((fileName) => !(fileName in SOURCE_METADATA));
  if (unmappedSourceFiles.length > 0) {
    throw new Error(
      `Missing bibliography metadata for source files: ${unmappedSourceFiles.join(", ")}`
    );
  }

  const staleMappings = Object.keys(SOURCE_METADATA).filter(
    (fileName) => !sourceFiles.includes(fileName)
  );
  if (staleMappings.length > 0) {
    throw new Error(
      `Bibliography metadata does not match sources folder: ${staleMappings.join(", ")}`
    );
  }

  return sourceFiles.map((fileName) => ({
    ...SOURCE_METADATA[fileName],
    fileName,
    title: fileName.replace(/\.pdf$/i, ""),
    anchorId: sourceAnchorId(fileName),
  }));
}
