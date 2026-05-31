import streamlit as st
from src.llm import call_llm
from src.pipeline import Solver, pipeline
import json
# 初始化session_state
if 'project_data' not in st.session_state:
    st.session_state.project_data = None
if 'project_details' not in st.session_state:
    st.session_state.project_details = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""


st.set_page_config(
    page_title="xxx",
    page_icon="📄",
    layout="wide"
)

st.title("信息门户")

st.markdown("---")

# st.subheader("AI助手")
st.write("在这里输入您的信息")

# 使用session_state保存用户输入
user_input = st.text_area(
    "请输入您的问题：",
    placeholder="请输入您的问题...",
    height=150,
    key="user_input",
    value=st.session_state.user_input
)

# Streamlit会自动更新session_state.user_input，无需手动修改

solver = Solver()
if st.button("发送", key="send_button"):
    if user_input.strip():
        with st.spinner("加载..."):
            try:
                current_id = solver.text_preprocess(user_input)
                project_data = solver.get_project_data(current_id)
                
                # 保存到session_state
                st.session_state.project_data = project_data
                st.session_state.project_details = []  # 重置详细信息
                
                st.success("解析完成！")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
    else:
        st.warning("请输入问题后再点击发送")

# 显示保存的解析结果
if st.session_state.project_data:
    project_data = st.session_state.project_data
    
    st.markdown("### 解析结果")
    st.markdown(f"**公司名称**: {project_data.name}")
    
    if project_data.projects:
        st.markdown("#### 项目基本信息")
        # 显示项目基本信息表格（不可编辑）
        basic_table_data = []
        for i, project in enumerate(project_data.projects, 1):
            basic_table_data.append({
                "序号": i,
                "项目名称": project.name,
                "项目领域": project.field,
                "应用知识产权": project.intellectual_property
            })
        st.table(basic_table_data)
        
        st.markdown("#### 知识产权详细信息输入")
        # 为每个项目创建一个文本框用于输入详细信息
        project_details = []
        for i, project in enumerate(project_data.projects, 1):
            st.markdown(f"**项目{i}：{project.name}**")
            detail_key = f"detail_input_{i}"
            # 从project实例中获取专利详细信息
            default_value = project_data.projects[i-1].patent_info if i-1 < len(project_data.projects) else ""
            # 如果project实例中没有，从session_state中获取
            if not default_value:
                for item in st.session_state.project_details:
                    if item["项目序号"] == i:
                        default_value = item["详细信息"]
                        break
            
            detail = st.text_area(
                f"请输入知识产权详细信息",
                value=default_value,
                height=100,
                key=detail_key,
                help="请输入详细的知识产权信息"
            )
            project_details.append({
                "项目序号": i,
                "项目名称": project.name,
                "详细信息": detail
            })
            st.markdown("---")
        
        # 添加提交按钮
        if st.button("提交详细信息"):
            # 保存详细信息到session_state
            st.session_state.project_details = project_details
            
            # 将专利详细信息写入project实例
            for item in project_details:
                project_index = item["项目序号"] - 1
                if 0 <= project_index < len(project_data.projects):
                    project_data.projects[project_index].patent_info = item["详细信息"]
            
            # # 保存project_data到本地文件（使用JSON序列化）
            # import json
            
            # 将project_data转换为字典格式
            def project_to_dict(project):
                return {
                    "name": project.name,
                    "project_id": project.project_id,
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "field": project.field,
                    "intellectual_property": project.intellectual_property,
                    "patent_info": project.patent_info,
                    "background": project.background,
                    "objectives": project.objectives,
                    "expected_benefits": project.expected_benefits,
                    "challenges": project.challenges,
                    "budget": project.budget,
                    "team_members": project.team_members
                }
            
            project_data_dict = {
                "name": project_data.name,
                "industry": project_data.industry,
                "location": project_data.location,
                "established_year": project_data.established_year,
                "description": project_data.description,
                "core_technologies": project_data.core_technologies,
                "patents": project_data.patents,
                "projects": [project_to_dict(p) for p in project_data.projects],
                "session_id": project_data.session_id
            }
            
            with open("project_data.json", "w", encoding="utf-8") as f:
                json.dump(project_data_dict, f, ensure_ascii=False, indent=2)
            
            # st.success("详细信息已提交并保存到项目中！项目数据已保存到本地文件 project_data.json")
            # 显示提交的详细信息
            # for item in project_details:
            #     st.write(f"项目{item['项目序号']}的详细信息: {item['详细信息']}")
            # 导入必要的模块
            1/0
            import time
            import threading
            import queue
            
            # 创建一个队列用于通信
            q = queue.Queue()
            
            # 定义一个函数来执行pipeline并返回执行时间
            def run_pipeline():
                start_time = time.time()
                pipeline(project_data_dict)
                end_time = time.time()
                execution_time = end_time - start_time
                q.put(execution_time)
            
            # 启动执行线程
            thread = threading.Thread(target=run_pipeline)
            thread.daemon = True
            thread.start()
            
            # 创建一个占位符用于显示计时信息
            timer_placeholder = st.empty()
            
            # 计时开始
            start_time = time.time()
            
            # 循环更新计时信息，直到pipeline执行完成
            while thread.is_alive():
                elapsed_time = time.time() - start_time
                timer_placeholder.info(f"正在处理中... 已用时：{elapsed_time:.0f}秒")
                time.sleep(1)
            
            # 获取执行时间
            execution_time = q.get()
            
            # 更新占位符显示最终结果
            timer_placeholder.success(f"项目处理完成！总执行时间：{execution_time:.0f}秒")


            st.markdown("---")
            # st.markdown("### AI回答")
            # response = project_data.generate_project_report()
            st.markdown(f"项目报告已生成！！！！！！")

st.markdown("---")
# st.markdown("### 使用说明")
# st.markdown("""
# 1. 在上方输入框中输入您的问题
# 2. 点击"发送"按钮
# 3. 等待AI助手回答您的问题
# """)
