import threading


class Singleton:

    singleton_lock = threading.Lock()
    singleton_instance = None

    # define the classmethod
    @classmethod
    def instance(cls):
        # check for the singleton instance
        if not cls.singleton_instance:
            with cls.singleton_lock:
                if not cls.singleton_instance:
                    cls.singleton_instance = cls()

        # return the singleton instance
        return cls.singleton_instance
