

from docx import Document
import os



if __name__ == '__main__':
    path = ['/Users/swh/project_launch/assets/舜斯-专审文件/RD/',
    '/Users/swh/project_launch/assets/索屿-专审材料/RD',
    '/Users/swh/project_launch/assets/恒葆诺沃专审立项材料/项目立项文件/'
    ]
    save_path = '/Users/swh/project_launch/assets/texts/'
    for p in path:
        for file in os.listdir(p):
            if file.endswith('.docx'):
                doc = Document(f'{p}/{file}')
                texts = []
                for para in doc.paragraphs:
                    texts.append(para.text)
                with open(f'{save_path}{file.split(".")[0]}.txt', 'w') as f:
                    # f.write('\n'.join(texts))
                    for idx, t in enumerate(texts):
                        f.write(f'{t}\n')
