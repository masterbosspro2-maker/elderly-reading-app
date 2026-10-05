import streamlit as st
import speech_recognition as sr
import io
from streamlit_mic_recorder import mic_recorder

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="โปรแกรมฝึกอ่านและตรวจเสียง", layout="centered")

st.title("🗣️ โปรแกรมฝึกอ่านและตรวจเสียง")

# รายการคำศัพท์
words = ["สวัสดี", "กินข้าว", "นอนหลับ", "สบายดีไหม", "ไปเที่ยว", "หนังสือ", "วันอาทิตย์", "วันจันทร์", "วันอังคาร", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "12"]

# ตัวแปรจำลำดับคำศัพท์
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# แสดงคำศัพท์ขนาดใหญ่ (ปรับสีให้เข้ากับ Dark Mode)
target_word = words[st.session_state.current_index]
st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{target_word}</h1>", unsafe_allow_html=True)

st.write("---")

# สร้างคอลัมน์วางปุ่มคู่กัน
col1, col2 = st.columns(2)

with col1:
    # ปุ่มอัดเสียงผ่านเบราว์เซอร์
    audio_data = mic_recorder(
        start_prompt="🎙️ กดเพื่อพูด",
        stop_prompt="⏹️ กำลังฟัง... (กดเพื่อหยุด)",
        format="wav",  # <-- เพิ่มบรรทัดนี้ลงไปครับ
        key='recorder'
    )

with col2:
    # ปุ่มเปลี่ยนคำถัดไป
    if st.button("คำต่อไป ➔", use_container_width=True):
        st.session_state.current_index = (st.session_state.current_index + 1) % len(words)
        st.rerun()

# เมื่อผู้ใช้พูดเสร็จและบันทึกเสียงเข้ามา
if audio_data is not None:
    audio_bytes = audio_data['bytes']
    r = sr.Recognizer()
    r.energy_threshold = 400
    
    try:
        # แปลงไฟล์เสียง Bytes นำเข้า SpeechRecognition
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            
        with st.spinner("⏳ กำลังประมวลผล..."):
            spoken_text = r.recognize_google(audio, language="th-TH")
            
        st.write(f"**ระบบได้ยินคำว่า:** {spoken_text}")
        
        # ตรวจสอบความถูกต้อง
        if spoken_text == target_word:
            st.success("✅ ยอดเยี่ยม! ออกเสียงถูกต้อง")
        else:
            st.error(f"❌ คุณพูดว่า '{spoken_text}'\nลองพูดใหม่อีกครั้งนะครับ")
            
    except sr.UnknownValueError:
        st.warning("⚠️ ฟังไม่ค่อยชัด ลองพูดดังขึ้นอีกนิดครับ")
    except sr.RequestError as e:
        st.error("❌ เชื่อมต่ออินเทอร์เน็ตไม่ได้")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
