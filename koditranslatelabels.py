import sublime_plugin
import sublime
import re
import os


class KodiTranslatedLabelToolTip(sublime_plugin.EventListener):

    def on_activated(self, view):
        # print("on_activated")
        self.get_settings()
        self.update_labels(view)
        sublime.set_timeout(lambda: self.run(view, 'activated'), 0)

    def on_selection_modified_async(self, view):
        # print("on_selection_modified_async")
        sublime.set_timeout(lambda: self.run(view, 'selection_modified'), 0)

    def run(self, view, where):
        if len(view.sel()) > 1:
            return
        else:
            view.hide_popup()
        if view.sel():
            scope_name = view.scope_name(view.sel()[0].b)
            selection = view.substr(view.word(view.sel()[0]))
            if "source.python" in scope_name or "text.xml" in scope_name:
                view.show_popup(self.return_label(view, selection), sublime.COOPERATE_WITH_AUTO_COMPLETE, location=-1, max_width=1000, on_navigate=lambda label_id, view=view: jump_to_label_declaration(view, label_id))

    def return_label(self, view, selection):
        if selection.isdigit():
            id_string = "#" + selection
            if id_string in self.id_list:
                index = self.id_list.index(id_string)
                return self.string_list[index + 1]
        return ""

    def get_settings(self):
        history_filename = 'KodiTranslateLabels.sublime-settings'
        history = sublime.load_settings(history_filename)
        self.kodi_path = history.get("kodi_path")
        # sublime.save_settings(history_filename)

    def get_addon_lang_file(self, path):
        if os.path.exists(os.path.join(path, "resources", "language", "English", "strings.po")):
            lang_file_path = os.path.join(path, "resources", "language", "English", "strings.po")
        elif os.path.exists(os.path.join(path, "..", "language", "English", "strings.po")):
            lang_file_path = os.path.join(path, "..", "language", "English", "strings.po")
        else:
            return ""
        return open(lang_file_path, "r").read()

    def get_kodi_lang_file(self, path):
        if os.path.exists(os.path.join(self.kodi_path, "addons", "resource.language.en_gb", "resources", "strings.po")):
            lang_file_path = os.path.join(self.kodi_path, "addons", "resource.language.en_gb", "resources", "strings.po")
        elif os.path.exists(os.path.join(self.kodi_path, "language", "English", "strings.po")):
            lang_file_path = os.path.join(self.kodi_path, "language", "English", "strings.po")
        else:
            return ""
        return open(lang_file_path, "r").read()

    def update_labels(self, view):
        if view.file_name():
            path, filename = os.path.split(view.file_name())
            lang_file = self.get_addon_lang_file(path)
            self.id_list = re.findall('^msgctxt \"(.*)\"[^\"]*', lang_file, re.MULTILINE)
            self.string_list = re.findall('^msgid \"(.*)\"[^\"]*', lang_file, re.MULTILINE)


class SetKodiFolderCommand(sublime_plugin.TextCommand):

    def run(self, view):
        sublime.message_dialog("test")



def jump_to_label_declaration(view, label_id):
    view.run_command("insert", {"characters": label_id})
    view.hide_popup()
