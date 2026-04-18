import os
import json
import pandas as pd

from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key = google_api_key)

# đọc file config
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

    functions = config.get('function', 'giới thiệu')
    initial_bot_message = config.get(
        'initial_bot_message',
        'chào bạn, tôi là chatbot hỗ trợ khách hàng'
    )



chatbot_df = pd.read_csv("chatbot.csv", encoding="utf-8")
products_df = pd.read_csv("products.csv", encoding="utf-8")
outfit_df = pd.read_csv("outfit.csv", encoding="utf-8")
payments_df = pd.read_csv("payments.csv", encoding="utf-8")


model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=f"""
Bạn là chatbot hỗ trợ khách hàng.

Bạn có thể:
- giới thiệu shopp 
- hiển thị menu
- tư vấn quần áo: {', '.join(products_df['name'].to_list())}
- gợi ý outfit theo từng mùa hoặc theo từng dịp , gồm các outfit như sau : {', '.join(outfit_df['style'].to_list())}
- hỗ trợ thanh toán

Nếu ngoài phạm vi thì trả lời thì sẽ báo chức năng này tôi không thể hỗ trợ và bạn có thể gọi điện trực tiếp qua số hotline : 0877996798
"""
)


def search_answer(user_text):
    for _, row in chatbot_df.iterrows():
        if row["question"] in user_text.lower():
            return row["answer"]
    return None



def get_products():
    result = []
    for _, row in products_df.iterrows():
        line = f"{row['name']} - {row['price']}k - size {row['size']} - {row['color']}"
        result.append(line)
    return "\n".join(result)



def get_outfit():
    # result = []
    # for _, row in outfit_df.iterrows():
    #     result.append(f"{row['style']}: {row['suggestion']}")
    # return "\n".join(result)
    return '\n'.join([f"**{row['style']}**: {row['suggestion']}" for index, row in outfit_df.iterrows()])



def get_payment():
    result = []
    for _, row in payments_df.iterrows():
        result.append(f"{row['method']}: {row['detail']}")
    return "\n".join(result)



def get_menu():
    result = []
    for _, row in menu_df.iterrows():
        result.append(f"{row['name']}: {row['description']}")
    return "\n".join(result)


def detect_type(text):
    text = text.lower()


    if "áo" in text or "quần" in text:
        return "product"

    if "mặc" in text or "outfit"  in text or "đi" in text or "mùa" in text:
        return "outfit"

    if "ship" in text or "thanh toán" in text:
        return "payment"

    return "ai"


def run_chatbot():

    st.title("Chatbot hỗ trợ khách hàng")
    st.write("xin chào, bạn cần hỗ trợ gì?")
    st.write("bạn có thể hỏi về sản phẩm hoặc shopp")

    
    if 'conversation_log' not in st.session_state:
        st.session_state.conversation_log = [
            {"role":"assistant", "content": initial_bot_message}
        ]

    
    for message in st.session_state.conversation_log:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])

    
    if prompt := st.chat_input("nhập câu hỏi..."):

        with st.chat_message("user"):
            st.write(prompt)

        st.session_state.conversation_log.append(
            {"role": "user", "content": prompt}
        )

        
        intent = detect_type(prompt)

        reply = search_answer(prompt)

        if not reply:

            if intent == "product":
                reply = get_products()

            elif intent == "outfit":
                reply = get_outfit()

            elif intent == "payment":
                reply = get_payment()

            elif intent == "menu":
                reply = get_menu()

            else:
                response = model.generate_content(prompt)
                reply = response.text

        
        with st.chat_message("assistant"):
            st.write(reply)

        st.session_state.conversation_log.append(
            {"role": "assistant", "content": reply}
        )


if __name__ == "__main__":
    run_chatbot()