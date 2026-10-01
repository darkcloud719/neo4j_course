import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

if not URI:
    raise ValueError("NEO4J_URI is not set in the environment variables.")
if not USERNAME:
    raise ValueError("NEO4J_USERNAME is not set in the environment variables.")
if not PASSWORD:
    raise ValueError("NEO4J_PASSWORD is not set in the environment variables.")
if not DATABASE:
    raise ValueError("NEO4J_DATABASE is not set in the environment variables.")

def run_query(driver, query, **parameters):
    records, summary, keys = driver.execute_query(
        query,
        parameters_=parameters,
        database_=DATABASE
    )

    return records, summary

with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
    driver.verify_connectivity()
    print("Connected to Neo4j database:", DATABASE)

    run_query(
        driver,
        """
        MERGE (a:Person {name: $name_a})
        MERGE (b:Person {name: $name_b})
        MERGE (a)-[r:KNOWS]->(b)
        SET r.since = $since
        """,
        name_a="Nicky Chang",
        name_b="Bill Chen",
        since=2026
    )

    records, _ = run_query(
        driver,
        """
        MATCH (a:Person {name: $name_a})-[r:KNOWS]->(b:Person {name: $name_b})
        RETURN a.name AS person_a, type(r) AS relationship,
                r.since AS since, b.name AS person_b
        """,
        name_a="Nicky Chang",
        name_b="Bill Chen"
    )

    for record in records:
        print(f"record: {record}")
        print(record.data())

    # run_query(
    #     driver,
    #     """
    #     MATCH (a:Person {name: $name_a})-[r:KNOWS]->(b:Person {name: $name_b})
    #     DELETE r
    #     """,
    #     name_a="Nicky Chang",
    #     name_b="Bill Chen"
    # )

    run_query(
            driver,
            """
            MATCH (a:Person {name: $name_a})-[r:KNOWS]->(b:Person {name: $name_b})
            RETURN a , b
            """,
            name_a="Nicky Chang",
            name_b="Bill Chen"
        )

    