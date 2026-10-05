import streamlit as st
import speech_recognition as sr
import io
from streamlit_mic_recorder import mic_recorder

# รายการคำศัพท์
words = ["สวัสดี", "กินข้าว", "นอนหลับ", "สบายดีไหม", "ไปเที่ยว", "หนังสือ", "วันอาทิตย์", "วันจันทร์", "วันอคาร", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "หนังสือ", "12"]

# ตั้งค่าหน้าจอ Streamlit
st.set_page_config(page_title="โปรแกรมฝึกอ่านและตรวจเสียง", layout="centered")
st.title("โปรแกรมฝึกอ่านและตรวจเสียง")

# --- ตั้งค่า Session State สำหรับเก็บค่าสถานะต่างๆ ---
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "status_text" not in st.session_state:
    st.session_state.status_text = ""
if "recorder_key" not in st.session_state:
    st.session_state.recorder_key = 0
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# ฟังก์ชันสำหรับเปลี่ยนคำถัดไป
def next_word():
    st.session_state.current_index = (st.session_state.current_index + 1) % len(words)
    st.session_state.status_text = ""
    st.session_state.recorder_key += 1  # เปลี่ยน Key เพื่อบังคับล้างเสียงคำเก่า
    st.session_state.last_processed_audio = None  # รีเซ็ตตัวเช็กประมวลผลซ้ำ

# --- ส่วนการแสดงผล GUI ---
current_word = words[st.session_state.current_index]
st.markdown(f"<h1 style='text-align: center; font-size: 72px; color: #333333;'>{current_word}</h1>", unsafe_allow_html=True)

if st.session_state.status_text:
    st.info(st.session_state.status_text)

st.write("")

col1, col2 = st.columns(2)

with col1:
    # ปุ่มอัดเสียงพร้อมข้อความแจ้งเตือนกดอัดซ้ำ
    audio_data = mic_recorder(
        start_prompt="🎙️ กดเพื่อพูด",
        stop_prompt="⏹ กำลังฟัง... (โปรดกดอัดซ้ำเพื่อประมวลผล)",
        format="wav",
        key=f"recorder_{st.session_state.recorder_key}"
    )
    st.caption("💡 โปรดกดอัดซ้ำเพื่อประมวลผลคำตอบ")

with col2:
    if st.button("คำต่อไป ➔", use_container_width=True):
        next_word()
        st.rerun()

# --- ส่วนประมวลผลเสียง ---
if audio_data is not None:
    # ดึง ID หรือ Bytes ของเสียงปัจจุบันมาเช็ก
    current_audio_id = audio_data.get('id', audio_data['bytes'])
    
    # ประมวลผลเฉพาะเมื่อเป็นเสียงใหม่ที่ไม่เคยทำมาก่อนเท่านั้น (แก้ Bug ประมวลผล 2 รอบ)
    if st.session_state.last_processed_audio != current_audio_id:
        st.session_state.last_processed_audio = current_audio_id
        
        r = sr.Recognizer()
        r.energy_threshold = 400
        
        with st.status("🔍 กำลังประมวลผลเสียง...", expanded=True) as status:
            try:
                st.write("1️⃣ ดึงข้อมูลเสียงจากไมโครโฟน...")
                audio_bytes = audio_data['bytes']
                
                st.write("2️⃣ กำลังแปลงไฟล์เสียงเข้าสู่ระบบ...")
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio = r.record(source)
                    
                st.write("3️⃣ กำลังส่งเสียงไปประมวลผลที่ Google Speech API...")
                spoken_text = r.recognize_google(audio, language="th-TH")
                
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
