"""
Глобальный менеджер тем оформления.
Применяет стили через QApplication для гарантированного наследования всеми виджетами.
"""

LIGHT_THEME = """
QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #FFFFFF;
}

QListWidget {
    background-color: #1E293B;
    color: #CBD5E1;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 5px;
}

QListWidget::item {
    padding: 15px 20px;
    margin: 3px 0;
    border-radius: 8px;
    border-left: 4px solid transparent;
    color: #CBD5E1;
}

QListWidget::item:hover {
    background-color: #334155;
    color: #FFFFFF;
}

QListWidget::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
    border-left: 4px solid #60A5FA;
    font-weight: bold;
}

QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
    min-height: 45px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QPushButton#delete_btn {
    background-color: #EF4444;
}

QPushButton#delete_btn:hover {
    background-color: #DC2626;
}

QPushButton:disabled {
    background-color: #94A3B8;
    color: #CBD5E1;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F1F5F9;
    border: 2px solid #E2E8F0;
    border-radius: 12px;
    gridline-color: #E2E8F0;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    font-size: 13px;
    color: #0F172A;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #F1F5F9;
    color: #0F172A;
    background-color: #FFFFFF;
}

QTableWidget::item:alternate {
    background-color: #F1F5F9;
}

QTableWidget::item:selected {
    background-color: #DBEAFE;
    color: #1E3A8A;
    border: none;
}
QTableWidget::item:focus {
    outline: none;
    border: none;
}

QTableWidget {
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
}
QHeaderView::section {
    background-color: #F1F5F9;
    color: #1E293B;
    font-weight: bold;
    padding: 14px;
    border: none;
    border-bottom: 3px solid #CBD5E1;
    font-size: 13px;
}

QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 2px solid #CBD5E1;
    border-radius: 8px;
    padding: 10px 14px;
    color: #0F172A;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    font-size: 13px;
    min-height: 40px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #2563EB;
    background-color: #FFFFFF;
}

QCheckBox, QRadioButton {
    spacing: 10px;
    font-size: 13px;
    color: #0F172A;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid #CBD5E1;
    border-radius: 5px;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #2563EB;
    border: 2px solid #2563EB;
}

QGroupBox {
    font-weight: bold;
    font-size: 14px;
    border: 2px solid #E2E8F0;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    background-color: #FFFFFF;
    color: #0F172A;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #2563EB;
}

QLabel {
    color: #0F172A;
    font-size: 13px;
    background-color: transparent;
}

QDialog {
    background-color: #FFFFFF;
}

QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    font-size: 14px;
    color: #0F172A;
}

QProgressBar {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    text-align: center;
    background-color: #F1F5F9;
    height: 25px;
    color: #0F172A;
}

QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 6px;
}

QScrollBar:vertical {
    background-color: #F1F5F9;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #CBD5E1;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94A3B8;
}

QScrollBar:horizontal {
    background-color: #F1F5F9;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #CBD5E1;
    border-radius: 6px;
    min-width: 30px;
}

QComboBox::drop-down {
    border: none;
    width: 40px;
}

QComboBox QAbstractItemView {
    border: 2px solid #E2E8F0;
    border-radius: 8px;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    background-color: white;
    outline: none;
}

QStatusBar {
    background-color: #F8FAFC;
    color: #64748B;
    border-top: 2px solid #E2E8F0;
    font-size: 12px;
}

QToolTip {
    background-color: #1E293B;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}

QFrame {
    background-color: transparent;
}

#dashboard_title {
    font-size: 28px;
    font-weight: bold;
    padding: 10px 0;
    color: #1E293B;
}

#dashboard_card {
    border-radius: 12px;
    padding: 25px;
    border: 2px solid #E2E8F0;
    background-color: #FFFFFF;
}

#card_title {
    font-size: 14px;
    color: #64748B;
}

#card_value {
    font-size: 32px;
    font-weight: bold;
    color: #2563EB;
}

QLabel#section_header {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #1E293B;
}

QLineEdit#search_input {
    padding: 10px 15px;
    border-radius: 8px;
}

QLabel#hint_label {
    color: #64748B;
    font-style: italic;
    font-size: 12px;
    padding: 8px;
    background-color: #F0F9FF;
    border-radius: 6px;
}

QFrame#sidebar_frame {
    background-color: #1E293B;
    border-right: 3px solid #334155;
}

QWidget#content_frame {
    background-color: #F8FAFC;
}

QLabel#header_label {
    color: #1E293B;
    font-size: 28px;
    font-weight: bold;
}

QLabel#logo_label {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: bold;
    padding: 25px 20px;
    background-color: #0F172A;
    border-bottom: 2px solid #334155;
}
/* ===== Диалог детального просмотра авто ===== */
QLabel#detail_title {
    font-size: 28px;
    font-weight: bold;
    padding: 10px 0;
}

QLabel#detail_image {
    border-radius: 10px;
    border: 2px solid #E2E8F0;
    background-color: #F1F5F9;
}

QLabel#detail_image_placeholder {
    border-radius: 10px;
    border: 2px dashed #94A3B8;
    background-color: #E2E8F0;
    color: #64748B;
    font-size: 16px;
}

QLabel#spec_label {
    font-weight: bold;
    font-size: 13px;
    color: #64748B;
}

QLabel#spec_value {
    font-size: 13px;
    padding: 5px;
    border-radius: 4px;
    background-color: #F8FAFC;
}

QLabel#detail_desc_title {
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
}

QLabel#detail_desc_text {
    font-size: 13px;
    padding: 10px;
    border-radius: 6px;
    background-color: #F1F5F9;
}

/* ===== Диалог "О программе" ===== */
QLabel#about_icon {
    font-size: 64px;
    padding: 0 15px;
}

QLabel#about_title {
    font-size: 32px;
    font-weight: bold;
    color: #2563EB;
}

QLabel#about_version {
    font-size: 16px;
    color: #64748B;
}

QFrame#about_separator {
    background-color: #E2E8F0;
    max-height: 2px;
}

QFrame#about_info_group {
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    padding: 15px;
    background-color: #F8FAFC;
}

QLabel#about_info_title {
    font-size: 16px;
    font-weight: bold;
    color: #1E293B;
}

QLabel#about_info_text {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
}
/* ===== КАЛЕНДАРЬ (QCalendarWidget) — светлая тема ===== */
QCalendarWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 2px solid #E2E8F0;
    border-radius: 10px;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
    font-size: 13px;
    minimum-height: 300px;
}

QCalendarWidget QWidget {
    background-color: #FFFFFF;
    color: #0F172A;
}

QCalendarWidget QToolButton {
    background-color: transparent;
    color: #0F172A;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    min-height: 32px;
    min-width: 32px;
    font-size: 13px;
}

QCalendarWidget QToolButton:hover {
    background-color: #E2E8F0;
}

QCalendarWidget QToolButton:pressed {
    background-color: #CBD5E1;
}

QCalendarWidget QMenu {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
}

QCalendarWidget QMenu::item {
    padding: 6px 20px;
    min-height: 24px;
}

QCalendarWidget QMenu::item:selected {
    background-color: #DBEAFE;
    color: #1E3A8A;
}

QCalendarWidget QSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 4px;
    min-height: 24px;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #F1F5F9;
    border-bottom: 2px solid #E2E8F0;
    padding: 8px;
}

QCalendarWidget QTableView {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    gridline-color: #E2E8F0;
    border: none;
    font-size: 13px;
}

QCalendarWidget QTableView::item {
    padding: 6px;
    color: #0F172A;
    border: 1px solid transparent;
    min-height: 36px;
    min-width: 36px;
}

QCalendarWidget QTableView::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
    border-radius: 6px;
}

QCalendarWidget QTableView::item:hover {
    background-color: #E0F2FE;
}

QCalendarWidget QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: bold;
    padding: 8px 4px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    font-size: 12px;
    min-height: 32px;
    min-width: 36px;
    text-align: center;
}
/* Таблица штрафов */
QTableWidget#penalty_table {
    background-color: #FFFFFF;
    alternate-background-color: #F1F5F9;
    color: #0F172A;
}

QTableWidget#penalty_table::item {
    background-color: #FFFFFF;
    color: #0F172A;
}

QTableWidget#penalty_table::item:alternate {
    background-color: #F1F5F9;
}
/* Таблица ТО */
QTableWidget#maintenance_table {
    background-color: #FFFFFF;
    alternate-background-color: #F1F5F9;
    color: #0F172A;
}

QTableWidget#maintenance_table::item {
    background-color: #FFFFFF;
    color: #0F172A;
}

QTableWidget#maintenance_table::item:alternate {
    background-color: #F1F5F9;
}
/* Стили для диалога редактирования авто */
QDialog QLineEdit, QDialog QSpinBox, QDialog QComboBox, QDialog QTextEdit {
    min-height: 40px;
    padding: 10px 14px;
}

QDialog QLabel {
    font-weight: bold;
}
/* ===== Панель информации о пользователе ===== */
QFrame#user_info_frame {
    background-color: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid #334155;
    margin: 0;
    padding: 0;
}

QLabel#user_name_label {
    font-size: 14px;
    font-weight: bold;
    color: #FFFFFF;
    padding: 0;
}

QLabel#user_role_label {
    font-size: 11px;
    color: #94A3B8;
    padding: 0;
}

/* ===== Таблица пользователей ===== */
QTableWidget#users_table {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    color: #0F172A;
}

QTableWidget#users_table::item {
    background-color: #FFFFFF;
    color: #0F172A;
}

QTableWidget#users_table::item:alternate {
    background-color: #F8FAFC;
}
/* Кнопка смены темы в сайдбаре */
QPushButton#theme_toggle_btn {
    background-color: #6366F1;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    font-size: 12px;
    padding: 8px;
    margin: 5px 0;
}
QPushButton#theme_toggle_btn:hover {
    background-color: #4F46E5;
}

/* Вкладки "О программе" */
QTabWidget#about_tabs::pane {
    border: none;
    padding: 10px;
}
QTabWidget#about_tabs QTabBar::tab {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}
QTabWidget#about_tabs QTabBar::tab:selected {
    border-bottom: 3px solid #2563EB;
    color: #2563EB;
}
/* ===== Таблица прав доступа (светлая тема) ===== */
QTableWidget#permissions_table {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    color: #0F172A;
    gridline-color: #E2E8F0;
}

QTableWidget#permissions_table::item {
    background-color: #FFFFFF;
    color: #0F172A;
    padding: 8px;
}

QTableWidget#permissions_table::item:alternate {
    background-color: #F8FAFC;
}

QTableWidget#permissions_table::item:selected {
    background-color: #DBEAFE;
    color: #1E3A8A;
}

QHeaderView#permissions_table {
    background-color: #F1F5F9;
    color: #1E293B;
    font-weight: bold;
}

QTableWidget#permissions_table QTableCornerButton::section {
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
}
"""

