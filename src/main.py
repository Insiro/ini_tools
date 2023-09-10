import json
from GiIni import GiLoader


file = "./temp/test.ini"
ini = GiLoader().load_ini(file)


ini.save("temp/tt.ini")


json.dump(ini.__dict__(), open("temp/tem.json", "w"), indent=2)
# print(jd)

# print(ini.sections["KeySwap"].get_value("condition"))
