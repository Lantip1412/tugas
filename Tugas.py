import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView

# Koneksi ke database MySQL
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='tugas'
    )

# Fungsi register dan login
def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO daftar (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
    conn.commit()
    cursor.close()
    conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM daftar WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user[0], password):
        return user[1]
    return None

def add_customer(nama, username, tgl, tgl_lahir, gender):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customer (nama, username, tgl, tgl_lahir, gender) VALUES (%s, %s, %s, %s, %s)", 
                (nama, username, tgl, tgl_lahir, gender))
    conn.commit()
    cursor.close()
    conn.close()

def get_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama, username, tlp, tgl_lahir, gender FROM customer")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return customers

# Fungsi untuk membuat popup
def show_popup(title, message, on_dismiss=None):
    layout = BoxLayout(orientation='vertical', padding=10)
    layout.add_widget(Label(text=message))
    close_button = Button(text='Close', size_hint_y=0.3)
    layout.add_widget(close_button)
    popup = Popup(title=title, content=layout, size_hint=(0.8, 0.4))
    close_button.bind(on_press=popup.dismiss)
    if on_dismiss:
        popup.bind(on_dismiss=on_dismiss)
    popup.open()

# Tampilan pendaftaran akun
class RegisterScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'

        self.username_input = TextInput(hint_text='Username')
        self.password_input = TextInput(hint_text='Password', password=True)
        self.role_spinner = Spinner(
            text='Select Role',
            values=('admin', 'customer')
        )
        self.add_widget(Label(text='Register Account'))
        self.add_widget(self.username_input)
        self.add_widget(self.password_input)
        self.add_widget(self.role_spinner)

        self.register_button = Button(text='Register')
        self.register_button.bind(on_press=self.register)
        self.add_widget(self.register_button)

        self.back_button = Button(text='Kembali')
        self.back_button.bind(on_press=self.go_to_login)
        self.add_widget(self.back_button)

    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        role = self.role_spinner.text.lower()
        if not username or not password or role == 'select role':
            show_popup('Error', 'Please enter all fields and select a role')
            return
        register_user(username, password, role)
        show_popup('Success', 'Registered successfully', on_dismiss=self.go_to_login)

    def go_to_login(self, instance):
        login_screen = self.screen_manager.get_screen('login').children[0]
        login_screen.reset_fields()
        self.screen_manager.current = 'login'

    def reset_fields(self):
        self.username_input.text = ''
        self.password_input.text = ''
        self.role_spinner.text = 'Select Role'

# Tampilan login menggunakan Kivy
class LoginScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'

        self.username_input = TextInput(hint_text='Username')
        self.password_input = TextInput(hint_text='Password', password=True)
        self.add_widget(Label(text='Login'))
        self.add_widget(self.username_input)
        self.add_widget(self.password_input)

        self.login_button = Button(text='Login')
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)

        self.register_button = Button(text='Go to Register')
        self.register_button.bind(on_press=self.go_to_register)
        self.add_widget(self.register_button)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if not username or not password:
            show_popup('Error', 'Please enter both username and password')
            return
        role = login_user(username, password)
        if role:
            self.reset_fields()
            if role == 'admin':
                self.screen_manager.current = 'admin'
            elif role == 'customer':
                self.screen_manager.current = 'customer'
        else:
            show_popup('Error', 'Invalid credentials')

    def go_to_register(self, instance):
        register_screen = self.screen_manager.get_screen('register').children[0]
        register_screen.reset_fields()
        self.screen_manager.current = 'register'

    def reset_fields(self):
        self.username_input.text = ''
        self.password_input.text = ''

# Tampilan Admin
class AdminScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.add_widget(Label(text='Admin Menu'))
        view_data_button = Button(text='View Data')
        view_data_button.bind(on_press=self.go_to_view_data)
        self.add_widget(view_data_button)
        add_customer_button = Button(text='Add Customer')
        add_customer_button.bind(on_press=self.go_to_add_customer)
        self.add_widget(add_customer_button)

        self.back_button = Button(text='Kembali')
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def go_to_view_data(self, instance):
        self.screen_manager.current = 'view_data'

    def go_to_add_customer(self, instance):
        self.screen_manager.current = 'add_customer'

    def go_back(self, instance):
        self.screen_manager.current = 'login'

