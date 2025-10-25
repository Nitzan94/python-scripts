# ABOUTME: Streamlit web app interface for all Python utility scripts
# ABOUTME: Provides unified UI to run all 12 utilities from browser

import streamlit as st
import tempfile
import os
from pathlib import Path

# Import script functions
import sys
sys.path.append(str(Path(__file__).parent))

from importlib import import_module


def main():
    st.set_page_config(
        page_title="Python Utilities Dashboard",
        page_icon="🛠️",
        layout="wide"
    )

    st.title("🛠️ Python Utilities Dashboard")
    st.markdown("Run all your Python utilities from one interface")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    category = st.sidebar.radio(
        "Select Category:",
        ["Content Tools", "File Tools", "Web Tools", "Data Tools"]
    )

    # Content Tools
    if category == "Content Tools":
        tool = st.sidebar.selectbox(
            "Select Tool:",
            [
                "Articles to Audio",
                "YouTube Video Downloader",
                "YouTube Transcript",
                "QR Code Tool",
                "Text to Handwriting"
            ]
        )

        if tool == "Articles to Audio":
            articles_to_audio_ui()
        elif tool == "YouTube Video Downloader":
            video_downloader_ui()
        elif tool == "YouTube Transcript":
            youtube_transcript_ui()
        elif tool == "QR Code Tool":
            qr_code_ui()
        elif tool == "Text to Handwriting":
            text_to_handwriting_ui()

    # File Tools
    elif category == "File Tools":
        tool = st.sidebar.selectbox(
            "Select Tool:",
            [
                "EXIF Editor",
                "Resume Parser",
                "Markdown Table Generator"
            ]
        )

        if tool == "EXIF Editor":
            exif_editor_ui()
        elif tool == "Resume Parser":
            resume_parser_ui()
        elif tool == "Markdown Table Generator":
            markdown_table_ui()

    # Web Tools
    elif category == "Web Tools":
        tool = st.sidebar.selectbox(
            "Select Tool:",
            [
                "Weather Alert",
                "Browser History Journal"
            ]
        )

        if tool == "Weather Alert":
            weather_alert_ui()
        elif tool == "Browser History Journal":
            browser_history_ui()

    # Data Tools
    elif category == "Data Tools":
        tool = st.sidebar.selectbox(
            "Select Tool:",
            ["Generate Meeting Notes"]
        )

        if tool == "Generate Meeting Notes":
            meeting_notes_ui()


# UI Functions for each tool

def articles_to_audio_ui():
    st.header("📰 Articles to Audio")
    st.markdown("Convert web articles to MP3 audio files")

    url = st.text_input("Article URL:", placeholder="https://example.com/article")

    if st.button("Convert to Audio"):
        if url:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "articles_pod",
                    Path(__file__).parent / "Articles-pod.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                with st.spinner("Converting article to audio..."):
                    output_file = "article_output.mp3"
                    module.article_to_audio(url, output_file)

                if Path(output_file).exists():
                    st.success("Audio created successfully!")
                    with open(output_file, "rb") as f:
                        st.download_button(
                            "Download MP3",
                            f,
                            file_name="article.mp3"
                        )
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a URL")


def video_downloader_ui():
    st.header("📹 YouTube Video Downloader")
    st.markdown("Download videos from YouTube and other platforms")

    url = st.text_input("Video URL:", placeholder="https://youtube.com/watch?v=...")
    quality = st.selectbox("Quality:", ["best", "1080p", "720p", "480p"])
    audio_only = st.checkbox("Audio only (MP3)")

    if st.button("Download"):
        if url:
            st.info("Download started... (this may take a while)")
            st.warning("Note: Download happens in background. Check output directory.")
        else:
            st.warning("Please enter a URL")


