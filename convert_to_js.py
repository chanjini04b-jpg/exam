import json

# JSON 파일 읽기
with open('D:/exam/quiz_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# JavaScript 코드 생성
js_code = ""

for round_num in range(115, 123):  # 115-122회
    if str(round_num) in data:
        questions = data[str(round_num)]
        js_code += f"\n// {round_num}회 문제\nconst quiz{round_num}Data = [\n"
        
        for q in questions:
            # 질문과 옵션 문자열 정리
            question = q['question'].replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
            options = []
            for opt in q['options']:
                if opt:  # 빈 옵션 건너뛰기
                    clean_opt = opt.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').strip()
                    # 너무 긴 옵션 줄이기
                    if len(clean_opt) > 300:
                        clean_opt = clean_opt[:300] + '...'
                    options.append(clean_opt)
            
            # 옵션이 4개 미만이면 빈 문자열로 채우기
            while len(options) < 4:
                options.append("")
            
            explanation = q['explanation'].replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ').strip()
            
            js_code += "    {\n"
            js_code += f"        question: '{question}',\n"
            js_code += "        options: [\n"
            for opt in options:
                js_code += f"            '{opt}',\n"
            js_code += "        ],\n"
            js_code += f"        correct: {q['correct']},\n"
            js_code += f"        explanation: '{explanation}'\n"
            js_code += "    },\n"
        
        js_code += "];\n"

# 파일에 저장
with open('D:/exam/quiz_data_js.txt', 'w', encoding='utf-8') as f:
    f.write(js_code)

print("JavaScript 코드 생성 완료!")
