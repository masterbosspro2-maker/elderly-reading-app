import streamlit as st
import speech_recognition as sr
import threading

# รายการคำศัพท์
words = ["สวัสดี", "กินข้าว", "นอนหลับ", "สบายดีไหม", "ไปเที่ยว", "หนังสือ", "วันอาทิตย์", "วันจันทร์", "วันอังคาร", "12"]

# ตั้งค่าหน้าจอ Streamlit
st.set_page_config(page_title="โปรแกรมฝึกอ่านและตรวจเสียง", layout="centered")
st.title("🗣️ โปรแกรมฝึกอ่านและตรวจเสียง")

# ตัวแปรจำลำดับคำศัพท์ และข้อความสถานะ
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "status_text" not in st.session_state:
    st.session_state.status_text = ""

# ฟังก์ชันสำหรับเปลี่ยนคำ
def next_word():
    st.session_state.current_index = (st.session_state.current_index + 1) % len(words)
    st.session_state.status_text = ""

# ฟังก์ชันฟังเสียงและตรวจความถูกต้อง 
def check_pronunciation():
    st.session_state.status_text = "🎙️ กำลังฟัง... พูดได้เลยครับ"
    
    r = sr.Recognizer()
    r.energy_threshold = 400
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1.0)
        
        try:
            print("กำลังรอรับเสียง...")
            audio = r.listen(source, timeout=20, phrase_time_limit=5)
            
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
            st.session_state.status_text = "ไม่ได้ยินเสียงเลย ลองกดปุ่มแล้วพูดใหม่นะครับ"
        except sr.UnknownValueError:
            st.session_state.status_text = "ฟังไม่ค่อยชัด ลองพูดดังขึ้นอีกนิดครับ"
        except sr.RequestError as e:
            st.session_state.status_text = "เชื่อมต่ออินเทอร์เน็ตไม่ได้"
        except Exception as e:
            st.session_state.status_text = "เกิดข้อผิดพลาดบางอย่าง"

# ฟังก์ชันเรียกใช้ Thread 
def start_listening():
    threading.Thread(target=check_pronunciation, daemon=True).start()

# --- ส่วนการแสดงผล GUI ---
current_word = words[st.session_state.current_index]
st.markdown(f"<h1 style='text-align: center; font-size: 72px; color: #333333;'>{current_word}</h1>", unsafe_allow_html=True)

if st.session_state.status_text:
    st.info(st.session_state.status_text)

st.write("")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ กดเพื่อพูด", use_container_width=True):
        start_listening()

with col2:
    if st.button("คำต่อไป ➔", use_container_width=True):
        next_word()
        st.rerun()