from flask import Flask,render_template,request,redirect,session,url_for, flash
from database import conn, cur
from functools import wraps

#functools import wraps is initialised to use the decorator function

# flask name initiates app- class obj
app = Flask(__name__)

#secret placed for runing sessions
app.secret_key="myduka123"

#Decorator function is used to give a func/route more functionality
#runs before the route function is processed

def login_required(f):
    @wraps(f)
    def protected(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        return redirect("/login")
    return protected

# Define a custom filter- this will be used to format the date
@app.template_filter('strftime')
def format_datetime(value, format="%B %d, %Y"):
    return value.strftime(format)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/navbar")
def navb():
    return render_template("navbar.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/about")
def about():
    return "About page info is supposed to be displayed on this route"

@app.route("/dashboard")
# @login_required
def dashboardfunc():
    cur.execute("SELECT sum (p.selling_price * s.quantity) as sales, s.created_at from sales as s join products as p on p.id=s.pid GROUP BY created_at ORDER BY created_at;")
    daily_sales=cur.fetchall()
   # print(daily_sales)
    x=[]
    y=[]
    for i in daily_sales:
        x.append(i[1].strftime("%B %d, %Y"))
        y.append(float(i[0]))
        
    # list comprehension
    #lx = [i[1].strftime("%B %d, %Y") for i in daily_sales]
    #ly = [i[0] for i in daily_sales]

    #append happens because it is inside a list
    #you can also add an if statement
    lx = [i[1].strftime("%B %d, %Y") for i in daily_sales if float(i[0])>60000]
    cur.execute("SELECT sum (p.selling_price * s.quantity) as Profit, p.name from products as p join sales as s on p.id=s.pid GROUP BY p.name ORDER BY profit desc;")
    profit_per_product=cur.fetchall()
    p=[]
    q=[]
    for z in profit_per_product:
        p.append(z[1])
        q.append(z[0])

        cur.execute("""
        SELECT SUM(p.selling_price * s.quantity) AS monthly_sales, 
               DATE_TRUNC('month', s.created_at) AS month 
        FROM sales AS s 
        JOIN products AS p ON p.id = s.pid 
        GROUP BY month 
        ORDER BY month;
    """)
    monthly_sales = cur.fetchall()
    m = [i[1].strftime("%B, %Y") for i in monthly_sales]
    n = [float(i[0]) for i in monthly_sales]

     # Data for the fourth chart (e.g., top 5 products)
    cur.execute("""
        SELECT p.name, SUM(p.selling_price * s.quantity) AS total_sales 
        FROM products AS p 
        JOIN sales AS s ON p.id = s.pid 
        GROUP BY p.name 
        ORDER BY total_sales DESC 
        LIMIT 5;
    """)
    top_products = cur.fetchall()
    t = [i[0] for i in top_products]
    u = [float(i[1]) for i in top_products]
    return render_template("dashboard.html",x=x,y=y,p=p,q=q,m=m, n=n, t=t, u=u)


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method=="POST":
        email=request.form["mail"]
        password=request.form["passw"]
        cur.execute("select id from users where email='{}' and password='{}'".format(email,password))
        row= cur.fetchone()
        if row== None:
            return "Invalid Credentials"
        else:
            session["email"]= email
            return redirect("/dashboard")
    else:
        return render_template("login.html")  


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["mail"]
        password = request.form["passw"]
        
        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash("Email already registered. Please use a different email.", "error")
            return redirect("/register")  # Redirect back to the registration page
        
        # Insert the new user into the database
        try:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            conn.commit()  # Commit the transaction
            flash("Registration successful! Please log in.", "success")
            return redirect("/login")
        except Exception as e:
            conn.rollback()  # Rollback if there's an issue
            flash(f"An error occurred: {e}", "error")
            return redirect("/register")
    else:
        return render_template("register.html")





@app.route("/products", methods=["GET", "POST"])
#get is fetching from database and post is getting from form which is filled and posted
#model view controller uses this to get data from database and send it to view-which works across all frameworks
# @login_required
def products():

    if request.method == "GET":
        cur.execute("SELECT * FROM products order by id desc")
        products = cur.fetchall()
        print(products)
        return render_template("products.html", products=products)
    else:
        name = request.form["name"]
        buying_price = float(request.form["bp"])
        selling_price = float(request.form["sp"])
        stock_quantity = int(request.form["stqu"])
        #print(name, buying_price, selling_price, stock_quantity) 
        if selling_price < buying_price:
            return "Selling price should be greater than buying price"
        
        query="insert into products(name,buying_price,selling_price,stock_quantity) "\
        "values('{}',{},{},{})".format(name,buying_price,selling_price,stock_quantity)

        cur.execute(query)
        conn.commit()
        return redirect("/products")  

# Implement proper error handling
@app.route("/sales", methods=["GET", "POST"])
def salez():
    if request.method == "POST":
        pid = request.form["pid"]
        amount = request.form["amount"]
        try:
            query_s = "INSERT INTO sales(pid, quantity, created_at) VALUES (%s, %s, now())"
            cur.execute(query_s, (pid, amount))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Error:", e)
        return redirect("/sales")

    else:
        cur.execute("select * from products")
        products=cur.fetchall()
        cur.execute("select sales.ID, products.Name, sales.quantity, sales.created_at "\
                    "from sales inner join products on sales.pid = products.id")
        sales=cur.fetchall()
        return render_template("sales.html",products=products,sales=sales)
    

app.run(debug=True)





