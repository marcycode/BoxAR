class Event():
    """
    Class representing events/functions that can be hooked in at runtime.
    Takes in a name, tickCount, function, and optional list of parameters.
    The func parameter should be a callable function that takes in the parameters specified in paramList.
    paramList is a list of strings representing the names of the parameters that the function takes in.
    tickRate specifies the frequency at which the function should be called.
    """

    def __init__(self, name: str, tickRate: int, func: callable, paramList: list[str] = []):
        self.name = name
        self.tickRate = tickRate
        self.func = func
        self.paramList = paramList


class EventManager():
    """
    The EventManager class allows registering and running events at runtime.
    Events are executed at their specified tickRate.
    Parameters to be passed in to the events are specified in the event's paramList.
    This must match the parameter names exactly as they are passed in as keyword arguments.
    """

    def __init__(self):
        self.events: list[Event] = []
        self.tickCount = 0
        self.maxTickCount = 0

    def addEvent(self, name, tickCount, func, paramList=[]):
        if name in [e.name for e in self.events]:
            raise ValueError(f"Event with name {name} already exists")
        self.events.append(Event(name, tickCount, func, paramList))
        if tickCount > self.maxTickCount:
            self.maxTickCount = tickCount

    def update(self, globalContext: dict):
        self.runEvents(globalContext)
        self.tickCount += 1
        if self.tickCount >= self.maxTickCount:
            self.tickCount = 0

    def removeEvent(self, name):
        for event in self.events:
            if event.name == name:
                if event.tickRate == self.maxTickCount:
                    self.maxTickCount = max(
                        [e.tickRate for e in self.events if e.name != name])
                self.events.remove(event)

    def runEvent(self, name: str, globalContext: dict):
        """
        Executes a single event in the handler. Bypasses the tickRate calculation.
        """
        for event in self.events:
            if event.name == name:
                # Extract only the relevant context variables for the function
                # Duplicated code; can be refactored later
                funcContext = {}
                for paramName in event.paramList:
                    if paramName not in globalContext:
                        raise ValueError(
                            f"Parameter {paramName} not found in global context. Required for event {event.name}")

                    funcContext[paramName] = globalContext[paramName]

                event.func(**funcContext)

    def runEvents(self, globalContext: dict):
        """
        Executes all events in the handler. 
        """
        for event in self.events:
            if self.tickCount % event.tickRate == 0:
                # Extract only the relevant context variables for the function
                # Duplicated code; can be refactored later
                funcContext = {}
                for paramName in event.paramList:
                    if paramName not in globalContext:
                        raise ValueError(
                            f"Parameter {paramName} not found in global context. Required for event {event.name}")

                    funcContext[paramName] = globalContext[paramName]

                event.func(**funcContext)
