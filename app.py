import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="E-Essay SMK Tatau",
    page_icon="🏫",
    layout="wide"
)

# CSS untuk tajuk supaya nampak cantik
st.markdown("""
<style>
    .main-header {
        font-size: 36px; 
        font-weight: bold; 
        color: #1E3A8A; /* Warna Biru Gelap Rasmi */
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 18px; 
        color: #555;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Tajuk Utama di Skrin
st.markdown('<div class="main-header">🏫 E-Essay SMK Tatau</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistem Semakan Karangan Digital - SMK Tatau (Powered by AI)</div>', unsafe_allow_html=True)

# --- SIDEBAR: TETAPAN ---
with st.sidebar:
    st.header("⚙️ Tetapan / Settings")
    # Letak URL logo sekolah (atau guna logo placeholder ini dulu)
    st.image("https://upload.wikimedia.org/wikipedia/ms/3/38/Sekolah_Menengah_Kebangsaan_Tatau.jpg", width=80) 
    
    # Cek jika kunci ada dalam Secrets (Untuk kegunaan awam)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Kunci API telah diaktifkan secara automatik oleh pemilik.")
    else:
        # Jika tiada secrets, minta pengguna masukkan sendiri
        api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")
        st.caption("Dapatkan kunci di aistudio.google.com")

    # ... kod api_key di atas ...
    
    st.divider()
    # Butang Diagnostik
    if st.button("Semak Sambungan Model"):
        try:
            genai.configure(api_key=api_key)
            list_models = genai.list_models()
            model_names = [m.name for m in list_models]
            st.write("Model yang ditemui:", model_names)
        except Exception as e:
            st.error(f"Ralat: {e}")
    
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
                    model = genai.GenerativeModel('gemini-2.0-flash-001')
                    
                    # Dapatkan Prompt ikut subjek
                    prompt_text = get_system_prompt(subjek, part_selection)
                    
                    # Hantar ke AI
                    response = model.generate_content([prompt_text, image])
                    
                    # Papar Hasil
                    st.markdown(response.text)
                    st.success("Semakan Selesai!")
                    
                except Exception as e:
                    # Tukar error teknikal kepada bahasa mudah faham
                    error_msg = str(e)
                    if "429" in error_msg or "Resource has been exhausted" in error_msg:
                        st.error("⚠️ Kuota Seminit Penuh! Sistem sedang 'berehat' sebentar.")
                        st.warning("Sila tunggu 1 minit, kemudian tekan butang Semak semula.")
                    else:
                        st.error(f"Berlaku ralat teknikal: {error_msg}")
                        st.info("Cuba refresh browser anda.")
    elif not api_key:
        st.warning("⚠️ Sila masukkan API Key di sebelah kiri dahulu.")
    elif not uploaded_file:
        st.info("Sila muat naik gambar untuk bermula.")
