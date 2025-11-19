import os
import re
import json

def clean_text(text):
    """텍스트 정리"""
    return text.strip()

def parse_options(text_block):
    """
    선택지 파싱 - 두 가지 패턴 모두 지원
    패턴1: ① ② ③ ④가 먼저, 그 다음 4개 내용
    패턴2: ① 내용1 ② 내용2 ③ 내용3 ④ 내용4
    """
    options = ['', '', '', '']
    
    # 패턴2: ① 내용 ② 내용 형식 먼저 체크 (더 명확함)
    pattern2 = r'①\s*\n([^\n②]+)\n②\s*\n([^\n③]+)\n③\s*\n([^\n④]+)\n④\s*\n([^\n\[]+)'
    match2 = re.search(pattern2, text_block, re.DOTALL)
    
    if match2:
        options = [
            clean_text(match2.group(1)),
            clean_text(match2.group(2)),
            clean_text(match2.group(3)),
            clean_text(match2.group(4))
        ]
        return options
    
    # 패턴1: ① ② ③ ④가 먼저 나오고 그 다음에 내용들
    # ①②③④를 찾고 그 다음 [답]까지의 내용을 4개로 분할
    marker_pattern = r'①\s*\n②\s*\n③\s*\n④\s*\n(.*?)(?=\[답\])'
    marker_match = re.search(marker_pattern, text_block, re.DOTALL)
    
    if not marker_match:
        # 마커가 한 줄에 있는 경우
        marker_pattern = r'①\s*②\s*③\s*④\s*\n(.*?)(?=\[답\])'
        marker_match = re.search(marker_pattern, text_block, re.DOTALL)
    
    if marker_match:
        content = marker_match.group(1).strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 4개 내용으로 나누기 - 빈 줄이나 명확한 구분이 없으면 균등 분할
        if len(lines) == 4:
            options = lines
        elif len(lines) > 4:
            # 4개보다 많으면 그룹핑 시도
            # 보통 첫 4개가 선택지
            options = lines[:4]
        elif len(lines) < 4:
            # 4개보다 적으면 남은 것을 빈 문자열로
            options = lines + [''] * (4 - len(lines))
        
        return options
    
    return options

def parse_table_in_question(question_text):
    """문제 텍스트에서 표 형식 데이터를 HTML 테이블로 변환"""
    # 표 형식 패턴 찾기 (구분, 제조부문 등이 있는 경우)
    if '구분' not in question_text and 'ㆍ' not in question_text:
        return question_text
    
    # ㆍ로 시작하는 리스트 항목들을 테이블로 변환
    lines = question_text.split('\n')
    table_lines = []
    non_table_lines = []
    in_table = False
    
    for line in lines:
        if line.strip().startswith('ㆍ') or '구분' in line or '제조부문' in line:
            table_lines.append(line.strip())
            in_table = True
        else:
            if in_table and table_lines:
                # 테이블 끝
                in_table = False
            if not in_table:
                non_table_lines.append(line)
    
    if table_lines:
        # 간단한 리스트 형태로 변환
        table_html = '<div style="margin:10px 0; padding:10px; background:#f9f9f9; border-left:3px solid #4a90e2;">'
        for line in table_lines:
            table_html += f'<div>{line}</div>'
        table_html += '</div>'
        
        # 원본에서 표 부분을 HTML로 교체
        for line in table_lines:
            question_text = question_text.replace(line, '', 1)
        question_text = question_text.replace('\n\n\n', '\n\n')
        question_text += '\n' + table_html
    
    return question_text

def parse_quiz_file_v3(file_path):
    """최종 개선 버전 파서"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    round_number = os.path.basename(file_path).replace('.txt', '').replace('회', '')
    
    # 각 문제를 [답] 패턴으로 구분
    # 문제는 "숫자. " 로 시작
    problem_pattern = r'(\d+)\.\s+(.*?)(?=\n\d+\.\s+|\Z)'
    problems = re.findall(problem_pattern, content, re.DOTALL)
    
    questions = []
    
    for q_num, q_content in problems:
        if q_num == round_number:  # 회차 번호는 스킵
            continue
        
        # [답] 부분 찾기
        answer_pattern = r'\[답\]\s*([①②③④])(.*?)$'
        answer_match = re.search(answer_pattern, q_content, re.DOTALL)
        
        if not answer_match:
            print(f"  ⚠️ {round_number}회 {q_num}번 - 정답을 찾을 수 없음")
            continue
        
        answer_symbol = answer_match.group(1)
        explanation = clean_text(answer_match.group(2))
        
        # 정답 인덱스
        answer_map = {'①': 0, '②': 1, '③': 2, '④': 3}
        correct_index = answer_map.get(answer_symbol, 0)
        
        # 문제 텍스트 (선택지 전까지)
        question_part = q_content[:q_content.find('①')]
        question_text = clean_text(question_part)
        
        # 표 형식 데이터 처리
        question_text = parse_table_in_question(question_text)
        
        # 선택지 파싱
        options = parse_options(q_content)
        
        # 선택지가 모두 비어있으면 스킵
        if all(not opt for opt in options):
            print(f"  ⚠️ {round_number}회 {q_num}번 - 선택지를 파싱할 수 없음")
            continue
        
        questions.append({
            'question': question_text,
            'options': options,
            'correct': correct_index,
            'explanation': explanation
        })
        
        if len(questions) % 5 == 0:
            print(f"  진행중... {len(questions)}개 완료")
    
    return {
        'round': round_number,
        'questions': questions
    }

def main():
    cbt_folder = 'D:\\exam\\cbt'
    all_data = {}
    
    print("📚 전산세무2급 문제 파싱 시작 (최종 개선 버전)\n")
    print("=" * 60)
    
    for filename in sorted(os.listdir(cbt_folder)):
        if filename.endswith('.txt'):
            file_path = os.path.join(cbt_folder, filename)
            print(f"\n처리중: {filename}")
            
            result = parse_quiz_file_v3(file_path)
            round_num = result['round']
            questions = result['questions']
            
            all_data[f'quiz{round_num}'] = questions
            
            status = "✅" if len(questions) == 15 else f"⚠️ ({len(questions)}/15)"
            print(f"{status} {round_num}회 처리 완료: {len(questions)}개 문제")
    
    # JSON 파일로 저장
    output_file = 'quiz_data_final.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"\n✅ 파싱 완료! 결과 저장: {output_file}")
    
    # 통계 출력
    print("\n📊 파싱 결과 통계:")
    print("-" * 60)
    total_questions = 0
    perfect_rounds = 0
    
    for round_key in sorted(all_data.keys(), key=lambda x: int(x.replace('quiz', ''))):
        questions = all_data[round_key]
        count = len(questions)
        total_questions += count
        
        if count == 15:
            perfect_rounds += 1
            status = "✅"
        else:
            status = "⚠️"
        
        print(f"  {status} {round_key}: {count}개 문제")
    
    print("-" * 60)
    print(f"\n📈 총 통계:")
    print(f"  • 완벽한 회차: {perfect_rounds}/11")
    print(f"  • 총 문제 수: {total_questions}개")
    print(f"  • 평균 문제 수: {total_questions/11:.1f}개/회차")

if __name__ == '__main__':
    main()
