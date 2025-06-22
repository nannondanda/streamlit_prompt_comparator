import streamlit as st
import openai
from dotenv import load_dotenv
import os

# 환경 변수 로드
# 사용자에게 API 키 입력 받기
user_api_key = st.text_input("OpenAI API 키를 입력하세요", type="password")

# 키가 없으면 실행 중단
if not user_api_key:
    st.warning("OpenAI API 키를 입력해야 합니다.")
    st.stop()

# 입력된 키로 설정
openai.api_key = user_api_key

SYSTEM_PROMPT = """당신은 도움이 되는 AI 어시스턴트입니다. 
다음 규칙을 엄격히 따르세요:
1. 사용자의 질문에 정확하고 일관된 답변을 제공하세요.
2. 답변은 항상 객관적이고 사실에 기반해야 합니다.
3. 동일한 질문에는 항상 동일한 답변을 제공하세요.
4. 불필요한 변형이나 창의적인 표현을 피하세요."""

# ---- UI 꾸미기 ----
st.set_page_config(page_title="프롬프트 엔지니어링 비교 도구", page_icon="🔬", layout="wide")
st.markdown(
    """
    <style>
    .main-title {font-size: 3.5rem; font-weight: bold; margin-bottom: 0.5rem; color: #1f77b4;}
    .subtitle {font-size: 1.3rem; color: #666; margin-bottom: 1rem; font-weight: 500;}
    .desc {font-size: 1.1rem; color: #555; margin-bottom: 1.5rem; line-height: 1.6;}
    .chatbox {background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .divider {height: 1px; background: #dee2e6; margin: 1.5rem 0;}
    .response-box {background: transparent; border: none; padding: 0.5rem 0; margin: 0.5rem 0; border-left: 4px solid #007bff; padding-left: 1rem;}
    .user-box {background: transparent; border: none; padding: 0.5rem 0; margin: 0.5rem 0; border-left: 4px solid #28a745; padding-left: 1rem;}
    .question-display {background: transparent; border: none; padding: 0.5rem 0; margin: 0.5rem 0; border-left: 4px solid #ffc107; padding-left: 1rem;}
    .model-selector {background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 1rem; margin-bottom: 1rem;}
    .input-section {background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 1.5rem; margin-bottom: 1rem;}
    .stButton > button {background-color: #007bff; color: white; border: none; border-radius: 4px; padding: 0.5rem 1rem; font-weight: 500;}
    .stButton > button:hover {background-color: #0056b3;}
    </style>
    """, unsafe_allow_html=True
)

# 헤더 섹션
st.markdown('<div class="main-title">🔬 프롬프트 엔지니어링 비교 분석 도구</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">LLM 모델별 응답 성능 및 일관성 분석</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="desc">이 도구는 기업 환경에서 프롬프트 엔지니어링의 효과를 정량적으로 분석할 수 있도록 설계되었습니다.<br>'
    '동일한 질문에 대한 다양한 LLM 모델의 응답을 비교하여 <b>응답 일관성</b>, <b>정확성</b>, <b>품질</b>을 평가할 수 있습니다.<br>'
    '프롬프트 최적화 및 모델 선택 의사결정에 활용하세요.</div>',
    unsafe_allow_html=True
)

# ---- 모델 선택 ----
st.markdown("### 🤖 비교할 AI 모델 선택")
model_options = [
    "gpt-3.5-turbo",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-4"
]
col_model1, col_model2 = st.columns(2)
with col_model1:
    model1 = st.selectbox("**첫 번째 AI 모델**", model_options, key="model1", help="비교할 첫 번째 AI 모델을 선택하세요")
with col_model2:
    model2 = st.selectbox("**두 번째 AI 모델**", model_options, key="model2", help="비교할 두 번째 AI 모델을 선택하세요")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---- 세션 상태 ----
if "messages1" not in st.session_state:
    st.session_state.messages1 = [{"role": "system", "content": SYSTEM_PROMPT}]
if "messages2" not in st.session_state:
    st.session_state.messages2 = [{"role": "system", "content": SYSTEM_PROMPT}]
if "response_cache" not in st.session_state:
    st.session_state.response_cache = {}
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "show_input" not in st.session_state:
    st.session_state.show_input = True

def get_chat_response(prompt, messages, model):
    cache_key = f"{model}::{prompt}"
    if cache_key in st.session_state.response_cache:
        return st.session_state.response_cache[cache_key]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        seed=42,
        presence_penalty=0,
        frequency_penalty=0,
        top_p=1,
        max_tokens=1000
    )
    assistant_response = response.choices[0].message.content
    st.session_state.response_cache[cache_key] = assistant_response
    return assistant_response

# ---- 질문 입력 ----
st.markdown("### 💬 질문 입력하기")

