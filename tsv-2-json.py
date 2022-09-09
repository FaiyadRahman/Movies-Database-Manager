import json
import re

def tsv2json(input_file, output_file):
    arr = []
    try:
        with open(input_file, "r", encoding="utf8") as file:
            a = file.readline()

            titles = [t.strip() for t in a.split("\t")]
            for line in file:
                d = {}
                for t, f in zip(titles, line.split("\t")):
                    # aggregrate the info into tuples
                    if t not in ["primaryProfession", "knownForTitles", "genres", "characters","averageRating"]:

                        if f.strip().isnumeric() and t not in ["primaryTitle","originalTitle"]:
                            d[t] = int(f.strip())
                        else:
                            d[t] = f.strip()
                    elif t == "characters":
                        f = f.strip()
                        # split list of characters at every "," that has a ' " ' before and after it
                        array = re.split(r'[?<="],[?="]', f)
                        array[0] = array[0].strip('["')
                        array[-1] = array[-1].strip('"]')
                        d[t] = array
                    elif t == "averageRating":
                        d[t] = float(f.strip())
                    else:
                        array = f.strip().split(",")
                        array[0] = array[0].strip('["')
                        array[-1] = array[-1].strip('"]')
                        d[t] = array

                arr.append(d)

            # write the arr to a json file
            with open(output_file, 'w') as output_file:
                output_file.write(json.dumps(arr, indent=4))
    except Exception as e:
        print("Error converting file")


def main():
    # driver code
    filenames = ["name.basics", "title.basics",
                 "title.principals", "title.ratings"]
    for name in filenames:
        print("Converting", name)
        tsv2json(name + ".tsv", name + ".json")
    print("Done")

main()