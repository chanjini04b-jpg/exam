import json

# 기존 완성본 로드 (수동 추가된 165개)
with open('quiz_data_final_complete.json', 'r', encoding='utf-8') as f:
    complete_data = json.load(f)

# 새로 파싱한 데이터 로드 (156개, 선택지 형식 개선됨)
with open('quiz_data_fixed.json', 'r', encoding='utf-8') as f:
    fixed_data = json.load(f)

# 병합: 새 파싱 데이터를 기본으로 하고, 누락된 문제는 기존 데이터에서 가져옴
final_data = {}

for round_key in complete_data.keys():
    round_num = round_key.replace('quiz', '')
    
    # 새 데이터 사용
    if round_key in fixed_data:
        final_data[round_key] = fixed_data[round_key]
        
        # 15개가 안되면 누락된 것을 기존 데이터에서 채움
        if len(fixed_data[round_key]) < 15:
            complete_questions = complete_data[round_key]
            fixed_questions = fixed_data[round_key]
            
            # 15개까지 채우기 (순서대로)
            for i in range(15):
                if i >= len(fixed_questions):
                    # 누락된 인덱스의 문제를 기존 데이터에서 가져옴
                    final_data[round_key].append(complete_questions[i])
    else:
        # 새 데이터에 없으면 기존 데이터 사용
        final_data[round_key] = complete_data[round_key]

# 저장
with open('quiz_data_merged.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

# JavaScript 변환
output = []
output.append("// 전산세무2급 기출문제 전체 데이터 (112-122회, 총 165문제)\n")
output.append("// 최종 완성본\n\n")

# 각 회차별 데이터
for round_num in range(112, 123):
    key = f'quiz{round_num}'
    if key in final_data:
        output.append(f"const quiz{round_num}Data = {json.dumps(final_data[key], ensure_ascii=False, indent=2)};\n\n")

# roundData 객체
output.append("// 회차별 데이터 매핑\n")
output.append("const roundData = {\n")
for i, round_num in enumerate(range(112, 123)):
    comma = "," if i < 10 else ""
    output.append(f"  {round_num}: quiz{round_num}Data{comma}\n")
output.append("};\n")

# 저장
with open('quiz_all_data.js', 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print("✅ 데이터 병합 및 JavaScript 변환 완료!")
print("=" * 60)
for key in sorted(final_data.keys(), key=lambda x: int(x.replace('quiz', ''))):
    count = len(final_data[key])
    if count == 15:
        print(f"  ✅ {key}: {count}개")
    else:
        print(f"  ⚠️ {key}: {count}개 (문제 발생!)")

total = sum(len(final_data[k]) for k in final_data)
print("=" * 60)
print(f"총 문제 수: {total}/165개")
