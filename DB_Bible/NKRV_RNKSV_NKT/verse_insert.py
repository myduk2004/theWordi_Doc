import datetime
import re
import pymysql
import os
# 1. 데이터베이스 연결 설정
db_config = {
    "host": "localhost",  # 안전하게 IP 주소로 설정
    "user": "",
    "password": "",
    "database": "",
    "charset": "utf8mb4",
}

# 2. 파일에서 데이터를 읽어와 data_list 구성하기 
file_path = input("작업할 파일명을 입력해주세요(ex:마태복음_개역개정.txt) : ").strip()   
if not os.path.exists(file_path):
    print(f"❌ 파일명 : {file_path}을 찾을 수 없습니다. 다시 확인해주세요. ")
    exit()

version_id = input("version_id를 입력해주세요.(ex:NKRV) : ").strip()
try:
    book_id = int(input("book_id를 입력해주세요.(ex:40) : ").strip())
except ValueError:
    book_id = 0

if not version_id or not book_id:
    print(f"❌ verseion_id, book_id : 유효한 값이 아닙니다. 다시 확인해주세요.")
    exit()



#file_path = "마태복음_개역개정.txt"  # 파일 경로를 본인 환경에 맞게 수정하세요
#file_path = f"{file_name}.txt"
 
data_list = []
current_time = datetime.datetime.now()
current_chapter = 0

# 장(Chapter) 판별을 위한 정규식 (예: 2장, 3장, 100장 등)
chapter_pattern = re.compile(r"^(\d+)장")
# 절(Verse) 판별을 위한 정규식 (예: 1. 헤롯 왕..., 24. 그의 소문이...)
verse_pattern = re.compile(r"^(\d+)\.\s*(.*)")

print("파일 분석을 시작합니다...")

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        # 같은 불필요한 태그나 빈 줄 제거
        line = re.sub(r"\\", "", line).strip()
        if not line:
            continue

        # 'X장' 패턴이 매칭되면 현재 '장' 번호 업데이트
        chapter_match = chapter_pattern.match(line)
        if chapter_match:
            current_chapter = int(chapter_match.group(1))
            continue

        # 'X. 내용' 패턴이 매칭되면 절 번호와 본문 추출하여 리스트에 담기
        verse_match = verse_pattern.match(line)
        if verse_match and current_chapter > 0:
            verse_num = int(verse_match.group(1))
            verse_text = verse_match.group(2).strip()

            # 스키마 구조: (version_id, book_id, chapter, verse, text, reg_id, reg_dt, upd_id, upd_dt)
            # 마태복음 가정이므로 book_id는 일단 1로 고정했습니다. 필요시 변경 가능합니다.
            record = (
                version_id,          # version_id
                book_id,               # book_id (마태복음)
                current_chapter, # chapter
                verse_num,       # verse
                verse_text,      # text
                1,               # reg_id
                current_time,    # reg_dt
                1,               # upd_id
                current_time     # upd_dt
            )
            data_list.append(record)

print(f"분석 완료! 총 {len(data_list)}개의 구절을 추출했습니다.")

# 3. DB 커넥션 및 데이터 삽입 실행
if not data_list:
    print("❌ 추출된 데이터가 없어 종료합니다. 파일 형식을 확인해주세요.")
    exit()

connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        sql = """
            INSERT INTO bible_verse (
                version_id, book_id, chapter, verse, text, reg_id, reg_dt, upd_id, upd_dt
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        print("DB 대용량 입력을 시작합니다...")
        cursor.executemany(sql, data_list)

        connection.commit()
        print("🎉 파일 안의 모든 성경 데이터가 성공적으로 저장되었습니다!")

except Exception as e:
    connection.rollback()
    print(f"❌ 에러가 발생하여 롤백되었습니다: {e}")

finally:
    connection.close()