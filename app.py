import pandas as pd
import mysql.connector
from flask import Flask,jsonify,request

app=Flask(__name__)

filename="D:/Excel/Customer Call List.xlsx"
xl_sheets=pd.ExcelFile(filename)
print(xl_sheets.sheet_names)

df=pd.read_excel(filename)
print(df.info())

df=df.drop_duplicates()
df=df.drop(columns="Not_Useful_Column")
df.head(20)
df["Last_Name"]=df["Last_Name"].str.strip("123._/")

df["Phone_Number"]=df["Phone_Number"].str.replace(r"[^a-zA-Z0-9]","",regex=True)
df["Phone_Number"]=df["Phone_Number"].apply(lambda ph: str(ph))
df["Phone_Number"]=df["Phone_Number"].apply(lambda ph_num: ph_num[0:3]+"-"+ph_num[3:6]+"-"+ph_num[6:10] if len(ph_num)==10 else ph_num)
df["Phone_Number"]=df["Phone_Number"].str.replace("nan","")
df["Phone_Number"]=df["Phone_Number"].str.replace("Na","")

df[["Street_Address","State","Zip_Code"]]=df["Address"].str.split(",",expand=True)

df["Paying Customer"]=df["Paying Customer"].str.replace("Yes","Y")
df["Paying Customer"]=df["Paying Customer"].str.replace("No","N")

df["Do_Not_Contact"]=df["Do_Not_Contact"].str.replace("Yes","Y")
df["Do_Not_Contact"]=df["Do_Not_Contact"].str.replace("No","N")

df=df.replace("N/a","")
df=df.fillna('')

df.columns=df.columns.str.replace("_"," ")
for i in range(len(df)):
    if df.loc[i,"Do Not Contact"]=='':
        df.loc[i,"Do Not Contact"]='N'


filteredDataFrame=df
with pd.ExcelWriter(filename,mode='a',engine="openpyxl",if_sheet_exists='replace') as writer:
    filteredDataFrame.to_excel(writer,sheet_name="Filtered Data",index=True)

for i in df.index:
    if df.loc[i,"Do Not Contact"]=='Y':
        df.drop(i,inplace=True)

for ind in df.index:
    if df.loc[ind,"Phone Number"]=='':
        df.drop(ind,inplace=True)

df=df.reset_index(drop=True)

with pd.ExcelWriter(filename,mode='a',engine="openpyxl",if_sheet_exists='replace') as writer:
    df.to_excel(writer,sheet_name="Filtered Target Data",index=False)

myDB=mysql.connector.connect(
    host="localhost",
    username="root",
    password="root",
    database="my_schema"
)
myCursor=myDB.cursor(buffered=True)

myCursor.execute("show tables")
tables=myCursor.fetchall()
table_list=[]
for table in tables:
    table_list.append(table[0])

list1=filename.split("/")
tableName=list1[len(list1)-1].split(".")[0].replace(" ","_")


tableColumns=df.columns.to_list()
tableColumns=[cols.replace(" ","_") for cols in tableColumns]

createTable=f"create table if not exists {tableName}({tableColumns[0]} varchar(100),{tableColumns[1]} varchar(100),{tableColumns[2]} varchar(100),{tableColumns[3]} varchar(100),{tableColumns[4]} varchar(255))"

if tableName.lower() not in [table.lower() for table in table_list]:
    myCursor.execute(createTable)
    print("Table created successfully")
else:
    print("Table already exists")
dataSet=[[] for _ in range(5)]
row1=df["CustomerID"].to_list()
row2=df["First Name"].tolist()
row3=df["Last Name"].to_list()
row4=df["Phone Number"].to_list()
row5=df["Address"].to_list()
dataSet=[row1,row2,row3,row4,row5]
print(dataSet)
val=[]

for col in range(len(dataSet[0])):
    temp=[]
    for row in range(len(dataSet)):
        temp.append(dataSet[row][col])
    val.append(tuple(temp))

myCursor.execute(f"select count(*) from {tableName}")
res=myCursor.fetchone()
if res[0]==0:
    statement=f"insert into {tableName} values(%s,%s,%s,%s,%s)"
    myCursor.executemany(statement,val)
    myDB.commit()
    print(myCursor.rowcount," rows are added in the table")
else:
    print("Rows are already added in the table")

@app.route("/table",methods=["GET"])
def filteredData():
    data={
        "Customer_ID":df["CustomerID"].to_list(),
        "First_Name":df["First Name"].to_list(),
        "Last_Name":df["Last Name"].to_list(),
        "Phone_Number":df["Phone Number"].to_list(),
        "Customer_Address":df["Address"].to_list()
    }
    return jsonify(data)

if __name__=="__main__":
    app.run(debug=True)
