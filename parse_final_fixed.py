import os
import re
import json

def parse_options_pattern1(text):
    """패턴1: ① ② ③ ④가 먼저 나오고, 아래에 4개 텍스트"""
    # ①②③④ 다음에 오는 4줄의 텍스트 추출
    pattern = r'①\s*\n②\s*\n③\s*\n④\s*\n(.*?)(?=\[답\])'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        content = match.group(1).strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) >= 4:
            return lines[:4]
    
    return None

def parse_options_pattern2(text):
    """패턴2: ① 텍스트1 ② 텍스트2 ③ 텍스트3 ④ 텍스트4 (한 줄 또는 여러 줄)"""
    pattern = r'①\s*([^②]+)②\s*([^③]+)③\s*([^④]+)④\s*([^\[]+)'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return [
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip(),
            match.group(4).strip()
        ]
    
    return None

def parse_options_pattern3(text):
    """패턴3: ① ③ / ② ④ 형식 (2x2 그리드)"""
    # 이 패턴은 특수한 경우이므로 수동으로 처리됨
    return None

def parse_quiz_file(file_path):
    """최종 완성 파서"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    round_number = os.path.basename(file_path).replace('.txt', '').replace('회', '')
    
    # 각 문제를 분리 (문제번호. 로 시작)
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
        explanation = answer_match.group(2).strip()
        
        # 정답 인덱스
        answer_map = {'①': 0, '②': 1, '③': 2, '④': 3}
        correct_index = answer_map.get(answer_symbol, 0)
        
        # 문제 텍스트 (선택지 전까지)
        question_part = q_content[:q_content.find('①')]
        question_text = question_part.strip()
        
        # 선택지 파싱 - 여러 패턴 시도
        options = None
        
        # 패턴1 시도: ①②③④ 먼저, 그 아래 4줄
        options = parse_options_pattern1(q_content)
        
        # 패턴2 시도: ① 텍스트1 ② 텍스트2 형식
        if not options:
            options = parse_options_pattern2(q_content)
        
        # 선택지가 없으면 스킵
        if not options or all(not opt for opt in options):
            print(f"  ⚠️ {round_number}회 {q_num}번 - 선택지를 파싱할 수 없음")
            continue
        
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
    
    print("📚 전산세무2급 문제 파싱 (최종 수정 버전)\n")
    print("=" * 60)
    
    for filename in sorted(os.listdir(cbt_folder)):
        if filename.endswith('.txt'):
            file_path = os.path.join(cbt_folder, filename)
            print(f"\n📖 {filename}")
            
            result = parse_quiz_file(file_path)
            round_num = result['round']
            questions = result['questions']
            
            all_data[f'quiz{round_num}'] = questions
            
            if len(questions) == 15:
                print(f"   ✅ 완벽! {len(questions)}개 문제")
            else:
                print(f"   ⚠️ {len(questions)}/15개 문제")
                # 누락된 문제 번호 출력
                parsed_nums = set()
                for q in questions:
                    # 문제 텍스트에서 번호 추출은 어려우므로 순서로 판단
                    pass
    
    # JSON 파일로 저장
    output_file = 'quiz_data_fixed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"\n✅ 파싱 완료: {output_file}")
    
    # 통계
    print("\n📊 최종 통계:")
    print("-" * 60)
    total = 0
    perfect = 0
    
    for key in sorted(all_data.keys(), key=lambda x: int(x.replace('quiz', ''))):
        count = len(all_data[key])
        total += count
        if count == 15:
            perfect += 1
            print(f"  ✅ {key}: {count}개")
        else:
            print(f"  ⚠️ {key}: {count}개")
    
    print("-" * 60)
    print(f"  완벽한 회차: {perfect}/11")
    print(f"  총 문제: {total}/165개 ({total/165*100:.1f}%)")

if __name__ == '__main__':
    main()
