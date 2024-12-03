
import oracledb
import API


def create_connection():
    try:
        connection = oracledb.connect(
            user="ebizai",
            password="ebizai",
            dsn="localhost:1521/FREEPDB1"
        )
        API.logger.info("Connection Establised Succesfully")
        return connection
    except oracledb.Error as e:
        API.logger.error(f"Error connecting to database: {e}")
        return None

def history(question,session_id,answer,token,time,user_id,date):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO rag_history (question, session_id, tokens, time_in_secs,user_id,conversation_date,answer)
        VALUES (:question, :session_id, :tokens, :time_in_secs,:user_id,:conversation_date,:answer)
        """
        data = {
            "question": question,
            "session_id": session_id,
            "answer": answer,
            "tokens": token,
            "time_in_secs": time,
            "user_id":user_id,
            "conversation_date":date
        }
        try:
            cursor.execute(insert_query, data)
            connection.commit()
            API.logger.info(f"Data Inserted Succesfully:{data}")
        except oracledb.DatabaseError as e:
            error, = e.args
            print("Error code:", error.code)
            print("Error message:", error.message)
        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()
    except Exception as e:
        return f"Error While Storing History:{e}"

