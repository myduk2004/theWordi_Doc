import json
import os

def parse_bible_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # JSON에서 data.chapter.title 가져오기
    chapter_title = data.get('data', {}).get('chapter', {}).get('title', '')
    
    # 만약 title 정보가 없으면 기본값 지정
    if not chapter_title:
        chapter_title = '정리된_성경_파일'
        
    # 파일명 최종 지정 (예: "마태복음 21" -> "마태복음 21.txt")
    output_txt_path = f"{chapter_title}.txt"
    
    # 장(Chapter) 번호 추출 (예: "MAT.21" -> 21)
    chapter_id = data.get('data', {}).get('chapter', {}).get('id', '')
    chapter_num = "1" # 기본값
    if chapter_id and '.' in chapter_id:
        chapter_num = chapter_id.split('.')[-1]
    
    # 구절들을 저장할 딕셔너리
    verses = {}
    content_list = data.get('data', {}).get('chapter', {}).get('content', [])
    
    for block in content_list:
        if 'content' in block:
            for item in block['content']:
                if item.get('type') == 'verse-text':
                    v_id = item.get('verseId')
                    if v_id:
                        try:
                            v_num = int(v_id.split('.')[-1])
                        except ValueError:
                            continue
                        
                        text = item.get('content', '')
                        if v_num not in verses:
                            verses[v_num] = []
                        verses[v_num].append(text)
                        
    # 텍스트 파일로 저장
    with open(output_txt_path, 'w', encoding='utf-8') as f_out:
        # 상단에 "X장" 타이틀 추가
        f_out.write(f"{chapter_num}장\n")
        
        # 1절부터 순서대로 정렬하여 출력
        for v_num in sorted(verses.keys()):
            full_text = " ".join(verses[v_num]).replace('\n', ' ').strip()
            full_text = " ".join(full_text.split())
            f_out.write(f"{v_num}. {full_text}\n")
            
    return output_txt_path

if __name__ == '__main__':
    input_file = 'json파일.txt'
    
    if os.path.exists(input_file):
        # 함수가 실행되면서 자동으로 파일명을 만들어 저장합니다.
        saved_filename = parse_bible_json(input_file)
        print(f"변환 완료! 결과가 '{saved_filename}' 파일로 저장되었습니다.")
    else:
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")