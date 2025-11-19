import os
import re
import json

def parse_single_line_options(text):
    """한 줄로 된 선택지 파싱: ① 내용1 ② 내용2 ③ 내용3 ④ 내용4"""
    pattern = r'①\s*([^②]+)②\s*([^③]+)③\s*([^④]+)④\s*([^\[]+)'
    match = re.search(pattern, text)
    if match:
        return [
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip(),
            match.group(4).strip()
        ]
    return None

def parse_multi_line_options(text):
    """여러 줄로 된 선택지 파싱"""
    # ① ② ③ ④가 먼저 나오고 그 다음에 내용
    marker_pattern = r'①\s*\n②\s*\n③\s*\n④\s*\n(.*?)(?=\[답\])'
    match = re.search(marker_pattern, text, re.DOTALL)
    
    if match:
        content = match.group(1).strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) >= 4:
            return lines[:4]
        else:
            # 4개보다 적으면 남은 것을 빈 문자열로
            return lines + [''] * (4 - len(lines))
    
    # ① 내용 ② 내용 형식
    pattern2 = r'①\s*\n([^②]+)②\s*\n([^③]+)③\s*\n([^④]+)④\s*\n([^\[]+)'
    match2 = re.search(pattern2, text, re.DOTALL)
    if match2:
        return [
            match2.group(1).strip(),
            match2.group(2).strip(),
            match2.group(3).strip(),
            match2.group(4).strip()
        ]
    
    return None

def parse_quiz_file_final(file_path):
    """최종 완성 버전 파서"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    round_number = os.path.basename(file_path).replace('.txt', '').replace('회', '')
    
    # 각 문제를 [답] 패턴으로 구분
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
        
        # 패턴1: 한 줄로 된 선택지
        options = parse_single_line_options(q_content)
        
        # 패턴2: 여러 줄로 된 선택지
        if not options:
            options = parse_multi_line_options(q_content)
        
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
    
    print("📚 전산세무2급 문제 파싱 (최종 완성 버전)\n")
    print("=" * 60)
    
    for filename in sorted(os.listdir(cbt_folder)):
        if filename.endswith('.txt'):
            file_path = os.path.join(cbt_folder, filename)
            print(f"\n📖 {filename}")
            
            result = parse_quiz_file_final(file_path)
            round_num = result['round']
            questions = result['questions']
            
            all_data[f'quiz{round_num}'] = questions
            
            if len(questions) == 15:
                print(f"   ✅ 완벽! {len(questions)}개 문제")
            else:
                print(f"   ⚠️ {len(questions)}/15개 문제")
    
    # JSON 파일로 저장
    output_file = 'quiz_data_complete.json'
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
