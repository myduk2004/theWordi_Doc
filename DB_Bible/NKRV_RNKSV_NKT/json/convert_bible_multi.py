import json
import os

def parse_multi_bible_json_standard():
    input_file = 'json작업.txt'  # 처리할 원본 파일명
    
    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
        return

    # 1. 파일명 조합 단어 받기
    user_word = input("파일 이름 뒤에 붙일 단어를 입력하세요 (예: 개역개정): ").strip()
    if not user_word:
        user_word = "결과"

    print(f"\n'{input_file}'의 모든 성경 장(Chapter) 수집을 시작합니다...")

    # 2. 표준 JSON 파일 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"오류: JSON 파일 읽기 실패 - {e}")
            return

    # 데이터가 단일 객체 {} 일 경우를 대비해 리스트 [] 구조로 통일화
    if isinstance(raw_data, dict):
        data_list = [raw_data]
    elif isinstance(raw_data, list):
        data_list = raw_data
    else:
        print("오류: 올바르지 않은 성경 데이터 구조입니다.")
        return

    base_title = "성경"
    text_content = []
    processed_count = 0

    # 3. 데이터 배열 내의 모든 장(Chapter)을 순회하며 추출
    for index, item in enumerate(data_list):
        if not isinstance(item, dict):
            continue
            
        actual_data = item.get('data', {})
        chapter_data = actual_data.get('chapter', {})
        
        if not chapter_data or 'content' not in chapter_data:
            continue

        processed_count += 1

        # 첫 장의 타이틀로 성경 이름 가져오기 (예: "마태복음 2" -> "마태복음")
        if processed_count == 1 and 'title' in chapter_data:
            base_title = chapter_data['title'].split()[0]

        # 장 번호 추출 ("number" 우선, 없으면 "id"에서 파싱)
        chapter_num = chapter_data.get('number', '')
        if not chapter_num:
            chapter_id = chapter_data.get('id', '')
            if chapter_id and '.' in chapter_id:
                chapter_num = chapter_id.split('.')[-1]
            else:
                chapter_num = str(processed_count)

        # 구절별 저장소 생성
        verses = {}
        content_list = chapter_data.get('content', [])

        for block in content_list:
            if isinstance(block, dict) and 'content' in block:
                for sub_item in block['content']:
                    if sub_item.get('type') == 'verse-text':
                        v_id = sub_item.get('verseId')
                        if v_id:
                            try:
                                v_num = int(v_id.split('.')[-1])
                            except ValueError:
                                continue
                            
                            text = sub_item.get('content', '')
                            if v_num not in verses:
                                verses[v_num] = []
                            verses[v_num].append(text)

        # 현재 장 데이터를 합산 리스트에 정렬하여 추가
        if verses:
            text_content.append(f"{chapter_num}장")
            for v_num in sorted(verses.keys()):
                full_text = " ".join(verses[v_num]).replace('\n', ' ').strip()
                full_text = " ".join(full_text.split())
                text_content.append(f"{v_num}. {full_text}")
            # 장과 장 분리용 공백 추가
            text_content.append("")

    if processed_count == 0:
        print("오류: 데이터 구조에서 'chapter' 혹은 'content' 블록을 찾지 못했습니다.")
        return

    # 4. 하나의 종합 텍스트 파일로 내보내기
    output_filename = f"{base_title}_{user_word}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f_out:
        f_out.write("\n".join(text_content).strip())

    print(f"\n변환 성공! 총 {processed_count}개의 장이 정상적으로 추출 및 병합되었습니다.")
    print(f"생성된 파일명: '{output_filename}'")

if __name__ == '__main__':
    parse_multi_bible_json_standard()