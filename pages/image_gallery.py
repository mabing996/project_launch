import streamlit as st
import os
from PIL import Image
import glob
from io import BytesIO

# 尝试导入 HEIC 支持库
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()  # 注册 HEIC 格式支持
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    st.warning("⚠️ 未安装 pillow-heif 库，HEIC 格式图片可能无法显示。请运行 `pip install pillow-heif` 来支持 HEIC 格式。")

# 设置页面标题和布局
st.set_page_config(
    page_title="图片展示",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("🖼️ 图片展示")

# 定义图片目录路径
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')

# 确保目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)

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
        # 使用 PIL 直接打开图片（pillow-heif 已注册了 HEIC 格式支持）
        img = Image.open(image_path)
        
        # 转换为RGB模式（确保返回标准PIL Image对象）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
    except Exception as e:
        st.error(f"无法加载图片 {image_path}: {str(e)}")
        return None

# 侧边栏控制
st.sidebar.header("🎛️ 控制面板")

# 获取所有图片
images = get_images()

if not images:
    st.info("📁 图片目录中没有找到图片文件")
    st.write(f"请将图片文件放入以下目录：{IMAGES_DIR}")
else:
    # 显示图片数量
    st.sidebar.info(f"📊 共找到 {len(images)} 张图片")

    # 选择显示模式
    display_mode = st.sidebar.selectbox(
        "📱 显示模式",
        ["网格视图", "单张浏览", "轮播模式"],
        index=0
    )

    # 图片大小控制
    image_size = st.sidebar.slider(
        "🔍 图片大小",
        min_value=100,
        max_value=800,
        value=400,
        step=50
    )

    # 网格列数控制
    if display_mode == "网格视图":
        columns = st.sidebar.slider(
            "📐 每行显示数量",
            min_value=1,
            max_value=6,
            value=3,
            step=1
        )

    # 网格视图模式
    if display_mode == "网格视图":
        st.header("🖼️ 网格视图")
        
        # 创建网格布局
        cols = st.columns(columns)
        for idx, image_path in enumerate(images):
            col = cols[idx % columns]
            
            with col:
                # 加载图片
                img = load_image(image_path)
                if img:
                    # 调整图片大小
                    img.thumbnail((image_size, image_size))
                    
                    # 显示图片
                    col.image(img, use_container_width=True, caption=os.path.basename(image_path))
                    
                    # 图片信息
                    file_size = os.path.getsize(image_path) / 1024
                    img_size = img.size
                    col.caption(f"📏 {img_size[0]}x{img_size[1]} | 📦 {file_size:.1f}KB")

    # 单张浏览模式
    elif display_mode == "单张浏览":
        st.header("🔍 单张浏览")
        
        # 图片选择器
        selected_image = st.selectbox(
            "选择图片",
            images,
            format_func=lambda x: os.path.basename(x)
        )
        
        if selected_image:
            # 加载并显示图片
            img = load_image(selected_image)
            if img:
                # 使用两列布局
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # 显示大图
                    st.image(img, use_container_width=True, caption=os.path.basename(selected_image))
                
                with col2:
                    # 显示图片信息
                    st.subheader("📋 图片信息")
                    file_size = os.path.getsize(selected_image) / 1024
                    img_size = img.size
                    img_format = os.path.splitext(selected_image)[1].upper()
                    
                    st.metric("文件名", os.path.basename(selected_image))
                    st.metric("文件大小", f"{file_size:.1f} KB")
                    st.metric("图片尺寸", f"{img_size[0]} x {img_size[1]}")
                    st.metric("文件格式", img_format)
                    st.metric("图片模式", img.mode)
                    
                    # 显示文件路径
                    st.text("文件路径:")
                    st.code(selected_image)

    # 轮播模式
    elif display_mode == "轮播模式":
        st.header("🎬 轮播模式")
        
        # 轮播控制
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0
        
        # 创建控制按钮
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ 上一张"):
                st.session_state.current_index = (st.session_state.current_index - 1) % len(images)
                st.rerun()
        
        with col2:
            if st.button("⏭️ 下一张"):
                st.session_state.current_index = (st.session_state.current_index + 1) % len(images)
                st.rerun()
        
        with col3:
            st.write(f"📍 第 {st.session_state.current_index + 1} / {len(images)} 张")
        
        with col4:
            if st.button("🔄 自动播放"):
                if 'auto_play' not in st.session_state:
                    st.session_state.auto_play = False
                st.session_state.auto_play = not st.session_state.auto_play
                if st.session_state.auto_play:
                    st.rerun()
        
        with col5:
            if st.button("🏠 首页"):
                st.session_state.current_index = 0
                st.rerun()
        
        # 自动播放功能
        if 'auto_play' in st.session_state and st.session_state.auto_play:
            import time
            time.sleep(2)
            st.session_state.current_index = (st.session_state.current_index + 1) % len(images)
            st.rerun()
        
        # 显示当前图片
        current_image = images[st.session_state.current_index]
        img = load_image(current_image)
        
        if img:
            # 调整图片大小
            display_img = img.copy()
            display_img.thumbnail((image_size * 2, image_size * 2))
            
            # 显示图片
            st.image(display_img, use_container_width=True, caption=os.path.basename(current_image))
            
            # 显示图片信息
            file_size = os.path.getsize(current_image) / 1024
            img_size = img.size
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文件大小", f"{file_size:.1f} KB")
            with col2:
                st.metric("图片尺寸", f"{img_size[0]} x {img_size[1]}")
            with col3:
                st.metric("图片模式", img.mode)

# 底部信息
st.markdown("---")
st.caption("💡 提示：使用侧边栏控制面板可以调整显示模式和图片大小")

# 添加图片上传功能
st.markdown("---")
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

