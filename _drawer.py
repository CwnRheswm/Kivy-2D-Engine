from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.uix.togglebutton import ToggleButton

'''
---------------------
Drawer() should be a basic instantiation of a drawer that can accept enough 'variables'
to build a new drawer from scratch without it being hardcoded in the Drawer() method.

Tray() holds the actual buttons for a Drawer(), and also should be able to be built from the
outside, not hardcoded. Button bindings should be passed into Tray() and states should be
returned from Tray(), which would also need to be returned through Drawer() to get up to
B/WBoard()

Tray() buttons.on_release calls self.parent.parent() [self.Drawer.BlackBoard()]
---------------------
'''
WIDTH = 100
HEIGHT = 100

class Tray(GridLayout):
    def __init__(self, ,**kwargs):
        GridLayout.__init__(self)

        self.save = False

        if 'rows' in kwargs.keys():
            self.rows = kwargs['rows']
        elif 'cols' in kwargs.keys():
            self.cols = kwargs['cols']
        
        self.bind(minimum_width = self.setter('width')) #allow for setting width
        self.bind(minimu_height = self.setter('height')) #allow for setting height
            
        '''for btn in btns:
            add = ToggleButton(text = btn, size_hint_y = None, height = HEIGHT,
                               size_hint_x = None, width = WIDTH)
            add.bind(on_release = self.btn_inst) #pass btn instance to on_release
            self.add_widget(add)'''

    def btn_inst(self, instance):
        try: self.parent.parent.on_release(instance) #pass the pressed button to BlackBoard() and let it control the action
        except: pass

    def clear_widgets(self):
        self.clear_widgets()

    def add_btns(self, btns, **kwargs):
        for btn in btns:
            add = ToggleButton(text = btn, size_hint_y = None, height = HEIGHT,
                               size_hint_x = None, width = WIDTH)
            
            if btn in kwargs.keys():
                if 'color' in kwargs[btn].keys():
                    add.background_color = kwargs[btn]['color']
                if 'down' in kwargs[btn].keys():
                    add.background_color = kwargs[btn]['down']
                if 'normal' in kwargs[btn].keys():
                    add.background_color = kwargs[btn]['normal']
                if 'border' in kwargs[btn].keys():
                    add.background_color = kwargs[btn]['border']
            else:
                if 'color' in kwargs.keys():
                    add.background_color = kwargs['color']
                if 'down' in kwargs.keys():
                    add.background_down = kwargs['down']
                if 'normal' in kwargs.keys():
                    add.background_normal = kwargs['normal']
                if 'border' in kwargs.keys():
                    add.border = kwargs['border']
                
            add.bind(on_release = self.btn_inst())
            self.add_widget(add)
            

class Drawer(ScrollView):
    #def __init__(self, border, btns): #change to accept any size, positional arguments to make it more flexible
    def __init__(self, size, opened, covered, scroll):
        '''
        size is a tuple of (width, height)
        opened is a tuple of (center_x, center_y) detailing its opened position
        closed is a tuple of (center_x, center_y) detailing its closed position
        scroll is a list of [do_scroll_x[True/False], do_scroll_y[True/False]]
        btns is a dictionary ?? of btns to pass Tray()...
        '''
        ScrollView.__init__(self)

        self.bar_width = 0

        self.size = size
        self.open = opened
        self.close = closed
        self.center = self.open
        self.do_scroll_x, self.do_scroll_y = scroll[0], scroll[1]
        self.track = []

        if self.size[0] > self.size[1]:
            self.tray = Tray(rows = 1)
        elif self.size[1] < self.size[0]:
            self.tray = Tray(cols = 1)
        self.add_widget(self.tray)

    border = border
    size_hint = None, None
    clasped = False
    auto_bring_to_front = True
    hidden = False

    def collide_ghost(self, x, y):
        if (x > self.open[0] and x < self.close[0]) or
        (x < self.open[0] and x > self.close[0]) or
        (y > self.open[1] and y < self.close[1]) or
        (y < self.open[1] and y > self.open[1]):
            return True
        
    def check_clasped(self, x, y):
        if self.collide_point(x, y):
            self.clasped = True
        elif self.collide_ghost(x, y) == True:
            self.clasped = None
        else:
            self.clasped = False

    def on_touch_down(self, touch):
        self.check_clasped(touch.x, touch.y)

        super(Drawer, self).on_touch_down(touch)

    def constrain_limits(self):
        if self.x < Window.width - self.width:
            self.x = Window.width - self.width
        elif self.x > Window.width:
            self.x = Window.width
        elif self.y < Window.height - self.height:
            self.y = Window.height - self.height
        elif self.y > Window.height:
            self.y = Window.height

    def slide(self, x, y):
        if self.do_scroll_x = True:
            move = x
        else:
            move = y
            
        if self.mode == 'unknown':
            self.track.append(round(move))
            if len(self.track) > 2:
                self.track.remove(self.track[0])
            if len(self.track) > 1:
                if self.do_scroll_x == True:
                    if self.track[1] > self.track[0]:
                        self.x += abs(self.track[0] - self.track[1])
                    elif self.track[1] < self.track[0]:
                        self.x -= abs(self.track[0] - self.track[1])
                elif self.do_scroll_y == True:
                    if self.track[1] > self.track[0]:
                        self.y += abs(self.track[0] - self.track[1])
                    elif self.track[1] < self.track[0]:
                        self.y -= abs(self.track[0] - self.track[1])

    mode = None

    def check_mode(self, touch):
        if self.clasped == True and self.mode == None:
            for key in touch.ud.keys():
                if type(key) == str and key.startswith('sv.'):
                    self.mode = touch.ud[key]['mode']

        elif self.clasped == None:
            self.mode = 'unknown'
        elif self.clasped == False:
            self.mode = None
                    
    def on_touch_move(self, touch):
        self.check_mode(touch)
        self.slide(touch.x, touch.y)
        self.constrain_limits()

        super(Drawer, self).on_touch_move(touch)

    def hide(self):
        if self.hidden == True:
            self.center = self.close
        elif self.hidden == False:
            self.center = self.open
            
    def release_clasp(self):
        if self.clasped == True:
            self.clasped = False
            self.mode = None

    def on_touch_up(self, touch):
        self.track = []
        self.release_clasp()
        super(Drawer, self).on_touch_up(touch)
        if self.collide_ghost(touch.x, touch.y):
            self.hidden = True
        self.hide()
