from fuzzywuzzy import fuzz
from history import create_connection
import oracledb

def find_similarity(given_name):
    names_list=fetch_unique_questions()
    matches = []
    for name in names_list:
        similarity_score = fuzz.ratio(given_name, name)
        if similarity_score>=90:
            matches.append((name, similarity_score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

def fetch_unique_questions():
    # Define the Oracle connection parameters
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT question FROM rag_history"
    cursor.execute(query)
    unique_questions = cursor.fetchall()
    questions_list = [row[0] for row in unique_questions]
    return questions_list


def fetch_answer_for_question(question):
    conn = create_connection()
    cursor = conn.cursor()

    # Define the SQL query with a placeholder for the question
    query = "SELECT answer FROM rag_history WHERE question = :question"

    # Execute the query with the question parameter
    cursor.execute(query, {"question": question})

    # Fetch the result
    result = cursor.fetchone()

    if result:
        return result


