import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Semakan SPM AI", layout="wide")

st.markdown("""
<style>
    .main-header {font-size: 30px; font-weight: bold; color: #2E86C1;}
    .sub-header {font-size: 20px; font-weight: bold; color: #444;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📝 Sistem Semakan Karangan SPM (AI)</div>', unsafe_allow_html=True)
st.info("Sistem ini menggunakan Google Gemini Flash untuk menyemak karangan berdasarkan format SPM sebenar.")

# --- SIDEBAR: TETAPAN ---
with st.sidebar:
    st.header("⚙️ Tetapan / Settings")
    # Kunci API dimasukkan oleh pengguna di sini
    api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
    st.caption("Kunci ini tidak disimpan. Ia hanya digunakan untuk sesi ini.")
    
    st.divider()
    
    # Pilih Subjek
    subjek = st.selectbox("Pilih Subjek / Select Subject:", ["Bahasa Melayu (SPM 1103)", "English (SPM 1119)"])
    
    # Tetapan Khusus Bahasa Inggeris
    part_selection = "General"
    if subjek == "English (SPM 1119)":
        part_selection = st.selectbox("Select Part:", ["Part 1 (Short Message)", "Part 2 (Guided Writing)", "Part 3 (Extended Writing)"])

# --- FUNGSI PROMPT KHAS (RUBRIK) ---
def get_system_prompt(subject, part):
    if subject == "Bahasa Melayu (SPM 1103)":
        return """
        Bertindak sebagai Penanda Kertas Bahasa Melayu SPM (Kod 1103) yang sangat berpengalaman.
        Tugas anda:
        1. Transkripsikan tulisan tangan dalam imej ini kepada teks.
        2. Semak karangan ini secara HOLISTIK berdasarkan piawaian SPM semasa.
        
        Kriteria Pemarkahan (Berdasarkan Rubrik SPM):
        - TEMA (Isi): Relevan, huraian jelas, contoh sesuai, kematangan fikiran.
        - BAHASA (Tatabahasa): Ejaan, imbuhan, struktur ayat, kosa kata luas & tepat.
        - PENGOLAHAN: Pemerengganan, kesinambungan idea (koheren & kohesi), gaya bahasa menarik (peribahasa).

        Sila berikan output dalam format berikut:
        
        ### 1. Transkripsi Ringkas
        (Tulis semula 2-3 ayat pertama untuk pengesahan)
        
        ### 2. Analisis Pemarkahan
        - **Kekuatan:** (Senaraikan apa yang murid buat dengan baik)
        - **Kelemahan:** (Senaraikan kesalahan ketara tatabahasa/struktur)
        - **Cadangan Penambahbaikan:** (Cara untuk dapat markah lebih tinggi)
        
        ### 3. Keputusan
        - **Gred Anggaran:** (Contoh: Cemerlang / Kepujian / Baik / Memuaskan)
        - **Anggaran Markah:** [Markah] / 100 (Atau /30 jika karangan pendek)
        """
    
    elif subject == "English (SPM 1119)":
        return f"""
        Act as a strict SPM English 1119 Examiner. 
        Your task is to grade the handwritten essay based on the **CEFR-aligned SPM Writing Marking Bands** for **{part}**.
        
        You must grade based on these 4 fixed criteria (Scale 0-5 per criterion):
        1. **CONTENT (C):** All content points included? Target reader informed?
        2. **COMMUNICATIVE ACHIEVEMENT (CA):** Register/Tone appropriate? Holds target reader's attention?
        3. **ORGANIZATION (O):** Logical flow? Use of connectors/cohesive devices?
        4. **LANGUAGE (L):** Vocabulary range, grammatical accuracy, sentence structures.

        Please provide the output in this format:

        ### 1. Transcription Snippet
        (First 2 sentences of the essay)

        ### 2. Band Analysis
        * **Content:** [Score 0-5] - (Explanation)
        * **Comm. Achievement:** [Score 0-5] - (Explanation)
        * **Organization:** [Score 0-5] - (Explanation)
        * **Language:** [Score 0-5] - (Explanation)

        ### 3. Corrections
        List top 3 grammatical errors found:
        * Error -> Correction

        ### 4. Final Score
        **Total Score:** [Sum] / 20
        """

# --- ANTARA MUKA UTAMA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Muat Naik / Upload")
    uploaded_file = st.file_uploader("Pilih gambar karangan (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Pratonton Gambar', use_column_width=True)

with col2:
    st.subheader("Hasil Semakan")
    
    if uploaded_file and api_key:
        if st.button("Mula Semakan / Start Grading", type="primary"):
            with st.spinner('Sedang menganalisis tulisan tangan & rubrik...'):
                try:
                    # Setup Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Dapatkan Prompt ikut subjek
                    prompt_text = get_system_prompt(subjek, part_selection)
                    
                    # Hantar ke AI
                    response = model.generate_content([prompt_text, image])
                    
                    # Papar Hasil
                    st.markdown(response.text)
                    st.success("Semakan Selesai!")
                    
                except Exception as e:
                    st.error(f"Ralat: {e}")
                    st.warning("Pastikan API Key anda betul dan gambar jelas.")
    
    elif not api_key:
        st.warning("⚠️ Sila masukkan API Key di sebelah kiri dahulu.")
    elif not uploaded_file:
        st.info("Sila muat naik gambar untuk bermula.")
