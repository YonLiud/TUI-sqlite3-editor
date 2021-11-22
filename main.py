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
        pass
    def beforeEditing(self):
        self._clear_all_widgets()
        self.name = "Create Table"
        self.add(npyscreen.ButtonPress, name="Confrim", when_pressed_function=self.on_ok, value=None)
        self.add(npyscreen.ButtonPress, name="Cancel", when_pressed_function=self.on_cancel, value=None)
        self.table_name = self.add(npyscreen.TitleText, name="Table Name: ")
        self.entries = []
        self.entries_display = self.add_widget(npyscreen.MultiLineEdit, value="", max_height=5, editable=False)
        self.column_name = self.add(npyscreen.TitleText, name="Column Name: ")
        self.column_type = self.add(npyscreen.TitleSelectOne, name="Type: ", values=["INTEGER", "TEXT", "REAL", "BLOB"], value=[1,], scroll_exit=True, max_height=5)
        self.add(npyscreen.ButtonPress, name="Save Column", when_pressed_function=self.saveColumn, value=None)
    def saveColumn(self):
        if self.column_name.value == "":
            npyscreen.notify_confirm("Column name cannot be empty", editw=1, wide=False)
        elif self.column_type.value == []:
            npyscreen.notify_confirm("Please select a type", editw=1, wide=False)
        else:
            self.column_type.value = ["INTEGER", "TEXT", "REAL", "BLOB"][self.column_type.value[0]]
            self.entries.append((self.column_name.value, self.column_type.value))
            self.column_name.value = ""
            self.column_type.value = [1,]
            self.entries_display.value = "\n".join([f"{x[0]}: {x[1]}" for x in self.entries])
            self.entries_display.display()

        
    
    def on_cancel(self):
        self.parentApp.change_form("TABLE")
        
    def on_ok(self):
        if self.table_name.value == "":
            npyscreen.notify_confirm("Table name cannot be empty", editw=1, wide=False)
        elif self.entries == []:
            npyscreen.notify_confirm("Please add atleast one column", editw=1, wide=False)
        elif executeQuery(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name.value}'", self.parentApp.database_connection) != []:
            npyscreen.notify_confirm(f"Table: {self.table_name.value} already exists", editw=1, wide=False)
        else:
            executeQuery(f"CREATE TABLE {self.table_name.value} ({', '.join([f'{x[0]} {x[1]}' for x in self.entries])})", self.parentApp.database_connection)
            self.parentApp.change_form("TABLE")
            npyscreen.notify_wait(f"Created Table {self.table_name.value}", wide=False)
        
        
class TableMenu(npyscreen.FormBaseNew):
    def create(self):
        self.name = "View Table"
        
def main():
    MyTUI().run()

if __name__ == '__main__':
    main()