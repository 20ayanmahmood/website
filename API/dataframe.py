import oracledb
import pandas as pd
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
import json
from fastapi.middleware.cors import CORSMiddleware
# FastAPI initialization
import logging
from fastapi import FastAPI, HTTPException, Request
load_dotenv()

genai.configure(api_key=os.environ["API_KEY"])


llm = genai.GenerativeModel("gemini-1.5-flash",generation_config={"temperature":0.8})
#Loggers
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

df=None
app=FastAPI()

origins = [
    "http://localhost",  
    "http://localhost:8000",
    "http://192.168.5.72",
    "http://192.168.5.151:8001"

]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

'''------------------------------------ Classes ----------------------------------------------------'''

class QueryRequest(BaseModel):
    sql_query: str
    user: str
    password: str
    dsn: str
    question:str

class Creds(BaseModel):
    sql_query: str
    user: str
    password: str
    dsn: str
class Question(BaseModel):
    question : str

'''----------------------------------------------  Function   -----------------------------------------'''

def data(sql_query,user,password,dsn):
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    # Fetch data from the database and load into a pandas DataFrame
    df = pd.read_sql(sql_query, con=connection)
    return df

def relevant_table(question,df):
    list1=[]
    for i in df.columns:
        list1.append(df[i].dtype)

    prompt = """
    Write Python pandas code based on the user's question: {question}.
    Print the most relevant table
    You have access to the following DataFrame column names:
    {df}
    datatype of columns list: {datatype}
    Sample of Data: {sample}
    Import All the neccessary libraries
    **Dataframe is df**.
    Make sure to include comments in the code.
    Output **only** the Python code, no explanation, no text, just code.
    Just show the relevant columns.
    The final output should be  an dataframe not an numeric or anything 
    **final output should be an pandas dataframe**
    **final dataframe variable name should be output_df**
    
    # Your code starts below:
    """

    prompt = PromptTemplate(template=prompt
    , input_variables=["question","df","datatype","sample"])
    prompt_formatted_str = prompt.format(
        question=question,df=df.columns,datatype=list1,sample=df.sample()
    )
    prediction = llm.generate_content(prompt_formatted_str)
    prediction =prediction.text
    prediction=prediction.replace("```python","")
    prediction=prediction.replace("```","")
    return prediction

# def convert_datetime_columns_to_str(df):
#     for col in df.columns:
#         # If the column is of datetime type, handle possible overflow errors
#         if df[col].dtype == "datetime64[ns]" or df[col].dtype == 'object':  # Include 'object' in case dates are strings
#             try:
#                 df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime, invalid values become NaT
#                 df[col] = df[col].astype(str)  # Convert datetime to string after handling invalid dates
#             except Exception as e:
#                 raise HTTPException(status_code=500, detail=f"Date conversion error: {str(e)}")
#     return df


'''-------------------------------------- API ---------------------------------'''


# @app.post("/questions")
# async def dataframe(query_request: QueryRequest):
#     try:
#         # Use the DataFrmae function to execute the SQL query and fetch data
#         df = data(query_request.sql_query, query_request.user, query_request.password, query_request.dsn)
#         question=query_request.question
#         code=relevant_table(question,df)
#         local_vars={"df":df,"output_df":None}
#         exec(code,{},local_vars)
#         output_df=local_vars.get("output_df")
#         output_json = {"Dataframe":output_df.to_json(orient="records", date_format="iso")}  # 'records' makes it list of dictionaries
#         return output_json
#     except Exception as e:
#         # Raise an HTTP exception with the error message
#         raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    

@app.post("/input")
async def creds(new_request:Creds):
    global df  # Access the global df
    try:
        # Fetch the DataFrame
        df = data(new_request.sql_query, new_request.user, new_request.password, new_request.dsn)
        return {"message": "DataFrame stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.post("/answer")
async def answer(question : Question):
    global df
    if df is None:
        raise HTTPException(status_code=400, detail="DataFrame has not been created yet.")
    else:
        try:
            question=question.question
            logger.info("Recieved question:%s",question)
            code=relevant_table(question,df)
            local_vars={"df":df,"output_df":None}
            exec(code,{},local_vars)
            output_df=local_vars.get("output_df")
            logger.info("Output Generated Successfully")
            output_json = {"Dataframe":output_df.to_json(orient="records", date_format="iso")}  
            return output_json
        except Exception as e:
            logger.info("Error:%s",e)
            return "Encountered an Error Please Re Run"

