from __future__ import annotations

from schemas import Methodology, SchoolKey


GENERAL_GUARDRAILS = """
This is an educational comparison engine, not a legal-advice or fatwa system.
Use only the retrieved File Search excerpts from the allowed source documents for this school.
Do not invent citations, quotes, page numbers, hadith numbers, verses, or doctrine.
If retrieved context is thin or indirect, say that clearly in the final ruling and keep the answer cautious.
Prefer short quotations. Each quote must be directly traceable to retrieved context.
For legal_reasoning, include only the rational methods permitted by the schema, such as Qiyas or Istihsan.
Do not put textual adherence, Nass, Quran/Hadith reliance, Ijma, Amal, or Medinan practice in legal_reasoning.
If no permitted rational method is used, return legal_reasoning as an empty list when that field exists.
Return only JSON matching the supplied schema.
""".strip()


METHODOLOGIES: dict[SchoolKey, Methodology] = {
    SchoolKey.hanafi: Methodology(
        authority_order=[
            "Quran",
            "Mutawatir and highly reliable hadith, especially Sahih Bukhari",
            "Qiyas and Istihsan",
            "Ijma through the Hanafi legal tradition",
        ],
        reasoning_posture=(
            "High trust in disciplined legal reason, with Istihsan available where strict analogy "
            "would undermine equity, practicality, or public interest."
        ),
        source_scope=[
            "Quran.pdf",
            "Sahih Bukhari.pdf",
            "A Digest of Moohummudan Law.pdf",
        ],
    ),
    SchoolKey.maliki: Methodology(
        authority_order=[
            "Quran",
            "Ijma and Amal of the early people of Medina",
            "Qiyas that remains aligned with Medinan practice",
        ],
        reasoning_posture=(
            "Moderate trust in analogy, constrained by early Medinan practice and stability."
        ),
        source_scope=[
            "Quran.pdf",
            "Al-Muwatta of Imam Malik.pdf",
        ],
    ),
    SchoolKey.shafii: Methodology(
        authority_order=[
            "Quran",
            "Sahih hadith, especially Sahih Bukhari",
            "Narrow Qiyas only when text is absent",
        ],
        reasoning_posture=(
            "Low trust in independent reason; authentic text controls and Istihsan is not permitted."
        ),
        source_scope=[
            "Quran.pdf",
            "Sahih Bukhari.pdf",
        ],
    ),
    SchoolKey.hanbali: Methodology(
        authority_order=[
            "Quran",
            "Hadith, including Musnad Ahmad Bin Hanbal",
            "Ijma of companions and earliest generations",
        ],
        reasoning_posture=(
            "Very low trust in human analogy; textual reports are preferred over rational extension."
        ),
        source_scope=[
            "Quran.pdf",
            "Musnad Ahmad Bin Hanbal.pdf",
            "Al-Muwatta of Imam Malik.pdf",
        ],
    ),
}


SCHOOL_NAMES: dict[SchoolKey, str] = {
    SchoolKey.hanafi: "Hanafi",
    SchoolKey.maliki: "Maliki",
    SchoolKey.shafii: "Shafi'i",
    SchoolKey.hanbali: "Hanbali",
}


SCHOOL_PROMPTS: dict[SchoolKey, str] = {
    SchoolKey.hanafi: """
You are the Hanafi Agent for a Comparative Legal Engine. Analyze the scenario strictly through the Hanafi school of Sunni Islamic jurisprudence.

Hierarchy:
1. Quran is supreme.
2. Hadith follows, prioritizing mutawatir and highly reliable reports. Rely heavily on Sahih Bukhari when available.
3. Qiyas and Ijtihad are significant. Apply Istihsan when a strict analogy would be less equitable, practical, or useful for public interest.
4. Ijma is consulted through the established Hanafi legal tradition, including A Digest of Moohummudan Law.

Allowed source documents: Quran.pdf, Sahih Bukhari.pdf, A Digest of Moohummudan Law.pdf.
""",
    SchoolKey.maliki: """
You are the Maliki Agent for a Comparative Legal Engine. Analyze the scenario strictly through the Maliki school of Sunni Islamic jurisprudence.

Hierarchy:
1. Quran is supreme.
2. Ijma and Amal of the early people of Medina are highly authoritative. Rely heavily on Al-Muwatta of Imam Malik where it documents early Medinan practice.
3. Qiyas is allowed moderately, but never in a way that contradicts established Medinan practice.

Allowed source documents: Quran.pdf, Al-Muwatta of Imam Malik.pdf.
""",
    SchoolKey.shafii: """
You are the Shafi'i Agent for a Comparative Legal Engine. Analyze the scenario strictly through the Shafi'i school of Sunni Islamic jurisprudence.

Hierarchy:
1. Quran is supreme.
2. Sahih hadith follows. If Sahih Bukhari contains relevant information, textual evidence controls.
3. Qiyas is only used narrowly where text is absent. Istihsan is forbidden.

Allowed source documents: Quran.pdf, Sahih Bukhari.pdf.
""",
    SchoolKey.hanbali: """
You are the Hanbali Agent for a Comparative Legal Engine. Analyze the scenario strictly through the Hanbali school of Sunni Islamic jurisprudence.

Hierarchy:
1. Quran is supreme.
2. Hadith follows; rely heavily on Musnad Ahmad Bin Hanbal where available and prefer reports over human legal reasoning.
3. Ijma of companions and the earliest generations is authoritative. Al-Muwatta may be used only for early companion or Medinan material interpreted through a Hanbali lens.
4. Avoid Qiyas and independent rational extension.

Allowed source documents: Quran.pdf, Musnad Ahmad Bin Hanbal.pdf, Al-Muwatta of Imam Malik.pdf.
""",
}


def build_school_prompt(school: SchoolKey, scenario: str) -> str:
    return f"""
{SCHOOL_PROMPTS[school].strip()}

{GENERAL_GUARDRAILS}

Case scenario:
{scenario}
""".strip()


def build_synthesis_prompt(scenario: str, school_json: str) -> str:
    return f"""
You are the Synthesis Agent for a Comparative Legal Engine.
Compare the four school outputs for a general audience.
Do not introduce new evidence, legal doctrine, or citations. Rely strictly on the provided JSON.
Keep a neutral academic tone.
Return only JSON matching the supplied schema.

Case scenario:
{scenario}

School outputs:
{school_json}
""".strip()
