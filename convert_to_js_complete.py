import json

# JSON 파일 로드
with open('quiz_data_final_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# JavaScript 파일 생성
output = []
output.append("// 전산세무2급 기출문제 전체 데이터 (112-122회, 총 165문제)\n")
output.append("// 자동 생성됨 - 수정하지 마세요\n\n")

# 각 회차별 데이터 변환
for round_num in range(112, 123):
    key = f'quiz{round_num}'
    if key in data:
        output.append(f"const quiz{round_num}Data = {json.dumps(data[key], ensure_ascii=False, indent=2)};\n\n")

# roundData 객체 생성
output.append("// 회차별 데이터 매핑\n")
output.append("const roundData = {\n")
for i, round_num in enumerate(range(112, 123)):
    comma = "," if i < 10 else ""
    output.append(f"  {round_num}: quiz{round_num}Data{comma}\n")
output.append("};\n")

# 파일 저장
with open('quiz_all_data.js', 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print("✅ JavaScript 변환 완료!")
print("=" * 60)
print(f"파일: quiz_all_data.js")
print(f"총 회차: 11개 (112-122회)")
print(f"총 문제: 165개")
print("=" * 60)