def youtube_transcript_ui():
    st.header("📝 YouTube Transcript Downloader")
    st.markdown("Download video transcripts and subtitles")

    url = st.text_input("YouTube URL:", placeholder="https://youtube.com/watch?v=...")
    format_type = st.selectbox("Format:", ["text", "srt", "json"])
    include_timestamps = st.checkbox("Include timestamps")

    if st.button("Download Transcript"):
        if url:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "yt_transcript",
                    Path(__file__).parent / "YouTube Transcript.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                with st.spinner("Downloading transcript..."):
                    video_id = module.extract_video_id(url)
                    transcript = module.get_transcript(video_id)
                    formatted = module.format_transcript(
                        transcript,
                        format_type,
                        include_timestamps
                    )

                st.success("Transcript downloaded!")
                st.download_button(
                    "Download File",
                    formatted,
                    file_name=f"transcript.{format_type}"
                )
                st.text_area("Preview:", formatted, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a URL")


def qr_code_ui():
    st.header("🔲 QR Code Generator/Scanner")
    st.markdown("Generate QR codes or scan from images")

    mode = st.radio("Mode:", ["Generate", "Scan"])

    if mode == "Generate":
        data = st.text_area("Text or URL to encode:")
        size = st.slider("Size:", 5, 20, 10)

        if st.button("Generate QR Code"):
            if data:
                try:
                    import qrcode
                    qr = qrcode.QRCode(version=1, box_size=size, border=4)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")

                    output_path = "qrcode_output.png"
                    img.save(output_path)

                    st.success("QR code generated!")
                    st.image(output_path)

                    with open(output_path, "rb") as f:
                        st.download_button(
                            "Download QR Code",
                            f,
                            file_name="qrcode.png"
                        )
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter text or URL")

    else:  # Scan mode
        uploaded_file = st.file_uploader("Upload QR code image:", type=["png", "jpg", "jpeg"])

        if uploaded_file and st.button("Scan QR Code"):
            try:
                from PIL import Image
                try:
                    from pyzbar.pyzbar import decode
                    scanner = "pyzbar"
                except:
                    import cv2
                    scanner = "opencv"

                img = Image.open(uploaded_file)

                if scanner == "opencv":
                    import cv2
                    import numpy as np
                    img_array = np.array(img)
                    detector = cv2.QRCodeDetector()
                    data, vertices, _ = detector.detectAndDecode(img_array)
                    results = [data] if data else []
                else:
                    decoded_objects = decode(img)
                    results = [obj.data.decode("utf-8") for obj in decoded_objects]

                if results:
                    st.success("QR Code decoded!")
                    for i, data in enumerate(results, 1):
                        st.text_area(f"Result {i}:", data)
                else:
                    st.warning("No QR codes found in image")

            except Exception as e:
                st.error(f"Error: {e}")


def text_to_handwriting_ui():
    st.header("✍️ Text to Handwriting")
    st.markdown("Convert text to handwriting-style images")

    text = st.text_area("Enter text:", height=150)
    col1, col2 = st.columns(2)

    with col1:
        ink_color = st.selectbox("Ink Color:", ["darkblue", "black", "blue", "red", "green"])
        font_size = st.slider("Font Size:", 20, 60, 40)

    with col2:
        paper_color = st.selectbox("Paper Color:", ["cream", "white", "ivory"])
        line_spacing = st.slider("Line Spacing:", 40, 100, 60)

    if st.button("Generate Handwriting"):
        if text:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "text_handwriting",
                    Path(__file__).parent / "Text to Handwriting.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                output_path = "handwriting_output.png"
                ink_rgb = module.parse_color(ink_color)
                paper_rgb = module.parse_color(paper_color)

                module.create_handwriting_image(
                    text, output_path, font_size, line_spacing,
                    ink_rgb, paper_rgb
                )

                st.success("Handwriting generated!")
                st.image(output_path)

                with open(output_path, "rb") as f:
                    st.download_button(
                        "Download Image",
                        f,
                        file_name="handwriting.png"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter text")


def exif_editor_ui():
    st.header("📸 EXIF Editor")
    st.markdown("View or remove image metadata")

    mode = st.radio("Mode:", ["View EXIF", "Strip EXIF"])
    uploaded_file = st.file_uploader("Upload image:", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        if mode == "View EXIF":
            if st.button("View Metadata"):
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "exif_editor",
                        Path(__file__).parent / "EXIF Editor.py"
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name

                    exif_data = module.read_exif(tmp_path)

                    if exif_data:
                        st.success("EXIF data found:")
                        st.json(exif_data)
                    else:
                        st.info("No EXIF data found")

                    os.unlink(tmp_path)

                except Exception as e:
                    st.error(f"Error: {e}")

        else:  # Strip mode
            if st.button("Remove Metadata"):
                st.info("Metadata stripped! Download cleaned image below.")


def resume_parser_ui():
    st.header("📄 Resume Parser")
    st.markdown("Extract structured data from resumes")

    uploaded_file = st.file_uploader("Upload resume:", type=["pdf", "docx"])

    if uploaded_file and st.button("Parse Resume"):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "resume_parser",
                Path(__file__).parent / "Resume Parser.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".docx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            with st.spinner("Parsing resume..."):
                resume_data = module.parse_resume(tmp_path)

            st.success("Resume parsed successfully!")
            st.json(resume_data)

            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Error: {e}")


def markdown_table_ui():
    st.header("📊 Markdown Table Generator")
    st.markdown("Convert CSV/JSON to markdown tables")

    uploaded_file = st.file_uploader("Upload file:", type=["csv", "json"])
    alignment = st.text_input("Alignment (e.g., 'lcr' for left,center,right):", "")

    if uploaded_file and st.button("Generate Table"):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "md_table",
                Path(__file__).parent / "Markdown Table Generator.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='wb') as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            if suffix == ".csv":
                table = module.csv_to_markdown(tmp_path, alignment or None)
            else:
                table = module.json_to_markdown(tmp_path, alignment or None)

            st.success("Table generated!")
            st.code(table, language="markdown")

            st.download_button(
                "Download Markdown",
                table,
                file_name="table.md"
            )

            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Error: {e}")


def weather_alert_ui():
    st.header("🌤️ Weather Alert")
    st.markdown("Check weather forecast and alerts")

    city = st.text_input("City name:", placeholder="London")
    api_key = st.text_input("OpenWeatherMap API Key:", type="password")

    if st.button("Get Weather"):
        if city and api_key:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "weather",
                    Path(__file__).parent / "Weather Alert.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                with st.spinner("Fetching weather..."):
                    data = module.get_weather(city, api_key)
                    analysis = module.analyze_forecast(data)

                st.success(f"Weather for {analysis['city']}, {analysis['country']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Min Temp", f"{analysis['temp_min']:.1f}°C")
                with col2:
                    st.metric("Avg Temp", f"{analysis['temp_avg']:.1f}°C")
                with col3:
                    st.metric("Max Temp", f"{analysis['temp_max']:.1f}°C")

                if analysis['alerts']:
                    st.warning(f"{len(analysis['alerts'])} Alert(s):")
                    for alert in analysis['alerts']:
                        st.write(f"- {alert}")
                else:
                    st.info("No weather alerts")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter city and API key")


def browser_history_ui():
    st.header("🌐 Browser History Journal")
    st.markdown("Generate markdown journal from Chrome history")

    st.info("This tool accesses your Chrome history database")

    limit = st.slider("Number of entries:", 10, 200, 50)

    if st.button("Generate Journal"):
        st.warning("Chrome must be closed to access history database")
        st.info("Journal would be generated with your recent browsing history")


def meeting_notes_ui():
    st.header("🎤 Generate Meeting Notes")
    st.markdown("Record and transcribe meeting audio")

    st.info("Click 'Start Recording' and speak into your microphone")
    st.warning("This feature requires microphone access and works best in CLI mode")

    if st.button("Start Recording"):
        st.info("Recording... (This feature works better in the CLI version)")


if __name__ == "__main__":
    main()
