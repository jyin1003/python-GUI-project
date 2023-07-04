import tkinter as tk
from tkinter import filedialog # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

#View Classese 
class InfoBar (AbstractGrid):
    """A view class that inherits from AbstractGrid and tk.Canvas. It is a grid 
        with 2 rows and 3 columns, which displays information to the user 
        about the number of days elapsed in the game, as well as the player's 
        energy and money."""
    def __init__ (self, master: tk.Tk | tk.Frame) -> None:
        """
        Establishes the AbstractGrid with 2 rows and 3 columns and the 
        given width and height.
        
        Parameters:
            tk.Tk | tk.Frame: frame which displays the InfoBar
            tuple[int, int]: the number of rows and columns
            tuple[int, int]: width in pixels, height in pixels
            
        Return:
            None
        """
        super().__init__(master,(2,3),
                         (FARM_WIDTH + INVENTORY_WIDTH, INFO_BAR_HEIGHT))
        self._layout = [
            [None, None, None],
            [None, None, None]
        ]
        self._master = master        
    
    def redraw(self, day: int, money: int, energy: int) -> None: 
        """ 
        Clears the InfoBar and redraws it to display the provided day, 
        money, and energy.
           
        Parameters:
            int: days elapsed
            int: amount of money the player has
            int: amount of energy the player has. Resets to 100 with each
                new day
                     
        Return:
            None
        """
        self.clear()
        labels = {'00':'Day:', '01':'Money:', '02':'Energy:', 
                  '10': day, 
                  '11': '${0}'.format(money),
                  '12': energy,
                  '20':None, '21':None, '22':None}
        for i, row in enumerate(self._layout):
            for j, col in enumerate(row):
                key = '{0}{1}'.format(i,j) 
                if i == 0:
                    self.annotate_position((i,j),'{0}'.format(labels[key]),
                                            HEADING_FONT)
                else:
                    self.annotate_position((i,j),'{0}'.format(labels[key])) 

class FarmView(AbstractGrid):
    """A view class that inherits from AbstractGrid and tk.Canvas. Displays the
        farm map, player, and plants."""
    def __init__ (self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int], 
                  size:tuple[int, int], **kwargs) -> None:
        """
        Sets up the FarmView to be an AbstractGrid with the appropriate 
        dimensions and size.         

        Parameters:
            tk.Tk | tk.Frame: frame which displays the FarmView
            tuple[int, int]: the number of rows and columns
            tuple[int, int]: width in pixels, height in pixels
            
        Return:
            None
        """
        super().__init__(master, dimensions,size)
        self._master = master
        self._size = size
        self._imageCache = {}

    def get_mapped_image (self, image_name: str, size: tuple[int, int]) -> str:
        """
        Maps the image name from the images folder and then returns the image 
        for the given image_name, resized appropriately according to the given
        tuple dimensions.
        
        Parameters:
            str: name of the image
            tuple: width in pixels, height in pixels
        
        Return:
            str: map of the image from the images folder  
        """
        image_map = 'images/{0}'.format(image_name)
        image = get_image(image_map, size, self._imageCache)
        return image
    
    def redraw(self, ground: list[str], plants: dict[tuple[int, int], Plant],
        player_position: tuple[int, int], player_direction: str) -> None:
        """
        Clears the farm view, then creates images for the ground,
        then the plants, then the player. 
        
        Args:
            list[str]: map file converted into a list of strings
            dict[tuple[int, int], Plant]: a dictionary mapping positions to 
                                            plants.
            tuple[int, int]: player's current (row, col) position
            str: string of the player's current direction
        
        Return:
            None
        """
        self.clear()
        for row in ground:
            row_length = len(row)
        image_size = (int(self._size[0]/row_length),
                      int(self._size[0]/row_length))
        map = {'G': self.get_mapped_image(IMAGES[GRASS],image_size),
               'U': self.get_mapped_image(IMAGES[UNTILLED],image_size),
               'S':self.get_mapped_image(IMAGES[SOIL],image_size)
               }
        
        for i,row in enumerate(ground):
            for j, tile in enumerate(row):
                midpoint = self.get_midpoint((i,j))
                self.create_image(midpoint,image = map[tile])
        
        for plant in plants:
            position = plant
            midpoint = self.get_midpoint(position)
            plant_image_name = get_plant_image_name(plants[plant])
            plant_image = self.get_mapped_image(plant_image_name,image_size)
            self.create_image(midpoint, image = plant_image)
            
        player_start = self.get_midpoint(player_position)
        self.create_image(player_start,image = self.get_mapped_image
                                                    (IMAGES[player_direction],
                                                     image_size))

