from abc import ABCMeta, abstractmethod


class ITransferMat(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def size(self):
        pass

