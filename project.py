from pymongo import MongoClient

def main():
    # driver code
    Port = input("Please enter a port: ")
    if not Port.isnumeric():
        print("Invalid port, try again")
        main()
        return
    client = MongoClient('localhost', int(Port))

    db = client["291db"]
    menu(db)

def menu(db):
    # menu options
    Option = input("Do you wish to search for a title, search for genres, search for cast/crew members, add a movie, add a cast/crew member, or exit? (SM,SG,SC,AM,AC,E): ")
    if Option.lower() == "sm":
        search_movies(db)
        return
    elif Option.lower() == "sg":
        search_genres(db)
        return
    elif Option.lower() == "sc":
        search_cast(db)
        return
    elif Option.lower() == "am":
        add_movie(db)
        return
    elif Option.lower() == "ac":
        add_cast(db)
        return
    elif Option.lower() == "e":
        exit()
    else:
        print("Invalid option")
        menu(db)
        return

def search_movies(db):
    movies_collection = db["title_basics"]
    Keywords = input("Enter keywords for a search: ").split()
    if len(Keywords) == 0:
        print("No keywords, please try again!")
        search_movies(db)
        return
    
    Query = []
    YearQuery = []
    # Found a keyword
    for i in Keywords:
        # numbers could be the year
        if i.isnumeric():
            YearQuery.append({"$or":[{"startYear": int(i)},{"primaryTitle": {"$regex": i,"$options": "i"}}]})
        else:
            # if not a number, just search for it
            Query.append({"primaryTitle": {"$regex": i,"$options": "i"}})
    
    FullQuery = []
    # There are normal word queries
    if len(Query) > 0:
        FullQuery.append({"$and": Query})
    # There are year queries
    if len(YearQuery) > 0:
        FullQuery.append({"$and": YearQuery})
    Movies = list(movies_collection.find({"$and": FullQuery},{"_id": 0}))
    # Print out all the movies
    for i in range(len(Movies)):
        print("#" + str(i) + ". Type: " + Movies[i]["titleType"] + " Title: "+ Movies[i]["primaryTitle"] + " Original Title: " + Movies[i]["originalTitle"] + " Adult?: " + (Movies[i]["isAdult"] == 1 and "Yes" or "No") + " Start Year: " + str(Movies[i]["startYear"]) + " End Year: " + str(Movies[i]["endYear"]) + " Runtime: " + str(Movies[i]["runtimeMinutes"]) + " Genres: " + ", ".join(Movies[i]["genres"]))
        print()
    if len(Movies) == 0:
        print("No results found!")
    Choice = input("Select a title # to see more info, or 'E' to return to the menu: ")
    if Choice.lower() == "e":
        menu(db)
        return
    elif Choice.isnumeric() and int(Choice) < len(Movies):
        Key = Movies[int(Choice)]["tconst"]
        Movie = list(db["title_ratings"].find({"tconst": Key}))
        if len(Movie) != 0:
            Movie = Movie[0]
            print("Rating: " + str(Movie["averageRating"]) + " Vote Count: " + str(Movie["numVotes"]))

            Cast = list(db["title_principals"].find({"tconst": Key}))
            # Print characters
            for i in Cast:
                CastKey = i["nconst"]
                Member = list(db["name_basics"].find({"nconst": CastKey}))[0]
                print(Member["primaryName"] + ", Characters: " + ", ".join(i["characters"]))
        else:
            print("Movie does not have any rating Data!")
            

        menu(db)
        return
    else:
        print("Invalid choice, returning to menu.")
        menu(db)
        return

