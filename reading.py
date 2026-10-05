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
    # เพิ่ม mic_recorder แทนการใช้ Threading/Microphone เดิม
    audio_data = mic_recorder(
        start_prompt="🎙️ กดเพื่อพูด",
        stop_prompt="⏹️️ กำลังฟัง... (กดเพื่อหยุด)",
        key='recorder'
    )

with col2:
    if st.button("คำต่อไป ➔", use_container_width=True):
        next_word()
        st.rerun()

# --- ส่วนประมวลผลเสียง (คง Logic เดิมของคุณไว้ทั้งหมด) ---
if audio_data is not None:
    r = sr.Recognizer()
    r.energy_threshold = 400
    
    try:
        # แปลงข้อมูลเสียงจาก mic_recorder ส่งเข้า SpeechRecognition
        audio_bytes = audio_data['bytes']
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = r.record(source)
            
        print("รับเสียงเสร็จแล้ว กำลังส่งไปแปลที่ Google...")
        st.session_state.status_text = "⏳ กำลังประมวลผล..."
        spoken_text = r.recognize_google(audio, language="th-TH")
        
        print(f"ระบบได้ยินคำว่า: {spoken_text}")
        
        target_word = words[st.session_state.current_index]
        if spoken_text == target_word:
            st.session_state.status_text = "✅ ยอดเยี่ยม! ออกเสียงถูกต้อง"
        else:
            st.session_state.status_text = f"❌ คุณพูดว่า '{spoken_text}'\nลองพูดใหม่อีกครั้งนะครับ"
            
    except sr.WaitTimeoutError:
        print("Error: หมดเวลา ไม่ได้ยินเสียง")
        st.session_state.status_text = "ไม่ได้ยินเสียงเลย ลองกดปุ่มแล้วพูดใหม่นะครับ"
    except sr.UnknownValueError:
        print("Error: ได้ยินเสียง แต่แปลไม่ออก")
        st.session_state.status_text = "ฟังไม่ค่อยชัด ลองพูดดังขึ้นอีกนิดครับ"
    except sr.RequestError as e:
        print(f"Error อินเทอร์เน็ต: {e}")
        st.session_state.status_text = "เชื่อมต่ออินเทอร์เน็ตไม่ได้"
    except Exception as e:
        print(f"Error อื่นๆ: {e}")
        st.session_state.status_text = f"Error อื่นๆ: {e}"
