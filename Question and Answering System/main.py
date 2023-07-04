from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from nomic import atlas
import nomic
import openai

# setting up the environment variables
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '<YourPineConeKey>')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV', '<YourPineConeEnvironment>') 
OPENAI_API_TYPE =  os.environ.get("OPENAI_API_TYPE","azure")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE","https://<YourAzureOpenAPIResourceName>.openai.azure.com/")
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION","2023-05-15")
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY','<YourAzureOpenAPIKey>')
OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME","YourAzureOpenAIEmbeddingDeploymentName")
OPENAI_EMBEDDING_MODEL_NAME = os.getenv("OPENAI_EMBEDDING_MODEL_NAME","text-embedding-ada-002")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME","<YourAzureOPenAIGGPT35DeploymentName>")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME","gpt-35-turbo")

#init Azure OpenAI
openai.api_type = "azure"
openai.api_version = OPENAI_API_VERSION
openai.api_base = OPENAI_API_BASE
openai.api_key = OPENAI_API_KEY

# Initialize the OpenAI embeddings model for vectorization
embeddings = OpenAIEmbeddings(
    model=OPENAI_EMBEDDING_DEPLOYMENT_NAME,
    openai_api_type=OPENAI_API_TYPE, 
    openai_api_key=OPENAI_API_KEY , chunk_size=1)

# initialize pinecone vector store
pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to api key in console
)

loader = UnstructuredPDFLoader("<PathtoLoadPDFBook>")
data = loader.load()

print (f'You have {len(data)} document(s) in your data')
print (f'There are {len(data[0].page_content)} characters in your document')

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap  = 20,
    length_function = len,
    add_start_index = True,
)

texts = text_splitter.split_documents(data)
print (f'Now you have {len(texts)} documents')

INDEX_NAME = "<YourPineconeIndexName>"
DIMENSIONS = 1536

# Create and configure index if doesn't already exist
if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(
        name=INDEX_NAME, 
        metric="cosine",
        dimension=DIMENSIONS)
    docsearch = Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=INDEX_NAME)

else:
     docsearch = Pinecone.from_existing_index(INDEX_NAME, embeddings)

############### Use the below code only if you want to visulaize the embeddings in 2D Atlas map ############################

# #Visualizing Open AI Embeddings in 2D Atlas map

# #init nomic
#nomic.login('YourNomicAPIKey')

# index = pinecone.Index("langchain-openai")
# query_response = index.query(
#     namespace='',
#     vector= [0] * 1536,
#     top_k=1000,
#     include_values=True,
#     include_metadata=True
# )

# ids = []
# embeddings = []
# data = []

# for i in query_response['matches']:
#     dictionary = {}
#     dictionary["id"] = i['id']
#     dictionary["text"] = i['metadata']['text']
#     data.append(dictionary.copy())
#     embeddings.append(i['values'])
    

# embeddings = np.array(embeddings)
# atlas.map_embeddings(embeddings=embeddings, data=data, id_field='id')
##############################################################################################################

# function for conversation
def ask_question(qa, question):
    result = qa({"query": question})
    print("Question:", question)
    print("Answer:", result["result"])

# initialize the chat model
llm = AzureChatOpenAI(deployment_name=OPENAI_DEPLOYMENT_NAME,
                      model_name=OPENAI_MODEL_NAME,
                      openai_api_base=OPENAI_API_BASE,
                      openai_api_version=OPENAI_API_VERSION,
                      openai_api_key=OPENAI_API_KEY,
                      )

#use the vector store as a retriever
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":2})

#Retrive a chain for quetion answer against an index
retrivedText = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=False)

while True:
        query = input('you: ')
        if query == 'q':
            break
        ask_question(retrivedText, query)
