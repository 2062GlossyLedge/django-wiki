from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.chat_message_histories import SQLChatMessageHistory


import getpass
import os, sys
import environ

env = environ.Env()
environ.Env.read_env()

os.environ["OPENAI_API_KEY"] = env("OPENAI_API_KEY")
from langchain_openai import ChatOpenAI

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = env("LANGCHAIN_API_KEY")

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")


class Chatbot:

    def save_chat_history(
        self, article_revision, session_id, user_message, bot_response
    ):
        ChatHistory.objects.create(
            article_revision=article_revision,
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
        )

    def handle_message(self, article_revision, session_id, userPrompt):
        # https://python.langchain.com/v0.1/docs/use_cases/question_answering/quickstart/
        # gives chatbot the content of the wiki page and the users prompt to generate a response
        loader = TextLoader("context.txt")
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(
            documents=splits, embedding=OpenAIEmbeddings()
        )

        # Retrieve and generate using the relevant snippets of the wiki page.
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 6}
        )
        ### Contextualize question ###
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        ### Answer question ###
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        # https://python.langchain.com/v0.1/docs/integrations/memory/sqlite/
        chain_with_history = RunnableWithMessageHistory(
            rag_chain,
            lambda session_id: SQLChatMessageHistory(
                session_id=session_id,
                connection_string="sqlite:///sqlite.db",
            ),
            history_messages_key="chat_history",
            input_messages_key="input",
            output_messages_key="answer",
        )

        # This is where we configure the session id
        config = {"configurable": {"session_id": session_id}}

        response = chain_with_history.invoke({"input": userPrompt}, config=config)[
            "answer"
        ]
        # send prompt and response to template
        response = userPrompt + ": " + response

        # Save chat history
        # self.save_chat_history(article_revision, session_id, userPrompt, response)

        return response
