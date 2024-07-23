import os
from fastapi import FastAPI, Request

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq

from dotenv import load_dotenv
from groq import Groq
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
import uuid
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

## create a global var for count of vector dbs in ####
vector_db_count=len(os.listdir('vector_dbs'))


###### CORS ######
app = FastAPI()
origins = [
    "http://localhost:3000",  # React app origin
    "http://localhost:5173/",  # Vite default dev server port
    "http://localhost:5173",
    "http://sgkg.tech"
    "http://sgkg.tech/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

######## GPT4All Embeddings ########

model_name = "all-MiniLM-L6-v2.gguf2.f16.gguf"
gpt4all_kwargs = {'allow_download': 'True'}
embeddings = GPT4AllEmbeddings(
    model_name=model_name,
    gpt4all_kwargs=gpt4all_kwargs
)

########create db ########

functions = [
    {
        "name": "hypothetical_questions",
        "description": "Generate hypothetical questions",
        "parameters": {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["questions"],
        },
    }
]

chain = (
    {"doc": lambda x: x.page_content}
    # Only asking for 3 hypothetical questions, but this could be adjusted
    | ChatPromptTemplate.from_template(
        "Generate a list of exactly 3 hypothetical questions that the below document could be used to answer:\n\n{doc}"
    )
    | ChatGroq(max_retries=0, model="llama3-groq-70b-8192-tool-use-preview").bind(
        functions=functions, function_call={"name": "hypothetical_questions"}
    )
    | JsonKeyOutputFunctionsParser(key_name="questions")
)

def create_question_rag():
    directory = 'pdfs'
    file_list = os.listdir(directory)
    loaders = [
        PyPDFLoader(f"pdfs/{x}") for x in file_list
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7000)
    docs = text_splitter.split_documents(docs)
    hypothetical_questions = chain.batch(docs, {"max_concurrency": 5})
    vectorstore = Chroma(
        collection_name="hypo-questions", embedding_function=GPT4AllEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"
    # The retriever (empty to start)
    global retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=store,
        id_key=id_key,
    )
    doc_ids = [str(uuid.uuid4()) for _ in docs]
    question_docs = []
    for i, question_list in enumerate(hypothetical_questions):
        question_docs.extend(
            [Document(page_content=s, metadata={id_key: doc_ids[i]}) for s in question_list]
        )
    retriever.vectorstore.add_documents(question_docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))
    #delete the pdfs
    for file in file_list:
        os.remove(f'pdfs/{file}')


def create_parent_doc_rag():
    directory = 'pdfs'
    file_list = os.listdir(directory)
    loaders = [
        PyPDFLoader(f"pdfs/{x}") for x in file_list
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    docs = text_splitter.split_documents(docs)
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="full_documents", embedding_function=GPT4AllEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"
    # The retriever (empty to start)
    global retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=store,
        id_key=id_key,
    )
    import uuid

    doc_ids = [str(uuid.uuid4()) for _ in docs]
    # The splitter to use to create smaller chunks
    child_text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)
    sub_docs = []
    for i, doc in enumerate(docs):
        _id = doc_ids[i]
        _sub_docs = child_text_splitter.split_documents([doc])
        for _doc in _sub_docs:
            _doc.metadata[id_key] = _id
        sub_docs.extend(_sub_docs)
    retriever.vectorstore.add_documents(sub_docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))
    for file in file_list:
        os.remove(f'pdfs/{file}')

def create_naive_rag():
    directory = 'pdfs'
    file_list = os.listdir(directory)
    loaders = [
        PyPDFLoader(f"pdfs/{x}") for x in file_list
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000)
    docs = text_splitter.split_documents(docs)
    # The vectorstore to use to index the child chunks
    embeddings = GPT4AllEmbeddings()
    vectorstore = Chroma.from_documents(docs, embeddings)
    global retriever
    retriever=vectorstore.as_retriever()
    for file in file_list:
        os.remove(f'pdfs/{file}')


######## Chroma Vectorstore ########

#### PROMPT GENERATOR ####

def prompt_generator(prompt):
    context_list=retriever.invoke(prompt)
    context=""
    for i in range(len(context_list)):
        context+=context_list[i].page_content+"\n"
        
    statement=f"Here is the context for your query: <context> \n {context} \n <context>"
    statement+=" using  this context answer the question below "
    statement+=f"<question> : \n {prompt} \n <question>"
    statement+=" \n Please provide the answer to the question above"
    return statement,context


######## AI Client  ########

client = Groq(api_key=GROQ_API_KEY)



