import streamlit as st
import os
import pandas as pd
from datetime import datetime

# 设置页面标题
st.title("文档管理系统")

# 定义文档目录路径
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'docs')

# 确保目录存在
os.makedirs(DOCS_DIR, exist_ok=True)

# 加载文档列表
def load_documents():
    documents = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith('.docx'):
            file_path = os.path.join(DOCS_DIR, filename)
            file_size = os.path.getsize(file_path) / 1024  # 转换为KB
            modified_time = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
            documents.append({
                '文件名': filename,
                '大小(KB)': round(file_size, 2),
                '修改时间': modified_date,
                '路径': file_path
            })
    return documents

# 加载文档数据
documents = load_documents()

# 显示文档列表
st.subheader("文档列表")

if documents:
    # 创建DataFrame
    df = pd.DataFrame(documents)
    
    # 显示表格
    st.dataframe(df[['文件名', '大小(KB)', '修改时间']], use_container_width=True)
    
    # 为每个文档提供操作按钮
    st.subheader("文档操作")
    
    for doc in documents:
        with st.expander(f"{doc['文件名']}"):
            col1, col2, col3 = st.columns(3)
            
            # 预览按钮
            with col1:
                if st.button(f"预览", key=f"preview_{doc['文件名']}"):
                    st.info("暂不支持")
                    st.write(f"文件路径: {doc['路径']}")
            
            # 下载按钮
            with col2:
                with open(doc['路径'], 'rb') as f:
                    st.download_button(
                        label="下载",
                        data=f,
                        file_name=doc['文件名'],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"download_{doc['文件名']}"
                    )
            
            # 删除按钮
            with col3:
                if st.button(f"删除", key=f"delete_{doc['文件名']}"):
                    try:
                        os.remove(doc['路径'])
                        st.success(f"成功删除文件: {doc['文件名']}")
                        # 重新加载文档列表
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除文件失败: {str(e)}")
else:
    st.info("当前目录下没有文档文件")

# 刷新按钮
if st.button("刷新文档列表"):
    st.rerun()
