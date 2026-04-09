In this repository we present a Comparative Legal Engine. It's an interactive tool that demonstrates how the different schools of Sunni Islamic law produce distinct legal outcomes for the same scenario. The user can provide any case scenario and our engine will weigh the sources of authority (Quran, Hadith, Qiyas, etc.) according to the specific hierarchy of the four Sunni schools. This tool is by no means supposed to be a replacement for a lawyer. Instead, it is meant to illustrate to the general public how and where the schools of law differ. 

The engine uses different sources of authority in Sunni Islamic Law:
- The Quran: is the foundational source of Islamic law. It is believed by Muslims to be the direct word of God revealed to the Prophet. It establishes the overarching legal, moral, and social principles and it is superior to all other sources of authority.
- The Sunnah: consists of the recorded sayings and actions of the Prophet. It’s based on how the Prophet ruled Medina and the constitution of Medina. The Sunnah goes into more details of the principles found in the Quran. Specifically for Sunni Muslims, they rely on canonical Hadith collections to document the Sunnah. The Hadith contains anecdotes of the Prophet.
- Ijma: is the unanimous agreement of Islamic scholars on specific legal issues, ensuring unity in interpretation. When the Quran and Sunnah do not explicitly address an issue, Ijma provides an authoritative ruling.
- Qiyas: is the process of applying analogical reasoning. It allows jurists to apply principles to contemporary modern issues. It serves as a mechanism for addressing issues that arose after the time of the Prophet.
- Ijtihad: is the process of independent legal reasoning. It is utilized to address issues not explicitly covered by traditional sources of law such as the Quran, Sunnah, and Ijma. It allows jurists to make decisions in a way that aligns with Divine Law while considering contemporary circumstances.

The four primary schools of law in Sunni Islam give varying precedence to each of the above sources of authority:
- Hanafi: was founded by Abu Hanifa in Iraq and is the most liberal school of law. Their trust in reason is very high and their primary goal is equity and practicality. The order of precedence is: 
    - Quran
    - Hadith, but they are picky about which Hadiths they accept. They lean heavily towards mutawatir Hadiths, those transmitted by such a large number of people that it is impossible for it to be forged. A good example is the Sahih Bukhari collection of Hadiths.
    - Qiyas and Ijtihad. They also have the Istihsan override. Jurists can set aside a strict general legal analogy (Qiyas) in favor of a different ruling that better serves public interest.
    - Ijma of scholars. The Fatawa 'Alamgiri is a highly respected and comprehensive reference.

- Maliki: was founded by Malik ibn Anas in Medina. Relies on the belief that the traditions of the people of Medina is the best representation of the Prophet’s intent. Their trust in reason is moderate and instead highly value the customs of Medina. Their primary goal is stability and tradition. The order of precedence is: 
    - Quran
    - Ijma of the people of Medina during the first few generations is valuable. The Al-Muwatta of Imam Malik is a great example documenting this.
    - Qiyas

- Shafi’i: was founded by Imam al-Shafi’i in Egypt. He wanted to prioritize authentic Hadith. Their trust in reason is low and their primary goal is consistency and certainty. The order of precedence is:
    - Quran
    - Sahih Hadith, if it exists then you cannot use Qiyas or Ijtihad. Specifically they rely on Sahih Bukhari.
    - Qiyas used in very specific narrow circumstances with no Istihsan allowed.

- Hanbali: was founded by Ahmad ibn Hanbal in Iraq and is the most conservative. He believed that human reason is flawed and only the Divine knows best. They prefer even a weak Hadith over a strong human logical argument. Their trust in reason is very low and their primary goal is purity. The order of precedence is:
    - Quran
    - Hadith. They use the largest volume of Hadiths, a good example is Musnad Ahmad Bin Hanbal.
    - Ijma of the first generation and companions of the Prophet. A good source is the The Al-Muwatta of Imam Malik.

# Sources
- The Quran (https://www.clearquran.com/downloads/quran-english-translation-clearquran-edition-allah.pdf)
- Sahih Bukhari (https://d1.islamhouse.com/data/en/ih_books/single/en_Sahih_Al-Bukhari.pdf)
- Fatawa 'Alamgiri. We use the popular translation "A Digest of Moohummudan Law" by Baillie, Neil B.E. (https://archive.org/details/dli.ministry.11968/mode/2up)
- Al-Muwatta of Imam Malik (https://ia903201.us.archive.org/22/items/al-muwatta-of-imam-malik/Al-Muwatta%20of%20Imam%20Malik.pdf)
- Musnad Ahmad Bin Hanbal. For storage concerns, we just use the 1st volume, in total there are around 20 volumes. (https://archive.org/details/musnad-ahmad-bin-hanbal-english-translation/mode/2up)

# Create the environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows Command Prompt)
.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt