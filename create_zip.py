import zipfile
import glob
import os

def create_ju_zip():
    """JU 파일들을 압축합니다."""
    ju_files = glob.glob("outputs/dataset/JU-*.jpg")
    
    with zipfile.ZipFile("KDOCS_SYNTH_JU_Samples.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in ju_files:
            zipf.write(file, os.path.basename(file))
    
    print(f"JU 압축 완료: {len(ju_files)}개 파일")

if __name__ == "__main__":
    create_ju_zip() 