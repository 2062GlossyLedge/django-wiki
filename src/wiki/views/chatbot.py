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
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.chat_history import HumanMessage, AIMessage, BaseMessage

from langchain_community.chat_message_histories import SQLChatMessageHistory


import getpass
import os, sys
import environ
import bs4
import pdb


env = environ.Env()
environ.Env.read_env()

os.environ["OPENAI_API_KEY"] = env("OPENAI_API_KEY")
from langchain_openai import ChatOpenAI

os.environ["GOOGLE_API_KEY"] = env("GOOGLE_API_KEY")

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = env("LANGCHAIN_API_KEY")

# llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.1)
# from langchain_google_vertexai import ChatVertexAI
# import vertexai
# from vertexai.preview import reasoning_engines

# vertexai.init(
#     project=env("GOOGLE_CLOUD_PROJECT_ID"),
#     location="us-central1",
#     staging_bucket=env("BUCKET_NAME"),
# )

# llm = ChatVertexAI(model="gemini-pro", temperature=0.1)

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

# llm = reasoning_engines.LangchainAgent(model="gemini-pro")

# create vectorstore
vectorstore = None

# have each wiki page have its own vectorstore
vectorstoreDict = dict()
docsDict = dict()


class Chatbot:

    def delete_chat_history(self, session):
        """delete chat history for a specific wiki page

        Args:
            urlPath (str): wiki page url
        """
        session_id0 = SQLChatMessageHistory(
            session_id=session,
            connection_string="sqlite:///sqlite.db",
        )

        session_id0 = SQLChatMessageHistory(
            session_id=session,
            connection_string="sqlite:///sqlite.db",
        )

        session_id0.clear()

    def getUserPrompt(self, userPrompt):
        return userPrompt

    def setPersonality(self, personality):
        if personality == "default":
            return "You are helpful and friendly assistant for question-answering tasks for WikiWard - a Wikipedia site"
        else:

            return f"You are {personality}. Act like this person or thing in your responses. State who you are at the beginning of your response."

    def handle_message_with_llm_knowledge(
        self, userPrompt, urlPath, personality, session
    ):
        """chatbot response to user input

        Args:
            userPrompt (str): user prompt

        Returns:
            str: chatbot response
        """
        # https://python.langchain.com/v0.1/docs/use_cases/question_answering/quickstart/

        global vectorstoreDict
        # breakpoint()

        # find if vectore already exists for current wiki page, else  scrape and create a new vectorstore if the URL hasn't been scraped yet
        if urlPath in vectorstoreDict:

            vectorstore = vectorstoreDict[urlPath]
            docs = docsDict[urlPath]
            if docs[0].page_content == "\n":
                docs[0].page_content = "No content found"

        else:
            # Scrape the wiki page
            loader = WebBaseLoader(
                web_paths=("http://localhost:8000/" + urlPath,),
                bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("wiki-article"))),
            )
            docs = loader.load()

            if docs[0].page_content == "\n":
                docs[0].page_content = "No content found"

            # print(docs)

            docsDict[urlPath] = docs

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)

            # create new vectore store

            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=OpenAIEmbeddings(),
                persist_directory="./chroma_db",
                # makes it so each stored db collection only holds document containing the contents of the single wiki page
                collection_name=urlPath.replace("/", ""),
            )
            vectorstoreDict[urlPath] = vectorstore
            # print(vectorstoreDict[urlPath]._collection)

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
        # helpful and friendly assistant for question-answering tasks for WikiWard - a spoiler free Wikipedia site.
        ### Answer question ###
        qa_system_prompt = (
            self.setPersonality(personality)
            + """\
        Use the following pieces of retrieved context to answer the question. \
        If the retrieved context does not answer the question, just say you don't know. \
        Use three sentences maximum and keep the answer concise.\
        Context: {context}\n\nQuestion: {input}
        """
        )

        # print(qa_system_prompt)
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        # this is where llm uses its model to answer the question
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        # https://python.langchain.com/v0.1/docs/integrations/memory/sqlite/
        chain_with_history = RunnableWithMessageHistory(
            rag_chain,
            # only use chat history from questions asked on the respective page
            lambda session_id: SQLChatMessageHistory(
                session_id=session,
                connection_string="sqlite:///sqlite.db",
            ),
            history_messages_key="chat_history",
            input_messages_key="input",
            output_messages_key="answer",
        )

        # This is where we configure the session id
        config = {"configurable": {"session_id": urlPath}}

        response = chain_with_history.invoke({"input": userPrompt}, config=config)[
            "answer"
        ]

    def handle_message_without_llm_knowledge(self, userPrompt, urlPath, session):
        """chatbot response to user input

        Args:
            userPrompt (str): user prompt

        Returns:
            str: chatbot response
        """
        global vectorstoreDict
        # breakpoint()

        # find if vectorstroe already holds contents of wiki page, else  scrape and create a new vectorstore if the URL hasn't been scraped yet
        if urlPath in vectorstoreDict:

            vectorstore = vectorstoreDict[urlPath]
            docs = docsDict[urlPath]

            if docs[0].page_content == "\n":
                docs[0].page_content = "No content found"

        else:
            # Scrape the wiki page
            loader = WebBaseLoader(
                web_paths=("http://localhost:8000/" + urlPath,),
                bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("wiki-article"))),
            )
            docs = loader.load()

            if docs[0].page_content == "\n":
                docs[0].page_content = "No content found"

            docsDict[urlPath] = docs

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)

            # create new vectore store

            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=OpenAIEmbeddings(),
                persist_directory="./chroma_db",
                # makes it so each stored db collection only holds document containing the contents of the single wiki page
                collection_name=urlPath.replace("/", ""),
            )
            vectorstoreDict[urlPath] = vectorstore

        # Retrieve and generate using the relevant snippets of the wiki page.
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 6}
        )

        prompt = hub.pull("rlm/rag-prompt")
        # prompt needs to be a dict
        # prompt = """You are an assistant for question-answering tasks for WikiWard - a spoiler free Wikipedia site. \
        # Use the following pieces of retrieved context to answer the question. \
        # If the retrieved context does not answer the question, just say you don't know. \
        # Use three sentences maximum and keep the answer concise.\
        # """

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        session_id1 = SQLChatMessageHistory(
            session_id=session,
            connection_string="sqlite:///sqlite.db",
        )

        # Add messages to the chat history

        userPromptMessage = HumanMessage(content=userPrompt)

        session_id1.add_user_message(userPromptMessage)

        response = rag_chain.invoke(userPrompt)

        responseMessage = AIMessage(content=response)
        session_id1.add_ai_message(responseMessage)
        return response

    def get_chat_history(self, session):
        """get chat history for a specific wiki page

        Args:
            urlPath (str): wiki page url

        Returns:
            list: chat history
        """
        session_id0 = SQLChatMessageHistory(
            session_id=session,
            connection_string="sqlite:///sqlite.db",
        )
        chat_history = str(session_id0)

        # Split the string by new lines
        lines = chat_history.split("\n")
        messages = []

        # Process each line
        for line in lines:
            if line.startswith("Human:"):
                # Remove the "Human:" label and strip leading/trailing whitespace
                messages.append(line.replace("Human:", "").strip())
            elif line.startswith("AI:"):
                # Remove the "AI:" label and strip leading/trailing whitespace
                messages.append(line.replace("AI:", "").strip())
            else:
                # If the line does not start with "Human:" or "AI:", it might be a continuation of the previous message
                if messages and not messages:
                    messages[-1] += " " + line.strip()
                elif messages and not messages:
                    messages[-1] += " " + line.strip()

        return messages
