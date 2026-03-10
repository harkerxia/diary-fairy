import os
import re
from datetime import datetime

def import_qmd_to_db(db_instance, user_id, qmd_folder):
    for filename in os.listdir(qmd_folder):
        if filename.endswith(".qmd") or filename.endswith(".md"):
            filepath = os.path.join(qmd_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = re.split(r'\n(?=#{2,3}\s)', content)
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            inserted_count = 0
            
            for chunk in chunks:
                chunk = chunk.strip()
                if len(chunk) > 10:
                    db_instance.insert_micro_memory(
                        user_id=user_id,
                        date=today_str,
                        source_type=f"qmd_{filename}",
                        content=chunk,
                        tags="qmd, archive"
                    )
                    inserted_count += 1
                    
            print(f"File {filename}: 成功导入 {inserted_count} 个记忆块。")