class ItemView(tk.Frame):
    """A view class that inherits from tk.Frame. Displays relevant information
        and buttons for a single item."""
    def __init__ (self, master: tk.Frame,
                item_name: str, amount: int, 
                select_command: Optional[Callable[[str], None]] = None, 
                sell_command: Optional[Callable[[str],None]] = None, 
                buy_command: Optional[Callable[[str], None]] = None) -> None:
        """
        Sets up the ItemView as a tk.Frame and creates the following internal 
        widgets: 
            A label containing the name of the item; 
            The amount of the item that the player has in their inventory; 
            The selling price of the item; 
            The buying price of the item (if the item can be bought); 
            If this item can be bought, a button for buying the item at the 
                listed buy price; 
            A button for selling the item at the listed sell price 
            (all items can be sold). 
        Also binds appropriate commands to each of the buttons and the select 
        command when either the ItemView frame or label is left clicked.
        
        Parameters:
            tk.Frame: frame which displays the ItemViews
            str: name of the item in the ItemView
            amount: amount of the item in the player's inventory
            select_command: callaback initated by the left-button click event
            sell_commmand: callback initiated by the sell button
            buy_command: callback initiated by the buy button
            
        Return:
            None
        """
        super().__init__(master, 
                         width = INVENTORY_WIDTH, 
                         height = FARM_WIDTH/6,
                         bg = INVENTORY_COLOUR,
                         highlightbackground = INVENTORY_OUTLINE_COLOUR, 
                         highlightthickness = 1
                        )
        self._master = master
        self._itemName = item_name
        self.bind("<Button-1>", select_command)
        
        self._labelFrame = tk.Frame(self, bg = INVENTORY_COLOUR)
        self._labelFrame.pack(side = tk.LEFT)
        self._nameLabel = tk.Label(self._labelFrame, text = '{0}: {1}'.
                                 format(self._itemName, amount),
                                 bg = INVENTORY_COLOUR)
        self._nameLabel.pack()
        self._nameLabel.bind("<Button-1>", select_command)
        self._sellLabel = tk.Label(self._labelFrame, 
                            text = 'Sell price: ${0}'.format
                            (SELL_PRICES[self._itemName]), 
                            bg=INVENTORY_COLOUR)
        self._sellLabel.pack()
        self._sellLabel.bind("<Button-1>", select_command)
            
        if self._itemName in SEEDS:
            self._buyLabel = tk.Label(self._labelFrame, 
                                      text = 'Buy price: ${0}'.format
                                    (BUY_PRICES[self._itemName]),
                                    bg = INVENTORY_COLOUR)
            self._buyLabel.bind("<Button-1>", select_command)
            buyButton = tk.Button(self, text = 'Buy', command = buy_command)
            buyButton.pack(side = tk.LEFT, ipadx=7, padx=5)
            sellButton = tk.Button(self, text = 'Sell', command = sell_command)
            sellButton.pack(side = tk.LEFT,ipadx=7, padx = 10)  
        else:
            self._buyLabel = tk.Label(self._labelFrame, 
                                    text = 'Buy price: $N/A',
                                    bg = INVENTORY_COLOUR)
            self._buyLabel.bind("<Button-1>", select_command)
            sellButton = tk.Button(self, text = 'Sell', command = sell_command)
            sellButton.pack(side = tk.LEFT, ipadx=7)  
        self._buyLabel.pack()    
    
    def update(self, amount: int, selected: bool = False) -> None:
        """
        Updates the text on the label, and the colour of this ItemView 
        appropriately.

        Parameters:
            int: amount of the item in the player's inventory
            bool: True if the selected item belongs to the itemView.
                Defaults to False.
                
        Return:
            None
        """
        self._nameLabel.configure(text = '{0}: {1}'.
                                 format(self._itemName, amount))
        if selected == True:
            self.config_colour('selected')
        if amount == 0:
            self.config_colour('empty')
        elif amount > 0 and selected == False:
            self.config_colour('unselected')
        
    def config_colour(self, action: str) -> None:
        """
        Configures the colour of the label frame and each label according to 
        the appropriate category.

        Parameters:
            str: 'selected' changes to the inventory selected colour
                 'unselected' changes to the default inventory colour
                 'empty' changes to the empty inventory colour
        
        Return:
            None
        """
        if action == 'selected':
                self.config(bg = INVENTORY_SELECTED_COLOUR)
                self._labelFrame.config(bg = INVENTORY_SELECTED_COLOUR)
                self._nameLabel.config(bg = INVENTORY_SELECTED_COLOUR)
                self._sellLabel.config(bg = INVENTORY_SELECTED_COLOUR)
                self._buyLabel.config(bg = INVENTORY_SELECTED_COLOUR)
        elif action == 'unselected':
                self.config(bg = INVENTORY_COLOUR)
                self._labelFrame.config(bg = INVENTORY_COLOUR)
                self._nameLabel.config(bg = INVENTORY_COLOUR)
                self._sellLabel.config(bg = INVENTORY_COLOUR)
                self._buyLabel.config(bg = INVENTORY_COLOUR)
        elif action == 'empty':
                self.config(bg = INVENTORY_EMPTY_COLOUR)
                self._labelFrame.config(bg = INVENTORY_EMPTY_COLOUR)
                self._nameLabel.config(bg = INVENTORY_EMPTY_COLOUR)
                self._sellLabel.config(bg = INVENTORY_EMPTY_COLOUR)
                self._buyLabel.config(bg = INVENTORY_EMPTY_COLOUR)  

    def get_name(self):
        """Returns the name of the item in the ItemView."""
        return self._itemName
        