def search_genres(db):
    # User inputs
    Genre = input("Enter a genre: ")
    MinVote = input("Enter a minimum vote count: ")
    if (not MinVote.isnumeric()):
        print("Invalid vote count, please try again!")
        search_genres(db)
        return
    Titles = db["title_basics"].aggregate([{"$lookup": {"from": "title_ratings", "localField": "tconst", "foreignField": "tconst", "as" : "ratings"}},{"$unwind":{"path": "$ratings"}},{"$match": {"genres" : {"$regex": Genre,"$options": "i"},"ratings.numVotes": { "$gt": int(MinVote) }}},{"$addFields": {"Rating": "$ratings.averageRating", "NumVotes": "$ratings.numVotes"}},{ "$sort" : {"ratings.averageRating": -1}}])
    # Prints all the titles and info
    for i in Titles:
        print(i["primaryTitle"] + " Number of Votes: " + str(i["NumVotes"]) + " Rating: " + str(i["Rating"]))
        print()
    if len(list(Titles)) == 0:
        print("No results found!")
    menu(db)
    return

def search_cast(db):
    Name = input("Enter a name: ")
    
    # find all the poeple that match the inputted name
    CastList = list(db["name_basics"].find({"primaryName":{"$regex": Name,"$options": "i"}}))
    if len(CastList) == 0:
        # if no result is found
        print("No one found, returning to menu.")
        menu(db)
        return

    for Cast in CastList:
        # get all the info for each result
        print("Name: "+ Cast["primaryName"])
        print("Professions:")
        for i in Cast["primaryProfession"]:
            if i.strip() != "":
                print(i)
        print("Movies:")
        # find a list of movies where the cast/crew member either had a job, or a character in a movie
        Movies = list(db["title_principals"].find({"$and": [{"nconst": Cast["nconst"]}, {
                        "$or": [{"job": {"$ne": "\\N"}}, {"characters": {"$nin": ["\\N"]}}]}]}))

        if Movies:
            # print movies and roles for each movie
            for movie in Movies:
                name = list(db["title_basics"].find(
                    {"tconst": movie["tconst"]}))[0]["primaryTitle"]
                job = list(movie["job"])[0]
                if job == "\\":
                    job = "None"
                characters = list(movie["characters"])
                for character in characters:
                    print("Movie:", name, "Job:", job,
                            "Character:", character)
        print()

    
    menu(db)
    return

def add_movie(db):
    # add a movie based on a unique id
    Id = input("Enter a unique ID: ")
    Title = input("Enter a title: ")
    Year = input("Enter a start year: ")
    Time = input("Enter a running time: ")
    Genres = input("Enter a list of genres: ").split()

    if (not Year.isnumeric()):
        print("Invalid year, please try again!")
        add_movie(db)
        return
    
    if (not Time.isnumeric()):
        print("Invalid time, please try again!")
        add_movie(db)
        return

    if (db["title_basics"].count_documents({"tconst": Id}) != 0):
        # check if entered id is unique
        print("ID is not unique, please try again!")
        add_movie(db)
        return

    # insert entered data into the db
    db["title_basics"].insert_one({"tconst": Id,"titleType": "movie", "primaryTitle": Title,"originalTitle": Title,"isAdult": "\\N","startYear": Year,"endYear": "\\N","runtimeMinutes": Time, "genres": Genres})

    print("Insertion complete!")
    menu(db)
    return

def add_cast(db):
    # ask user for input
    CId = input("Enter a crew ID: ")
    TId = input("Enter a title ID: ")
    Category = input("Enter a category: ")
    if (db["title_basics"].count_documents({"tconst": TId}) == 0):
        # check if title exists
        print("Title does not exist, returning to menu.")
        menu(db)
        return
    if (db["name_basics"].count_documents({"nconst": CId}) == 0):
        # check if user exists
        print("User does not exist, returning to menu.")
        menu(db)
        return

    # setting the ordering and inserting into the db
    Ordering = 1
    Titles = list(db["title_principals"].find({"tconst": TId}).sort("ordering", -1))
    if (len(Titles) > 0):
        Ordering = int(Titles[0]["ordering"]) + 1
    db["title_principals"].insert_one({"tconst": TId,"ordering": Ordering, "nconst": CId,"category": Category,"job": "\\N","characters": ["\\N"]})
    
    print("Insertion complete!")
    menu(db)
    return



main()