DARK_THEME = """
/* Окно входа */
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0F172A, 
        stop:0.5 #1E293B, 
        stop:1 #0F172A);
}

QWidget {
background-color: #0F172A;
color: #E2E8F0;
font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
font-size: 13px;
}

QMainWindow {
    background-color: #020617;
}

QListWidget {
    background-color: #1E293B;
    color: #CBD5E1;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 5px;
}

QListWidget::item {
    padding: 15px 20px;
    margin: 3px 0;
    border-radius: 8px;
    border-left: 4px solid transparent;
    color: #CBD5E1;
}

QListWidget::item:hover {
    background-color: #334155;
    color: #FFFFFF;
}

QListWidget::item:selected {
    background-color: #3B82F6;
    color: #FFFFFF;
    border-left: 4px solid #60A5FA;
    font-weight: bold;
}

QPushButton {
    background-color: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 13px;
    min-height: 45px;
}

QPushButton:hover {
    background-color: #2563EB;
}

QPushButton:pressed {
    background-color: #1D4ED8;
}

QPushButton#delete_btn {
    background-color: #EF4444;
}

QPushButton#delete_btn:hover {
    background-color: #DC2626;
}

QPushButton:disabled {
    background-color: #475569;
    color: #94A3B8;
}

QTableWidget {
    background-color: #1E293B;
    alternate-background-color: #334155;
    border: 2px solid #475569;
    border-radius: 12px;
    gridline-color: #475569;
    selection-background-color: #1E40AF;
    selection-color: #FFFFFF;
    font-size: 13px;
    color: #E2E8F0;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #334155;
    color: #E2E8F0;
    background-color: #1E293B;
}

QTableWidget::item:alternate {
    background-color: #334155;
}

QTableWidget::item:selected {
    background-color: #1E40AF;
    color: #FFFFFF;
    border: none;
}
QTableWidget::item:focus {
    outline: none;
    border: none;
}

QTableWidget {
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
}
QHeaderView::section {
    background-color: #334155;
    color: #E2E8F0;
    font-weight: bold;
    padding: 14px;
    border: none;
    border-bottom: 3px solid #475569;
    font-size: 13px;
}

QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
    background-color: #1E293B;
    border: 2px solid #475569;
    border-radius: 8px;
    padding: 10px 14px;
    color: #E2E8F0;
    selection-background-color: #3B82F6;
    selection-color: #FFFFFF;
    font-size: 13px;
    min-height: 40px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #3B82F6;
    background-color: #334155;
}

QCheckBox, QRadioButton {
    spacing: 10px;
    font-size: 13px;
    color: #E2E8F0;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid #475569;
    border-radius: 5px;
    background-color: #1E293B;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #3B82F6;
    border: 2px solid #3B82F6;
}

QGroupBox {
    font-weight: bold;
    font-size: 14px;
    border: 2px solid #475569;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    background-color: #1E293B;
    color: #E2E8F0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #60A5FA;
}

QLabel {
    color: #E2E8F0;
    font-size: 13px;
    background-color: transparent;
}

QDialog {
    background-color: #1E293B;
}

QMessageBox {
    background-color: #1E293B;
}

QMessageBox QLabel {
    font-size: 14px;
    color: #E2E8F0;
}

QProgressBar {
    border: 2px solid #475569;
    border-radius: 8px;
    text-align: center;
    background-color: #334155;
    height: 25px;
    color: #E2E8F0;
}

QProgressBar::chunk {
    background-color: #3B82F6;
    border-radius: 6px;
}

QScrollBar:vertical {
    background-color: #334155;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748B;
}

QScrollBar:horizontal {
    background-color: #334155;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #475569;
    border-radius: 6px;
    min-width: 30px;
}

QComboBox::drop-down {
    border: none;
    width: 40px;
}

QComboBox QAbstractItemView {
    border: 2px solid #475569;
    border-radius: 8px;
    selection-background-color: #1E40AF;
    selection-color: #FFFFFF;
    background-color: #1E293B;
    color: #E2E8F0;
    outline: none;
}

QStatusBar {
    background-color: #0F172A;
    color: #CBD5E1;
    border-top: 2px solid #334155;
    font-size: 12px;
}

QToolTip {
    background-color: #334155;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}

QFrame {
    background-color: transparent;
}

#dashboard_title {
    font-size: 28px;
    font-weight: bold;
    padding: 10px 0;
    color: #E2E8F0;
}

#dashboard_card {
    border-radius: 12px;
    padding: 25px;
    border: 2px solid #475569;
    background-color: #1E293B;
}

#card_title {
    font-size: 14px;
    color: #94A3B8;
}

#card_value {
    font-size: 32px;
    font-weight: bold;
    color: #60A5FA;
}

QLabel#section_header {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #E2E8F0;
}

QLineEdit#search_input {
    padding: 10px 15px;
    border-radius: 8px;
}

QLabel#hint_label {
    color: #94A3B8;
    font-style: italic;
    font-size: 12px;
    padding: 8px;
    background-color: #1E3A5F;
    border-radius: 6px;
}

QFrame#sidebar_frame {
    background-color: #0F172A;
    border-right: 3px solid #1E293B;
}

QWidget#content_frame {
    background-color: #0F172A;
}

QLabel#header_label {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: bold;
}

QLabel#logo_label {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: bold;
    padding: 25px 20px;
    background-color: #0F172A;
    border-bottom: 2px solid #1E293B;
}
/* ===== Диалог детального просмотра авто ===== */
QLabel#detail_title {
    font-size: 28px;
    font-weight: bold;
    padding: 10px 0;
}

QLabel#detail_image {
    border-radius: 10px;
    border: 2px solid #E2E8F0;
    background-color: #F1F5F9;
}

QLabel#detail_image_placeholder {
    border-radius: 10px;
    border: 2px dashed #94A3B8;
    background-color: #E2E8F0;
    color: #64748B;
    font-size: 16px;
}

QLabel#spec_label {
    font-weight: bold;
    font-size: 13px;
    color: #64748B;
}

QLabel#spec_value {
    font-size: 13px;
    padding: 5px;
    border-radius: 4px;
    background-color: #F8FAFC;
}

QLabel#detail_desc_title {
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
}

QLabel#detail_desc_text {
    font-size: 13px;
    padding: 10px;
    border-radius: 6px;
    background-color: #F1F5F9;
}

/* ===== Диалог "О программе" ===== */
QLabel#about_icon {
    font-size: 64px;
    padding: 0 15px;
}

QLabel#about_title {
    font-size: 32px;
    font-weight: bold;
    color: #2563EB;
}

QLabel#about_version {
    font-size: 16px;
    color: #64748B;
}

QFrame#about_separator {
    background-color: #E2E8F0;
    max-height: 2px;
}

QFrame#about_info_group {
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    padding: 15px;
    background-color: #F8FAFC;
}

QLabel#about_info_title {
    font-size: 16px;
    font-weight: bold;
    color: #1E293B;
}

QLabel#about_info_text {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
}
/* ===== Диалог детального просмотра авто (тёмная тема) ===== */
QLabel#detail_title {
    font-size: 28px;
    font-weight: bold;
    padding: 10px 0;
    color: #E2E8F0;
}

QLabel#detail_image {
    border-radius: 10px;
    border: 2px solid #475569;
    background-color: #1E293B;
}

QLabel#detail_image_placeholder {
    border-radius: 10px;
    border: 2px dashed #64748B;
    background-color: #334155;
    color: #94A3B8;
    font-size: 16px;
}

QLabel#spec_label {
    font-weight: bold;
    font-size: 13px;
    color: #94A3B8;
}

QLabel#spec_value {
    font-size: 13px;
    padding: 5px;
    border-radius: 4px;
    background-color: #334155;
    color: #E2E8F0;
}

QLabel#detail_desc_title {
    font-weight: bold;
    font-size: 14px;
    margin-top: 10px;
    color: #E2E8F0;
}

QLabel#detail_desc_text {
    font-size: 13px;
    padding: 10px;
    border-radius: 6px;
    background-color: #1E293B;
    color: #CBD5E1;
}

/* ===== Диалог "О программе" (тёмная тема) ===== */
QLabel#about_icon {
    font-size: 64px;
    padding: 0 15px;
}

QLabel#about_title {
    font-size: 32px;
    font-weight: bold;
    color: #60A5FA;
}

QLabel#about_version {
    font-size: 16px;
    color: #94A3B8;
}

QFrame#about_separator {
    background-color: #475569;
    max-height: 2px;
}

QFrame#about_info_group {
    border-radius: 10px;
    border: 1px solid #475569;
    padding: 15px;
    background-color: #1E293B;
}

QLabel#about_info_title {
    font-size: 16px;
    font-weight: bold;
    color: #E2E8F0;
}

QLabel#about_info_text {
    font-size: 13px;
    color: #CBD5E1;
    line-height: 1.6;
}
/* ===== КАЛЕНДАРЬ (QCalendarWidget) — тёмная тема ===== */
QCalendarWidget {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 2px solid #475569;
    border-radius: 10px;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
    font-size: 13px;
    minimum-height: 300px;
}

QCalendarWidget QWidget {
    background-color: #1E293B;
    color: #E2E8F0;
}

QCalendarWidget QToolButton {
    background-color: transparent;
    color: #E2E8F0;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    min-height: 32px;
    min-width: 32px;
    font-size: 13px;
}

QCalendarWidget QToolButton:hover {
    background-color: #334155;
}

QCalendarWidget QToolButton:pressed {
    background-color: #475569;
}

QCalendarWidget QMenu {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    border-radius: 6px;
}

QCalendarWidget QMenu::item {
    padding: 6px 20px;
    min-height: 24px;
}

QCalendarWidget QMenu::item:selected {
    background-color: #1E40AF;
    color: #FFFFFF;
}

QCalendarWidget QSpinBox {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 4px;
    min-height: 24px;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #334155;
    border-bottom: 2px solid #475569;
    padding: 8px;
}

QCalendarWidget QTableView {
    background-color: #1E293B;
    alternate-background-color: #334155;
    selection-background-color: #1E40AF;
    selection-color: #FFFFFF;
    gridline-color: #475569;
    border: none;
    font-size: 13px;
}

QCalendarWidget QTableView::item {
    padding: 6px;
    color: #E2E8F0;
    border: 1px solid transparent;
    min-height: 36px;
    min-width: 36px;
}

QCalendarWidget QTableView::item:selected {
    background-color: #3B82F6;
    color: #FFFFFF;
    border-radius: 6px;
}

QCalendarWidget QTableView::item:hover {
    background-color: #475569;
}

QCalendarWidget QHeaderView::section {
    background-color: #334155;
    color: #CBD5E1;
    font-weight: bold;
    padding: 8px 4px;
    border: none;
    border-bottom: 2px solid #475569;
    font-size: 12px;
    min-height: 32px;
    min-width: 36px;
    text-align: center;
}
/* Таблица штрафов */
QTableWidget#penalty_table {
    background-color: #1E293B;
    alternate-background-color: #334155;
    color: #E2E8F0;
}

QTableWidget#penalty_table::item {
    background-color: #1E293B;
    color: #E2E8F0;
}

QTableWidget#penalty_table::item:alternate {
    background-color: #334155;
}
/* Таблица ТО */
QTableWidget#maintenance_table {
    background-color: #1E293B;
    alternate-background-color: #334155;
    color: #E2E8F0;
}

QTableWidget#maintenance_table::item {
    background-color: #1E293B;
    color: #E2E8F0;
}

QTableWidget#maintenance_table::item:alternate {
    background-color: #334155;
}
/* Стили для диалога редактирования авто */
QDialog QLineEdit, QDialog QSpinBox, QDialog QComboBox, QDialog QTextEdit {
    min-height: 40px;
    padding: 10px 14px;
}

QDialog QLabel {
    font-weight: bold;
}
/* ===== Панель информации о пользователе (тёмная тема) ===== */
QFrame#user_info_frame {
    background-color: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid #334155;
}

QLabel#user_name_label {
    color: #FFFFFF;
}

QLabel#user_role_label {
    color: #94A3B8;
}

/* ===== Таблица пользователей (тёмная тема) ===== */
QTableWidget#users_table {
    background-color: #1E293B;
    alternate-background-color: #334155;
    color: #E2E8F0;
}

QTableWidget#users_table::item {
    background-color: #1E293B;
    color: #E2E8F0;
}

QTableWidget#users_table::item:alternate {
    background-color: #334155;
}
/* Стили для окна управления БД в тёмной теме */
QLabel#db_info_label {
    color: #E2E8F0;
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 10px;
}

QGroupBox QLabel {
    color: #E2E8F0;
}

QGroupBox {
    color: #E2E8F0;
    border: 2px solid #475569;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #60A5FA;
    font-weight: bold;
    font-size: 14px;
}
/* Кнопка смены темы в сайдбаре */
QPushButton#theme_toggle_btn {
    background-color: #6366F1;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    font-size: 12px;
    padding: 8px;
    margin: 5px 0;
}
QPushButton#theme_toggle_btn:hover {
    background-color: #4F46E5;
}

/* Вкладки "О программе" */
QTabWidget#about_tabs::pane {
    border: none;
    padding: 10px;
}
QTabWidget#about_tabs QTabBar::tab {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}
QTabWidget#about_tabs QTabBar::tab:selected {
    border-bottom: 3px solid #2563EB;
    color: #2563EB;
}
/* ===== Таблица прав доступа (тёмная тема) ===== */
QTableWidget#permissions_table {
    background-color: #1E293B;
    alternate-background-color: #334155;
    color: #E2E8F0;
    gridline-color: #475569;
}

QTableWidget#permissions_table::item {
    background-color: #1E293B;
    color: #E2E8F0;
    padding: 8px;
}

QTableWidget#permissions_table::item:alternate {
    background-color: #334155;
}

QTableWidget#permissions_table::item:selected {
    background-color: #3B82F6;
    color: #FFFFFF;
}

QHeaderView#permissions_table {
    background-color: #334155;
    color: #E2E8F0;
    font-weight: bold;
}

QTableWidget#permissions_table QTableCornerButton::section {
    background-color: #334155;
    border: 1px solid #475569;
}
"""

def get_theme(theme_name: str) -> str:
    """Возвращает QSS-строку для указанной темы."""
    if theme_name == "dark":
        return DARK_THEME
    return LIGHT_THEME