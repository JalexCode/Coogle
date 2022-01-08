with open("cuba_provinces_and_municipalities.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    dict = {}
    for line in lines:
        if "//" in line:
            continue
        if line != "":
            province_municip = line.split(":")
            print(province_municip)
            province = province_municip[0]
            municip = province_municip[1].split(", ")
            dict[province] = [m.strip() for m in municip]
    import json
    with open("cuba_provinces_and_municipalities.json", "w", encoding="utf-8") as json_file:
        json.dump(dict, json_file, ensure_ascii=False)