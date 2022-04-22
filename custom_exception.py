class SingletonException(Exception):
    """Exception raised if there are more than one instance to a singlton.
        Attributes:
            salary -- input salary which caused the error
            message -- explanation of the error
        """

    def __init__(self, cls_name, message="SingletonException: There is already one instance of this object"):
        self.__cls_name = cls_name
        self.__message = message
        super().__init__(self.__message)

    def __str__(self):
        return f"{self.__cls_name} {self.__message}"