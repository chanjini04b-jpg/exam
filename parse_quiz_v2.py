import os
import re
import json

def parse_table(text):
    """표 형태의 텍스트를 HTML 테이블로 변환"""
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return text
    
    # 표 형태인지 확인 (여러 줄이 있고, 일정한 패턴이 있는지)
    has_table_pattern = any('구분' in line or '제조부문' in line or '보조부문' in line for line in lines[:3])
    
    if not has_table_pattern:
        return text
    
    # 간단한 HTML 테이블 생성
    table_html = '<table border="1" style="border-collapse:collapse;margin:10px 0;">\n'
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        # 탭이나 여러 공백으로 구분된 셀들
        cells = re.split(r'\t+|\s{2,}', line.strip())
        cells = [c for c in cells if c]  # 빈 셀 제거
        
        if i == 0:
            # 헤더 행
            table_html += '  <tr>'
            for cell in cells:
                table_html += f'<th style="padding:5px;background:#f0f0f0;">{cell}</th>'
            table_html += '</tr>\n'
        else:
            # 데이터 행
            table_html += '  <tr>'
            for cell in cells:
                table_html += f'<td style="padding:5px;">{cell}</td>'
            table_html += '</tr>\n'
    
    table_html += '</table>'
    return table_html

def parse_quiz_file(file_path):
    """개선된 퀴즈 파일 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    round_number = os.path.basename(file_path).replace('.txt', '').replace('회', '')
    
    # [답] 기준으로 문제 분리
    questions_raw = re.split(r'\n(?=\d+\.\s)', content)
    questions = []
    
    for q_block in questions_raw:
        if not q_block.strip() or q_block.strip() == round_number + '회':
            continue
        
        # 문제 번호와 제목 추출
        question_match = re.match(r'(\d+)\.\s+(.*?)(?=\n①|\n\n①)', q_block, re.DOTALL)
        if not question_match:
            continue
        
        q_num = question_match.group(1)
        question_text = question_match.group(2).strip()
        
        # 선택지 번호와 내용 분리
        # ① ② ③ ④가 먼저 나오고, 그 다음에 내용이 나옴
        options_pattern = r'①\s*\n②\s*\n③\s*\n④\s*\n(.*?)(?=\n\n\[답\]|\[답\])'
        options_match = re.search(options_pattern, q_block, re.DOTALL)
        
        if not options_match:
            # 다른 패턴 시도: ① ② ③ ④가 한 줄에 있을 수도
            options_pattern2 = r'①\s*②\s*③\s*④\s*\n(.*?)(?=\n\n\[답\]|\[답\])'
            options_match = re.search(options_pattern2, q_block, re.DOTALL)
        
        if not options_match:
            print(f"  ⚠️ {round_number}회 {q_num}번 - 선택지 패턴을 찾을 수 없음")
            continue
        
        # 선택지 내용 추출
        options_text = options_match.group(1).strip()
        options_lines = options_text.split('\n')
        options = []
        
        # 선택지는 보통 4개씩 그룹으로 나뉨
        # 각 선택지가 여러 줄일 수 있으므로 빈 줄이나 다음 문제 시작까지를 하나의 선택지로
        current_option = []
        for line in options_lines:
            line = line.strip()
            if not line:
                if current_option:
                    options.append(' '.join(current_option))
                    current_option = []
            else:
                current_option.append(line)
        
        if current_option:
            options.append(' '.join(current_option))
        
        # 선택지가 4개가 아니면 조정
        if len(options) > 4:
            # 너무 많으면 처음 4개만
            options = options[:4]
        elif len(options) < 4:
            # 부족하면 빈 문자열로 채움
            while len(options) < 4:
                options.append('')
        
        # 정답 추출
        answer_match = re.search(r'\[답\]\s*([①②③④])', q_block)
        if not answer_match:
            print(f"  ⚠️ {round_number}회 {q_num}번 - 정답을 찾을 수 없음")
            continue
        
        answer_symbol = answer_match.group(1)
        answer_map = {'①': 0, '②': 1, '③': 2, '④': 3}
        correct_index = answer_map.get(answer_symbol, 0)
        
        # 해설 추출
        explanation_match = re.search(r'\[답\]\s*[①②③④]\s*(.*?)(?=\n\n\d+\.|$)', q_block, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ''
        
        # 문제 텍스트에서 표 형태 데이터 처리
        if '구분' in question_text or 'ㆍ' in question_text:
            # 표 형태가 있을 가능성
            table_pattern = r'(구분.*?)(?=\n①|\n\n①|$)'
            table_match = re.search(table_pattern, question_text, re.DOTALL)
            if table_match:
                table_text = table_match.group(1)
                table_html = parse_table(table_text)
                question_text = question_text.replace(table_text, '\n' + table_html)
        
        questions.append({
            'question': question_text,
            'options': options,
            'correct': correct_index,
            'explanation': explanation
        })
    
    return {
        'round': round_number,
        'questions': questions
    }

def main():
    cbt_folder = 'D:\\exam\\cbt'
    all_data = {}
    
    print("📚 전산세무2급 문제 파싱 시작 (개선된 버전)\n")
    
    for filename in sorted(os.listdir(cbt_folder)):
        if filename.endswith('.txt'):
            file_path = os.path.join(cbt_folder, filename)
            print(f"처리중: {filename}")
            
            result = parse_quiz_file(file_path)
            round_num = result['round']
            questions = result['questions']
            
            all_data[f'quiz{round_num}'] = questions
            print(f"  ✅ {round_num}회 처리 완료: {len(questions)}개 문제\n")
    
    # JSON 파일로 저장
    output_file = 'quiz_data_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 파싱 완료! 결과 저장: {output_file}")
    
    # 통계 출력
    print("\n📊 파싱 결과 통계:")
    total_questions = 0
    for round_key, questions in sorted(all_data.items()):
        count = len(questions)
        total_questions += count
        status = "✅" if count == 15 else "⚠️"
        print(f"  {status} {round_key}: {count}개 문제")
    
    print(f"\n총 {total_questions}개 문제 파싱 완료!")

if __name__ == '__main__':
    main()
