import psycopg2

conn = psycopg2.connect(host="localhost" , port="5432", user="postgres", database="myduka", password="Glorious")


cur = conn.cursor()


print("Database connected successfully!")



