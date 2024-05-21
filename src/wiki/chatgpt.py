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

os.environ["OPENAI_API_KEY"] = getpass.getpass()

# import dotenv

# dotenv.load_dotenv()

# query = sys.argv[0]

# loader = TextLoader('data.txt')
# index = VectorstoreIndexCreator().fron_loaders([loader])

# print(index.query(query))

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# Load, chunk and index the contents of the blog.
# loader = WebBaseLoader(
#     web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )
loader = TextLoader('data.txt')
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

for chunk in rag_chain.stream("When is my birthday"):
    print(chunk, end="", flush=True)
    