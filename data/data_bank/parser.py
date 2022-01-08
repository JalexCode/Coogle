from bs4 import BeautifulSoup

with open("Condiciones meteorológicas - OpenWeatherMap.html", "r", encoding="utf-8") as raw_html:
    main_soup = BeautifulSoup(raw_html.read(), "html.parser")
    tables = main_soup.find_all("table", {"class": "table table-bordered"})
    _json = {"ID":[], "Main":[], "Description":[], "Icon":[]}
    n = 0
    a = False
    for table in tables:
        if not a:
            a = True
            continue
        # table_name = table.find("caption")
        # if table_name:
        #     table_name = table_name.text.strip()
        # else:
        #     table_name = "Tabla %d"%n
        #     n += 1
        # print(table_name)
        # # annado al _json
        # _json[table_name] = {}
        # column_name = table.find_all("th")
        # print(f"Agregando {len(column_name)} columnas")
        # for c in column_name:
        #     print(c.text)
        #     _json[table_name][c.text.strip()] = []
        data = table.find_all("td")
        print(f"Agregando {len(data)} filas\n======================")
        column_name = ["ID", "Main", "Description", "Icon"]
        i = 0
        for d in data:
            column = column_name[i]
            value = d.text.strip()
            _json[column].append(value)
            if i == len(column_name) - 1:
                i = 0
            else:
                i += 1
        # i = 0
        # for d in data:
        #     column = column_name[i].text.strip()
        #     value = d.text.strip()
        #     _json[table_name][column].append(value)
        #     if i == len(column_name)-1:
        #         i = 0
        #     else:
        #         i += 1
    import json
    with open("open_weather.json", "w", encoding="utf-8") as json_file:
        json.dump(_json, json_file, ensure_ascii=False)