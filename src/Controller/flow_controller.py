import sys

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QStackedWidget

from view.menue_view import menue_view
from view.login_view import login_view
from view.pfad_view import pfad_view
from view.datei_liste_view import datei_liste_view
from view.chat_view import chat_view
from view.chat_history_view import chat_history_view

from model.pfad_validator import pfad_validator
from controller.datei_manager import datei_manager
from controller.backup_manager import backup_manager
from controller.ki_analyzer import ki_analyzer
from controller.chat_history_service import chat_history_service
from controller.user_settings_store import user_settings_store

from controller.auth_flow import auth_flow
from controller.settings_flow import settings_flow
from controller.file_list_flow import file_list_flow
from controller.file_access_flow import file_access_flow
from controller.file_mutation_flow import file_mutation_flow
from controller.chat_core_flow import chat_core_flow
from controller.chat_file_flow import chat_file_flow
from controller.history_flow import history_flow
from controller.backup_flow import backup_flow


class flow_controller:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.api_base_url = "http://localhost:8000"
        self.auth_token = None
        self.current_username = None
        self.file_records = []
        self.visible_file_records = []
        self.file_sort_mode = "Name (A-Z)"
        self.file_search_query = ""
        self.ki_analyzer = ki_analyzer()
        self.chat_messages = []
        self.current_chat_id = None
        self.is_temp_chat = False
        self.chat_started = False
        self.chat_file_context = []
        self.chat_file_meta = []
        self.visible_history_entries = []
        self.history_sort_mode = "Datum (neu-alt)"
        self.history_search_query = ""
        self._chat_thread = None
        self._chat_worker = None
        self.settings = QSettings("swe_dhbw", "swe_dhbw")
        self.history_service = chat_history_service(self.settings)
        self.user_settings_store = user_settings_store("swe_dhbw")

        self.start_view = menue_view()
        self.login_view = login_view()
        self.pfad_view = pfad_view()
        self.datei_liste_view = datei_liste_view()
        self.chat_view = chat_view()
        self.history_view = chat_history_view()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)
        self.stack.addWidget(self.datei_liste_view)
        self.stack.addWidget(self.chat_view)
        self.stack.addWidget(self.history_view)

        self.pfad_validator = pfad_validator()
        self.datei_manager = datei_manager(self.pfad_validator)
        self.backup_manager = backup_manager(self.datei_manager)

        self.settings_flow = settings_flow(self)
        self.auth_flow = auth_flow(self)
        self.file_list_flow = file_list_flow(self)
        self.file_access_flow = file_access_flow(self)
        self.file_mutation_flow = file_mutation_flow(self)
        self.chat_core_flow = chat_core_flow(self)
        self.chat_file_flow = chat_file_flow(self)
        self.history_flow = history_flow(self)
        self.backup_flow = backup_flow(self)

        self.__setup_connections()
        self.auth_flow.load_saved_credentials()
        self.settings_flow.apply_saved_theme()

    def run(self):
        self.stack.setCurrentWidget(self.start_view)
        self.stack.show()
        self.auth_flow.start_splash()
        return self.app.exec()

    def __setup_connections(self):
        self.login_view.get_btn_login().clicked.connect(self.auth_flow.on_login_clicked)
        self.login_view.get_btn_register().clicked.connect(self.auth_flow.on_register_clicked)

        self.datei_liste_view.get_btn_refresh().clicked.connect(
            self.file_list_flow.load_files_and_show
        )
        self.datei_liste_view.get_btn_history().clicked.connect(
            self.history_flow.on_history_clicked
        )
        self.datei_liste_view.get_btn_settings().clicked.connect(
            self.settings_flow.on_settings_clicked
        )
        self.datei_liste_view.get_btn_logout().clicked.connect(
            self.auth_flow.on_logout_clicked
        )
        self.datei_liste_view.get_btn_upload().clicked.connect(
            self.file_mutation_flow.on_upload_clicked
        )
        self.datei_liste_view.get_btn_download().clicked.connect(
            self.file_access_flow.on_download_clicked
        )
        self.datei_liste_view.get_btn_delete().clicked.connect(
            self.file_mutation_flow.on_delete_clicked
        )
        self.datei_liste_view.get_btn_ai_summary().clicked.connect(
            self.chat_core_flow.on_ai_summary_clicked
        )
        self.datei_liste_view.get_btn_select_all().clicked.connect(
            self.file_list_flow.on_files_select_all_clicked
        )
        self.datei_liste_view.request_open.connect(
            self.file_access_flow.on_file_open_requested
        )
        self.datei_liste_view.request_details.connect(
            self.file_list_flow.on_file_details_requested
        )
        self.datei_liste_view.sort_changed.connect(
            self.file_list_flow.on_file_sort_changed
        )
        self.datei_liste_view.search_changed.connect(
            self.file_list_flow.on_file_search_changed
        )

        self.chat_view.get_btn_send().clicked.connect(
            self.chat_core_flow.on_chat_send_clicked
        )
        self.chat_view.get_btn_back().clicked.connect(
            self.chat_core_flow.on_chat_back_clicked
        )
        self.chat_view.get_btn_select_files().clicked.connect(
            self.chat_file_flow.on_chat_select_files_clicked
        )
        self.chat_view.get_btn_clear_files().clicked.connect(
            self.chat_file_flow.on_chat_clear_files_clicked
        )

        self.history_view.get_btn_open().clicked.connect(
            self.history_flow.on_history_open_clicked
        )
        self.history_view.get_btn_delete().clicked.connect(
            self.history_flow.on_history_delete_clicked
        )
        self.history_view.get_btn_select_all().clicked.connect(
            self.history_flow.on_history_select_all_clicked
        )
        self.history_view.get_btn_back().clicked.connect(
            self.history_flow.on_history_back_clicked
        )
        self.history_view.request_open.connect(
            self.history_flow.on_history_open_requested
        )
        self.history_view.sort_changed.connect(
            self.history_flow.on_history_sort_changed
        )
        self.history_view.request_rename.connect(
            self.history_flow.on_history_rename_clicked
        )
        self.history_view.search_changed.connect(
            self.history_flow.on_history_search_changed
        )

        self.pfad_view.get_btn_ok().clicked.connect(self.backup_flow.on_pfad_ok)
