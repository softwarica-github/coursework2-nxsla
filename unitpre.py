import unittest
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os

def create_new_file_and_save():

 class TestCreateNewFileAndSave(unittest.TestCase):
    def setUp(self):
        import sqlite3
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE files (name TEXT, content TEXT, date_created TEXT)''')

    def tearDown(self):
        self.conn.close()

    def test_create_new_file_and_save(self):
        new_file_dialog = tk.Toplevel()
        new_file_content = tk.Text(new_file_dialog)
        new_file_content.insert(tk.END, "Test content")
        test_file_path = "test_file.txt"
        filedialog.asksaveasfilename = lambda **args: test_file_path
        create_new_file_and_save()
        with open(test_file_path, "r") as test_file:
            content = test_file.read()
            self.assertEqual(content, "Test content")
            
        self.cursor.execute('SELECT * FROM files')
        row = self.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], os.path.basename(test_file_path))
        self.assertEqual(row[1], "Test content")
        self.assertIsNotNone(datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
        new_file_dialog.destroy()
        os.remove(test_file_path)

if __name__ == '__main__':
    unittest.main()