#Controller Class
         
class FarmGame():
    """The controller class for the overall game. Responsible for creating and
    maintaining instances of the model and view classes, event handling, and 
    facilitating communication between the model and view classes.
    """
    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """
        Sets the title of the window.
        Creates the FarmModel instance.
        Creates an instance of the current map.
        Creates an instance of the player from the FarmModel
        Creates an instance of the player's inventory.
        Initialises an empty list to store each of the ItemViews.
        Creates the title banner.
        Creates instances of the view classes in the correct display format. 
        Creates a button to enable users to increment the day. When this button 
            is pressed, the model should advance to the next day with the view 
            classes reflecting appropriates changes in the model.
        Bind the keypresses.
        Calls the redraw method to ensure the view draws according to the
            current model state.

        Parameters:
            tk.Tk: master root frame of the entire window
            str: string that maps to the map file 
            
        Return:
            None
        """
        self._master = master
        self._master.title('Farm Game')
        self._farmModel = FarmModel(map_file)
        self._currentMap = self._farmModel.get_map()
        self._player = self._farmModel.get_player()
        self._inventory = self._player.get_inventory()
        self._itemViewList = []
        
        #create the banner
        headerFrame = tk.Frame(self._master)
        headerFrame.pack(side = tk.TOP, fill = tk.X)
        header = get_image('images/header.png', 
                           (FARM_WIDTH + INVENTORY_WIDTH, BANNER_HEIGHT),
                           IMAGES
                           )
        headerLabel = tk.Label(headerFrame, image=header)
        headerLabel.pack()
        
        #create the next day frame and button to ensure appropriate layout
        nextdayFrame = tk.Frame(self._master)
        nextdayFrame.pack(side = tk.BOTTOM)
        nextdayButton = tk.Button(nextdayFrame, text = 'Next day',
                                  command = self.next_day)
        nextdayButton.pack(side = tk.BOTTOM)
        
        #instantiate the InfoBar
        self._infoBar = InfoBar(self._master)
        self._infoBar.redraw(self._farmModel.get_days_elapsed(), 
                       self._player.get_money(),
                       self._player.get_energy())
        self._infoBar.pack(side = tk.BOTTOM)

        #instantiate the FarmView
        self._farmView = FarmView(self._master,
                            self._farmModel.get_dimensions(),
                            (FARM_WIDTH,FARM_WIDTH)) 
        self._farmView.pack(side=tk.LEFT)
        self._farmView.redraw(read_map(map_file),
                        self._farmModel.get_plants(),
                        self._farmModel.get_player_position(), 
                        self._farmModel.get_player_direction())         
        
        #instantiate the ItemViews
        inventoryFrame = tk.Frame(self._master, 
                                  width = INVENTORY_WIDTH,
                                  height = FARM_WIDTH)
        inventoryFrame.pack(side=tk.RIGHT)
        
        #create an ItemView instance for each of the six items
        
        for item in ITEMS:
            itemAmount = self.get_inventory_amt(item)
            itemView = ItemView(inventoryFrame, item, itemAmount,
                                lambda event, item = item: 
                                    self.select_item(item),
                                lambda item = item: 
                                    self.sell_item(item), 
                                lambda item = item: 
                                    self.buy_item(item))
            self._itemViewList.append(itemView)
        for each_view in self._itemViewList:
            each_view.pack()
            #prevent frame from re-adjausting
            each_view.pack_propagate(False) 
        
        self._master.bind("<KeyPress>", self.handle_keypress)
        self.redraw()
    
    def next_day(self):
        """Helper function: executes the two commands needed to advance to the 
            next day"""
        self._farmModel.new_day()
        self.redraw()
        
    def redraw(self):
        """Redraws the FarmView, InfoBar and each ItemView based on the current 
            model state."""
        self._farmView.redraw(self._currentMap,
                              self._farmModel.get_plants(),
                              self._farmModel.get_player_position(), 
                              self._farmModel.get_player_direction())   
        
        self._infoBar.redraw(self._farmModel.get_days_elapsed(), 
                             self._player.get_money(),
                             self._player.get_energy())
        
        for each_view in self._itemViewList:
            itemName = each_view.get_name()
            itemAmount = self.get_inventory_amt(itemName)
            #check if the ItemView is the selected item
            if itemName == self._player.get_selected_item():
                each_view.update(itemAmount, True)
            else: #otherwise unselect the current one
                each_view.update(itemAmount)
        
    def handle_keypress(self, event: tk.Event) -> None:
        """
        An event handler to be called when a keypress event occurs. The view
        then updates to reflect changes.

        Parameter:
            tk.Event: the key pressed
            
        Return:
            None
        """
        #handle player's movements
        player_moves = {'w':UP, 
                        'a':LEFT,
                        's':DOWN,
                        'd':RIGHT}
        if event.char in player_moves:
            self._farmModel.move_player(player_moves[event.char])
        
        #handle farming activities
        elif event.char == 't':
            self._farmModel.till_soil((self._farmModel.get_player_position()))
        elif event.char == 'u':
            self._farmModel.untill_soil((self._farmModel.
                                         get_player_position()))
        elif event.char == 'p':
            seeds = {'Potato Seed':PotatoPlant(), 
                      'Kale Seed': KalePlant(),
                      'Berry Seed': BerryPlant()}
            selected_item = self._player.get_selected_item()
            #test if the selected item is a seed
            if selected_item in seeds:
                plant = seeds[self._player.get_selected_item()]
                #test if the player's position is soil
                position = self._player.get_position()
                row, col = position
                if self._currentMap[row][col] == SOIL:
                    #test if there are seeds left to plant
                    if selected_item in self._inventory:
                        success = self._farmModel.add_plant(position, plant) 
                        #handle Exception errors to make sure only successful
                        #planting results in removing one seed from inventory
                        if success == True:
                            self._player.remove_item((selected_item,1))                              
        elif event.char == 'h':
            position = self._player.get_position()
            harvest = self._farmModel.harvest_plant(position)
            #handle Exception errors to ensure that only successful harvests
            #add to the player's inventory
            if harvest != None:
                self._player.add_item(harvest)
        elif event.char == 'r':
            position = self._player.get_position()
            self._farmModel.remove_plant(position)        
        
        self.redraw()
        
    def select_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView for item selection when 
        the left mouse button is clicked.
        
        Parameters:
            str: the item name of the selected ItemView
            
        Return:
            None        
        """
        itemAmount = self.get_inventory_amt(item_name)
        #only select itemviews with amounts above 0
        if itemAmount != 0:
            self._player.select_item(item_name)

        self.redraw()
                
    def buy_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView that can buy item, then 
        redraws the view to reflect changes.
        
        Parameters:
            str: the item name of the selected ItemView
            
        Return:
            None  
        """
        self._player.buy(item_name, BUY_PRICES[item_name])
        self.redraw()
    
    def sell_item(self, item_name: str) -> None:  
        """
        The callback to be given to each ItemView for selling items, then 
        redraws the view to reflect changes.
        
        Parameters:
            str: the item name of the selected ItemView
            
        Return:
            None  
        """
        self._player.sell(item_name, SELL_PRICES[item_name])
        self.redraw()          
    
    def get_inventory_amt (self, item_name: str) -> int:
        """
        Helper function: find an item's amount in the player's inventory.
        
        Parameters:
            str: the item name to find in the inventory 
            
        Return:
            int: the amount of the item in the inventory  
        """
        if item_name in self._inventory:
            itemAmount = self._inventory[item_name]
        else:
            itemAmount = 0
        return itemAmount
         
def play_game(root: tk.Tk, map_file: str) -> None:
    """Constucts the controller instance using given map file and the root 
        tk.Tk parameter. Keeps the root window open to listen for events."""
    FarmGame(root, map_file)
    root.mainloop()
      
def main() -> None:
    """Constructs the root tk.TK instance. Calls the play_game function,
        passing in the newly created root tk.Tk instance and the path to a 
        map file. """
    root = tk.Tk()
    root.geometry('{0}x{1}'.format(str(FARM_WIDTH + INVENTORY_WIDTH), \
                                str(FARM_WIDTH+INFO_BAR_HEIGHT+BANNER_HEIGHT)))
    #height of button is 35
    play_game(root, 'maps/map1.txt')
    

if __name__ == '__main__':
    main()
