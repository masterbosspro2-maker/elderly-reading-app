import streamlit as st
import speech_recognition as sr
import io
from streamlit_mic_recorder import mic_recorder

# รายการคำศัพท์
words = ["สวัสดี", "กินข้าว", "นอนหลับ", "สบายดีไหม", "ไปเที่ยว", "หนังสือ", "วันอาทิตย์", "วันจันทร์", "วันอังคาร", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "12"]

# ตั้งค่าหน้าจอ Streamlit
st.set_page_config(page_title="โปรแกรมฝึกอ่านและตรวจเสียง", layout="centered")
st.title("โปรแกรมฝึกอ่านและตรวจเสียง")

# ตัวแปรจำลำดับคำศัพท์ และข้อความสถานะ
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "status_text" not in st.session_state:
    st.session_state.status_text = ""

# ฟังก์ชันสำหรับเปลี่ยนคำ
def next_word():
    st.session_state.current_index = (st.session_state.current_index + 1) % len(words)
    st.session_state.status_text = ""

# --- ส่วนการแสดงผล GUI ---
current_word = words[st.session_state.current_index]
st.markdown(f"<h1 style='text-align: center; font-size: 72px; color: #333333;'>{current_word}</h1>", unsafe_allow_html=True)

if st.session_state.status_text:
    st.info(st.session_state.status_text)

st.write("")

col1, col2 = st.columns(2)

with col1:
    audio_data = mic_recorder(
        start_prompt="🎙️ กดเพื่อพูด",
        stop_prompt="⏹ กำลังฟัง... (กดเพื่อหยุด)",
        format="wav",  # <-- เพิ่มบรรทัดนี้ลงไปครับ
        key='recorder'
    )

with col2:
    if st.button("คำต่อไป ➔", use_container_width=True):
        next_word()
        st.rerun()

# --- ส่วนประมวลผลเสียง + แสดงสถานะ Realtime ---
if audio_data is not None:
    r = sr.Recognizer()
    r.energy_threshold = 400
    
    # ใช้ st.status เพื่อบอกขั้นตอนการทำงานแบบ Realtime
    with st.status("🔍 กำลังประมวลผลเสียง...", expanded=True) as status:
        try:
            # ขั้นตอนที่ 1: เตรียมไฟล์เสียง
            st.write("1️⃣ ดึงข้อมูลเสียงจากไมโครโฟน...")
            audio_bytes = audio_data['bytes']
            
            # ขั้นตอนที่ 2: โหลดไฟล์เสียง
            st.write("2️⃣ กำลังแปลงไฟล์เสียงเข้าสู่ระบบ...")
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio = r.record(source)
                
            # ขั้นตอนที่ 3: ส่งไปแปลที่ Google
            st.write("3️⃣ กำลังส่งเสียงไปประมวลผลที่ Google Speech API...")
            spoken_text = r.recognize_google(audio, language="th-TH")
            
            # เมื่อเสร็จสิ้นกระบวนการ
            status.update(label="✅ ประมวลผลเสร็จสิ้น!", state="complete", expanded=False)
            
            target_word = words[st.session_state.current_index]
            if spoken_text == target_word:
                st.session_state.status_text = f"✅ ยอดเยี่ยม! ออกเสียงถูกต้อง (ได้ยินว่า: '{spoken_text}')"
            else:
                st.session_state.status_text = f"❌ คุณพูดว่า '{spoken_text}'\nลองพูดใหม่อีกครั้งนะครับ"
                
        except sr.WaitTimeoutError:
            status.update(label="❌ หมดเวลา", state="error", expanded=False)
            st.session_state.status_text = "ไม่ได้ยินเสียงเลย ลองกดปุ่มแล้วพูดใหม่นะครับ"
        except sr.UnknownValueError:
            status.update(label="❌ ถอดรหัสเสียงไม่สำเร็จ", state="error", expanded=False)
            st.session_state.status_text = "ฟังไม่ค่อยชัด ลองพูดดังขึ้นอีกนิดครับ"
        except sr.RequestError as e:
            status.update(label="❌ เชื่อมต่ออินเทอร์เน็ตไม่ได้", state="error", expanded=False)
            st.session_state.status_text = "เชื่อมต่ออินเทอร์เน็ตไม่ได้"
        except Exception as e:
            status.update(label="❌ เกิดข้อผิดพลาด", state="error", expanded=False)
            st.session_state.status_text = f"Error อื่นๆ: {e}"
