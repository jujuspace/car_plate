import gradio as gr
import cv2
import numpy as np
import os
import json
import glob
from PIL import Image, ImageDraw

class PointAnnotator:
    def __init__(self, images_folder):
        self.images_folder = images_folder
        self.annotations = {}  # 이미지명: [4개 점] 저장
        self.current_points = []  # 현재 선택중인 점들
        self.current_image_path = None
        self.annotation_file = "annotations.json"

        # 기존 어노테이션 로드
        self.load_annotations()

        # 이미지 파일 목록 가져오기
        self.image_files = self.get_image_files()
        self.current_index = 0

    def get_image_files(self):
        """모든 세그먼트의 이미지 파일 목록을 가져옵니다"""
        image_files = []
        for segment_folder in ['segment_1', 'segment_2', 'segment_3']:
            folder_path = os.path.join(self.images_folder, segment_folder)
            if os.path.exists(folder_path):
                files = glob.glob(os.path.join(folder_path, "*.jpg"))
                image_files.extend(files)
        return sorted(image_files)

    def load_annotations(self):
        """저장된 어노테이션을 로드합니다"""
        if os.path.exists(self.annotation_file):
            with open(self.annotation_file, 'r') as f:
                self.annotations = json.load(f)
            print(f"기존 어노테이션 {len(self.annotations)}개를 로드했습니다.")
        else:
            print("새로운 어노테이션 파일을 시작합니다.")

    def save_annotations(self):
        """어노테이션을 JSON 파일로 저장합니다"""
        with open(self.annotation_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
        print(f"어노테이션을 {self.annotation_file}에 저장했습니다.")

    def get_current_image(self):
        """현재 이미지를 가져옵니다"""
        if not self.image_files:
            return None, "이미지 파일이 없습니다."

        self.current_image_path = self.image_files[self.current_index]
        image = cv2.imread(self.current_image_path)
        if image is None:
            return None, f"이미지를 로드할 수 없습니다: {self.current_image_path}"

        # BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 현재 이미지의 기존 점들 로드
        image_name = os.path.basename(self.current_image_path)
        if image_name in self.annotations:
            self.current_points = self.annotations[image_name].copy()
        else:
            self.current_points = []

        # 점들을 이미지에 그리기
        annotated_image = self.draw_points_on_image(image, self.current_points)

        info = f"이미지 {self.current_index + 1}/{len(self.image_files)}: {image_name}"
        info += f"\n현재 점 개수: {len(self.current_points)}/4"
        if len(self.current_points) == 4:
            info += " ✓ 완료"

        return annotated_image, info

    def draw_points_on_image(self, image, points):
        """이미지에 점들을 그립니다"""
        if not points:
            return image

        # PIL로 변환해서 그리기
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)

        # 점들 그리기
        for i, (x, y) in enumerate(points):
            # 점 그리기 (빨간 원)
            radius = 8
            draw.ellipse([x-radius, y-radius, x+radius, y+radius],
                        fill='red', outline='white', width=2)
            # 번호 표시
            draw.text((x+10, y-10), str(i+1), fill='white')

        # 4개 점이 모두 있으면 사각형 그리기
        if len(points) == 4:
            # 점들을 순서대로 연결
            for i in range(4):
                start = points[i]
                end = points[(i+1) % 4]
                draw.line([start[0], start[1], end[0], end[1]],
                         fill='green', width=3)

        return np.array(pil_image)

    def add_point(self, evt: gr.SelectData):
        """클릭한 위치에 점을 추가합니다"""
        if len(self.current_points) >= 4:
            return self.get_current_image()

        x, y = evt.index[0], evt.index[1]
        self.current_points.append([x, y])

        # 4개 점이 모두 찍히면 자동 저장
        if len(self.current_points) == 4:
            image_name = os.path.basename(self.current_image_path)
            self.annotations[image_name] = self.current_points.copy()
            self.save_annotations()

        return self.get_current_image()

    def clear_points(self):
        """현재 이미지의 점들을 삭제합니다"""
        self.current_points = []
        image_name = os.path.basename(self.current_image_path)
        if image_name in self.annotations:
            del self.annotations[image_name]
            self.save_annotations()
        return self.get_current_image()

    def next_image(self):
        """다음 이미지로 이동"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
        return self.get_current_image()

    def prev_image(self):
        """이전 이미지로 이동"""
        if self.current_index > 0:
            self.current_index -= 1
        return self.get_current_image()

    def save_current(self):
        """현재 점들을 강제로 저장"""
        if self.current_points and self.current_image_path:
            image_name = os.path.basename(self.current_image_path)
            self.annotations[image_name] = self.current_points.copy()
            self.save_annotations()
            return self.get_current_image()
        return self.get_current_image()

# Gradio 인터페이스 생성
def create_interface():
    images_folder = "data/2_useful_images"
    annotator = PointAnnotator(images_folder)

    with gr.Blocks(title="차량 번호판 4점 어노테이션") as demo:
        gr.Markdown("# 차량 번호판 4점 어노테이션 도구")
        gr.Markdown("이미지를 클릭하여 번호판의 4개 모서리 점을 선택하세요.")

        with gr.Row():
            with gr.Column(scale=3):
                image_display = gr.Image(
                    label="이미지 (클릭하여 점 추가)",
                    type="numpy",
                    interactive=True
                )

            with gr.Column(scale=1):
                info_text = gr.Textbox(
                    label="정보",
                    lines=3,
                    interactive=False
                )

                with gr.Row():
                    prev_btn = gr.Button("← 이전", variant="secondary")
                    next_btn = gr.Button("다음 →", variant="secondary")

                clear_btn = gr.Button("점 삭제", variant="stop")
                save_btn = gr.Button("저장", variant="primary")

                progress_text = gr.Textbox(
                    label="진행상황",
                    value=f"전체 이미지: {len(annotator.image_files)}개",
                    interactive=False
                )

        # 이벤트 바인딩
        image_display.select(
            annotator.add_point,
            outputs=[image_display, info_text]
        )

        next_btn.click(
            annotator.next_image,
            outputs=[image_display, info_text]
        )

        prev_btn.click(
            annotator.prev_image,
            outputs=[image_display, info_text]
        )

        clear_btn.click(
            annotator.clear_points,
            outputs=[image_display, info_text]
        )

        save_btn.click(
            annotator.save_current,
            outputs=[image_display, info_text]
        )

        # 초기 이미지 로드
        demo.load(
            annotator.get_current_image,
            outputs=[image_display, info_text]
        )

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)