import streamlit as st
import os
from PIL import Image
import glob
import time

# 尝试导入 HEIC 支持库
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
st.header("📤 上传新图片")

uploaded_files = st.file_uploader(
    "选择图片文件上传",
    type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic'],
    accept_multiple_files=True,
    help="支持多种图片格式，包括 HEIC 格式"
)

if uploaded_files:
    upload_count = 0
    for uploaded_file in uploaded_files:
        try:
            # 生成唯一的文件名（使用时间戳）
            import time
            timestamp = int(time.time() * 1000)
            file_ext = os.path.splitext(uploaded_file.name)[1]
            new_filename = f"IMG_{timestamp}{file_ext}"
            save_path = os.path.join(IMAGES_DIR, new_filename)
            
            # 保存文件
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            upload_count += 1
            st.success(f"✅ 已保存：{new_filename}")
            
        except Exception as e:
            st.error(f"❌ 保存失败 {uploaded_file.name}: {str(e)}")
    
    if upload_count > 0:
        st.info(f"🎉 成功上传 {upload_count} 张图片")
        # 提示用户刷新页面查看新图片
        if st.button("🔄 刷新页面查看新图片"):
            st.rerun()

# 最近上传的图片预览
st.markdown("---")
# 设置页面标题和布局
st.set_page_config(
    page_title="图片管理",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("🗂️ 图片后台管理")

# 定义图片目录路径
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')

# 支持的图片格式
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']

# 获取所有图片文件
def get_images():
    images = []
    for ext in SUPPORTED_FORMATS:
        images.extend(glob.glob(os.path.join(IMAGES_DIR, f'*{ext}')))
        images.extend(glob.glob(os.path.join(IMAGES_DIR, f'*{ext.upper()}')))
    return sorted(images)

# 加载图片数据
@st.cache_resource
def load_image(image_path):
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        st.error(f"无法加载图片 {image_path}: {str(e)}")
        return None

# 初始化会话状态
if 'selected_images' not in st.session_state:
    st.session_state.selected_images = []
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

# 获取所有图片
images = get_images()

# 侧边栏统计信息
st.sidebar.header("📊 统计信息")
st.sidebar.info(f"📁 图片总数: {len(images)}")

# 批量删除按钮
if images:
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader(f"图片列表 ({len(images)} 张)")
    with col2:
        if st.button("🗑️ 批量删除选中", type="primary", use_container_width=True):
            if st.session_state.selected_images:
                st.session_state.delete_confirm = ("batch", st.session_state.selected_images.copy())
            else:
                st.warning("请先选择要删除的图片")

# 删除确认对话框
if st.session_state.delete_confirm:
    delete_type, delete_list = st.session_state.delete_confirm
    with st.expander("⚠️ 确认删除", expanded=True):
        st.warning(f"确定要删除 {len(delete_list)} 张图片吗？此操作不可撤销！")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认删除", type="primary"):
                deleted_count = 0
                for img_path in delete_list:
                    try:
                        os.remove(img_path)
                        deleted_count += 1
                        if img_path in st.session_state.selected_images:
                            st.session_state.selected_images.remove(img_path)
                    except Exception as e:
                        st.error(f"删除失败 {os.path.basename(img_path)}: {str(e)}")
                st.success(f"成功删除 {deleted_count} 张图片")
                st.session_state.delete_confirm = None
                st.rerun()
        with col2:
            if st.button("❌ 取消"):
                st.session_state.delete_confirm = None
                st.rerun()

# 图片网格展示
if images:
    # 获取列数设置
    columns = st.sidebar.slider("📐 每行显示数量", min_value=2, max_value=6, value=4, step=1)
    cols = st.columns(columns)
    
    # 按修改时间排序（最新的在前）
    images_with_time = []
    for img_path in images:
        try:
            mtime = os.path.getmtime(img_path)
            images_with_time.append((img_path, mtime))
        except:
            images_with_time.append((img_path, 0))
    images_with_time.sort(key=lambda x: x[1], reverse=True)
    sorted_images = [img[0] for img in images_with_time]
    
    for idx, image_path in enumerate(sorted_images):
        col = cols[idx % columns]
        
        with col:
            # 选择框
            is_selected = image_path in st.session_state.selected_images
            checkbox = st.checkbox(
                "选择", 
                value=is_selected, 
                key=f"checkbox_{idx}"
            )
            
            # 更新选择状态
            if checkbox != is_selected:
                if checkbox:
                    st.session_state.selected_images.append(image_path)
                else:
                    st.session_state.selected_images.remove(image_path)
            
            # 加载并显示图片
            img = load_image(image_path)
            if img and img.size[0] > 0 and img.size[1] > 0:
                try:
                    img_copy = img.copy()
                    if img_copy.size[0] > 200 or img_copy.size[1] > 200:
                        img_copy.thumbnail((200, 200))
                    st.image(img_copy, width='stretch', caption=os.path.basename(image_path))
                except Exception as e:
                    st.warning(f"⚠️ 无法显示图片: {str(e)}")
            else:
                st.warning(f"⚠️ 无法加载图片: {os.path.basename(image_path)}")
            
            # 删除按钮
            if st.button(f"🗑️ 删除", key=f"delete_single_{idx}", use_container_width=True):
                st.session_state.delete_confirm = ("single", [image_path])
                st.rerun()

else:
    st.info("📁 图片目录中没有找到图片文件")
    st.write(f"目录路径: {IMAGES_DIR}")

# 选中状态提示
if st.session_state.selected_images:
    st.sidebar.info(f"✅ 已选择: {len(st.session_state.selected_images)} 张")
    if st.sidebar.button("🗑️ 删除选中", type="primary"):
        st.session_state.delete_confirm = ("batch", st.session_state.selected_images.copy())
        st.rerun()

# 底部信息
st.markdown("---")
st.caption("💡 提示：勾选图片后可以批量删除，或点击单张图片的删除按钮单独删除")

# 上传功能
st.markdown("---")
st.header("📤 上传新图片")

uploaded_files = st.file_uploader(
    "选择图片文件上传",
    type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic'],
    accept_multiple_files=True,
    help="支持多种图片格式，包括 HEIC 格式",
    key="uploader"
)

if uploaded_files:
    upload_count = 0
    for uploaded_file in uploaded_files:
        try:
            timestamp = int(time.time() * 1000)
            file_ext = os.path.splitext(uploaded_file.name)[1]
            new_filename = f"IMG_{timestamp}{file_ext}"
            save_path = os.path.join(IMAGES_DIR, new_filename)
            
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            upload_count += 1
            st.success(f"✅ 已保存：{new_filename}")
            
        except Exception as e:
            st.error(f"❌ 保存失败 {uploaded_file.name}: {str(e)}")
    
    if upload_count > 0:
        st.info(f"🎉 成功上传 {upload_count} 张图片")
        if st.button("🔄 刷新页面查看新图片"):
            st.rerun()