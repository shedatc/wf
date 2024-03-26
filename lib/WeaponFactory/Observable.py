class Observable:

    def __init__(self):
        self.observers = []

    def register_observer(self, observer):
        self.observers.append(observer)

    # Observer must implement the following:
    #     def notify(self, event, observable, **kwargs)
    def notify_observers(self, event, **kwargs):
        for o in self.observers:
            o.notify(event, self, **kwargs)
