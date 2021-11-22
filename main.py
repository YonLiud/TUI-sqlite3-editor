from ctypes import sizeof
import npyscreen, curses, sqlite3, os

def executeQuery(query, conn):
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    return c.fetchall()


class MyTUI(npyscreen.NPSAppManaged):
    
    database_connection = None
    active_table = None
    
    def onStart(self):
        self.addForm("MAIN", SelectDatabase)
        self.addForm("TABLE", TablesMenu)
        self.addForm("COLUMN", TableMenu)
        self.addForm("CREATE_TABLE", CreateTable)
        
    def onCleanExit(self):
        npyscreen.notify_wait("Goodbye!")
        self.database_connection.close()
        
    def change_form(self, name):
        self.switchForm(name)
        
class SelectDatabase(npyscreen.ActionForm):
    def create(self):
        self.filename = self.add(npyscreen.TitleFilename, name="Database File: ")
    def on_ok(self):
        if self.filename.value == "":
            npyscreen.notify_confirm("File path cannot be empty", editw=1, wide=True)
        if os.path.isfile(self.filename.value):
            try:
                sqlite3.connect(self.filename.value).close()
            except sqlite3.Error as e:
                npyscreen.notify_confirm(str(e), editw=1, wide=True)
            else:
                self.parentApp.database_connection = sqlite3.connect(self.filename.value)
                self.parentApp.change_form("TABLE")
        else:
            create_file = npyscreen.notify_yes_no(f"File: {self.filename.value}\nFile does not exist. Create?", editw=1)
            if create_file:
                sqlite3.connect(self.filename.value).close()
                self.parentApp.database_connection = sqlite3.connect(self.filename.value)
                self.parentApp.change_form("TABLE")
                
    
class TablesMenu(npyscreen.FormBaseNew):
    def create(self):
        self.name = "Table Managment"
    def beforeEditing(self):
        self._clear_all_widgets()
        self.tables = []
        self.tables += executeQuery("SELECT name FROM sqlite_master WHERE type='table'", self.parentApp.database_connection)
        self.option = self.add(npyscreen.TitleSelectOne, name="Table: ", values=[x[0] for x in self.tables], scroll_exit=True, max_height=5)
        self.add(npyscreen.ButtonPress, name="View Table", when_pressed_function=self.viewTable, value=None)
        self.add(npyscreen.ButtonPress, name="Create Table", when_pressed_function=self.createTable, value=None)
    def viewTable(self):
        if self.option.value == [] or self.option.value == None:
            npyscreen.notify_confirm(f"Please Select a table", editw=1, wide=False)
        else:
            self.parentApp.change_form("COLUMN")
    def createTable(self):
        self.parentApp.change_form("CREATE_TABLE")

class CreateTable(npyscreen.FormBaseNew):
    def create(self):
        self.name = "Create Table"
        self.name = self.add(npyscreen.TitleText, name="Table Name: ")
        self.add(npyscreen.ButtonPress, name="Create Table", when_pressed_function=self.on_ok, value=None)
    def on_ok(self):
        # create table
        executeQuery(f"CREATE TABLE {self.name.value} (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)", self.parentApp.database_connection)
        npyscreen.notify_wait(f"Created Table {self.name.value}", wide=False)
        self.parentApp.change_form("TABLE")
        
        
class TableMenu(npyscreen.FormBaseNew):
    def create(self):
        self.name = "View Table"
    # def on_ok(self):
    #     self.parentApp.change_form("TABLE")
    # def afterEditing(self):
    #     self.parentApp.active_table = None
    #     self.add(npyscreen.ButtonPress, name="Return", value_changed_callback=self.on_ok, value=None)
    # def beforeEditing(self):
    #     self.add(npyscreen.TitleText, name="Table Name: ", value=self.parentApp.active_table[0])
    #     self.columns = executeQuery(f"PRAGMA table_info({self.parentApp.active_table[0]})", self.parentApp.database_connection)
    #     self.add(npyscreen.TitleMultiSelect, name="Columns: ", values=str(self.columns), scroll_exit=True, max_height=5)
        
def main():
    MyTUI().run()

if __name__ == '__main__':
    main()