def query_modifier(messages):
    user_message = messages[-1].content
    if len(messages) == 1:
        return user_message
    system_prompt = """
    You are an expert query reformulation assistant. Your task is to modify the given query to make it self-sufficient and not require any context to answer. The modified query should be clear, concise, and able to stand alone.

    Guidelines:
    1. Identify the core question or request in the query.
    2. Add any missing context from previous messages if necessary.
    3. Rephrase the query as a clear question or statement.
    4. Ensure the modified query contains all relevant information.
    5. Avoid references to previous conversation or external context.

    some examples of query modification:
    <previous_conversation> The Industrial Revolution had a significant impact on society and the economy. <previous_conversation> now modify the user message based on the conversation history <user_message> "What about its impact?" <user_message>
    Modified: "What was the impact of the Industrial Revolution on society and the economy?"

    <previous_conversation> The world war 2 was a global conflict that lasted from 1939 to 1945. <previous_conversation> now modify the user message based on the conversation history <user_message> "What happened during the war?" <user_message>
    Modified: "What events occurred during World War II?"

    <previous_conversation> The Mona Lisa is a famous painting by Leonardo da Vinci. <previous_conversation> now modify the user message based on the conversation history <user_message> "Tell me about it." <user_message>
    Modified: "What is the significance of the Mona Lisa painting by Leonardo da Vinci?"


    """
    previous_conversation=""
    for i in range(len(messages)-1):
        previous_conversation+=messages[i].content+"\n"
    modify_prompt = f"<previous_conversation> {previous_conversation} <previous_conversation> now modify the user message based on the conversation history <user_message> {user_message} <user_message>"
    stream = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": system_prompt},
        ] +
        [
            {"role": m.role, "content": m.content}
            for m in messages[:-1]
        ] + [{"role": "user", "content": modify_prompt}],
        temperature=0.0,
    )

    response = stream.choices[0].message.content
    return response


######## API Endpoints ########
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class rag_type(BaseModel):
    rag: str


### few shots ####

# few_shots=[
#     {'role':'user',
#     'content':'''Here is the context for your query: <context> \n before age of 50 years due to heart disease in one or more\nrelatives\n7. Disability from heart disease in a close relative before age\nof 50 years\n8. Specific knowledge of certain cardiac conditions in family\nmembers: hypertrophic cardiomyopathy, dilated cardiomy-\nopathy, long QT syndrome or other ion channelopathies,\nMarfan syndrome, or other important arrhythmias\nphysical Examination\n9. Heart murmur\n10. Diminished femoral pulse (to exclude coarctation)\n11. Phenotype of Marfan syndrome\n12. Brachial artery blood pressure (sitting position)\nReproduced with permission from Lawless CE, Asplund C, Asif IM,\net al. Protecting the heart of the American athlete: proceedings of\nthe American College of Cardiology Sports and Exercise Cardiology\nThink Tank October 18, 2012, Washington, DC. J Am Coll Cardiol.\n2014;64(20):2146–2171.CMDT23_Ch10_p0323-p0441.indd \n439 30/06/22 3:10 PM\nHistory of ischemic heart disease\nHistory of heart failure\nInsulin treatment for diabetes mellitus\nSerum creatinine level > 2 mg/dL (> 176.8 mcmol/L)\nHistory of cerebrovascular disease\nScoring (Number of\nPredictors Present)Risk of Major Cardiac\nComplications1None\n0.4%\nOne 1%\nTwo 2.4%\nMore than two 5.4%1\nCardiac death, MI, or nonfatal cardiac arrest.\nData from Devereaux PJ et al. Perioperative cardiac events in\npatients undergoing noncardiac surgery: a review of the magni-\ntude of the problem, the pathophysiology of the events and\nmethods to estimate and communicate risk. CMAJ. 2005;173:627.CMDT23_Ch03_p0042-p0051.indd \n43 25/06/22 2:41 PM\nCHApTER 10440 CMDT 2023T\nable 10–20. Recommendations or competitive sports participation among athletes with potential causes o SCD.Condition\n36th Bethesda Conference Euroean Society of Cardiology\nStructural Cardiac Abnormalities\nHCM Exclude athletes with a probable or definitive\nclinical diagnosis from all competitive sports.\nGenotype-positive/phenotype-negative\nathletes may still compete.Exclude athletes with a probable or definitive clinical\ndiagnosis from all competitive sports.\nExclude genotype-positive/phenotype-negative\nindividuals from competitive sports.\nARVC Exclude athletes with a probable or definitive\ndiagnosis from competitive sports.Exclude athletes with a probable or definitive\ndiagnosis from competitive sports.\nCCAA Exclude from competitive sports. Not applicable.\nParticipation in all sports 3 months after successful\nsurgery would be permitted for an athlete\nwith ischemia, ventricular arrhythmia or\ntachyarrhythmia, or LV dysfunction during maximal\nexercise testing.\nElectrical Cardiac Abnormalities\nWPW Athletes without structural heart disease, without\na history of palpitations, or without tachycardia\ncan participate in all competitive sports.\nIn athletes with symptoms, electrophysiological\nstudy and ablation are recommended. Return to\ncompetitive sports is allowed after corrective ablation,\nprovided that the ECG has normalized.Athletes without structural heart disease,\nwithout a history of palpitations, or without\ntachycardia can participate in all competitive\nsports.\nIn athletes with symptoms, electrophysiological\nstudy and ablation are recommended. Return to\ncompetitive sports is allowed after corrective\nablation, provided that the ECG has normalized.\nLQTS Exclude any athlete with a previous cardiac arrest\nor syncopal episode from competitive sports.\nAsymptomatic patients restricted to competitive\nlow-intensity sports.\nGenotype-positive/phenotype-negative athletes\nmay still compete.Exclude any athlete with a clinical or genotype\ndiagnosis from competitive sports.\nBrS Exclude from all competitive sports except those\nof low intensity.Exclude from all competitive sports.\nCPVT Exclude all patients with a clinical diagnosis from\ncompetitive sports.\nGenotype-positive/phenotype-negative patients\nmay still compete in low-intensity sports.Exclude all patients with a clinical diagnosis\nfrom competitive sports.\nGenotype-positive/phenotype-negative\npatients are also excluded.\nAcquired Cardiac Abnormalities\nCommotio cordis Eligibility for returning to competitive sport in survivors\nis a matter of individual clinical judgment. Survivors\nmust undergo a thorough cardiovascular workup\nincluding 12-lead ECG, ambulatory ECG monitoring,\nand echocardiography.Not applicable.\nMyocarditis Exclude from all competitive sports.\nConvalescent period of 6 months.\nAthletes may return to competition when test\nresults normalize.Exclude from all competitive sports.\nConvalescent period of 6 months.\nAthletes may return to competition when\ntest results normalize.\nARVC, arrhythmogenic right ventricular cardiomyopathy; BrS, Brugada syndrome; CCAA, congenital coronary artery anomalies; CPVT, cat-\necholaminergic polymorphic ventricular tachycardia; HCM, hypertrophic cardiomyopathy; LQTS, long QT syndrome; SCD, sudden cardi ac\ndeath; WPW, Wolff-Parkinson-White syndrome.\nReproduced with permission from Chandra N et al. Sudden cardiac death in young athletes: practical challenges and diagnostic di lemmas.\nJ Am Coll Cardiol. 2013;61(10):1027–1040.CMDT23_Ch10_p0323-p0441.indd \n440 30/06/22 3:10 PM\n \n <context> using  this context answer the question below <question> : \n heart failure \n <question> \n Please provide the answer to the question above
    
