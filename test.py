from fastmcp import FastMCP
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expences.db")

mcp = FastMCP("ExpenceTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
create table if not exist expences(
    id integer primary key autoincrement,
    date  text not null,
    amount real not null,
    catagory text not null,
    subcatagory text default '',
    note text default ''
)
""")

init_db()



@mcp.tool
def add_expence(date, amount, catagory, subcatagory='', note=''):
    '''add new expence entry to the database'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "insert into expences(date,amount, catagory, subcatagory, note) values (?,?,?,?,?)",
            (date,amount,catagory,subcatagory,note)
        )
        return {'status':'ok', 'id':cur.lastrowid}


@mcp.tool
def list_expences(start_date, end_date):
    """list all entries from the databaseS"""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
        """
        SELECT id,date,amount,catagory,subcatagory, note " \
        "FROM expences "
        "WHERE date between ? AND ?"
        "ORDER BY id ASC
        """,
        (start_date,end_date)
        )
        cols = [id[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]




@mcp.tool
def summarize(start_date,end_date,catagory=None):
    """summarize expenses by catagory within inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        query = (
            """
            SELECT catagory ,SUM(amount) as total_amount
            FROM expences
            WHERE date BETWEEN ? AND ?
            """
        )
        params = [start_date,end_date]

        if catagory:
            query += "AND catagory = ?"
            params.append(catagory)

        query += "GROUP BY catagory ORDER BY catagory ASC"

        cur  = c.execute(query,params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]
    


if __name__ == "__main__":
    mcp.run()