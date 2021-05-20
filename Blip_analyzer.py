import numpy as np

# # from BaseDriver import LabberDriver


class Driver(LabberDriver):
    """Detect blips in single shot traces"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection."""
        self.Blip = Blip()
        self.Blip.__init__()
        self.Blip.sampling_rate = self.getValue("Sampling Rate")

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation."""
        if "Search Window 1" in quant.name:
            self.Blip.searchwindow[0] = value
        elif "Search Window 2" in quant.name:
            self.Blip.searchwindow[1] = value
        else:
            name = quant.set_cmd
            type(self.Blip).__dict__[name].__set__(self.Blip, value)

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation."""
        name = quant.get_cmd
        return getattr(Blip,name)

class Blip:
    def __init__(self):
        self.sampling_rate = 1.8e9
        self.searchwindow = np.array([np.nan,np.nan])
        self.refwindow = np.array([])
        self.threshold = np.nan
        self.reflevel = np.nan
        self.trace = np.array([])
        self.segmentlength = 1
        self.probability = np.nan
        self.I_avg = np.nan
        self._count = np.nan
        self._searchindex = np.array([])

    @property
    def searchwindow(self):
        return self._searchwindow

    @searchwindow.setter
    def searchwindow(self, value):
        if value is not None:
            self._searchindex = value*self.sampling_rate
            self._searchindex = self._searchindex.astype(int)
            self._searchwindow = value

    @property
    def _searchindex(self):
        return self.__searchindex

    @_searchindex.setter
    def _searchindex(self, value):
        self.__searchindex = value

    @property
    def refwindow(self):
        return self.refwindow

    @refwindow.setter
    def refwindow(self, value):
        self._refwindow = value

    @property
    def _refindex(self):
        self._refindex = self.refwindow*self.sampling_rate
        return self._refindex

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = value

    @property
    def trace(self):
        return self._trace

    @trace.setter
    def trace(self, value):
        self._trace = value

    @property
    def segmentlength(self):
        return self._segmentlength

    @segmentlength.setter
    def segmentlength(self, value):
        self._segmentlength = value
        if self.trace.size > 0:
            trace = self.update()
            self.trace = trace

    @property
    def reflevel(self):
        return self._reflevel

    @reflevel.setter
    def reflevel(self, value):
        self._reflevel = value

    @property
    def probability(self):
        self.update()
        return self._probability

    @probability.setter
    def probability(self, value):
        self._probability = value

    @property
    def I_avg(self):
        self.update()
        return self._I_avg

    @I_avg.setter
    def I_avg(self, value):
        self._I_avg = value

    @property
    def _count(self):
        return self.__count

    @_count.setter
    def _count(self, value):
        self.__count = value

    def update(self):
        print("Updated???")
        trace = self.trace
        L = self.segmentlength
        trace = np.append(
            trace, np.nan*np.zeros(int(np.ceil(trace.size/L)*L-trace.size)))
        trace = trace.reshape(int(np.ceil(trace.size/L)), L)

        if np.isnan(self.reflevel) == 0:
            trace = trace - self.reflevel
            # # Search for blip
        if self.searchwindow.size > 1:
            searchind = self._searchindex
            self._count = np.sum(
                np.any(trace[:, searchind[0]:searchind[1]] > self.threshold, axis=1))
            self.probability = self._count/trace.shape[0]
            self.I_avg = np.nanmean(trace[:, searchind[0]:searchind[1]])

        return trace


if __name__ == "__main__":
    pass
