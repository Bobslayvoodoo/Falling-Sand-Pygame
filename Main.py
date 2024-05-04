import pygame
import random
import math
pygame.init()

# Classes
class Box():
    def __init__(self):
        self.__ObjectQueue = []
        self.__Inside = []
        self.CurrentElementNumber = 0
        self.PlaceRadius = 1
        self.__CurrentPlacing = PlaceableElementsList[self.CurrentElementNumber]
        self.__M2Debouce = 0
        self.__M2Cooldown = 200
        self.__PauseDebouce = 0
        self.__PauseCooldown = 200
        self.__Temperature = 15
        
        self.__Buttons = []
        self.__ButtonYSize = 50
        self.__Paused = False
        for y in range((ScreenHeight-self.__ButtonYSize)//TileSize):
            self.__Inside.append([])
            for x in range(ScreenWidth//TileSize):
                self.__Inside[-1].append(VOID)

    def MouseToCoords(self,MousePos):
        
        if MousePos[1] > self.__ButtonYSize:
            PosY = ((MousePos[1]-self.__ButtonYSize) // TileSize)
            PosX = MousePos[0] // TileSize
            InBox = True
        else:
            PosX = MousePos[0]
            PosY = MousePos[1]
            InBox = False

        return PosX,PosY,InBox
            
            

    def GetCirclePos(Center,Radius):
        Positions = []
        CenterX = Center[0]
        CenterY = Center[1]
        IntRadius = int(math.ceil(Radius))
        for NewY in range(CenterY-IntRadius,CenterY+IntRadius):
            for NewX in range(CenterX-IntRadius,CenterX+IntRadius):
                Distance = math.sqrt(((CenterX-NewX)**2)+((CenterY-NewY)**2))
                if Distance < Radius:
                    Positions.append((NewX,NewY))

        return Positions

    def GetObjectFromPos(self,Pos):
        if 0 <= Pos[0] < len(self.__Inside[0]) and 0 <= Pos[1] < len(self.__Inside):
            return self.__Inside[Pos[1]][Pos[0]]
        else:
            return EDGE

    def FindInDirection(self,StartPos,Direction,Length,Target):
        for Progress in range(1,Length+1):
            CurrentPosition = (StartPos[0] + Direction[0]*Progress,StartPos[1] + Direction[1]*Progress)
            CurrentObject = self.GetObjectFromPos(CurrentPosition)
            if CurrentObject == Target:
                return CurrentPosition
            elif type(CurrentObject).__mro__[-2] == Matter and CurrentObject.Element == Target:
                return CurrentPosition
                      
        return None
            

    def GetTemperature(self):
        return self.__Temperature

    def RemoveAtPos(self,Pos):
        Object = self.GetObjectFromPos(Pos)
        if Object != EDGE:
            self.__ObjectQueue.remove(Object)
            self.__Inside[Pos[1]][Pos[0]] = VOID

    def ChangeTempAtPos(self,Pos,Change,Limit):
        Object = self.GetObjectFromPos(Pos)
        if Object == EDGE or Object ==VOID:
            return False
        Object.ChangeTemp(Change,Limit)
        return True

    def Move(self,MatterObject,RelativePos):
        MatterX,MatterY = MatterObject.GetPos()
        DestinationX = MatterX + RelativePos[0]
        DestinationY = MatterY + RelativePos[1]
        DestinationObject = self.GetObjectFromPos((DestinationX,DestinationY))
        if DestinationObject == EDGE:
            return False
        if DestinationObject == VOID or DestinationObject.CanReplace(MatterObject,RelativePos):
            self.__Inside[DestinationY][DestinationX] = MatterObject
            MatterObject.SetPos((DestinationX,DestinationY))
            self.__Inside[MatterY][MatterX] = DestinationObject
            if DestinationObject != VOID:
                DestinationObject.SetPos((MatterX,MatterY))
            return True
        return False
        
    def CreateAtPos(self,Pos,Type,Temperature=None):
        if not Type in Elements.keys():
            if self.GetObjectFromPos(Pos) != VOID:
                self.RemoveAtPos(Pos)
            return
        NewElement = Elements[Type]
        if self.GetObjectFromPos(Pos) == VOID:
            if Temperature == None:
                Temperature = self.__Temperature
                
            NewElement = NewElement(Pos,self,Temperature)
            self.__ObjectQueue.append(NewElement)
            self.__Inside[Pos[1]][Pos[0]] = NewElement
            

    def Tick(self):
        if not self.__Paused:
            for CurrentT in self.__ObjectQueue:
                CurrentT.Tick()

        
    def CheckForUserInputs(self):
        Mouse = pygame.mouse.get_pressed()
        MousePos = pygame.mouse.get_pos()
        PosX,PosY,Inside = self.MouseToCoords(MousePos)
        if Mouse[0]:
            if Inside:
                if self.PlaceRadius > 1:
                    Positions = Box.GetCirclePos((PosX,PosY),self.PlaceRadius)
                    for Pos in Positions:
                        self.CreateAtPos(Pos,self.__CurrentPlacing)
                else:
                    self.CreateAtPos((PosX,PosY),self.__CurrentPlacing)
            else:
                for B in self.__Buttons:
                    B.CheckForSelect((PosX,PosY))
        if Mouse[2]:
            if pygame.time.get_ticks() - self.__M2Debouce > self.__M2Cooldown:
                self.__M2Debouce = pygame.time.get_ticks()
                print(f"Your mouse is at {PosX,PosY} and is{'' if Inside else ' not'} inside the box")

        Buttons = pygame.key.get_pressed()
        NewRadius = self.PlaceRadius
        #Numbers:
        if Buttons[pygame.K_1]:
            NewRadius = 1
        elif Buttons[pygame.K_2]:
            NewRadius = 1.1
        elif Buttons[pygame.K_3]:
            NewRadius = 1.8
        elif Buttons[pygame.K_4]:
            NewRadius = 3.2
        elif Buttons[pygame.K_5]:
            NewRadius = 5
        elif Buttons[pygame.K_6]:
            NewRadius = 6
        elif Buttons[pygame.K_7]:
            NewRadius = 7
        elif Buttons[pygame.K_8]:
            NewRadius = 8
        elif Buttons[pygame.K_9]:
            NewRadius = 9
        elif Buttons[pygame.K_0]:
            NewRadius = 100
        elif Buttons[pygame.K_SPACE]:
            
            if pygame.time.get_ticks() - self.__PauseDebouce > self.__PauseCooldown:
                self.__PauseDebouce = pygame.time.get_ticks()
                self.__Paused = not self.__Paused

        self.PlaceRadius = NewRadius

    def ChangeCurrentPlacing(self,Change):
        if type(Change) == int:
            self.CurrentElementNumber += Change
            self.CurrentElementNumber = self.CurrentElementNumber % len(PlaceableElementsList)
            self.__CurrentPlacing = PlaceableElementsList[self.CurrentElementNumber]
            print(self.__CurrentPlacing)
        elif type(Change) == str:
            self.CurrentElementNumber = PlaceableElementsList.index(Change)
            self.__CurrentPlacing = Change
            print(self.__CurrentPlacing)
            

    def SetUpButtons(self):
        YSize = 50
        XSize = int(ScreenWidth // len(PlaceableElementsList))
        for X,Element in enumerate(PlaceableElementsList):
            if Element in Elements:
                El = Elements[Element]((0,0),self,self.__Temperature)
            else:
                El = "DELETE"
            NewButton = Button(self,El,X*XSize,0,XSize,YSize)
            self.__Buttons.append(NewButton)

    def Draw(self):
        self.CheckForUserInputs()
        for Y,Row in enumerate(self.__Inside):
            for X,T in enumerate(Row):
                if T != VOID:
                    Rect = pygame.Rect(X*TileSize,(Y*TileSize)+self.__ButtonYSize,TileSize,TileSize)
                    pygame.draw.rect(Screen,T.Colour,Rect)
        for B in self.__Buttons:
            B.Draw()

class Button:
    def __init__(self,ParentBox,ElementObject,StartX,StartY,XSize,YSize):
        self.ParentBox = ParentBox
        self.__Rectangle = pygame.Rect(StartX,StartY,XSize,YSize)
        if ElementObject == "DELETE":
            self.__Colour = (255,255,0)
            self.__Element = ElementObject
        else:
            self.__Colour = ElementObject.DefaultColour
            self.__Element = ElementObject.Element

    def Draw(self):
        pygame.draw.rect(Screen,self.__Colour,self.__Rectangle)

    def CheckForSelect(self,MousePos):
        if self.__Rectangle.collidepoint(MousePos):
            self.ParentBox.ChangeCurrentPlacing(self.__Element)
        
        
        


class Matter():
    def __init__(self,Pos,Parent,Temperature):
        self._X = Pos[0]
        self._Y = Pos[1]
        self._ParentBox = Parent
        self._Temperature = Temperature
        self._TimeSinceLastMove = 0
        self._SkipChance = 0.25
        self._Skips = 0
        self._MaxSkips = 30
        self._Density = 1

    def GetPos(self):
        return (self._X,self._Y)

    def SetPos(self,NewPos):
        self._X = NewPos[0]
        self._Y = NewPos[1]

    def GetDensity(self):
        return self._Density

    def ChangeTemp(self,Change,Limit):
        self._Temperature += Change
        if Change >0 and self._Temperature > Limit:
            self.Temperature = Limit
        elif Change < 0 and self.Temperature < Limit:
            self.Temperature = Limit

    def CanReplace(self,Other,Direction=(0,0)):
        if Other:
            if self.Element == Other.Element:
                return False
            OtherDensity = Other.GetDensity()
            MyDensity = self.GetDensity()
            Operator = "=="
            if Direction[1] < 0: # other going up
                Operator = "<"
            elif Direction[1] > 0: # other going down
                Operator = ">"
            else:
                Operator = ">"

            Verdict = eval(f"OtherDensity {Operator} MyDensity")
            return Verdict
        return True

    def _DecideSkip(self):
        SkipChance = self._SkipChance
        MaxSkips = self._MaxSkips
        if self._TimeSinceLastMove > 60:
            SkipChance = 0.9
            MaxSkips *= 5
        if random.random() < SkipChance and self._Skips < MaxSkips:
            self._Skips += 1
            return True
        self._Skips = 0
        return False

    def Tick(self):
        if self._DecideSkip():
            return True
        self._TimeSinceLastMove += 1
        if self._Temperature < self._ParentBox.GetTemperature():
            self._Temperature += 0.2
        elif self._Temperature > self._ParentBox.GetTemperature():
            self._Temperature -= 0.2
        return

class Solid(Matter):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
    


class Falling(Solid):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._SkipChance = 0.1

    def Tick(self):
        if super().Tick():
            return True
        # Try down, down left then down right
        Directions = [(0,1)]
        if random.random() > 0.50:
            Directions.append((-1,1))
            Directions.append((1,1))
        else:
            Directions.append((1,1))
            Directions.append((-1,1))
            
        for Direction in Directions:
            if self._ParentBox.Move(self,Direction):
                self._TimeSinceLastMove = 0
                break
        self._TimeSinceLastMove += 1

class Sand(Falling):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "sand"
        self.DefaultColour = (200,170,0)
        Red = self.DefaultColour[0] + random.randrange(-5,5)
        Green = self.DefaultColour[1] + random.randrange(-1,1)
        Blue = self.DefaultColour[2]
        self.Colour = (Red,Green,Blue)
    def Tick(self):
        if super().Tick():
            return True

        if self._TimeSinceLastMove < 150:
            return
        for Y in range(1,10):
            AboveObject = self._ParentBox.GetObjectFromPos((self._X,self._Y-Y))
            if AboveObject == VOID or AboveObject == EDGE:
                break
            if AboveObject.Element != "sand":
                if AboveObject.Element == "sandstone":
                    self._ParentBox.RemoveAtPos(self.GetPos())
                    self._ParentBox.CreateAtPos(self.GetPos(),"sandstone",self._Temperature)

                break
        else:
            self._ParentBox.RemoveAtPos(self.GetPos())
            self._ParentBox.CreateAtPos(self.GetPos(),"sandstone",self._Temperature)
            

class Dirt(Falling):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "dirt"
        self.DefaultColour = (204,146,29)
        Red = self.DefaultColour[0] + random.randrange(-10,10)
        Green = self.DefaultColour[1] + random.randrange(-10,10)
        Blue = self.DefaultColour[2] + random.randrange(-10,10)
        self.Colour = (Red,Green,Blue)
        
    def Tick(self):
        if super().Tick():
            return True
        
        DirtAbove = 0
        for Y in range(1,10):
            AboveObject = self._ParentBox.GetObjectFromPos((self._X,self._Y-Y))
            if AboveObject == VOID or AboveObject == EDGE:
                break
            if AboveObject.Element == "water":
                self._ParentBox.RemoveAtPos(AboveObject.GetPos())
                self._ParentBox.RemoveAtPos(self.GetPos())
                self._ParentBox.CreateAtPos(self.GetPos(),"mud",self._Temperature)
                break
            elif AboveObject.Element == "dirt":
                if self._TimeSinceLastMove > 150:
                    DirtAbove += 1
            elif AboveObject.Element == "compresseddirt" and self._TimeSinceLastMove > 150:
                self._ParentBox.RemoveAtPos(self.GetPos())
                self._ParentBox.CreateAtPos(self.GetPos(),"compresseddirt",self._Temperature)
                break
            else:
                break
        else:
            if DirtAbove > 7:
                self._ParentBox.RemoveAtPos(self.GetPos())
                self._ParentBox.CreateAtPos(self.GetPos(),"compresseddirt",self._Temperature)
                
            

class Mud(Falling):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "mud"
        self.DefaultColour = (71,56,13)
        Red = self.DefaultColour[0] + random.randrange(-10,10)
        Green = self.DefaultColour[1] + random.randrange(-10,10)
        Blue = self.DefaultColour[2] + random.randrange(-10,10)
        self.Colour = (Red,Green,Blue)
        self._Density = 1
        self._SkipChance = 0.9
        self._MaxSkip = 200

        

class Salt(Falling):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "salt"
        self.DefaultColour = (200,200,200)
        Red = self.DefaultColour[0] + random.randrange(-10,10)
        Green = self.DefaultColour[1] + random.randrange(-10,10)
        Blue = self.DefaultColour[2] + random.randrange(-10,10)
        self.Colour = (Red,Green,Blue)


    def Tick(self):
        if super().Tick():
            return True
        AboveObject = self._ParentBox.GetObjectFromPos((self._X,self._Y-1))
        if AboveObject != VOID and AboveObject != EDGE and AboveObject.Element == "water":
            self._ParentBox.RemoveAtPos(AboveObject.GetPos())
            self._ParentBox.RemoveAtPos(self.GetPos())
            self._ParentBox.CreateAtPos(self.GetPos(),"saltwater",self._Temperature)

        
            

class Stationary(Solid):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._SkipChance = 0.1
        self._MaxSkips = 30
    def CanReplace(self,Other,Direction=(0,0)):
        return False

class Stone(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._SkipChance = 1
        self._MaxSkips = float("inf")
        self.Element = "stone"
        self.DefaultColour = (100,100,100)
        self.Colour = self.DefaultColour

class Sandstone(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._SkipChance = 1
        self._MaxSkips = float("inf")
        self.Element = "sandstone"
        self.DefaultColour = (150,130,0)
        self.Colour = self.DefaultColour

class CompressedDirt(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._SkipChance = 1
        self._MaxSkips = float("inf")
        self.Element = "compresseddirt"
        self.DefaultColour = (170,120,20)
        self.Colour = self.DefaultColour

class HeatElement(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "heatelement"
        self.DefaultColour = (255,0,0)
        self.Colour = self.DefaultColour
        self._MaxHeat = 200
        self._HeatRadius = 5
        
    def Tick(self):
        if super().Tick():
            return True
        Positions = Box.GetCirclePos((self._X,self._Y),self._HeatRadius)
        for Pos in Positions:
            self._ParentBox.ChangeTempAtPos(Pos,1,self._MaxHeat)

class Duplicator(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "duplicator"
        self.DefaultColour = (252, 3, 215)
        self.Colour = self.DefaultColour
        self._SkipChance = 0.25

    def Tick(self):
        
        if super().Tick():
            return True
        Original = self._ParentBox.GetObjectFromPos((self._X,self._Y-1))
        Duplicated = False
        if Original != VOID and type(Original) != Duplicator and Original != EDGE:
            self._ParentBox.CreateAtPos((self._X,self._Y+1),Original.Element)
            Duplicated = True

        if Duplicated:
            self._TimeSinceLastMove = 0

class Blackhole(Stationary):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "blackhole"
        self.DefaultColour = (252, 111, 3)
        self.Colour = self.DefaultColour
        self._SkipChance = 0.25

    def Tick(self):
        if super().Tick():
            return True
        Positions = Box.GetCirclePos((self._X,self._Y),5)
        Removed = False
        for Pos in Positions:
            Object = self._ParentBox.GetObjectFromPos(Pos)
            if type(Object) != Blackhole and Object != VOID and Object != EDGE:
                self._ParentBox.RemoveAtPos(Pos)
                Removed = True
        if Removed:
            self._TimeSinceLastMove = 0

class Liquid(Matter):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._Density = 0.5

    def Tick(self):
        if super().Tick():
            return True
        # Down then left then right
        for Direction in ((0,1),(-1,0),(1,0)):
            if self._ParentBox.Move(self,Direction):
                self._TimeSinceLastMove = 0
                break
        self._TimeSinceLastMove += 1
    



class Water(Liquid):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "water"
        self.DefaultColour = (0,0,189)
        Red = self.DefaultColour[0]
        Green = self.DefaultColour[1]
        Blue = self.DefaultColour[2] + random.randrange(-10,10)
        self.Colour = (Red,Green,Blue)

    def Tick(self):
        if super().Tick():
            return True
        if self._Temperature >= 125:
            self._ParentBox.RemoveAtPos(self.GetPos())
            self._ParentBox.CreateAtPos(self.GetPos(),"steam",Temperature=self._Temperature)
        

class SaltWater(Liquid):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "saltwater"
        self.DefaultColour = (75,75,189)
        Red = self.DefaultColour[0] + random.randrange(-10,10)
        Green = self.DefaultColour[1] + random.randrange(-10,10)
        Blue = self.DefaultColour[2] + random.randrange(-10,10)
        self.Colour = (Red,Green,Blue)
        self._Density = 0.51

class Gas(Matter):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self._Density = 0.1

    def Tick(self):
        if super().Tick():
            return True
        # Up then left then right
        for Direction in ((0,-1),(-1,0),(1,0)):
            if self._ParentBox.Move(self,Direction):
                self._TimeSinceLastMove = 0
                break
        self._TimeSinceLastMove += 1


class Steam(Gas):
    def __init__(self,Pos,Parent,Temperature):
        super().__init__(Pos,Parent,Temperature)
        self.Element = "steam"
        self.DefaultColour = (200,200,200)
        Red = self.DefaultColour[0] + random.randrange(-5,5)
        Green = self.DefaultColour[1] + random.randrange(-5,5)
        Blue = self.DefaultColour[2] + random.randrange(-5,5)
        self.Colour = (Red,Green,Blue)

    def Tick(self):
        if super().Tick():
            return True
        if self._Temperature < 75:
            self._ParentBox.RemoveAtPos(self.GetPos())
            self._ParentBox.CreateAtPos(self.GetPos(),"water")




# pre game
Elements = {"sand":Sand,
            "water":Water,
            "stone":Stone,
            "salt":Salt,
            "saltwater":SaltWater,
            "dirt":Dirt,
            "mud":Mud,
            "heatelement":HeatElement,
            "duplicator":Duplicator,
            "blackhole":Blackhole,
            "steam":Steam,
            "sandstone":Sandstone,
            "compresseddirt":CompressedDirt}
PlaceableElementsList = ["sand","water","stone","salt","dirt","heatelement","duplicator","blackhole","DELETE"]
ElementsList = list(Elements.keys())
VOID = " "
EDGE = "|"
Clock = pygame.time.Clock()
FPSLimit = 60
TileSize = 10
DisplayInfo = pygame.display.Info()
ScreenWidth = int(DisplayInfo.current_w*0.8) // TileSize * TileSize
ScreenHeight = int(DisplayInfo.current_h*0.8) // TileSize * TileSize
Screen = pygame.display.set_mode((ScreenWidth,ScreenHeight))
CurrentBox = Box()
CurrentBox.SetUpButtons()
Run = True
while Run:
    Clock.tick(FPSLimit)
    for Event in pygame.event.get():
        if Event.type == pygame.QUIT:
            Run = False

    Screen.fill((0,0,0))
    CurrentBox.Tick()
    CurrentBox.Draw()
    pygame.display.update()

pygame.quit()

    



    
