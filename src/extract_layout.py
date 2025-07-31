import cv2
import yaml
import numpy as np
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# --- 설정 파일 경로 ---
# 이제 이 스크립트는 수정할 필요가 없습니다.
FIELD_DEFINITIONS_DIR = "configs/field_definitions"
ASSETS_DIR = "assets/templates"
CONFIG_DIR = "configs"

class LayoutExtractor:
    """
    GUI를 통해 문서 이미지에서 필드 레이아웃을 추출하는 클래스.
    모든 상태와 로직을 캡슐화하여 코드 안정성을 높임.
    """
    def __init__(self, config, image_path, load_yaml_path):
        self.config = config
        self.image_path = image_path
        self.load_yaml_path = load_yaml_path
        
        self.window_name = "KDOCS_SYNTH Layout Extractor - [Hover + DEL] to Delete Fields"
        self.original_img = cv2.imread(self.image_path)
        if self.original_img is None:
            raise FileNotFoundError(f"Image not found at {self.image_path}")

        self.layouts = {"field_boxes": {}}
        self.points = []
        self.current_box = None # [수정됨] 드래그 중인 박스를 저장
        self.guide_xy = None
        self.detected_grid = []  # 검출된 격자선들
        self.show_grid = False
        self.column_guides = []  # 열 가이드라인들
        self.show_columns = False
        
        # 상태 관리 변수
        self.mode = "DRAW" # DRAW, EDIT, RENAME, MODIFY, INPUT, SELECT
        self.drawing = False
        self.show_sample = False
        self.show_crosshair = True  # 기본 활성화
        self.mouse_pos = (0, 0)
        self.field_being_modified = None
        self.field_to_rename = None
        self.input_text = ""
        self.suggestion_active = False
        
        # 필드 선택 리스트 관련
        self.field_list_visible = False
        self.field_list_scroll = 0
        self.field_list_selected = 0
        self.available_fields = self.config.get('fields', [])
        self.selected_field_name = None  # 리스트에서 선택된 필드명
        
        # Tab 순환 기능
        self.tab_cycling = False
        self.suggestion_index = 0 # [수정됨] 변수명 통일
        
        # 자동 저장 설정
        self.auto_save = True
        self.current_autosave_file = None  # 현재 자동저장 파일
        
        # 시각적 피드백 시스템
        self.feedback_message = ""
        self.feedback_timer = 0
        self.feedback_color = (255, 255, 255)
        
        # 자석 효과 (스냅) 설정
        self.snap_enabled = True
        self.snap_distance = 15  # 픽셀 단위
        
        # ESC 안전 처리
        self.esc_pressed_time = 0
        
        # 강화된 십자선 설정
        self.crosshair_enhanced = False
        self.crosshair_color = (0, 255, 0)  # 밝은 초록색 (더 잘 보임)
        self.crosshair_enhanced_color = (255, 0, 255)  # 밝은 보라색 (강조시)
        
        # 종료 확인 설정
        self.exit_confirmation = False
        self.exit_confirmation_timer = 0
        
        # 필드 이름 숨김 기능
        self.hide_field_names = False
        
        # 샘플 이미지 로드
        self.sample_img = self._load_sample_image()

        # 복사/붙여넣기 변수 추가
        self.copied_box = None  # (width, height) 형태로 저장

    def run(self):
        """ 메인 루프를 실행하여 프로그램을 시작합니다. """
        self._setup_window()
        self._load_initial_data()

        quit_flag = False
        try:
            while not quit_flag:
                # [수정됨] UI 업데이트 타이머 로직 추가
                if self.feedback_timer > 0:
                    self.feedback_timer -= 1
                if self.exit_confirmation and self.exit_confirmation_timer > 0:
                    self.exit_confirmation_timer -= 1
                    if self.exit_confirmation_timer == 0:
                        self.exit_confirmation = False
                        self._show_feedback("Exit Cancelled", (100, 255, 100))

                display_img = self._draw_ui()
                cv2.imshow(self.window_name, display_img)
                key = cv2.waitKey(20) & 0xFF

                if key == 255: continue # 키 입력이 없으면 루프 계속

                # 종료 확인 상태 처리
                if self.exit_confirmation:
                    if key == 27: # ESC
                        print("\n[i] Exit confirmed.")
                        quit_flag = True
                    else:
                        self.exit_confirmation = False
                        print("[i] Exit cancelled. Continue working.")
                        self._show_feedback("Exit Cancelled", (100, 255, 100))
                    continue

                # ESC 키 공통 처리
                if key == 27: # ESC
                    if self.field_list_visible:
                        self.field_list_visible = False
                        self._show_feedback("List Closed", (200, 200, 200))
                    elif self.mode in ["INPUT", "MODIFY"]:
                        self.mode = "DRAW"; self.input_text = ""; self.points = []; self.current_box = None
                        self._reset_tab_cycling()
                        self._show_feedback("Input Cancelled", (255, 200, 100))
                    else:
                        self._show_exit_confirmation()
                    continue

                # 모드별 키 처리
                if self.mode == "INPUT" and not self.field_list_visible:
                    self._handle_input_mode(key)
                elif self.field_list_visible:
                    quit_flag = self._handle_field_list_navigation(key)
                else:
                    quit_flag = self._handle_command_mode(key)
                
        except KeyboardInterrupt:
            print("\n[i] Ctrl+C pressed. Exiting...")
            quit_flag = True
        except Exception as e:
            print(f"\n[!] Unexpected error: {e}")
            import traceback
            traceback.print_exc() # [추가됨] 디버깅을 위한 상세 에러 로그
            quit_flag = True
        finally:
            # Ctrl+Q로 종료한 경우 저장하지 않음
            if not hasattr(self, 'exit_without_save') or not self.exit_without_save:
            # 정상 종료 시 최종 저장
            self._save_layouts()
            if self.current_autosave_file and os.path.exists(os.path.join(CONFIG_DIR, self.current_autosave_file)):
                print(f"\n[i] Work also saved in autosave file: {self.current_autosave_file}")
                print(f"[i] You can load this file next time if needed.")
            else:
                print("\n[i] Exited without saving.")
            cv2.destroyAllWindows()


    def _load_sample_image(self):
        """ 작업 중인 문서 종류에 맞는 샘플 이미지를 찾아서 로드합니다. """
        doc_folder = self.config.get('template_folder', '')
        sample_filenames = [f"{doc_folder}_filled_sample.jpg", f"{doc_folder}_filled_sample1.jpg", f"GA_filled_sample1.jpg"]
        
        search_paths = [os.path.join("assets", "samples"), os.path.join(ASSETS_DIR, doc_folder)]

        for path in search_paths:
            for filename in sample_filenames:
                sample_path = os.path.join(path, filename)
                if os.path.exists(sample_path):
                    sample_img = cv2.imread(sample_path)
                    if sample_img is not None:
                        h, w, _ = self.original_img.shape
                        resized_img = cv2.resize(sample_img, (w, h))
                        print(f"\n[i] Sample image loaded: {sample_path}")
                        return resized_img
        
        print(f"\n[i] Note: No sample image found for '{doc_folder}'. Overlay feature will be disabled.")
        return None

    def _setup_window(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self._mouse_callback_wrapper)
        
        h, w, _ = self.original_img.shape
        screen_h, screen_w = 1000, 1800
        
        scale = min(screen_w / w, screen_h / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        
        cv2.resizeWindow(self.window_name, new_w, new_h)
        print(f"[i] Window resized to {new_w}x{new_h} (scale: {scale:.2f})")

    def _mouse_callback_wrapper(self, event, x, y, flags, param):
        """마우스 콜백을 클래스 메서드로 래핑합니다."""
        self._mouse_callback(event, x, y, flags, param)

    def _mouse_callback(self, event, x, y, flags, param):
        self.mouse_pos = (x, y) # 항상 마우스 위치 업데이트

        if self.mode not in ["DRAW", "MODIFY"]:
            # 편집/리네임 모드에서 클릭 처리
            if event == cv2.EVENT_LBUTTONDOWN:
                field = self._get_hovered_field()
                if not field: return

                if self.mode == "EDIT":
                    self.mode = "MODIFY"
                    self.field_being_modified = field
                    self._show_feedback(f"Modify '{field}'. Draw new box.", (0, 255, 255))
                elif self.mode == "RENAME":
                    self.mode = "INPUT"
                    self.field_to_rename = field
                    self.input_text = field
                    self._show_feedback(f"Renaming '{field}'...", (255, 255, 0))
            return

        # 드래그 시작
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.points = [(x, y)]
            self.current_box = [self.points[0], self.points[0]]

        # 드래그 중
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.current_box[1] = (x, y)

        # 드래그 종료
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.current_box[1] = (x, y)
                self._on_box_drawn() # 박스 그리기 완료 처리

    def _snap_to_grid(self, x, y):
        # 스냅 로직 (가장 가까운 선 또는 점에 붙임)
        snap_x, snap_y = x, y
        min_dist_x, min_dist_y = self.snap_distance, self.snap_distance

        # 기존 박스의 모서리에 스냅
        for p in self.layouts["field_boxes"].values():
            for px in [p[0], p[2]]:
                if abs(x - px) < min_dist_x:
                    min_dist_x = abs(x - px)
                    snap_x = px
            for py in [p[1], p[3]]:
                if abs(y - py) < min_dist_y:
                    min_dist_y = abs(y - py)
                    snap_y = py
        
        return snap_x, snap_y

    def _load_initial_data(self):
        if self.load_yaml_path and os.path.exists(self.load_yaml_path):
            try:
                with open(self.load_yaml_path, 'r', encoding='utf-8') as f:
                    loaded_data = yaml.safe_load(f)
                    if 'field_boxes' in loaded_data:
                        self.layouts['field_boxes'] = loaded_data['field_boxes']
                        print(f"\n[i] Successfully loaded {len(self.layouts['field_boxes'])} fields from '{self.load_yaml_path}'")
            except Exception as e:
                print(f"\n[!] Warning: Could not load or parse YAML file: {e}")
    
    def _get_status_text(self):
        status_map = {
            "DRAW": "MODE: DRAW - Drag to create a box",
            "INPUT": f"MODE: INPUT - Naming field... '{self.input_text}'",
            "EDIT": "MODE: EDIT - Click a box to select, then DEL to delete",
            "RENAME": "MODE: RENAME - Click a box to rename",
            "MODIFY": f"MODE: MODIFY - Draw new box for '{self.field_being_modified}'"
        }
        return status_map.get(self.mode, "MODE: UNKNOWN")

    def _draw_ui(self):
        if self.show_sample and self.sample_img is not None:
            display_img = cv2.addWeighted(self.original_img, 0.5, self.sample_img, 0.5, 0)
        else:
            display_img = self.original_img.copy()

        h, w, _ = display_img.shape

        if self.show_crosshair:
            color = self.crosshair_enhanced_color if self.crosshair_enhanced else self.crosshair_color
            thickness = 2 if self.crosshair_enhanced else 1
            cv2.line(display_img, (self.mouse_pos[0], 0), (self.mouse_pos[0], h), color, thickness)
            cv2.line(display_img, (0, self.mouse_pos[1]), (w, self.mouse_pos[1]), color, thickness)
            if self.crosshair_enhanced:
                cv2.circle(display_img, self.mouse_pos, 5, color, 2)

        for name, p in self.layouts["field_boxes"].items():
            is_hovered = p[0] <= self.mouse_pos[0] <= p[2] and p[1] <= self.mouse_pos[1] <= p[3]
            
            if name == self.field_being_modified:
                box_color, text_color, thickness = (0, 255, 255), (0, 255, 255), 4
            elif is_hovered and self.mode == "EDIT":
                box_color, text_color, thickness = (255, 0, 0), (255, 255, 255), 3  # 빨간색으로 선택 가능 표시
            elif is_hovered:
                box_color, text_color, thickness = (255, 100, 255), (255, 255, 255), 3
            else:
                box_color, text_color, thickness = (0, 255, 0), (0, 255, 0), 2
            
            cv2.rectangle(display_img, (p[0], p[1]), (p[2], p[3]), box_color, thickness)
            
            # 필드 이름 숨김 기능
            if not self.hide_field_names:
                text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(display_img, (p[0], p[1] - 25), (p[0] + text_size[0] + 4, p[1] - 5), (0, 0, 0), -1)
                cv2.putText(display_img, name, (p[0] + 2, p[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            
            if is_hovered:
                hint_text = f"[DEL] to delete '{name}'"
                hint_size = cv2.getTextSize(hint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(display_img, (p[0], p[3] + 5), (p[0] + hint_size[0] + 4, p[3] + 25), (0, 0, 0), -1)
                cv2.putText(display_img, hint_text, (p[0] + 2, p[3] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # [수정됨] 현재 그리는 박스 (드래그 중) - 실시간 표시
        if self.drawing and self.current_box and len(self.current_box) == 2:
            p1, p2 = self.current_box
            # 박스가 유효한지 확인
            if p1 and p2 and p1 != p2:
                cv2.rectangle(display_img, p1, p2, (255, 0, 0), 2)  # 파란색으로 드래그 중인 박스 표시

        # [수정됨] _on_box_drawn 호출 로직 제거
        # 그리기 관련 로직은 mouse_callback으로 모두 이동함
        
        # [추가됨] 상태 및 피드백 메시지 표시
        status_text = self._get_status_text()
        hide_status = " [HIDE: ON]" if self.hide_field_names else ""
        status_text += hide_status
        cv2.rectangle(display_img, (10, 10), (w - 10, 40), (0, 0, 0), -1)
        cv2.putText(display_img, status_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if self.feedback_timer > 0 and self.feedback_message:
            feedback_size = cv2.getTextSize(self.feedback_message, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(display_img, (10, h - 40), (10 + feedback_size[0] + 20, h - 10), (0, 0, 0), -1)
            cv2.putText(display_img, self.feedback_message, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.feedback_color, 2)

        if self.field_list_visible:
            self._draw_field_list(display_img, w, h)
        
        if self.exit_confirmation:
            self._draw_exit_confirmation(display_img, w, h)

        return display_img

    def _on_box_drawn(self):
        if not self.current_box: return # [추가됨] 박스가 없으면 아무것도 안 함
        
        p1, p2 = self.current_box
        x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
        x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
        
        # [수정됨] 박스가 너무 작으면 무시
        if abs(x1-x2) < 5 or abs(y1-y2) < 5:
            print("Box is too small, ignored.")
            self.points = []; self.current_box = None
            return

        self.points = [(x1,y1), (x2,y2)] # 정규화된 좌표 저장

        if self.mode == "MODIFY":
            field_name = self.field_being_modified
            self.layouts["field_boxes"][field_name] = [x1, y1, x2, y2]
            print(f"Updated field '{field_name}'")
            self.field_being_modified = None
            self.mode = "DRAW"
            self._auto_save()
        else: # DRAW 모드
            if self.selected_field_name:
                field_name = self.selected_field_name
                self.layouts["field_boxes"][field_name] = [x1, y1, x2, y2]
                print(f"Saved field '{field_name}' (from list selection)")
                self.selected_field_name = None
                self._auto_save()
            else:
                self._start_tab_cycling()
                self.mode = "INPUT"
        
        self.current_box = None # 박스 처리 후 초기화

    def _start_tab_cycling(self):
        """TAB 순환 시작 - 전진/후진 모두 지원"""
        self.unused_fields = [f for f in self.available_fields if f not in self.layouts['field_boxes']]
        if self.unused_fields:
            self.tab_cycling = True
            self.suggestion_index = 0
            self.input_text = self.unused_fields[0]
            self.suggestion_active = True
            print(f"Tab cycling started: {self.input_text} (1/{len(self.unused_fields)}) - TAB:Next, Shift+TAB:Prev")
            self._show_feedback(f"TAB Cycling: {self.input_text} (1/{len(self.unused_fields)})", (255, 255, 100), 120)
        else:
            self.input_text = "" # [수정됨] 제안할 필드가 없을 때 빈 문자열로 시작
            print("No unused fields available for tab cycling")
            self._show_feedback("No More Fields Available", (255, 100, 100))

    def _cycle_to_next_field(self, direction=1):
        """필드 순환 - direction: 1(앞으로), -1(뒤로)"""
        if self.unused_fields and self.tab_cycling:
            self.suggestion_index = (self.suggestion_index + direction + len(self.unused_fields)) % len(self.unused_fields)
            self.input_text = self.unused_fields[self.suggestion_index]
            current_pos = self.suggestion_index + 1
            direction_text = "→" if direction == 1 else "←"
            print(f"Tab cycling {direction_text}: {self.input_text} ({current_pos}/{len(self.unused_fields)})")
            self._show_feedback(f"{direction_text} {self.input_text} ({current_pos}/{len(self.unused_fields)})", (255, 255, 100), 60)

    def _handle_input_mode(self, key):
        if key == 13: # Enter
            new_name = self.input_text
            if not new_name:
                print("Error: Field name cannot be empty. Cancelling.")
                self.mode = "DRAW"; self.input_text = ""; self.points = []
                self._reset_tab_cycling()
                return

            if self.field_to_rename:
                if new_name != self.field_to_rename:
                    self.layouts["field_boxes"][new_name] = self.layouts["field_boxes"].pop(self.field_to_rename)
                    print(f"Renamed '{self.field_to_rename}' to '{new_name}'")
                    self._show_feedback(f"Renamed: {new_name}", (100, 255, 100))
                self.field_to_rename = None
            else:
                x1, y1 = self.points[0]; x2, y2 = self.points[1]
                self.layouts["field_boxes"][new_name] = [x1, y1, x2, y2]
                print(f"Saved field '{new_name}'")
                self._show_feedback(f"Saved: {new_name}", (100, 255, 100))
            
            self._auto_save()
            self.mode = "DRAW"; self.input_text = ""; self.points = []
            self._reset_tab_cycling()

        elif key == 8: # Backspace
            if self.suggestion_active:
                self.input_text = ""; self.suggestion_active = False
            else:
                self.input_text = self.input_text[:-1]
        
        elif key == 9: # Tab
            self._cycle_to_next_field(1) if self.tab_cycling else self._start_tab_cycling()
        
        elif key == 25 or key == 353 or key == ord('`'): # Shift+Tab or Backtick
            self._cycle_to_next_field(-1) if self.tab_cycling else self._start_tab_cycling()

        elif 32 <= key <= 126: # Printable ASCII
            # SHIFT 키 감지 및 대문자 처리
            if 65 <= key <= 90:  # A-Z (대문자)
                char = chr(key)
            elif 97 <= key <= 122:  # a-z (소문자)
                char = chr(key).upper()  # 소문자를 대문자로 변환
            else:
                char = chr(key)  # 기타 문자는 그대로
            
            if self.suggestion_active:
                self.input_text = char; self.suggestion_active = False
                self._reset_tab_cycling()
            else:
                self.input_text += char
    
    def _reset_tab_cycling(self):
        self.tab_cycling = False
        self.suggestion_index = 0
        self.unused_fields = []
        self.suggestion_active = False

    def _show_exit_confirmation(self):
        self.exit_confirmation = True
        self.exit_confirmation_timer = 300
        print("\n[CONFIRMATION] Press ESC again to exit, or any other key to continue.")

    def _handle_command_mode(self, key):
        # Ctrl+Q: 저장하지 않고 종료
        if key == 17:  # Ctrl+Q (Ctrl=17)
            print("\n[EXIT] Exiting without saving...")
            self.exit_without_save = True
            return True
        
        if key in [ord('q'), ord('Q')]:
            self._show_exit_confirmation()
            return False
        
        key_map = {
            'r': self._reset_box, 'c': self._copy_box, 'v': self._paste_box,
            'l': self._clear_guide, 'e': self._toggle_edit_mode, 't': self._toggle_rename_mode,
            's': self._toggle_sample, 'x': self._toggle_crosshair, 'u': self._undo,
            46: self._delete_hovered, 127: self._delete_hovered, 8: self._delete_hovered, # DEL key (여러 키 코드 지원)
            'i': self._save_annotated_image, # [변경됨] 단축키 'v' -> 'i'
            'g': self._toggle_grid, 'h': self._toggle_field_names, # H: 필드 이름 토글
            32: self._show_field_list, # Space key
            'z': self._toggle_snap
        }
        
        action = key_map.get(key) or key_map.get(chr(key).lower())
        if action:
            action()
        else:
            # DEL 키 디버깅을 위해 키 코드 출력
            if key in [46, 127, 8]:
                print(f"[DEBUG] DEL key pressed with code: {key}")
                self._delete_hovered()
        return False
    
    # [리팩토링] 커맨드 함수 분리
    def _reset_box(self):
        self.points = []; self.current_box = None
        print("Reset: Current box cleared.")
        self._show_feedback("Box Reset", (255, 200, 100))
    def _copy_box(self):
        copied_field = self._get_hovered_field()
        if copied_field:
            p = self.layouts["field_boxes"][copied_field]
            self.copied_box = (p[2] - p[0], p[3] - p[1])
            print(f"COPIED: '{copied_field}' size ({self.copied_box[0]}x{self.copied_box[1]})")
            self._show_feedback(f"Copied: {copied_field} ({self.copied_box[0]}x{self.copied_box[1]})", (100, 255, 255), 60)
        else: self._show_feedback("No field under cursor to copy", (200, 200, 200))
    def _paste_box(self):
        if self.copied_box and self.mouse_pos:
            width, height = self.copied_box; x, y = self.mouse_pos
            self.current_box = [(x, y), (x + width, y + height)]
            self.drawing = False
            self._on_box_drawn()
            self._show_feedback(f"Pasted: {width}x{height}", (255, 255, 100), 60)
        elif not self.copied_box: self._show_feedback("No box copied yet", (200, 200, 200))
    def _clear_guide(self):
        self.guide_xy = None
        print("Clear: Grid guide removed.")
        self._show_feedback("Guide Cleared", (255, 200, 100))
    def _toggle_mode(self, mode_name):
        current_mode_attr = f"is_{mode_name.lower()}_mode"
        target_mode = mode_name.upper()
        
        if self.mode == target_mode:
            self.mode = "DRAW"
            status = "OFF"
        else:
            self.mode = target_mode
            status = "ON"
        print(f"{mode_name} mode: {status}")
        self._show_feedback(f"{mode_name} Mode: {status}", (100, 200, 255))
    def _toggle_edit_mode(self): self._toggle_mode("Edit")
    def _toggle_rename_mode(self): self._toggle_mode("Rename")
    def _toggle_sample(self):
        if self.sample_img is not None:
            self.show_sample = not self.show_sample
            self._show_feedback(f"Sample: {'ON' if self.show_sample else 'OFF'}", (255, 150, 255))
        else: self._show_feedback("No Sample Available", (255, 100, 100))
    def _toggle_crosshair(self):
        self.show_crosshair = not self.show_crosshair
        self._show_feedback(f"Crosshair: {'ON' if self.show_crosshair else 'OFF'}", (255, 255, 100))
    def _undo(self):
        if self.layouts["field_boxes"]:
            last_field = list(self.layouts["field_boxes"].keys())[-1]
            del self.layouts["field_boxes"][last_field]
            print(f"UNDO: Removed '{last_field}'")
            self._show_feedback(f"Undone: {last_field}", (255, 100, 100))
            self._auto_save()
        else: self._show_feedback("Nothing to Undo", (200, 200, 200))
    def _delete_hovered(self):
        # EDIT 모드에서는 선택된 필드를 삭제
        if self.mode == "EDIT" and self.field_being_modified:
            deleted_field = self.field_being_modified
            del self.layouts["field_boxes"][deleted_field]
            print(f"DELETED: Removed '{deleted_field}' (from EDIT mode)")
            self._show_feedback(f"Deleted: {deleted_field}", (255, 50, 50), 60)
            self.field_being_modified = None
            self.mode = "DRAW"
            self._auto_save()
        else:
            # 일반 모드에서는 마우스가 올라간 필드를 삭제
            deleted_field = self._get_hovered_field()
            if deleted_field:
                del self.layouts["field_boxes"][deleted_field]
                print(f"DELETED: Removed '{deleted_field}'")
                self._show_feedback(f"Deleted: {deleted_field}", (255, 50, 50), 60)
                self._auto_save()
            else: 
                self._show_feedback("No Field to Delete", (200, 200, 200))
    def _save_annotated_image(self): # 단축키 'i'
        self._save_annotated_image_file()
        self._show_feedback("Image Saved", (100, 255, 100))
    def _toggle_grid(self):
        if not self.detected_grid: self._detect_table_grid()
        if self.detected_grid:
            self.show_grid = not self.show_grid
            self._show_feedback(f"Grid: {'ON' if self.show_grid else 'OFF'}", (200, 255, 200))
    def _toggle_columns(self): # 미구현 기능
        print("Column guides feature is not fully implemented.")
    def _toggle_snap(self):
        self.snap_enabled = not self.snap_enabled
        self._show_feedback(f"Snap: {'ON' if self.snap_enabled else 'OFF'}", (255, 200, 0))

    def _toggle_field_names(self):
        self.hide_field_names = not self.hide_field_names
        self._show_feedback(f"Field Names: {'HIDDEN' if self.hide_field_names else 'SHOWN'}", (255, 150, 255))

    def _detect_table_grid(self):
        """이미지에서 테이블 격자선을 자동으로 검출합니다."""
        print("\n[i] Detecting table grid lines...")
        
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        # 조명 변화에 더 강한 적응형 스레시홀드 사용
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # --- 수평선 검출 ---
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        h_lines = cv2.HoughLinesP(detect_horizontal, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        # --- 수직선 검출 ---
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        v_lines = cv2.HoughLinesP(detect_vertical, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        self.detected_grid = []
        if h_lines is not None:
            for line in h_lines:
                x1, y1, x2, y2 = line[0]
                self.detected_grid.append(('horizontal', y1, x1, x2))
        if v_lines is not None:
            for line in v_lines:
                x1, y1, x2, y2 = line[0]
                self.detected_grid.append(('vertical', x1, y1, y2))
        
        self.show_grid = bool(self.detected_grid)
        
        if self.detected_grid:
            h_count = len(h_lines) if h_lines is not None else 0
            v_count = len(v_lines) if v_lines is not None else 0
            print(f"[i] Detected {h_count} horizontal + {v_count} vertical lines. Grid overlay activated.")
        else:
            print("[!] No clear grid lines detected.")

    def _get_hovered_field(self):
        for name, p in self.layouts["field_boxes"].items():
            if p[0] <= self.mouse_pos[0] <= p[2] and p[1] <= self.mouse_pos[1] <= p[3]:
                return name
        return None

    def _handle_field_list_navigation(self, key):
        used_fields = set(self.layouts['field_boxes'].keys())
        available_unused = [field for field in self.available_fields if field not in used_fields]
        
        if not available_unused:
            self.field_list_visible = False; return False
            
        if key == 13: # Enter
            if 0 <= self.field_list_selected < len(available_unused):
                selected = available_unused[self.field_list_selected]
                self.field_list_visible = False
                self._select_field_for_box(selected)
                self._show_feedback(f"Selected: {selected}", (100, 255, 100))
            return False
        elif key in [ord('w'), 82]: # W or Up Arrow
            self.field_list_selected = max(0, self.field_list_selected - 1)
            self._update_field_scroll(available_unused)
        elif key in [ord('s'), 84]: # S or Down Arrow
            self.field_list_selected = min(len(available_unused) - 1, self.field_list_selected + 1)
            self._update_field_scroll(available_unused)
        elif key in [ord('q'), ord('Q')]:
            return True # Quit
        return False
    
    def _update_field_scroll(self, available_fields):
        visible_count = 18
        if self.field_list_selected < self.field_list_scroll:
            self.field_list_scroll = self.field_list_selected
        elif self.field_list_selected >= self.field_list_scroll + visible_count:
            self.field_list_scroll = self.field_list_selected - visible_count + 1
    
    def _select_field_for_box(self, field_name):
        print(f"Selected field '{field_name}'. Now draw a box for this field.")
        self.selected_field_name = field_name
        self.mode = "DRAW"

    def _show_field_list(self):
        self.field_list_visible = True
        self.field_list_scroll = 0
        self.field_list_selected = 0
        self._show_feedback("Field List Opened", (100, 255, 255))
        print("Field list opened. Use W/S/Arrows to navigate, Enter to select, ESC to close.")

    def _show_feedback(self, message, color=(100, 255, 100), duration=60):
        self.feedback_message = message
        self.feedback_color = color
        self.feedback_timer = duration
    
    def _auto_save(self):
        if not self.layouts["field_boxes"] or not self.auto_save: return
        try:
            image_filename = os.path.basename(self.image_path)
            base_name = os.path.splitext(image_filename)[0]
            
            if self.current_autosave_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.current_autosave_file = f"{base_name}_autosave_{timestamp}.yaml"
            
            auto_save_path = os.path.join(CONFIG_DIR, self.current_autosave_file)
            
            # 필드 정의 파일의 순서대로 정렬
            sorted_field_boxes = {}
            if 'fields' in self.config:
                for field_name in self.config['fields']:
                    if field_name in self.layouts["field_boxes"]:
                        sorted_field_boxes[field_name] = self.layouts["field_boxes"][field_name]
            
            # 정의되지 않은 필드들도 추가
            for field_name, coords in self.layouts["field_boxes"].items():
                if field_name not in sorted_field_boxes:
                    sorted_field_boxes[field_name] = coords
            
            save_layouts = {'field_boxes': sorted_field_boxes}
            save_layouts['meta'] = {
                'source_image': image_filename,
                'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'doc_type': self.config.get('doc_type', 'UNKNOWN'),
                'auto_save': True,
                'field_count': len(self.layouts["field_boxes"])
            }
            
            with open(auto_save_path, 'w', encoding='utf-8') as f:
                yaml.dump(save_layouts, f, allow_unicode=True, sort_keys=False, indent=4)
            
            print(f"[AUTO-SAVE] {len(self.layouts['field_boxes'])} fields -> {self.current_autosave_file}")
        except Exception as e:
            print(f"[AUTO-SAVE ERROR] {e}")

    def _save_layouts(self):
        if not self.layouts["field_boxes"]:
            print("\nNo layout data was created. Nothing to save.")
            return

        try:
            image_filename = os.path.basename(self.image_path)
            base_name = os.path.splitext(image_filename)[0]
            output_filename = f"{base_name}_layout.yaml"
            output_path = os.path.join(CONFIG_DIR, output_filename)

            # 필드 정의 파일의 순서대로 정렬
            sorted_field_boxes = {}
            if 'fields' in self.config:
                for field_name in self.config['fields']:
                    if field_name in self.layouts["field_boxes"]:
                        sorted_field_boxes[field_name] = self.layouts["field_boxes"][field_name]
            
            # 정의되지 않은 필드들도 추가
            for field_name, coords in self.layouts["field_boxes"].items():
                if field_name not in sorted_field_boxes:
                    sorted_field_boxes[field_name] = coords

            self.layouts['meta'] = {
                'source_image': image_filename,
                'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'doc_type': self.config.get('doc_type', 'UNKNOWN'),
                'field_count': len(self.layouts["field_boxes"])
            }
            
            # 정렬된 필드 박스로 저장
            save_data = {'field_boxes': sorted_field_boxes, 'meta': self.layouts['meta']}
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(save_data, f, allow_unicode=True, sort_keys=False, indent=4)
            print(f"\nLayout data successfully saved to '{output_path}' (sorted by field definition order)")
        except Exception as e:
            print(f"\n[!] Error saving layouts: {e}")
    
    def _save_annotated_image_file(self):
        if not self.layouts["field_boxes"]:
            print("No fields to save in image."); return
        
        # [수정됨] UI 요소(피드백 등)를 제외한 순수 주석 이미지를 만들기 위해 별도 렌더링
        clean_img = self.original_img.copy()
        for name, p in self.layouts["field_boxes"].items():
            cv2.rectangle(clean_img, (p[0], p[1]), (p[2], p[3]), (0, 255, 0), 2)
            text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(clean_img, (p[0], p[1] - 25), (p[0] + text_size[0] + 4, p[1] - 5), (0, 0, 0), -1)
            cv2.putText(clean_img, name, (p[0] + 2, p[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        image_filename = os.path.basename(self.image_path)
        base_name = os.path.splitext(image_filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{base_name}_annotated_{timestamp}.jpg"
        output_path = os.path.join("assets/results", output_filename) # [변경됨] 저장 경로 명확화
        os.makedirs("assets/results", exist_ok=True)
        
        success = cv2.imwrite(output_path, clean_img)
        if success:
            print(f"\nAnnotated image saved to '{output_path}'")
        else:
            print(f"\nError: Failed to save annotated image to '{output_path}'")
    
# [수정] 아래 함수 전체를 복사하여 기존 코드를 대체해주세요.
def _detect_table_grid(self):
    """ 이미지에서 테이블 격자선을 자동으로 검출합니다. """
    print("\n[i] Detecting table grid lines...")
    
    gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
    # 조명 변화에 더 강한 적응형 스레시홀드 사용
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # --- 수평선 검출 ---
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    h_lines = cv2.HoughLinesP(detect_horizontal, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    
    # --- 수직선 검출 ---
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    v_lines = cv2.HoughLinesP(detect_vertical, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    
    self.detected_grid = []
    if h_lines is not None:
        for line in h_lines:
            x1, y1, x2, y2 = line[0]
            self.detected_grid.append(('horizontal', y1, x1, x2))
    if v_lines is not None:
        for line in v_lines:
            x1, y1, x2, y2 = line[0]
            self.detected_grid.append(('vertical', x1, y1, y2))
    
    self.show_grid = bool(self.detected_grid)
    
    if self.detected_grid:
        # [수정됨] NumPy 배열의 진리값 오류를 해결하기 위해 명시적으로 None을 확인합니다.
        h_count = len(h_lines) if h_lines is not None else 0
        v_count = len(v_lines) if v_lines is not None else 0
        print(f"[i] Detected {h_count} horizontal + {v_count} vertical lines. Grid overlay activated.")
    else:
        print("[!] No clear grid lines detected.")

def _draw_field_list(self, img, w, h):
    list_w, list_h = 500, 600
    start_x, start_y = (w - list_w) // 2, (h - list_h) // 2
    
    overlay = img.copy()
    cv2.rectangle(overlay, (start_x, start_y), (start_x + list_w, start_y + list_h), (50, 50, 50), -1)
    cv2.addWeighted(overlay, 0.9, img, 0.1, 0, dst=img)
    cv2.rectangle(img, (start_x, start_y), (start_x + list_w, start_y + list_h), (200, 200, 200), 3)

    cv2.putText(img, "Field Selection (W/S/Arrows, Enter, ESC)", (start_x + 10, start_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    
    available_unused = [f for f in self.available_fields if f not in self.layouts['field_boxes']]
    
    if not available_unused:
        cv2.putText(img, "All fields have been used!", (start_x + 50, start_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
        return

    visible_count = 18
    y_offset = 80
    for i in range(visible_count):
        field_idx = i + self.field_list_scroll
        if field_idx >= len(available_unused): break
        
        field_name = available_unused[field_idx]
        y_pos = start_y + y_offset + i * 25
        
        if field_idx == self.field_list_selected:
            cv2.rectangle(img, (start_x + 5, y_pos - 15), (start_x + list_w - 5, y_pos + 5), (100, 150, 100), -1)
            text_color = (0, 0, 0)
        else:
            text_color = (255, 255, 255)
        
        cv2.putText(img, field_name, (start_x + 15, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

def _print_instructions(self):
    print("--- KDOCS_SYNTH Layout Extractor (User-Friendly Version) ---")
    print(f"\n[i] Processing Image: {os.path.basename(self.image_path)}")
    print(f"[i] Available Fields: {len(self.available_fields)}")
    print("\n[Quick Start Guide]")
    print(" 1. Drag mouse to draw a box.")
    print(" 2. Type field name or use TAB to cycle, then press Enter.")
    print(" 3. Hover over a box and press DEL to delete.")
    print("\n[Key Controls]")
    print(" C/V: Copy/Paste Size | Z: Toggle Snap | U: Undo")
    print(" E: Edit Mode | T: Rename Mode | S: Toggle Sample")
    print(" X: Toggle Crosshair | G: Toggle Grid | R: Reset Drawing")
    print(" I: Save Image | DEL: Delete Field | ESC/Q: Exit") # [수정됨] 'V' -> 'I'
    print("----------------------------------------------------")

def _auto_initialize(self):
    """자동 초기화를 수행합니다."""
    if self.original_img is not None:
        self._detect_table_grid()

def _draw_exit_confirmation(self, img, w, h):
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, dst=img)
    
    dialog_w, dialog_h = 600, 300
    start_x, start_y = (w - dialog_w) // 2, (h - dialog_h) // 2
    
    cv2.rectangle(img, (start_x, start_y), (start_x + dialog_w, start_y + dialog_h), (40, 40, 40), -1)
    cv2.rectangle(img, (start_x, start_y), (start_x + dialog_w, start_y + dialog_h), (255, 255, 255), 5)
    
    cv2.putText(img, "EXIT CONFIRMATION", (start_x + 30, start_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 100), 3)
    field_count = len(self.layouts["field_boxes"])
    cv2.putText(img, f"Fields created: {field_count}", (start_x + 30, start_y + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
    cv2.putText(img, "Are you sure you want to exit?", (start_x + 30, start_y + 190), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, "ESC: Confirm Exit  |  Any key: Cancel", (start_x + 30, start_y + 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)


# [수정됨] 마우스 콜백 로직 (드래그-앤-드롭)
def _mouse_callback(self, event, x, y, flags, param):
    self.mouse_pos = (x, y) # 항상 마우스 위치 업데이트

    if self.mode not in ["DRAW", "MODIFY"]:
            # [추가됨] 편집/리네임 모드에서 클릭 처리
        if event == cv2.EVENT_LBUTTONDOWN:
            field = self._get_hovered_field()
            if not field: return

            if self.mode == "EDIT":
                self.mode = "MODIFY"
                self.field_being_modified = field
                self._show_feedback(f"Modify '{field}'. Draw new box.", (0, 255, 255))
            elif self.mode == "RENAME":
                self.mode = "INPUT"
                self.field_to_rename = field
                self.input_text = field
                self._show_feedback(f"Renaming '{field}'...", (255, 255, 0))
        return

    # 드래그 시작
    if event == cv2.EVENT_LBUTTONDOWN:
        self.drawing = True
        # [수정됨] 스냅 기능 적용된 시작점
        snapped_x, snapped_y = self._snap_to_grid(x, y) if self.snap_enabled else (x, y)
        self.points = [(snapped_x, snapped_y)]
        self.current_box = [self.points[0], self.points[0]]

    # 드래그 중
    elif event == cv2.EVENT_MOUSEMOVE:
        if self.drawing:
            # [수정됨] 스냅 기능 적용된 끝점
            snapped_x, snapped_y = self._snap_to_grid(x, y) if self.snap_enabled else (x, y)
            self.current_box[1] = (snapped_x, snapped_y)

    # 드래그 종료
    elif event == cv2.EVENT_LBUTTONUP:
        if self.drawing:
            self.drawing = False
            snapped_x, snapped_y = self._snap_to_grid(x, y) if self.snap_enabled else (x, y)
            self.current_box[1] = (snapped_x, snapped_y)
            self._on_box_drawn() # 박스 그리기 완료 처리

def _snap_to_grid(self, x, y):
    # [추가됨] 스냅 로직 (가장 가까운 선 또는 점에 붙임)
    snap_x, snap_y = x, y
    min_dist_x, min_dist_y = self.snap_distance, self.snap_distance

    # 기존 박스의 모서리에 스냅
    for p in self.layouts["field_boxes"].values():
        for px in [p[0], p[2]]:
            if abs(x - px) < min_dist_x:
                min_dist_x = abs(x - px)
                snap_x = px
        for py in [p[1], p[3]]:
            if abs(y - py) < min_dist_y:
                min_dist_y = abs(y - py)
                snap_y = py
    
    return snap_x, snap_y


def select_doc_type():
    """ 터미널에서 사용자에게 문서 종류를 선택하게 합니다. """
    if not os.path.exists(FIELD_DEFINITIONS_DIR):
        print(f"Error: Field definition directory not found at '{FIELD_DEFINITIONS_DIR}'")
        return None

    configs = []
    for filename in sorted(os.listdir(FIELD_DEFINITIONS_DIR)):
        if filename.endswith(".yaml"):
            try:
                with open(os.path.join(FIELD_DEFINITIONS_DIR, filename), 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    config_data['filename'] = filename
                    configs.append(config_data)
            except Exception as e:
                print(f"Warning: Could not load or parse {filename}: {e}")
    
    if not configs:
        print("Error: No valid field definition files (.yaml) found.")
        return None

    print("\n작업할 문서 종류를 선택하세요:")
    for i, config in enumerate(configs):
        print(f"  {i + 1}: {config.get('doc_type', 'Unknown')}")
    
    while True:
        try:
            choice = int(input("번호를 입력하세요 (종료하려면 0): "))
            if choice == 0: return None
            if 1 <= choice <= len(configs):
                return configs[choice - 1]
            else: print("잘못된 번호입니다. 다시 입력해주세요.")
        except (ValueError, EOFError):
            print("숫자를 입력해주세요.")

def get_file_paths(selected_config):
    """ 파일 탐색기를 열어 이미지와 YAML 경로를 가져옵니다. """
    root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)

    template_folder = selected_config.get('template_folder', '')
    initial_dir = os.path.join(ASSETS_DIR, template_folder)
    
    print(f"\nPlease select the '{selected_config.get('doc_type')}' image file to process...")
    
    # [수정됨] f-string 오타를 수정했습니다.
    image_path = filedialog.askopenfilename(
        parent=root, title=f"Select '{selected_config.get('doc_type')}' Image File",
        initialdir=initial_dir, filetypes=(("Image Files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
    )
    
    load_from_yaml_path = ""
    if image_path:
        print("Please select a YAML file to load as a template (optional)...")
        load_from_yaml_path = filedialog.askopenfilename(
            parent=root, title="Select YAML Layout File to Load (Optional)",
            initialdir=CONFIG_DIR, filetypes=(("YAML files", "*.yaml"), ("All files", "*.*"))
        )
    
    root.destroy()
    return image_path, load_from_yaml_path

if __name__ == '__main__':
    try:
        import cv2, yaml, tkinter
    except ImportError as e:
        print(f"Error: Missing required package '{e.name}'.")
        print("Please install it by running: pip install opencv-contrib-python pyyaml")
    else:
        while True:
            selected_config = select_doc_type()
            if not selected_config:
                print("\nExiting."); break

            image_path, load_from_yaml_path = get_file_paths(selected_config)

            if image_path:
                try: # [추가됨] 앱 실행 중 발생하는 예외 처리
                    app = LayoutExtractor(config=selected_config, image_path=image_path, load_yaml_path=load_from_yaml_path)
                    app.run()
                except FileNotFoundError as e:
                    print(f"\n[ERROR] {e}")
                except Exception as e:
                    print(f"\n[CRITICAL ERROR] An unexpected error occurred: {e}")
            else:
                print("No image file selected.")
            
            print("-" * 50)
            restart = input("다른 문서를 작업하시겠습니까? (y/n): ").lower()
            if restart != 'y':
                print("\nExiting."); break