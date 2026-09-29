import json

import pandas as pd
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="철도 민원 AI 어시스턴트", layout="wide")

client = OpenAI()


def classify_complaint(text):
    system_prompt = "너는 철도 역사 민원 분류 담당자다. 반드시 JSON으로만 답한다."
    few_shot = (
        '문의: "에스컬레이터가 멈췄어요" '
        '답변: {"분류": "승강설비", "긴급도": "높음"} '
    )
    user_prompt = few_shot + f'문의: "{text}"'
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


st.title("🚉 철도 민원 AI 어시스턴트")
st.write("민원 업로드부터 자동 분류, 상담 챗봇까지 한 화면에서 처리합니다.")

st.metric("전체 접수 민원", "12건")

with st.sidebar:
    st.header("메뉴")
    st.write("철도 민원 AI 어시스턴트")
    st.caption("2일차 실습용 프로토타입")

    # 추가:START
    # if st.button("대화 초기화"):
    #     st.session_state.messages = []
    #     st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])
    # 추가:END

tab1, tab2 = st.tabs(["📂 민원 업로드", "💬 민원 상담 챗봇"])

with tab1:
    st.subheader("민원 업로드 및 자동 분류")

    st.subheader("민원 현황 요약")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 접수", "12건")
    with col2:
        st.metric("처리 완료", "8건")
    with col3:
        st.metric("처리 대기", "4건")

    uploaded_file = st.file_uploader("민원 CSV 파일 업로드", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(f"총 {len(df)}건의 민원을 불러왔습니다.")

        category = st.selectbox("민원 유형 선택", ["전체", "승강설비", "위생", "안내설비"])
        if category != "전체":
            filtered = df[df["분류"] == category]
        else:
            filtered = df
        st.write(f"{category} 민원 {len(filtered)}건")
        st.dataframe(filtered)

        if st.button("자동 분류 실행"):
            with st.spinner("AI가 민원을 분류하는 중입니다..."):
                df["분류"] = df["text"].apply(lambda t: classify_complaint(t)["분류"])
            st.success(f"{len(df)}건의 분류가 완료되었습니다.")
            st.dataframe(df)

    st.subheader("새 민원 접수")
    with st.form("complaint_form"):
        station = st.text_input("발생 역")
        content = st.text_area("민원 내용")
        submitted = st.form_submit_button("접수하기")

    if submitted:
        st.success(f"[{station}] 민원이 접수되었습니다.")
        st.write(f"내용: {content}")

with tab2:
    st.subheader("민원 상담 챗봇")

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("민원을 입력해 주세요")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            result = classify_complaint(user_input)
            reply = f"분류: {result['분류']}로 접수되었습니다."
        except Exception as e:
            reply = "일시적인 오류로 분류에 실패했습니다. 잠시 후 다시 시도해 주세요."
            st.warning(f"오류 상세: {e}")

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()