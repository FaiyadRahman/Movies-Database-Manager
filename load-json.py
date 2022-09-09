from pymongo import MongoClient
import json

def create_indexes(db):
    db["title_basics"].create_index([("primaryTitle", 1)])
    db["title_basics"].create_index([("startYear", 1)])
    db["title_basics"].create_index([("genres", 1)])
    db["title_ratings"].create_index([("averageRating", -1)])
    db["title_ratings"].create_index([("numVotes", 1)])
    db["title_ratings"].create_index([("tconst", "hashed")])
    db["title_basics"].create_index([("tconst", "hashed")])
    db["title_principals"].create_index([("tconst", "hashed")])
    db["title_principals"].create_index([("nconst", "hashed")])
    db["name_basics"].create_index([("nconst", "hashed")])

def main():
    collection_names = ["name_basics", "title_basics", "title_principals", "title_ratings"]
    file_names = ["name.basics.json", "title.basics.json", "title.principals.json", "title.ratings.json"]
    port = input("Please enter a valid port number: ")
    while not port.isnumeric():
        port = input("Invalid port. Please enter a valid port number: ")
    port = int(port)
    client = MongoClient('localhost', port)
    db = client["291db"]    

    for i, file_name in enumerate(file_names):
        with open(file_name, 'r',) as f:
            contents = json.loads(f.read())
        collection = db[collection_names[i]]
        collection.delete_many({})
        collection.insert_many(contents)
    
    create_indexes(db)
    
    print("done")
    

if __name__ == "__main__":
    main()