# Tampilan Customer
class CustomerScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.add_widget(Label(text='Customer View Data'))

        self.back_button = Button(text='Kembali')
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def go_back(self, instance):
        self.screen_manager.current = 'login'

# Tampilan Add Customer
class AddCustomerScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.nama_input = TextInput(hint_text='Nama')
        self.username_input = TextInput(hint_text='Username')
        self.tgl_input = TextInput(hint_text='No Telepon')
        self.tgl_lahir_input = TextInput(hint_text='Tanggal Lahir (YYYY-MM-DD)')
        self.gender_spinner = Spinner(
            text='Select Gender',
            values=('male', 'female')
        )

        self.add_widget(Label(text='Add Customer'))
        self.add_widget(self.nama_input)
        self.add_widget(self.username_input)
        self.add_widget(self.tgl_input)
        self.add_widget(self.tgl_lahir_input)
        self.add_widget(self.gender_spinner)

        self.add_customer_button = Button(text='Add Customer')
        self.add_customer_button.bind(on_press=self.add_customer)
        self.add_widget(self.add_customer_button)

        self.back_button = Button(text='Kembali')
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def add_customer(self, instance):
        nama = self.nama_input.text
        username = self.username_input.text
        tlp = self.tgl_input.text
        tgl_lahir = self.tgl_input.text
        gender = self.gender_spinner.text.lower()
        if not nama or not username or not tlp or not tgl_lahir or gender == 'select gender':
            show_popup('Error', 'Please fill in all fields and select gender')
            return
        add_customer(nama, username, tlp, tgl_lahir, gender)

        show_popup('Success', 'Customer added successfully', on_dismiss=self.go_back)

    def go_back(self, instance):
        self.screen_manager.current = 'admin'

# Tampilan View Data
class ViewDataScreen(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = 'vertical'

        self.add_widget(Label(text='View Data'))
        self.load_data()

        self.back_button = Button(text='Kembali')
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def load_data(self):
        customers = get_customers()
        data_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        data_layout.bind(minimum_height=data_layout.setter('height'))

        for customer in customers:
            customer_info = f"Name: {customer[0]}, Username: {customer[1]}, Phone: {customer[2]}, Birth Date: {customer[3]}, Gender: {customer[4]}"
            data_layout.add_widget(Label(text=customer_info, size_hint_y=None, height=40))

        scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))
        scroll_view.add_widget(data_layout)
        self.add_widget(scroll_view)

    def go_back(self, instance):
        self.screen_manager.current = 'admin'

# Aplikasi menggunakan ScreenManager
class UserManagementApp(App):
    def build(self):
        sm = ScreenManager()
        
        login_screen = Screen(name='login')
        login_screen.add_widget(LoginScreen(screen_manager=sm))
        sm.add_widget(login_screen)
        
        register_screen = Screen(name='register')
        register_screen.add_widget(RegisterScreen(screen_manager=sm))
        sm.add_widget(register_screen)
        
        admin_screen = Screen(name='admin')
        admin_screen.add_widget(AdminScreen(screen_manager=sm))
        sm.add_widget(admin_screen)

        customer_screen = Screen(name='customer')
        customer_screen.add_widget(CustomerScreen(screen_manager=sm))
        sm.add_widget(customer_screen)

        add_customer_screen = Screen(name='add_customer')
        add_customer_screen.add_widget(AddCustomerScreen(screen_manager=sm))
        sm.add_widget(add_customer_screen)

        view_data_screen = Screen(name='view_data')
        view_data_screen.add_widget(ViewDataScreen(screen_manager=sm))
        sm.add_widget(view_data_screen)

        return sm

if __name__ == '__main__':
    UserManagementApp().run()