# 입력창 표시/숨김 토글 버튼
col_toggle, col_info = st.columns([1, 3])
with col_toggle:
    if st.button("📝 질문 입력창 보기/숨기기", key="toggle_input"):
        st.session_state.show_input = not st.session_state.show_input

if st.session_state.show_input:
    with st.form("common_form", clear_on_submit=True):
        common_prompt = st.text_area(
            "두 AI 모델에게 동일한 질문을 입력하세요", 
            height=120, 
            key="common_input",
            help="비교 분석을 위해 두 AI 모델에게 같은 질문을 물어보세요. 예: '인공지능의 미래에 대해 설명해주세요'"
        )
        col_submit, col_clear = st.columns(2)
        with col_submit:
            submitted = st.form_submit_button("🚀 두 AI 모델에게 질문하기", use_container_width=True)
        with col_clear:
            if st.form_submit_button("🗑️ 모든 대화 지우기", use_container_width=True):
                st.session_state.conversation_history = []
                st.session_state.messages1 = [{"role": "system", "content": SYSTEM_PROMPT}]
                st.session_state.messages2 = [{"role": "system", "content": SYSTEM_PROMPT}]
                st.rerun()
        
        if submitted and common_prompt:
            # 두 챗봇의 메시지에 질문 추가
            st.session_state.messages1.append({"role": "user", "content": common_prompt})
            st.session_state.messages2.append({"role": "user", "content": common_prompt})
            
            # 두 챗봇의 응답 가져오기
            response1 = get_chat_response(common_prompt, st.session_state.messages1, model1)
            response2 = get_chat_response(common_prompt, st.session_state.messages2, model2)
            
            # 응답을 메시지에 추가
            st.session_state.messages1.append({"role": "assistant", "content": response1})
            st.session_state.messages2.append({"role": "assistant", "content": response2})
            
            # 대화 기록에 추가
            st.session_state.conversation_history.append({
                "question": common_prompt,
                "response1": response1,
                "response2": response2,
                "model1": model1,
                "model2": model2
            })
else:
    st.info("💡 질문 입력창이 숨겨져 있습니다. '📝 질문 입력창 보기/숨기기' 버튼을 클릭하여 표시하세요.")

# ---- 분석 결과 표시 ----
if st.session_state.conversation_history:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 비교 결과")
    
    # 통계 정보
    total_tests = len(st.session_state.conversation_history)
    st.metric("총 질문 수", total_tests)
    
    for i, conv in enumerate(reversed(st.session_state.conversation_history)):
        st.markdown(f"#### 질문 #{len(st.session_state.conversation_history) - i}")
        
        # 질문 표시 (한 번만)
        st.markdown('<div class="question-display">', unsafe_allow_html=True)
        if conv["question"].strip():
            st.markdown("**💬 질문:**")
            st.markdown(f"> {conv['question']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 응답 표시
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown(f"**🤖 {conv['model1']} 답변:**")
            st.write(conv["response1"])
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown(f"**🤖 {conv['model2']} 답변:**")
            st.write(conv["response2"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        if i < len(st.session_state.conversation_history) - 1:  # 마지막 항목이 아니면 구분선 추가
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ---- 고급 분석 모드 (선택사항) ----
with st.expander("🔧 개별 AI 모델과 대화하기"):
    st.markdown("### 각 AI 모델과 개별적으로 대화하기")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{model1}와 1:1 대화**")
        for message in st.session_state.messages1[1:]:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        with st.form("form1", clear_on_submit=True):
            prompt1 = st.text_input(f"{model1}에게 개별 질문하기", key="input1")
            submitted1 = st.form_submit_button("전송", use_container_width=True)
            if submitted1 and prompt1:
                st.session_state.messages1.append({"role": "user", "content": prompt1})
                with st.chat_message("user"):
                    st.write(prompt1)
                with st.chat_message("assistant"):
                    assistant_response = get_chat_response(prompt1, st.session_state.messages1, model1)
                    st.write(assistant_response)
                    st.session_state.messages1.append({"role": "assistant", "content": assistant_response})

    with col2:
        st.markdown(f"**{model2}와 1:1 대화**")
        for message in st.session_state.messages2[1:]:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        with st.form("form2", clear_on_submit=True):
            prompt2 = st.text_input(f"{model2}에게 개별 질문하기", key="input2")
            submitted2 = st.form_submit_button("전송", use_container_width=True)
            if submitted2 and prompt2:
                st.session_state.messages2.append({"role": "user", "content": prompt2})
                with st.chat_message("user"):
                    st.write(prompt2)
                with st.chat_message("assistant"):
                    assistant_response = get_chat_response(prompt2, st.session_state.messages2, model2)
                    st.write(assistant_response)
                    st.session_state.messages2.append({"role": "assistant", "content": assistant_response})