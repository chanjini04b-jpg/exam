import json

def convert_to_javascript(json_file, output_file):
    """JSON을 JavaScript 형식으로 변환"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    js_content = "// 전산세무2급 기출문제 데이터 (자동 생성)\n\n"
    
    for round_key in sorted(data.keys(), key=lambda x: int(x.replace('quiz', ''))):
        round_num = round_key.replace('quiz', '')
        questions = data[round_key]
        
        js_content += f"// {round_num}회 ({len(questions)}문제)\n"
        js_content += f"const quiz{round_num}Data = "
        js_content += json.dumps(questions, ensure_ascii=False, indent=2)
        js_content += ";\n\n"
    
    # roundData 객체 생성
    js_content += "// 회차별 데이터 매핑\n"
    js_content += "const roundData = {\n"
    
    for round_key in sorted(data.keys(), key=lambda x: int(x.replace('quiz', ''))):
        round_num = round_key.replace('quiz', '')
        js_content += f"  {round_num}: quiz{round_num}Data,\n"
    
    js_content += "};\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ JavaScript 변환 완료: {output_file}")
    print(f"   총 {len(data)}개 회차, {sum(len(q) for q in data.values())}개 문제")

if __name__ == '__main__':
    convert_to_javascript('quiz_data_final.json', 'quiz_all_data.js')
