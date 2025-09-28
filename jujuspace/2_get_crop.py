import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import json
import os

class LicensePlateExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("차량 번호판 좌표 추출기")
        self.root.geometry("1600x1000")
        
        self.image = None
        self.image_path = None
        self.display_image = None
        self.perspective_image = None
        self.crop_zoom_image = None
        self.canvas = None
        self.perspective_canvas = None
        self.crop_zoom_canvas = None
        self.points = []
        self.dragging = False
        self.drag_index = -1
        self.scale_factor = 1.0
        
        # 좌표 입력 변수들
        self.coord_vars = []
        self.coord_entries = []
        
        # 확대 설정
        self.zoom_factor = 3.0
        self.crop_margin = 100  # 주변 영역 마진
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메뉴 프레임
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=10)
        
        tk.Button(menu_frame, text="이미지 불러오기", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="좌표 초기화", command=self.reset_points).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="좌표 저장", command=self.save_coordinates).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="좌표 불러오기", command=self.load_coordinates).pack(side=tk.LEFT, padx=5)
        tk.Button(menu_frame, text="Perspective 저장", command=self.save_perspective).pack(side=tk.LEFT, padx=5)
        
        # 메인 프레임 (좌우 분할)
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 왼쪽 프레임 (원본 이미지)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        
        tk.Label(left_frame, text="원본 이미지", font=("Arial", 12, "bold")).pack()
        
        self.canvas = tk.Canvas(left_frame, bg="gray")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # 오른쪽 프레임
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Perspective 변환 결과
        tk.Label(right_frame, text="Perspective 변환 결과 (880x440)", font=("Arial", 12, "bold")).pack()
        
        self.perspective_canvas = tk.Canvas(right_frame, bg="lightgray", width=880, height=440)
        self.perspective_canvas.pack(pady=5)
        
        # 확대된 crop 영역
        tk.Label(right_frame, text="선택 영역 확대보기 (3배 확대)", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        
        self.crop_zoom_canvas = tk.Canvas(right_frame, bg="lightblue", width=880, height=300)
        self.crop_zoom_canvas.pack(pady=5)
        
        # 좌표 입력 프레임
        coord_frame = tk.LabelFrame(right_frame, text="좌표 수정", font=("Arial", 10, "bold"))
        coord_frame.pack(fill=tk.X, pady=10)
        
        self.setup_coordinate_inputs(coord_frame)
        
        # 이벤트 바인딩
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
        # 좌표 정보 프레임
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        self.info_label = tk.Label(info_frame, text="좌표 정보: 이미지를 불러와주세요")
        self.info_label.pack()
        
        # 사용법 안내
        help_text = """
사용법:
1. '이미지 불러오기'로 블랙박스 이미지를 선택하세요
2. 번호판의 4개 모서리를 순서대로 클릭하세요 (좌상→우상→우하→좌하)
3. 점을 드래그하거나 우측 좌표 입력란에서 정확한 값을 입력하세요
4. 4개 점이 모두 설정되면 우측에 880x440 크기의 perspective 변환 결과와 3배 확대된 crop 영역이 표시됩니다
5. '좌표 저장' 또는 'Perspective 저장'으로 결과를 저장하세요
        """
        help_label = tk.Label(self.root, text=help_text, justify=tk.LEFT, font=("Arial", 9))
        help_label.pack(pady=5)
        
    def setup_coordinate_inputs(self, parent):
        """좌표 입력 위젯들 설정"""
        labels = ['1. 좌상단', '2. 우상단', '3. 우하단', '4. 좌하단']
        
        for i in range(4):
            frame = tk.Frame(parent)
            frame.pack(fill=tk.X, pady=2)
            
            tk.Label(frame, text=labels[i], width=10, anchor='w').pack(side=tk.LEFT)
            
            # X 좌표
            tk.Label(frame, text="X:").pack(side=tk.LEFT, padx=(5, 0))
            x_var = tk.StringVar()
            x_entry = tk.Entry(frame, textvariable=x_var, width=8)
            x_entry.pack(side=tk.LEFT, padx=(0, 5))
            x_var.trace('w', lambda *args, idx=i, coord='x': self.on_coordinate_change(idx, coord))
            
            # Y 좌표
            tk.Label(frame, text="Y:").pack(side=tk.LEFT)
            y_var = tk.StringVar()
            y_entry = tk.Entry(frame, textvariable=y_var, width=8)
            y_entry.pack(side=tk.LEFT, padx=(0, 5))
            y_var.trace('w', lambda *args, idx=i, coord='y': self.on_coordinate_change(idx, coord))
            
            # 적용 버튼
            apply_btn = tk.Button(frame, text="적용", 
                                command=lambda idx=i: self.apply_coordinate_change(idx))
            apply_btn.pack(side=tk.LEFT)
            
            self.coord_vars.append((x_var, y_var))
            self.coord_entries.append((x_entry, y_entry))
            
    def on_coordinate_change(self, index, coord):
        """좌표 입력값이 변경될 때 호출"""
        # 실시간 업데이트는 하지 않고, 적용 버튼을 눌렀을 때만 적용
        pass
        
    def apply_coordinate_change(self, index):
        """좌표 변경 적용"""
        try:
            x_str = self.coord_vars[index][0].get()
            y_str = self.coord_vars[index][1].get()
            
            if x_str and y_str:
                x = int(x_str)
                y = int(y_str)
                
                # 점이 이미 존재하는 경우 업데이트, 없으면 추가
                while len(self.points) <= index:
                    self.points.append([0, 0])
                    
                self.points[index] = [x, y]
                self.draw_points()
                self.update_perspective()
                self.update_crop_zoom()
                
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력해주세요.")
            
    def update_coordinate_inputs(self):
        """현재 점들의 좌표를 입력창에 반영"""
        for i in range(4):
            if i < len(self.points):
                self.coord_vars[i][0].set(str(self.points[i][0]))
                self.coord_vars[i][1].set(str(self.points[i][1]))
            else:
                self.coord_vars[i][0].set("")
                self.coord_vars[i][1].set("")
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.points = []
            self.update_coordinate_inputs()
            self.display_image_on_canvas()
            self.perspective_canvas.delete("all")
            self.crop_zoom_canvas.delete("all")
            
    def display_image_on_canvas(self):
        if self.image is None:
            return
            
        # 캔버스 크기에 맞게 이미지 스케일 조정
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_image_on_canvas)
            return
            
        img_height, img_width = self.image.shape[:2]
        
        # 스케일 팩터 계산
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        self.scale_factor = min(scale_w, scale_h) * 0.9  # 여백을 위해 0.9 곱함
        
        # 이미지 리사이즈
        new_width = int(img_width * self.scale_factor)
        new_height = int(img_height * self.scale_factor)
        
        resized_image = cv2.resize(self.image, (new_width, new_height))
        
        # PIL Image로 변환 후 PhotoImage로 변환
        pil_image = Image.fromarray(resized_image)
        self.display_image = ImageTk.PhotoImage(pil_image)
        
        # 캔버스에 이미지 표시
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                               image=self.display_image, anchor=tk.CENTER)
        
        self.draw_points()
        
    def screen_to_image_coords(self, screen_x, screen_y):
        """화면 좌표를 원본 이미지 좌표로 변환"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width = int(self.image.shape[1] * self.scale_factor)
        img_height = int(self.image.shape[0] * self.scale_factor)
        
        # 이미지가 캔버스 중앙에 위치하므로 오프셋 계산
        offset_x = (canvas_width - img_width) // 2
        offset_y = (canvas_height - img_height) // 2
        
        # 화면 좌표에서 이미지 내 좌표로 변환
        img_x = (screen_x - offset_x) / self.scale_factor
        img_y = (screen_y - offset_y) / self.scale_factor
        
        return int(img_x), int(img_y)
        
    def image_to_screen_coords(self, img_x, img_y):
        """원본 이미지 좌표를 화면 좌표로 변환"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_width = int(self.image.shape[1] * self.scale_factor)
        img_height = int(self.image.shape[0] * self.scale_factor)
        
        offset_x = (canvas_width - img_width) // 2
        offset_y = (canvas_height - img_height) // 2
        
        screen_x = img_x * self.scale_factor + offset_x
        screen_y = img_y * self.scale_factor + offset_y
        
        return int(screen_x), int(screen_y)
        
    def on_click(self, event):
        if self.image is None:
            return
            
        # 드래그할 점 찾기
        self.drag_index = self.find_nearest_point(event.x, event.y)
        
        if self.drag_index >= 0:
            self.dragging = True
        elif len(self.points) < 4:
            # 새로운 점 추가
            img_x, img_y = self.screen_to_image_coords(event.x, event.y)
            self.points.append([img_x, img_y])
            self.draw_points()
            self.update_coordinate_inputs()
            self.update_perspective()
            self.update_crop_zoom()
            
    def on_drag(self, event):
        if self.dragging and self.drag_index >= 0:
            img_x, img_y = self.screen_to_image_coords(event.x, event.y)
            self.points[self.drag_index] = [img_x, img_y]
            self.draw_points()
            self.update_coordinate_inputs()
            self.update_perspective()
            self.update_crop_zoom()
            
    def on_release(self, event):
        self.dragging = False
        self.drag_index = -1
        
    def on_double_click(self, event):
        if self.image is None:
            return
            
        point_index = self.find_nearest_point(event.x, event.y)
        if point_index >= 0:
            self.edit_point_coordinates(point_index)
            
    def find_nearest_point(self, x, y, threshold=20):
        """가장 가까운 점의 인덱스 반환"""
        for i, point in enumerate(self.points):
            screen_x, screen_y = self.image_to_screen_coords(point[0], point[1])
            distance = ((x - screen_x) ** 2 + (y - screen_y) ** 2) ** 0.5
            if distance <= threshold:
                return i
        return -1
        
    def edit_point_coordinates(self, index):
        """점의 좌표를 직접 입력으로 수정"""
        current_x, current_y = self.points[index]
        
        new_x = simpledialog.askinteger("X 좌표 수정", 
                                       f"점 {index+1}의 X 좌표 (현재: {current_x}):",
                                       initialvalue=current_x)
        if new_x is not None:
            new_y = simpledialog.askinteger("Y 좌표 수정", 
                                           f"점 {index+1}의 Y 좌표 (현재: {current_y}):",
                                           initialvalue=current_y)
            if new_y is not None:
                self.points[index] = [new_x, new_y]
                self.draw_points()
                self.update_coordinate_inputs()
                self.update_perspective()
                self.update_crop_zoom()
                
    def draw_points(self):
        """점들을 캔버스에 그리기"""
        if self.image is None:
            return
            
        # 기존 점들과 선들 제거 (이미지는 유지)
        items = self.canvas.find_all()
        for item in items:
            tags = self.canvas.gettags(item)
            if 'point' in tags or 'line' in tags or 'text' in tags:
                self.canvas.delete(item)
                
        # 점들 그리기
        colors = ['red', 'green', 'blue', 'yellow']
        labels = ['좌상', '우상', '우하', '좌하']
        
        for i, point in enumerate(self.points):
            screen_x, screen_y = self.image_to_screen_coords(point[0], point[1])
            
            # 점 그리기
            self.canvas.create_oval(screen_x-8, screen_y-8, screen_x+8, screen_y+8,
                                  fill=colors[i], outline='black', width=2, tags='point')
            
            # 라벨 그리기
            self.canvas.create_text(screen_x, screen_y-20, text=f"{i+1}.{labels[i]}",
                                  fill='white', font=('Arial', 10, 'bold'), tags='text')
                                  
        # 4개 점이 모두 있으면 사각형 그리기
        if len(self.points) == 4:
            for i in range(4):
                x1, y1 = self.image_to_screen_coords(self.points[i][0], self.points[i][1])
                x2, y2 = self.image_to_screen_coords(self.points[(i+1)%4][0], self.points[(i+1)%4][1])
                self.canvas.create_line(x1, y1, x2, y2, fill='cyan', width=2, tags='line')
                
        self.update_info()
        
    def update_perspective(self):
        """Perspective 변환 수행 및 표시"""
        if self.image is None or len(self.points) != 4:
            self.perspective_canvas.delete("all")
            return
            
        try:
            # 원본 점들 (시계방향: 좌상, 우상, 우하, 좌하)
            src_points = np.float32(self.points)
            
            # 목표 점들 (880x440 크기)
            dst_points = np.float32([
                [0, 0],         # 좌상
                [880, 0],       # 우상  
                [880, 440],     # 우하
                [0, 440]        # 좌하
            ])
            
            # Perspective 변환 매트릭스 계산
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            
            # Perspective 변환 적용
            self.perspective_image = cv2.warpPerspective(self.image, matrix, (880, 440))
            
            # PIL Image로 변환 후 PhotoImage로 변환
            pil_image = Image.fromarray(self.perspective_image)
            perspective_photo = ImageTk.PhotoImage(pil_image)
            
            # 캔버스에 표시
            self.perspective_canvas.delete("all")
            self.perspective_canvas.create_image(440, 220, image=perspective_photo, anchor=tk.CENTER)
            
            # 이미지 참조 유지 (가비지 컬렉션 방지)
            self.perspective_canvas.image = perspective_photo
            
        except Exception as e:
            print(f"Perspective 변환 오류: {e}")
            self.perspective_canvas.delete("all")
            self.perspective_canvas.create_text(440, 220, 
                                              text="Perspective 변환 실패\n점들이 올바르게 설정되었는지 확인하세요",
                                              fill='red', font=('Arial', 12), anchor=tk.CENTER)
                                              
    def update_crop_zoom(self):
        """선택된 영역의 확대된 crop 영역 표시"""
        if self.image is None or len(self.points) < 1:
            self.crop_zoom_canvas.delete("all")
            return
            
        try:
            # 모든 점들의 경계 상자 계산
            points_array = np.array(self.points)
            min_x = max(0, int(np.min(points_array[:, 0])) - self.crop_margin)
            max_x = min(self.image.shape[1], int(np.max(points_array[:, 0])) + self.crop_margin)
            min_y = max(0, int(np.min(points_array[:, 1])) - self.crop_margin)
            max_y = min(self.image.shape[0], int(np.max(points_array[:, 1])) + self.crop_margin)
            
            # crop 영역 추출
            crop_region = self.image[min_y:max_y, min_x:max_x].copy()
            
            if crop_region.size == 0:
                return
                
            # 확대
            zoom_height = int(crop_region.shape[0] * self.zoom_factor)
            zoom_width = int(crop_region.shape[1] * self.zoom_factor)
            zoomed_crop = cv2.resize(crop_region, (zoom_width, zoom_height), interpolation=cv2.INTER_CUBIC)
            
            # 캔버스 크기에 맞게 조정
            canvas_width = 880
            canvas_height = 300
            
            # 이미지가 캔버스보다 크면 다시 스케일 조정
            if zoom_width > canvas_width or zoom_height > canvas_height:
                scale_w = canvas_width / zoom_width
                scale_h = canvas_height / zoom_height
                scale = min(scale_w, scale_h) * 0.9
                
                final_width = int(zoom_width * scale)
                final_height = int(zoom_height * scale)
                zoomed_crop = cv2.resize(zoomed_crop, (final_width, final_height))
            
            # 확대된 이미지에서 점들의 위치 계산
            zoom_points = []
            crop_scale = self.zoom_factor
            
            # 캔버스 크기에 맞게 최종 스케일 조정된 경우 고려
            if zoom_width > canvas_width or zoom_height > canvas_height:
                scale_w = canvas_width / zoom_width
                scale_h = canvas_height / zoom_height
                final_scale = min(scale_w, scale_h) * 0.9
                crop_scale *= final_scale
            
            for point in self.points:
                # crop 영역 내에서의 상대 좌표
                rel_x = (point[0] - min_x) * crop_scale
                rel_y = (point[1] - min_y) * crop_scale
                zoom_points.append([rel_x, rel_y])
            
            # PIL Image로 변환
            self.crop_zoom_image = zoomed_crop
            pil_image = Image.fromarray(zoomed_crop)
            crop_photo = ImageTk.PhotoImage(pil_image)
            
            # 캔버스에 표시
            self.crop_zoom_canvas.delete("all")
            self.crop_zoom_canvas.create_image(canvas_width//2, canvas_height//2, 
                                             image=crop_photo, anchor=tk.CENTER)
            
            # 확대된 이미지에서 점들 그리기
            colors = ['red', 'green', 'blue', 'yellow']
            labels = ['1', '2', '3', '4']
            
            img_center_x = canvas_width // 2
            img_center_y = canvas_height // 2
            img_offset_x = img_center_x - zoomed_crop.shape[1] // 2
            img_offset_y = img_center_y - zoomed_crop.shape[0] // 2
            
            for i, zoom_point in enumerate(zoom_points):
                if i < len(self.points):
                    screen_x = zoom_point[0] + img_offset_x
                    screen_y = zoom_point[1] + img_offset_y
                    
                    # 점 그리기
                    self.crop_zoom_canvas.create_oval(screen_x-6, screen_y-6, screen_x+6, screen_y+6,
                                                    fill=colors[i], outline='black', width=2, tags='zoom_point')
                    
                    # 라벨 그리기
                    self.crop_zoom_canvas.create_text(screen_x, screen_y-15, text=labels[i],
                                                    fill='white', font=('Arial', 10, 'bold'), tags='zoom_text')
            
            # 4개 점이 모두 있으면 사각형 그리기
            if len(zoom_points) == 4:
                for i in range(4):
                    x1 = zoom_points[i][0] + img_offset_x
                    y1 = zoom_points[i][1] + img_offset_y
                    x2 = zoom_points[(i+1)%4][0] + img_offset_x
                    y2 = zoom_points[(i+1)%4][1] + img_offset_y
                    self.crop_zoom_canvas.create_line(x1, y1, x2, y2, fill='cyan', width=2, tags='zoom_line')
            
            # 이미지 참조 유지
            self.crop_zoom_canvas.image = crop_photo
            
        except Exception as e:
            print(f"Crop zoom 업데이트 오류: {e}")
            self.crop_zoom_canvas.delete("all")
            self.crop_zoom_canvas.create_text(440, 150, 
                                            text="확대 영역 표시 실패",
                                            fill='red', font=('Arial', 12), anchor=tk.CENTER)
        
    def update_info(self):
        """좌표 정보 업데이트"""
        if not self.points:
            self.info_label.config(text="좌표 정보: 번호판의 4개 모서리를 클릭하세요")
        else:
            info_text = f"좌표 정보 ({len(self.points)}/4): "
            for i, point in enumerate(self.points):
                info_text += f"점{i+1}({point[0]}, {point[1]}) "
            self.info_label.config(text=info_text)
            
    def reset_points(self):
        """모든 점 초기화"""
        self.points = []
        self.draw_points()
        self.update_coordinate_inputs()
        self.perspective_canvas.delete("all")
        self.crop_zoom_canvas.delete("all")
        
    def save_coordinates(self):
        """좌표를 JSON 파일로 저장"""
        if len(self.points) != 4:
            messagebox.showwarning("경고", "4개의 점이 모두 설정되어야 저장할 수 있습니다.")
            return
            
        if not self.image_path:
            messagebox.showwarning("경고", "이미지가 로드되지 않았습니다.")
            return
        
        # 이미지 파일명에서 확장자 제거하고 JSON 파일명 생성
        image_filename = os.path.basename(self.image_path)
        base_name = os.path.splitext(image_filename)[0]
        suggested_filename = f"{base_name}.json"
        
        # 폴더 선택 후 파일명 자동 생성
        save_dir = filedialog.askdirectory(title="저장할 폴더를 선택하세요")
        
        if save_dir:
            file_path = os.path.join(save_dir, suggested_filename)
            
            # 파일이 이미 존재하는 경우 확인
            if os.path.exists(file_path):
                result = messagebox.askyesno("파일 덮어쓰기", 
                                           f"'{suggested_filename}' 파일이 이미 존재합니다.\n덮어쓰시겠습니까?")
                if not result:
                    return
            
            data = {
                "image_path": self.image_path,
                "image_filename": os.path.basename(self.image_path) if self.image_path else None,
                "license_plate_coordinates": self.points,
                "image_size": [self.image.shape[1], self.image.shape[0]] if self.image is not None else None,
                "perspective_size": [880, 440],
                "created_timestamp": __import__('datetime').datetime.now().isoformat()
            }
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("완료", f"좌표가 저장되었습니다:\n{file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"파일 저장 중 오류가 발생했습니다: {str(e)}")
            
    def save_perspective(self):
        """Perspective 변환된 이미지 저장"""
        if self.perspective_image is None:
            messagebox.showwarning("경고", "Perspective 변환된 이미지가 없습니다.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Perspective 이미지 저장",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        
        if file_path:
            # RGB를 BGR로 변환해서 저장
            bgr_image = cv2.cvtColor(self.perspective_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, bgr_image)
            messagebox.showinfo("완료", f"Perspective 이미지가 저장되었습니다: {file_path}")
            
    def load_coordinates(self):
        """저장된 좌표 불러오기"""
        file_path = filedialog.askopenfilename(
            title="좌표 불러오기",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.points = data.get("license_plate_coordinates", [])
                
                # 저장된 이미지 경로 정보 표시
                saved_image_path = data.get("image_path", "")
                saved_filename = data.get("image_filename", "")
                
                if saved_image_path or saved_filename:
                    info_msg = f"좌표가 불러와졌습니다.\n"
                    if saved_filename:
                        info_msg += f"원본 파일명: {saved_filename}\n"
                    if saved_image_path:
                        info_msg += f"원본 경로: {saved_image_path}\n"
                    info_msg += "\n현재 이미지와 동일한지 확인하세요."
                    messagebox.showinfo("좌표 불러오기 완료", info_msg)
                
                self.draw_points()
                self.update_coordinate_inputs()
                self.update_perspective()
                self.update_crop_zoom()
                
            except Exception as e:
                messagebox.showerror("오류", f"좌표 파일을 불러오는 중 오류가 발생했습니다: {str(e)}")
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LicensePlateExtractor()
    app.run()