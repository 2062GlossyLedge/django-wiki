from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import getpass
import os, sys
import environ
env = environ.Env()
environ.Env.read_env()

#langsmith 

os.environ["OPENAI_API_KEY"] = env("OPENAI_API_KEY")


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

#Load, chunk and index the contents of the blog.
loader = WebBaseLoader(
    web_paths=("http://localhost:8000/dune/characters/paul-atriedes/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("wiki-article")
        )
    ),
 )
# loader = TextLoader('data.txt')
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the blog.
#retriever = vectorstore.as_retriever()
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

print('***')
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# rag_chain.invoke("What is Task Decomposition?")

# # cleanup
# vectorstore.delete_collection()

for chunk in rag_chain.stream("Who is paul"):
    print(chunk, end="", flush=True)
    