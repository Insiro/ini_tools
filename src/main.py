import json
from GiIni import GiLoader


file = "./merged.ini"
ini = GiLoader().load_ini(file)


ini.save("tt.ini")

# jd = json.dumps(ini.__dict__(), indent=2)
# json.dump(ini.__dict__(), open("tem.json", "w"), indent=2)
# print(jd)

# print(ini.sections["KeySwap"].get_value("condition"))