#     '''},
#     {'role':'assistant',
#     'content':''' #Heart Failure \n\nHeart failure is a condition where the heart cannot pump blood efficiently to meet the body's needs. It can be caused by various factors, including high blood pressure, coronary artery disease, heart valve problems, cardiomyopathy, and congenital heart defects.\n\nIn the context you provided, there are several risk factors for major cardiac complications, one of which is a history of heart failure. The presence of multiple risk factors increases the likelihood of cardiac complications during noncardiac surgery.\n\nRegarding sports participation, athletes with a history of heart failure are generally advised to avoid competitive sports, as they have an increased risk of cardiac events. However, individual clinical judgment is essential, and athletes may return to competition when test results normalize after a convalescent period, such as in myocarditis.\n\nIt is important to consult a healthcare professional for personalized advice and recommendations regarding heart failure and sports participation.
# '''
#     }
# ]


@app.post("/create_db/")
async def create_db(request: rag_type):
    # create_vector_db()
    rag_type=request.rag
    if rag_type=="naive":
        create_naive_rag()
    elif rag_type=="parent":
        create_parent_doc_rag()
    elif rag_type=="question":
        create_question_rag()
    return {"response": "<strong> You can now chat with the uploaded pdfs <strong> "}

@app.post("/doctor/")
async def chat(request: ChatRequest):
    messages = request.messages
    modified_user_query=query_modifier(messages)

    newprompt,context=prompt_generator(modified_user_query)
    stream = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you always use the Markdown format to provide the answer to the user's question. if you do not use the markdown format when it is possible you will be penalized. try to always answer in bullet points or numbered lists. use different headings to separate different sections. never use the 'in the provided context' phrase. or similar phrases. always provide the answer directly."},
        ] +
        [
            {"role": m.role, "content": m.content}
            for m in messages[:-1]
        ] + [{"role": "user", "content": newprompt}],
        temperature=0.0,
    )

    response = stream.choices[0].message.content
    return {"response": response,'modified_prompt':modified_user_query,'context':newprompt}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


