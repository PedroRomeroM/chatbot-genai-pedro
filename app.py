import os
from typing import Iterable

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(".env")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"
MODEL = os.getenv("NVIDIA_MODEL", DEFAULT_MODEL)

SYSTEM_PROMPT = """
Voce e um assistente especializado em engenharia de prompt e produtos de GenAI.

Seu papel e ajudar o usuario a entender, testar e melhorar prompts para modelos
de linguagem. Responda em portugues do Brasil, com clareza, exemplos praticos e
sem inventar informacoes quando a pergunta depender de dados externos.
"""


def get_client() -> OpenAI | None:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url=NVIDIA_BASE_URL,
    )


def build_messages() -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT.strip()}]
    messages.extend(st.session_state.messages)
    return messages


def stream_answer(client: OpenAI) -> Iterable[str]:
    response = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(),
        temperature=0.35,
        top_p=0.9,
        max_tokens=1024,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


st.set_page_config(
    page_title="Chatbot GenAI NVIDIA",
    page_icon="🤖",
    layout="wide",
)

st.title("Chatbot GenAI com NVIDIA")
st.caption("Streamlit + Python + modelo open source servido pela NVIDIA NIM")

with st.sidebar:
    st.header("Configuracao")
    st.markdown(f"**Modelo:** `{MODEL}`")
    st.markdown("**Provedor:** NVIDIA API Catalog / NIM")
    st.markdown("**Tema:** Engenharia de prompt e GenAI")

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Ola. Como posso ajudar com engenharia de prompt ou GenAI?",
            }
        ]
        st.rerun()

    st.divider()
    st.markdown(
        "Esta aplicacao usa uma chave `NVIDIA_API_KEY` configurada no ambiente "
        "da VM. A chave nao fica no codigo nem no repositorio."
    )

client = get_client()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ola. Como posso ajudar com engenharia de prompt ou GenAI?",
        }
    ]

if client is None:
    st.error(
        "A variavel NVIDIA_API_KEY nao esta configurada. "
        "Defina a chave no ambiente antes de iniciar o Streamlit."
    )
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Digite sua pergunta")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Gerando resposta..."):
            try:
                answer = st.write_stream(stream_answer(client))
            except Exception as error:  # noqa: BLE001 - Streamlit should show API failures cleanly.
                st.error("Nao foi possivel gerar a resposta agora.")
                st.caption(str(error))
                answer = ""

    if answer:
        st.session_state.messages.append({"role": "assistant", "content": answer})
