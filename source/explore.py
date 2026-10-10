import json

#신문 어휘 의미 분석 말뭉치(corpus)
NXLS25 = "../data/NIKL_LS_2025_v1.0/NXLS2502512313.json"

with open(NXLS25, encoding="utf-8") as f:
    data = json.load(f)

    #들여쓰기:2 / 3000글자만 출력
    #print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    print("=====")

    docs = data["document"]
    for doc in docs:
        print(doc["paragraph"])

    '''
    for k,v in data.items():
        print(k,json.dumps(v,ensure_ascii=False)[:100])
    #print(f"{json.dumps(data.get(key1)[1],ensure_ascii=False,indent=2)[:200]}")
    '''