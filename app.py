import openai
import langchain 
import streamlit as st
import os 
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv 
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.document_loaders import UnstructuredURLLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter 


load_dotenv() 

def loadurl(url):
    doc = UnstructuredURLLoader(urls=[url])
    loder = doc.load()
    return loder

def originaldoc(url):
  #page = requests.get(url)
  data = Article(url, language="en")
  data.download()
  data.parse()
  #data = soup.find('div', class_ = 'vector-body').text
  return data.text()



def chunk(data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1600,
        chunk_overlap = 20
    )
    textsplit = splitter.split_documents(data)
    return textsplit

template_title = PromptTemplate(
  template="You are good content generator. Reading the following document take out relevent metadata and Generate one  engaging title for the given topic focused on {data}",
  input_variables=['data']
  )

template_content = PromptTemplate(
  template="You are good content generator. Generate a  engaging content that is SEO Optimized for the given title focused on {title}",
  input_variables=['title']
  )


#llm = OpenAI(temperature=0.9, verbose= True)

#title_chain = LLMChain(llm=llm, prompt=template_title, verbose= True,output_key='title')

#content_chain = LLMChain(llm=llm, prompt=template_content, verbose= True,output_key='content')

#sequential_chain = SequentialChain(chains=[title_chain,content_chain], input_variables=['data'],output_variables=['title','content']) 


st.set_page_config(page_title="LLM")
st.header("SEO Optimizes Article Generation Application")

input_url = st.text_input("Input: ", key="input")

submit_button = st.button("Click Here To Generate")

if submit_button:

    #urldata = loadurl(input_url)
    orignal = originaldoc(input_url)
    #splitdata = chunk(urldata)
    #response = sequential_chain(splitdata)

    st.subheader("The Response is")
    #st.write(response['title'])
    #st.write(response['content'])
    st.write(orignal)
    #st.write(urldata)
