import os
import re
import json

def parse_question_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 회차 번호 추출
    match = re.search(r'(\d+)회', content)
    if not match:
        return None, []
    round_num = match.group(1)
    
    # 문제들을 분리 (1. 2. 3. ... 으로 시작하는 부분)
    questions = []
    
    # [답] 기준으로 문제 분리
    parts = content.split('[답]')
    
    for i in range(1, min(16, len(parts))):  # 최대 15문제
        try:
            # 이전 부분의 마지막 문제와 현재 답 부분
            if i < len(parts):
                # 문제 부분 추출
                problem_part = parts[i-1]
                answer_part = '[답]' + parts[i]
                
                # 문제 번호로 시작하는 부분 찾기
                question_match = re.search(r'(\d+)\.\s+(.+?)(?=①|$)', problem_part, re.DOTALL)
                if not question_match:
                    continue
                
                question_text = question_match.group(2).strip()
                
                # 선택지 추출
                options = []
                for opt_num in ['①', '②', '③', '④']:
                    opt_match = re.search(rf'{opt_num}\s*([^①②③④\[]+)', problem_part)
                    if opt_match:
                        options.append(opt_match.group(1).strip())
                
                if len(options) != 4:
                    continue
                
                # 정답 추출
                answer_match = re.search(r'\[답\]\s*([①②③④])', answer_part)
                if not answer_match:
                    continue
                
                answer_map = {'①': 0, '②': 1, '③': 2, '④': 3}
                correct_idx = answer_map.get(answer_match.group(1), -1)
                
                if correct_idx == -1:
                    continue
                
                # 해설 추출
                explanation_match = re.search(r'\[답\]\s*[①②③④]\s*(.+?)(?=\n\n|\d+\.\s|$)', answer_part, re.DOTALL)
                explanation = ''
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                    # 여러 줄 정리
                    explanation = ' '.join(explanation.split())
                
                questions.append({
                    'question': question_text,
                    'options': options,
                    'correct': correct_idx,
                    'explanation': explanation
                })
                
        except Exception as e:
            print(f'  문제 {i} 파싱 오류: {e}')
            continue
    
    return round_num, questions

# 114~122회 파싱
all_data = {}
for i in range(114, 123):
    filepath = f'D:/exam/cbt/{i}회.txt'
    if os.path.exists(filepath):
        try:
            round_num, questions = parse_question_file(filepath)
            if round_num and len(questions) > 0:
                all_data[round_num] = questions
                print(f'{i}회 처리 완료: {len(questions)}개 문제')
            else:
                print(f'{i}회 처리 실패: 문제를 찾을 수 없음')
        except Exception as e:
            print(f'{i}회 처리 실패: {e}')

# JSON으로 저장
with open('D:/exam/quiz_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print('\n완료! quiz_data.json 파일이 생성되었습니다.')
print(f'총 {len(all_data)}개 회차 처리됨')
